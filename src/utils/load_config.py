import os
from dotenv import load_dotenv
import yaml
from pyprojroot import here
import shutil
import chromadb
import google.generativeai as genai

print("Environment variables are loaded:", load_dotenv())


class LoadConfig:
    def __init__(self) -> None:
        with open(here("configs/app_config.yml")) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)

        self.load_directories(app_config=app_config)
        self.load_llm_configs(app_config=app_config)
        self.load_gemini_models()
        self.load_chroma_client()
        self.load_rag_config(app_config=app_config)

        # Optional cleanup
        # self.remove_directory(self.uploaded_files_sqldb_directory)

    def load_directories(self, app_config):
        def _abs(path_value: str) -> str:
            return str(here(path_value))

        self.stored_csv_xlsx_directory = _abs(
            app_config.get("stored_csv_xlsx_directory", "data/csv_xlsx")
        )
        self.persist_directory = _abs(
            app_config.get("persist_directory", "data/chroma")
        )
        self.uploaded_files_sqldb_directory = _abs(
            app_config.get("uploaded_files_sqldb_directory", "data/uploaded_files_sqldb.db")
        )
        self.stored_csv_xlsx_sqldb_directory = _abs(
            app_config.get("stored_csv_xlsx_sqldb_directory", "data/csv_xlsx_sqldb.db")
        )

    def _resolve_model(self, requested: str | None) -> str:
        """Normalize model names away from unstable aliases like -latest/-002.
        Prefer stable IDs supported by google-generativeai.
        """
        if not requested or requested.strip() == "":
            return "gemini-2.5-flash"
        name = requested.strip()
        # Map '-latest' to base
        if name.endswith("-latest"):
            if "pro" in name:
                return "gemini-2.5-pro"
            return "gemini-2.5-flash"
        # Map specific version suffixes like -002/-001 to base
        if name.endswith("-002") or name.endswith("-001"):
            if name.startswith("gemini-2.5-pro"):
                return "gemini-2.5-pro"
            if name.startswith("gemini-2.5-flash") or name.startswith("gemini-2.0-flash"):
                return "gemini-2.5-flash"
        # Handle legacy model names
        if "gemini-1.5-flash-8b" in name or "gemini-2.5-flash-8b" in name:
            return "gemini-2.5-flash"
        if "gemini-1.5-flash" in name:
            return "gemini-2.5-flash"
        return name

    def load_llm_configs(self, app_config):
        # Prefer env override; normalize to stable model IDs
        requested = os.getenv("GEMINI_MODEL_NAME")
        self.model_name = self._resolve_model(requested)
        self.model_fallback_names = self._load_model_fallbacks(self.model_name)
        self.embedding_model_name = "models/text-embedding-004"
        print(f"[Gemini] Requested model: {requested!r} -> Using: {self.model_name}")
        print(f"[Gemini] Model fallback chain: {self.model_fallback_names}")

        self.agent_llm_system_role = app_config["llm_config"]["agent_llm_system_role"]
        self.rag_llm_system_role = app_config["llm_config"]["rag_llm_system_role"]
        self.temperature = app_config["llm_config"]["temperature"]

    def _load_model_fallbacks(self, primary_model: str) -> list[str]:
        """Build ordered model fallback list, starting with the configured model."""
        models: list[str] = [primary_model]

        env_fallbacks = os.getenv("GEMINI_MODEL_FALLBACKS", "")
        for chunk in env_fallbacks.replace(";", ",").replace("\n", ",").split(","):
            candidate = self._resolve_model(chunk.strip())
            if candidate and candidate not in models:
                models.append(candidate)

        # Safe defaults for free tier when 2.5-pro is exhausted/unavailable.
        for candidate in ["gemini-2.5-flash", "gemini-2.0-flash"]:
            resolved = self._resolve_model(candidate)
            if resolved and resolved not in models:
                models.append(resolved)

        return models

    def load_gemini_models(self):
        self.gemini_api_keys = self._load_gemini_api_keys()
        self.active_gemini_key_index = 0

        # Configure Gemini client with the first available key
        self._configure_gemini_client(0)
        print(f"[Gemini] google-generativeai SDK version: {getattr(genai, '__version__', 'unknown')}")

        # Keep existing attributes for compatibility with the rest of the codebase
        self.gemini_llm = genai.GenerativeModel(self.model_name)
        self.gemini_embed = genai

    def _load_gemini_api_keys(self) -> list[str]:
        keys: list[str] = []

        # Primary list variable supports comma/semicolon/newline separated keys.
        keys_blob = os.getenv("GEMINI_API_KEYS", "")
        for chunk in keys_blob.replace(";", ",").replace("\n", ",").split(","):
            key = chunk.strip()
            if key:
                keys.append(key)

        # Backward-compatible single-key variables.
        for name in ["GEMINI_API_KEY", "GEMINI_API_KEY_FALLBACK"]:
            key = os.getenv(name, "").strip()
            if key:
                keys.append(key)

        # De-duplicate while preserving order.
        unique_keys: list[str] = []
        for key in keys:
            if key not in unique_keys:
                unique_keys.append(key)

        if not unique_keys:
            raise ValueError(
                "Missing Gemini API key. Set GEMINI_API_KEY, or provide multiple keys via GEMINI_API_KEYS."
            )
        return unique_keys

    def _configure_gemini_client(self, key_index: int) -> None:
        api_key = self.gemini_api_keys[key_index]
        genai.configure(api_key=api_key)
        self.active_gemini_key_index = key_index
        print(f"[Gemini] Active API key index: {key_index + 1}/{len(self.gemini_api_keys)}")

    def _is_quota_or_rate_limit_error(self, err: Exception) -> bool:
        text = str(err).lower()
        return (
            "429" in text
            or "quota" in text
            or "rate limit" in text
            or "resource_exhausted" in text
            or "exceeded your current quota" in text
        )

    def _try_generate_with_key(self, prompt: str, key_index: int, model_name: str):
        self._configure_gemini_client(key_index)
        model = genai.GenerativeModel(model_name)
        self.gemini_llm = model
        return model.generate_content(prompt)

    def llm_unavailable_message(self) -> str:
        return (
            "The AI service is temporarily unavailable right now. "
            "Please try again in a minute."
        )

    def generate_content_with_fallback(self, prompt: str, extra_models: list | None = None):
        """
        Generate content with API-key and model fallback on quota/rate-limit errors.
        """
        models = list(self.model_fallback_names)
        if extra_models:
            for m in extra_models:
                rm = self._resolve_model(str(m))
                if rm and rm not in models:
                    models.append(rm)

        key_count = len(self.gemini_api_keys)
        start = self.active_gemini_key_index
        last_err: Exception | None = None
        saw_retryable_error = False

        for model_name in models:
            print(f"[Gemini] generate with model: {model_name}")
            for offset in range(key_count):
                idx = (start + offset) % key_count
                try:
                    return self._try_generate_with_key(prompt, idx, model_name)
                except Exception as err:
                    last_err = err
                    is_retryable = self._is_quota_or_rate_limit_error(err)
                    if not is_retryable:
                        raise

                    saw_retryable_error = True
                    has_more_keys = offset < key_count - 1
                    if has_more_keys:
                        print(f"[Gemini] Key {idx + 1} quota/rate-limited for {model_name}. Trying next key.")
                        continue

            print(f"[Gemini] All keys exhausted for model {model_name}. Trying next model if available.")

        if saw_retryable_error:
            print(f"[Gemini] All configured keys/models failed due to quota/rate-limit. Last error: {last_err}")
            raise RuntimeError(self.llm_unavailable_message())

        if last_err is not None:
            raise last_err

        raise RuntimeError(self.llm_unavailable_message())

    def load_chroma_client(self):
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_directory
        )

    def load_rag_config(self, app_config):
        self.collection_name = app_config["rag_config"]["collection_name"]
        self.top_k = app_config["rag_config"]["top_k"]

    def remove_directory(self, directory_path: str):
        if os.path.exists(directory_path):
            try:
                shutil.rmtree(directory_path)
                print(f"The directory '{directory_path}' has been successfully removed.")
            except OSError as e:
                print(f"Error: {e}")
        else:
            print(f"The directory '{directory_path}' does not exist.")

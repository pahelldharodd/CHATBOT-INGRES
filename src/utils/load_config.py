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
        self.stored_csv_xlsx_directory = app_config.get("stored_csv_xlsx_directory", "data/csv_xlsx")
        self.persist_directory = app_config.get("persist_directory", "data/chroma")
        self.uploaded_files_sqldb_directory = app_config.get("uploaded_files_sqldb_directory", "data/uploaded_sqldb")
        self.stored_csv_xlsx_sqldb_directory = app_config.get("stored_csv_xlsx_sqldb_directory", "data/csv_xlsx_sqldb.db")

    def load_llm_configs(self, app_config):
        # Use a stable, repo-controlled default to avoid OS env breakage.
        # If you want to allow overrides later, wire it through app_config instead of OS env.
        raw_model = "gemini-1.5-flash-latest"
        print(f"[Gemini] Using repo default model (ignoring OS env): {raw_model}")

        # Normalize common/legacy model names to valid, accessible versions
        def _normalize_model_name(name: str) -> str:
            # If a full path was provided (Vertex/Publisher format), reduce it to just the model token
            # e.g., projects/.../publishers/google/models/gemini-1.5-flash-002 -> gemini-1.5-flash-002
            if "/models/" in name:
                try:
                    name = name.split("/models/")[-1]
                except Exception:
                    pass

            # Prefer the "-latest" aliases to avoid version access issues (e.g., -002 not enabled)
            alias_map = {
                "gemini-1.5-flash": "gemini-1.5-flash-latest",
                "gemini-1.5-pro": "gemini-1.5-pro-latest",
                # "gemini-1.5-flash-002": "gemini-1.5-flash-latest",
                # "gemini-1.5-pro-002": "gemini-1.5-pro-latest",
            }
            if name in alias_map:
                return alias_map[name]
            # Generic: map any explicit -002 suffix to -latest
            if name.endswith("-002"):
                return name.replace("-002", "-latest")
            # If a full Vertex publisher pa
            # th is mistakenly provided, patch the model token
            # e.g., projects/.../models/gemini-1.5-flash-002 -> .../models/gemini-1.5-flash-latest
            if "gemini-1.5-flash-002" in name:
                return name.replace("gemini-1.5-flash-002", "gemini-1.5-flash-latest")
            if "gemini-1.5-pro-002" in name:
                return name.replace("gemini-1.5-pro-002", "gemini-1.5-pro-latest")
            return name

        self.model_name = _normalize_model_name(raw_model)
        print(f"[Gemini] Configured model name: {self.model_name}")

        # Embeddings model (keep stable default as well)
        self.embedding_model_name = "models/text-embedding-004"

        self.agent_llm_system_role = app_config["llm_config"]["agent_llm_system_role"]
        self.rag_llm_system_role = app_config["llm_config"]["rag_llm_system_role"]
        self.temperature = app_config["llm_config"]["temperature"]

    def load_gemini_models(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment!")

        # Configure Gemini client
        genai.configure(api_key=api_key)
        try:
            sdk_version = getattr(genai, "__version__", "unknown")
        except Exception:
            sdk_version = "unknown"
        print(f"[Gemini] google-generativeai SDK version: {sdk_version}")

        # Chat/completion model
        selected_model = self.model_name
        try:
            self.gemini_llm = genai.GenerativeModel(selected_model)
            # lightweight call to validate model availability (tokenize is cheap)
            try:
                _ = self.gemini_llm.count_tokens("ping")
                print(f"[Gemini] Using model: {selected_model}")
            except Exception:
                # continue if count_tokens isn't available in SDK; model object created is still fine
                print(f"[Gemini] Initialized model: {selected_model}")
        except Exception as e:
            print(f"[Gemini] Failed to init model '{selected_model}': {e}")
            fallbacks = [
                "gemini-1.5-flash-latest",
                "gemini-1.5-pro-latest",
            ]
            # ensure we don't try the same model twice
            fallbacks = [m for m in fallbacks if m != selected_model]
            last_err = e
            for alt in fallbacks:
                try:
                    print(f"[Gemini] Trying fallback model: {alt}")
                    self.gemini_llm = genai.GenerativeModel(alt)
                    selected_model = alt
                    print(f"[Gemini] Using fallback model: {selected_model}")
                    break
                except Exception as ee:
                    last_err = ee
                    continue
            else:
                # no break occurred
                raise last_err

        # Embedding model
        self.gemini_embed = genai

    def generate_content_with_fallback(self, prompt: str, extra_models: list | None = None):
        """
        Generate content with robust fallbacks, independent of OS env.
        Tries a sequence of known-accessible model names if the primary fails.
        """
        tried = set()
        # Conservative, widely available candidates
        candidates = [
            self.model_name,
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-1.5-pro",
        ]
        if extra_models:
            candidates = list(dict.fromkeys([*candidates, *extra_models]))

        last_err = None
        for m in candidates:
            if m in tried:
                continue
            tried.add(m)
            try:
                print(f"[Gemini] generate with model: {m}")
                model = genai.GenerativeModel(m)
                return model.generate_content(prompt)
            except Exception as e:
                print(f"[Gemini] generate failed for {m}: {e}")
                last_err = e
                continue
        if last_err:
            raise last_err
        raise RuntimeError("Gemini generation failed with no models attempted.")

    def load_chroma_client(self):
        self.chroma_client = chromadb.PersistentClient(
            path=str(here(self.persist_directory))
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

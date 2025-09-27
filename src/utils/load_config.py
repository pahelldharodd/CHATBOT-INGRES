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
        self.embedding_model_name = "models/text-embedding-004"
        print(f"[Gemini] Requested model: {requested!r} -> Using: {self.model_name}")

        self.agent_llm_system_role = app_config["llm_config"]["agent_llm_system_role"]
        self.rag_llm_system_role = app_config["llm_config"]["rag_llm_system_role"]
        self.temperature = app_config["llm_config"]["temperature"]

    def load_gemini_models(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment!")

        # Configure Gemini client
        genai.configure(api_key=api_key)
        print(f"[Gemini] google-generativeai SDK version: {getattr(genai, '__version__', 'unknown')}")

        # Only use the correct model
        self.gemini_llm = genai.GenerativeModel(self.model_name)
        self.gemini_embed = genai

    def generate_content_with_fallback(self, prompt: str, extra_models: list | None = None):
        """
        Generate content using only the configured Gemini model (no fallbacks).
        """
        print(f"[Gemini] generate with model: {self.model_name}")
        model = genai.GenerativeModel(self.model_name)
        return model.generate_content(prompt)

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

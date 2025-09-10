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
        # Load model + config from YAML + environment
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")  # default to flash
        self.embedding_model_name = os.getenv("GEMINI_EMBED_MODEL", "models/embedding-001")

        self.agent_llm_system_role = app_config["llm_config"]["agent_llm_system_role"]
        self.rag_llm_system_role = app_config["llm_config"]["rag_llm_system_role"]
        self.temperature = app_config["llm_config"]["temperature"]

    def load_gemini_models(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment!")

        # Configure Gemini client
        genai.configure(api_key=api_key)

        # Chat/completion model
        self.gemini_llm = genai.GenerativeModel(self.model_name)

        # Embedding model
        self.gemini_embed = genai

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

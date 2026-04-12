import os
import socket
import traceback
import re
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import chromadb
import google.generativeai as genai
from pyprojroot import here


class AskRequest(BaseModel):
    question: str
    top_k: int | None = 4


def _get_env(name: str, default: str | None = None) -> str:
    val = os.getenv(name, default if default is not None else "")
    if not val:
        raise ValueError(f"Missing required environment variable: {name}")
    return val


def _vector_dim(value: Any) -> int | None:
    if value is None:
        return None
    if hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, dict):
        value = value.get("values") or value.get("embedding") or value.get("embedding_values")
        if hasattr(value, "tolist"):
            value = value.tolist()
    if isinstance(value, list):
        if not value:
            return None
        first = value[0]
        if isinstance(first, (int, float)):
            return len(value)
        if hasattr(first, "tolist"):
            first = first.tolist()
        if isinstance(first, list):
            return len(first)
    return None


def _extract_embedding_vector(resp: Any) -> List[float] | None:
    if not isinstance(resp, dict):
        return None
    vec = resp.get("embedding")
    if vec is None:
        return None
    if hasattr(vec, "tolist"):
        vec = vec.tolist()
    if isinstance(vec, dict):
        vec = vec.get("values") or vec.get("embedding") or vec.get("embedding_values")
        if hasattr(vec, "tolist"):
            vec = vec.tolist()
    if isinstance(vec, list) and vec and isinstance(vec[0], (int, float)):
        return vec  # type: ignore[return-value]
    return None


def _question_keywords(question: str) -> List[str]:
    stopwords = {
        "what", "when", "where", "which", "who", "whom", "whose", "why", "how",
        "is", "are", "was", "were", "the", "and", "for", "with", "from", "into",
        "about", "tell", "show", "give", "me", "please", "can", "could", "would",
        "should", "annual", "year", "years", "data", "historical", "assistant",
    }
    tokens = re.split(r"[^a-zA-Z0-9]+", question.lower())
    return [token for token in tokens if len(token) >= 3 and token not in stopwords]


def _search_historical_csv_context(question: str, top_k: int = 4) -> tuple[list[str], list[dict[str, Any]]]:
    csv_root = Path(here("header_flat_csv"))
    if not csv_root.exists():
        csv_root = Path(here("data/header_flat_csv"))
    if not csv_root.exists():
        return [], []

    keywords = _question_keywords(question)
    if not keywords:
        keywords = [question.lower().strip()]

    matches: list[tuple[int, str, dict[str, Any]]] = []
    for csv_path in sorted(csv_root.glob("*.csv")):
        try:
            import pandas as pd

            df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
        except Exception as exc:
            print(f"[historical_fallback_csv] Skipping {csv_path.name}: {exc}")
            continue

        for row_index, row in df.head(1200).iterrows():
            row_text = " | ".join(str(value).lower() for value in row.tolist())
            score = sum(1 for keyword in keywords if keyword in row_text)
            if score <= 0:
                continue

            state = str(row.get("STATE") or row.get("state") or "").strip()
            district = str(row.get("DISTRICT") or row.get("district") or "").strip()
            year = str(row.get("YEAR") or row.get("year") or "").strip()
            header = f"[CSV] {csv_path.name}"
            if state or district or year:
                header += f" | {state} {district} {year}".strip()
            body = "\n".join(f"{col}: {row[col]}" for col in row.index[: min(len(row.index), 24)])
            matches.append((score, f"{header}\n{body}", {"source": csv_path.name, "row_index": int(row_index), "state": state, "district": district, "year": year}))

    matches.sort(key=lambda item: (-item[0], item[2].get("year", ""), item[2].get("state", ""), item[2].get("district", "")))
    selected = matches[: max(1, top_k)]
    context_blocks = [item[1] for item in selected]
    sources = [
        {
            "id": f"csv-{meta['source']}-{meta['row_index']}",
            "label": f"S{i + 1}",
            "source": meta["source"],
            "page": meta.get("row_index"),
            "metadata": meta,
        }
        for i, (_, _, meta) in enumerate(selected)
    ]
    return context_blocks, sources


def _pick_available_port(start_port: int, host: str = "0.0.0.0", attempts: int = 20) -> int:
    for port in range(start_port, start_port + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"No free port found starting from {start_port}")


class HistoricalGeminiClient:
    def __init__(self) -> None:
        self.api_keys = self._load_api_keys()
        self.model_fallback_names = self._load_model_fallbacks()
        self.active_key_index = 0
        self._configure(self.active_key_index)

    def _load_api_keys(self) -> List[str]:
        keys: List[str] = []

        keys_blob = os.getenv("HISTORICAL_API_KEYS", "")
        for chunk in keys_blob.replace(";", ",").replace("\n", ",").split(","):
            key = chunk.strip()
            if key:
                keys.append(key)

        for name in ["HISTORICAL_API_KEY", "HISTORICAL_API_KEY_FALLBACK"]:
            key = os.getenv(name, "").strip()
            if key:
                keys.append(key)

        unique: List[str] = []
        for key in keys:
            if key not in unique:
                unique.append(key)

        if not unique:
            raise ValueError(
                "Missing historical Gemini API key. Set HISTORICAL_API_KEY, "
                "or provide multiple keys via HISTORICAL_API_KEYS."
            )
        return unique

    def _configure(self, key_index: int) -> None:
        genai.configure(api_key=self.api_keys[key_index])
        self.active_key_index = key_index
        print(f"[Historical Gemini] Active API key index: {key_index + 1}/{len(self.api_keys)}")

    def _load_model_fallbacks(self) -> List[str]:
        primary = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-pro").strip() or "gemini-2.5-pro"
        models = [self._normalize_model(primary)]

        env_fallbacks = os.getenv("GEMINI_MODEL_FALLBACKS", "")
        for chunk in env_fallbacks.replace(";", ",").replace("\n", ",").split(","):
            candidate = self._normalize_model(chunk.strip())
            if candidate and candidate not in models:
                models.append(candidate)

        for candidate in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
            normalized = self._normalize_model(candidate)
            if normalized and normalized not in models:
                models.append(normalized)

        return models

    def _normalize_model(self, name: str) -> str:
        n = (name or "").strip()
        if not n:
            return "gemini-2.5-flash"
        if n.endswith("-latest"):
            if "pro" in n:
                return "gemini-2.5-pro"
            return "gemini-2.5-flash"
        if n.endswith("-002") or n.endswith("-001"):
            if n.startswith("gemini-2.5-pro"):
                return "gemini-2.5-pro"
            if n.startswith("gemini-2.5-flash") or n.startswith("gemini-2.0-flash"):
                return "gemini-2.5-flash"
        if "gemini-1.5-flash" in n:
            return "gemini-2.5-flash"
        return n

    def _is_quota_or_rate_limit_error(self, err: Exception) -> bool:
        text = str(err).lower()
        return (
            "429" in text
            or "quota" in text
            or "rate limit" in text
            or "resource_exhausted" in text
            or "exceeded your current quota" in text
        )

    def unavailable_message(self) -> str:
        return (
            "Historical assistant is temporarily unavailable right now. "
            "Please try again in a minute."
        )

    def _retry_with_keys(self, action):
        key_count = len(self.api_keys)
        start = self.active_key_index
        last_err: Exception | None = None

        for offset in range(key_count):
            idx = (start + offset) % key_count
            try:
                self._configure(idx)
                return action()
            except Exception as err:
                last_err = err
                retryable = self._is_quota_or_rate_limit_error(err)
                has_more_keys = offset < key_count - 1
                if retryable and has_more_keys:
                    print(f"[Historical Gemini] Key {idx + 1} quota/rate-limited. Trying next key.")
                    continue
                if not retryable:
                    raise

        print(f"[Historical Gemini] All keys exhausted. Last error: {last_err}")
        if last_err is not None:
            raise last_err
        raise RuntimeError(self.unavailable_message())

    def embed_content(self, model: str, content: str):
        return self._retry_with_keys(lambda: genai.embed_content(model=model, content=content))

    def generate_content(self, model_name: str, prompt: str):
        requested = self._normalize_model(model_name)
        models = [requested]
        for candidate in self.model_fallback_names:
            if candidate not in models:
                models.append(candidate)

        last_err: Exception | None = None
        for candidate_model in models:
            try:
                print(f"[Historical Gemini] Generating with model: {candidate_model}")
                return self._retry_with_keys(lambda: genai.GenerativeModel(candidate_model).generate_content(prompt))
            except Exception as err:
                last_err = err
                if not self._is_quota_or_rate_limit_error(err):
                    raise
                print(f"[Historical Gemini] Model {candidate_model} quota/rate-limited. Trying next model.")

        if last_err is not None:
            raise RuntimeError(self.unavailable_message()) from last_err
        raise RuntimeError(self.unavailable_message())


def embed_texts_gemini(texts: List[str]) -> List[List[float]]:
    # Call Gemini embedding API per text to avoid SDK batch-shape differences
    embeddings: List[List[float]] = []
    for t in texts:
        resp = HISTORICAL_GEMINI.embed_content(model="models/text-embedding-004", content=t)
        vec = _extract_embedding_vector(resp)
        if not vec:
            raise RuntimeError("Failed to get embedding from Gemini for the given text.")
        embeddings.append(vec)
    return embeddings


def embed_texts_st(texts: List[str], model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[List[float]]:
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "sentence-transformers is required to query a 384-dim index. "
            "Install with: pip install sentence-transformers"
        ) from e
    model = SentenceTransformer(model_name)
    vecs = model.encode(texts, normalize_embeddings=True)
    # Ensure list of lists
    if hasattr(vecs, "tolist"):
        vecs = vecs.tolist()
    if isinstance(vecs, list) and isinstance(vecs[0], (float, int)):
        vecs = [vecs]
    return vecs  # type: ignore


def _check_embedding_dimension(collection: chromadb.Collection, q_emb: List[float]) -> None:
    """Best-effort check to ensure query embedding dim matches stored vectors."""
    try:
        probe = collection.peek(1, include=["embeddings"])  # type: ignore[arg-type]
    except Exception:
        # peek not available in some versions; fallback to get first id via get()
        probe = collection.get(limit=1, include=["embeddings"])  # type: ignore[arg-type]
    emb_list = probe.get("embeddings") if isinstance(probe, dict) else None
    stored_dim = _vector_dim(emb_list)
    if stored_dim is not None:
        query_dim = _vector_dim(q_emb)
        if query_dim is not None and stored_dim != query_dim:
            raise ValueError(
                f"Embedding dimension mismatch (stored={stored_dim}, query={query_dim}). "
                "This usually means the Chroma DB was built with a different embedding model. "
                "Fix by: (1) switching the query embedder to match the original model, or "
                "(2) rebuilding data/chroma_historical using models/text-embedding-004."
            )


def _detect_stored_dim(collection: chromadb.Collection) -> int | None:
    try:
        probe = collection.peek(1, include=["embeddings"])  # type: ignore[arg-type]
    except Exception:
        probe = collection.get(limit=1, include=["embeddings"])  # type: ignore[arg-type]
    emb_list = probe.get("embeddings") if isinstance(probe, dict) else None
    return _vector_dim(emb_list)


def build_prompt(context_chunks: List[str], question: str) -> str:
    context = "\n\n".join(context_chunks)
    instructions = (
        "You are a domain expert on India's historical groundwater assessments."
        " Use only the evidence from CONTEXT when answering."
        " Follow these steps:\n"
        "1. Read the CONTEXT carefully.\n"
        "2. If the answer is not fully supported, respond with: 'I don't know based on the provided documents.'\n"
        "3. Otherwise craft a helpful response that:\n"
        "   • Starts with a one-sentence overview.\n"
        "   • Includes bullet points for key figures, definitions, or procedures.\n"
        "   • Ends with an 'Suggested follow-up' line offering one short related question.\n"
    )
    return (
        f"{instructions}\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n"
        "Provide the answer in Markdown."
    )


def answer_with_rag(collection: chromadb.Collection, question: str, top_k: int = 4) -> Dict[str, Any]:
    context_blocks: List[str] = []
    sources: list[dict[str, Any]] = []

    try:
        # Pick embedder based on stored dim
        stored_dim = _detect_stored_dim(collection)
        if stored_dim == 384:
            st_model = os.getenv("HISTORICAL_ST_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            q_emb = embed_texts_st([question], model_name=st_model)[0]
        else:
            # Default to Gemini (768 dims for text-embedding-004)
            q_emb = embed_texts_gemini([question])[0]
            # Validate embedding dimension against stored vectors to avoid runtime errors
            _check_embedding_dimension(collection, q_emb)
        res = collection.query(query_embeddings=[q_emb], n_results=max(1, min(10, top_k)))

        documents = res.get("documents", [[]])[0]
        metadatas = res.get("metadatas", [[]])[0]
        ids = res.get("ids", [[]])[0]

        for idx, (doc, meta, doc_id) in enumerate(zip(documents, metadatas, ids)):
            label = f"S{idx + 1}"
            meta = meta or {}
            source_name = meta.get("source") or meta.get("file_path") or meta.get("path") or "Document"
            page = meta.get("page") or meta.get("page_number")
            header = f"[{label}] {source_name}"
            if page:
                header += f", page {page}"
            body = (doc or "").strip()
            context_blocks.append(f"{header}\n{body}")
            sources.append({
                "id": doc_id,
                "label": label,
                "source": source_name,
                "page": page,
                "metadata": meta,
            })
    except Exception as exc:
        print(f"[historical_answer_fallback] Using CSV fallback because Chroma failed: {exc}")
        context_blocks, sources = _search_historical_csv_context(question, top_k=top_k)
        if not context_blocks:
            return {
                "answer": "I don't know based on the provided documents.",
                "sources": [],
            }

    # Build prompt and get answer from Gemini
    prompt = build_prompt(context_blocks, question)
    requested = os.getenv("GEMINI_MODEL_NAME", "models/gemini-1.5-flash")
    # Normalize unstable aliases
    def _resolve_model(name: str) -> str:
        n = (name or "").strip()
        if not n:
            return "models/gemini-1.5-flash"
        if n.endswith("-latest"):
            if "pro" in n:
                return "models/gemini-1.5-pro"
            return "models/gemini-1.5-flash"
        if n.endswith("-002") or n.endswith("-001"):
            if n.startswith("gemini-1.5-pro"):
                return "models/gemini-1.5-pro"
            if n.startswith("gemini-1.5-flash-8b") or n.startswith("gemini-1.5-flash"):
                return "models/gemini-1.5-flash"
        return n
    model_name = _resolve_model(requested)
    llm_resp = HISTORICAL_GEMINI.generate_content(model_name, prompt)
    answer_text = llm_resp.text if getattr(llm_resp, "text", None) else str(llm_resp)

    return {"answer": answer_text.strip(), "sources": sources}


def get_historical_collection() -> chromadb.Collection:
    persist_path = str(here("data/chroma_historical"))
    client = chromadb.PersistentClient(path=persist_path)
    # Try to find a relevant collection; if only one exists, use it
    cols = client.list_collections()
    if not cols:
        raise RuntimeError(f"No collections found in {persist_path}. Please build the historical Chroma DB first.")
    # Prefer a collection that looks historical
    preferred_names = {"historical", "historical_pdfs", "ingres_historical"}
    name_to_col = {c.name: c for c in cols}
    chosen = None
    for name in preferred_names:
        if name in name_to_col:
            chosen = name_to_col[name]
            break
    if chosen is None:
        # Fallback: first collection
        chosen = cols[0]
    # Reopen by name to ensure a standard collection handle
    return client.get_collection(chosen.name)


# Initialize FastAPI app
load_dotenv()
historical_app = FastAPI(title="Historical PDF RAG Service")
HISTORICAL_GEMINI = HistoricalGeminiClient()

# Historical Gemini is configured via HistoricalGeminiClient with key fallback support.

# CORS to allow Vite dev origin
historical_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@historical_app.get("/historical/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "sdk": getattr(genai, "__version__", "unknown")}


@historical_app.post("/historical/ask")
def historical_ask(req: AskRequest) -> Dict[str, Any]:
    try:
        collection = get_historical_collection()
        return answer_with_rag(collection, req.question, req.top_k or 4)
    except RuntimeError as e:
        # User-safe message for key exhaustion/quota issues.
        print(f"[historical_ask] RuntimeError: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        # Print on server for quick diagnosis and return a clear error to the client
        print(f"[historical_ask] Error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Historical assistant request failed.")


@historical_app.get("/historical/debug")
def historical_debug() -> Dict[str, Any]:
    info: Dict[str, Any] = {}
    try:
        persist_path = str(here("data/chroma_historical"))
        client = chromadb.PersistentClient(path=persist_path)
        cols = client.list_collections()
        info["persist_path"] = persist_path
        info["collections"] = [c.name for c in cols]
        try:
            chosen = get_historical_collection()
            info["chosen_collection"] = chosen.name
        except Exception as exc:
            info["chosen_collection_error"] = str(exc)
            info["chosen_collection"] = None
        info["stored_embedding_dim"] = None
        info["embedding_model"] = "models/text-embedding-004"
        info["llm_model"] = os.getenv("GEMINI_MODEL_NAME", "models/gemini-1.5-flash")
    except Exception as e:
        print(f"[historical_debug] Error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    return info


if __name__ == "__main__":
    import uvicorn
    port = _pick_available_port(int(os.getenv("HISTORICAL_PORT", "7861")))
    print(f"[Historical Gemini] Starting on port {port}")
    uvicorn.run(historical_app, host="0.0.0.0", port=port)

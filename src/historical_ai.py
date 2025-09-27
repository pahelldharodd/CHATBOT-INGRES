import os
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


def embed_texts_gemini(texts: List[str]) -> List[List[float]]:
    # Call Gemini embedding API per text to avoid SDK batch-shape differences
    embeddings: List[List[float]] = []
    for t in texts:
        resp = genai.embed_content(model="models/text-embedding-004", content=t)
        vec = resp.get("embedding") if isinstance(resp, dict) else None  # type: ignore
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
    # Convert numpy arrays to Python lists to avoid ambiguous truth-value checks
    if emb_list is not None and hasattr(emb_list, "tolist"):
        emb_list = emb_list.tolist()
    stored_dim = None
    if isinstance(emb_list, list) and len(emb_list) > 0 and emb_list[0] is not None:
        first_vec = emb_list[0]
        if hasattr(first_vec, "tolist"):
            first_vec = first_vec.tolist()
        if isinstance(first_vec, list):
            stored_dim = len(first_vec)
    if stored_dim is not None:
        query_dim = len(q_emb)
        if stored_dim != query_dim:
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
    if emb_list is not None and hasattr(emb_list, "tolist"):
        emb_list = emb_list.tolist()
    if isinstance(emb_list, list) and len(emb_list) > 0 and emb_list[0] is not None:
        first_vec = emb_list[0]
        if hasattr(first_vec, "tolist"):
            first_vec = first_vec.tolist()
        if isinstance(first_vec, list):
            return len(first_vec)
    return None


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

    context_blocks: List[str] = []
    sources = []

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

    # Build prompt and get answer from Gemini
    prompt = build_prompt(context_blocks, question)
    requested = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    # Normalize unstable aliases
    def _resolve_model(name: str) -> str:
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
        # Handle legacy model names
        if "gemini-1.5-flash-8b" in n or "gemini-2.5-flash-8b" in n:
            return "gemini-2.5-flash"
        if "gemini-1.5-flash" in n:
            return "gemini-2.5-flash"
        return n
    model_name = _resolve_model(requested)
    llm = genai.GenerativeModel(model_name)
    llm_resp = llm.generate_content(prompt)
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

# Configure Gemini with the HISTORICAL_API_KEY (separate from main app)
genai.configure(api_key=_get_env("GEMINI_API_KEY"))

# CORS to allow Vite dev origin
historical_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
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
    except Exception as e:
        # Print on server for quick diagnosis and return a clear error to the client
        print(f"[historical_ask] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@historical_app.get("/historical/debug")
def historical_debug() -> Dict[str, Any]:
    info: Dict[str, Any] = {}
    try:
        persist_path = str(here("data/chroma_historical"))
        client = chromadb.PersistentClient(path=persist_path)
        cols = client.list_collections()
        info["persist_path"] = persist_path
        info["collections"] = [c.name for c in cols]
        chosen = get_historical_collection()
        info["chosen_collection"] = chosen.name
        # Count docs (best effort)
        try:
            info["count"] = chosen.count()  # type: ignore[attr-defined]
        except Exception:
            # Fallback: try get ids
            got = chosen.get(include=["ids"], limit=1)
            info["count"] = len(got.get("ids", []))
        # Stored embedding dimension (robust to NumPy arrays)
        stored_dim = None
        try:
            probe = chosen.peek(1, include=["embeddings"])  # type: ignore[arg-type]
        except Exception:
            probe = chosen.get(limit=1, include=["embeddings"])  # type: ignore[arg-type]
        emb_list = probe.get("embeddings") if isinstance(probe, dict) else None
        if emb_list is not None and hasattr(emb_list, "tolist"):
            emb_list = emb_list.tolist()
        if isinstance(emb_list, list) and len(emb_list) > 0 and emb_list[0] is not None:
            first_vec = emb_list[0]
            if hasattr(first_vec, "tolist"):
                first_vec = first_vec.tolist()
            if isinstance(first_vec, list):
                stored_dim = len(first_vec)
        info["stored_embedding_dim"] = stored_dim
        info["embedding_model"] = "models/text-embedding-004"
        info["llm_model"] = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    except Exception as e:
        print(f"[historical_debug] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    return info


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("HISTORICAL_PORT", "7861"))
    uvicorn.run(historical_app, host="0.0.0.0", port=port)

import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
import nltk
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from config import EMBED_MODEL, RETRIEVAL_TOP_K

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder

# In-memory vector store (replaces ChromaDB)
_vector_store = []  # list of {"text": str, "embedding": np.array, "source": str, "chunk": int}

# BM25 index kept in memory
_bm25_corpus = []
_bm25_metadata = []
_bm25_index = None

import json

INDEX_DIR = "data/rag_index"


def save_index():
    """Persist vector store and BM25 corpus to disk."""
    os.makedirs(INDEX_DIR, exist_ok=True)

    # Save embeddings as numpy array
    if _vector_store:
        embeddings = np.array([item["embedding"] for item in _vector_store])
        np.save(f"{INDEX_DIR}/embeddings.npy", embeddings)

        # Save metadata (text, source, chunk) as JSON
        metadata = [{"text": item["text"], "source": item["source"], "chunk": item["chunk"]}
                    for item in _vector_store]
        with open(f"{INDEX_DIR}/metadata.json", "w") as f:
            json.dump(metadata, f)

    print(f"[RAG] Index saved ({len(_vector_store)} chunks)")


def load_index():
    """Load vector store and BM25 corpus from disk if it exists."""
    global _bm25_index

    emb_path = f"{INDEX_DIR}/embeddings.npy"
    meta_path = f"{INDEX_DIR}/metadata.json"

    if not (os.path.exists(emb_path) and os.path.exists(meta_path)):
        print("[RAG] No saved index found — starting fresh")
        return False

    embeddings = np.load(emb_path)
    with open(meta_path) as f:
        metadata = json.load(f)

    for i, item in enumerate(metadata):
        _vector_store.append({
            "text": item["text"],
            "embedding": embeddings[i],
            "source": item["source"],
            "chunk": item["chunk"]
        })
        _bm25_corpus.append(item["text"])
        _bm25_metadata.append({"source": item["source"], "chunk_number": item["chunk"]})

    tokenized = [c.lower().split() for c in _bm25_corpus]
    _bm25_index = BM25Okapi(tokenized)

    print(f"[RAG] Index loaded ({len(_vector_store)} chunks)")
    return True


def sentence_aware_chunk(text: str, max_sentences: int = 5, overlap: int = 1) -> list:
    """Chunk by sentences, not words. Much better for retrieval."""
    sentences = nltk.sent_tokenize(text)
    chunks = []
    for i in range(0, len(sentences), max_sentences - overlap):
        chunk = " ".join(sentences[i:i + max_sentences])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def index_document(filepath: str, title: str = None):
    global _bm25_index
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    source = title or os.path.basename(filepath)
    chunks = sentence_aware_chunk(text)
    embeddings = embedder.encode(chunks)

    # Store in numpy vector store
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        _vector_store.append({
            "text": chunk,
            "embedding": embedding,
            "source": source,
            "chunk": i
        })

    # Add to BM25 corpus (lexical search)
    for i, chunk in enumerate(chunks):
        _bm25_corpus.append(chunk)
        _bm25_metadata.append({"source": source, "chunk_number": i})

    # Rebuild BM25 index
    tokenized = [c.lower().split() for c in _bm25_corpus]
    _bm25_index = BM25Okapi(tokenized)

    print(f"Indexed {len(chunks)} chunks from '{source}'")
    save_index()


def vector_search(query: str, n: int = 4) -> list:
    if not _vector_store:
        return []
    query_embedding = embedder.encode([query])[0]
    scores = [
        float(np.dot(query_embedding, item["embedding"]) /
              (np.linalg.norm(query_embedding) * np.linalg.norm(item["embedding"]) + 1e-8))
        for item in _vector_store
    ]
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n]
    return [
        {
            "text": _vector_store[i]["text"],
            "source": _vector_store[i]["source"],
            "chunk": _vector_store[i]["chunk"],
            "method": "vector"
        }
        for i in top_indices
    ]


def bm25_search(query: str, n: int = 4) -> list:
    if _bm25_index is None:
        return []
    scores = _bm25_index.get_scores(query.lower().split())
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n]
    return [
        {
            "text": _bm25_corpus[i],
            "source": _bm25_metadata[i]["source"],
            "chunk": _bm25_metadata[i]["chunk_number"],
            "method": "bm25",
            "score": scores[i]
        }
        for i in top_indices if scores[i] > 0
    ]


def hybrid_search(query: str, n: int = 4) -> list:
    """Combine vector and BM25 results, deduplicate."""
    vector_results = vector_search(query, n)
    bm25_results = bm25_search(query, n)

    seen = set()
    combined = []
    for result in vector_results + bm25_results:
        key = (result["source"], result["chunk"])
        if key not in seen:
            seen.add(key)
            combined.append(result)

    return combined[:n]


def answer_with_rag(question: str) -> str:
    from client import client  # lazy import — avoids hang with SentenceTransformer + PyTorch
    chunks = hybrid_search(question, n=RETRIEVAL_TOP_K)
    context = "\n\n".join([
        f"[Source: {c['source']}, chunk {c['chunk']}, method: {c['method']}]\n{c['text']}"
        for c in chunks
    ])

    prompt = f"""Answer this career question using ONLY the documents below.
After your answer, add a 'Sources:' section listing which documents you used.

Documents:
{context}

Question: {question}"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
# Load persisted index on import
load_index()

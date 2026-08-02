import os
import nltk
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CHROMA_DIR, EMBED_MODEL, RETRIEVAL_TOP_K

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

# Load embedding model directly
embedder = SentenceTransformer(EMBED_MODEL)

db = chromadb.EphemeralClient()
collection = db.get_or_create_collection("career_knowledge")

# BM25 index kept in memory
_bm25_corpus = []
_bm25_metadata = []
_bm25_index = None


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

    # Generate embeddings directly
    embeddings = embedder.encode(chunks).tolist()

    # Index in ChromaDB (vector search)
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"{source}_chunk_{i}" for i in range(len(chunks))],
        metadatas=[{
            "source": source,
            "chunk_number": i,
            "total_chunks": len(chunks),
            "filepath": filepath
        } for i in range(len(chunks))]
    )

    # Add to BM25 corpus (lexical search)
    for i, chunk in enumerate(chunks):
        _bm25_corpus.append(chunk)
        _bm25_metadata.append({"source": source, "chunk_number": i})

    # Rebuild BM25 index
    tokenized = [c.lower().split() for c in _bm25_corpus]
    _bm25_index = BM25Okapi(tokenized)

    print(f"Indexed {len(chunks)} chunks from '{source}'")


def vector_search(query: str, n: int = 4) -> list:
    query_embedding = embedder.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=n)
    return [
        {"text": doc, "source": meta["source"], "chunk": meta["chunk_number"], "method": "vector"}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


def bm25_search(query: str, n: int = 4) -> list:
    if _bm25_index is None:
        return []
    scores = _bm25_index.get_scores(query.lower().split())
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n]
    return [
        {"text": _bm25_corpus[i], "source": _bm25_metadata[i]["source"],
         "chunk": _bm25_metadata[i]["chunk_number"], "method": "bm25", "score": scores[i]}
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


def answer_with_rag(question: str, claude_client) -> str:
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

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
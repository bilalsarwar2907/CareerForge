from rag import sentence_aware_chunk


def test_chunking_returns_list():
    text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence. Sixth sentence."
    chunks = sentence_aware_chunk(text, max_sentences=3, overlap=1)
    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)


def test_chunking_overlap():
    """Overlap means consecutive chunks share content."""
    text = ". ".join([f"Sentence {i}" for i in range(10)]) + "."
    chunks = sentence_aware_chunk(text, max_sentences=3, overlap=1)
    assert len(chunks) >= 3


def test_chunking_empty_text():
    chunks = sentence_aware_chunk("", max_sentences=5, overlap=1)
    assert chunks == []


def test_chunking_single_sentence():
    chunks = sentence_aware_chunk("Just one sentence.", max_sentences=5, overlap=1)
    assert len(chunks) == 1
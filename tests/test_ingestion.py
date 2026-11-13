
from rag.ingestion import DocumentIngestion


def test_ingestion_loads_all_faqs():
    ingestion = DocumentIngestion(
        "knowledge_base/documents"
    )

    chunks = ingestion.ingest()

    assert len(chunks) == 18


def test_chunk_contains_question_and_answer():
    ingestion = DocumentIngestion(
        "knowledge_base/documents"
    )

    chunks = ingestion.ingest()

    first_chunk = chunks[0]

    assert "Question:" in first_chunk["content"]
    assert "Answer:" in first_chunk["content"]


def test_chunk_contains_metadata():
    ingestion = DocumentIngestion(
        "knowledge_base/documents"
    )

    chunks = ingestion.ingest()

    metadata = chunks[0]["metadata"]

    assert "source" in metadata
    assert "category" in metadata
    assert "question" in metadata
    assert "faq_number" in metadata


def test_faq_categories():
    ingestion = DocumentIngestion(
        "knowledge_base/documents"
    )

    chunks = ingestion.ingest()

    categories = {
        chunk["metadata"]["category"]
        for chunk in chunks
    }

    assert categories == {
        "billing",
        "account",
        "technical"
    }

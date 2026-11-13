
from rag.ingestion import DocumentIngestion
from rag.embeddings import FAQEmbedder
from rag.vector_store import FAQVectorStore


class FAQRetriever:
    """
    Coordinates FAQ ingestion, embedding, indexing,
    and semantic retrieval.
    """

    def __init__(
        self,
        documents_dir: str = "knowledge_base/documents",
        persist_directory: str = "data/chroma_db"
    ):
        self.ingestion = DocumentIngestion(documents_dir)
        self.embedder = FAQEmbedder()
        self.vector_store = FAQVectorStore(
            persist_directory=persist_directory
        )

    def index_documents(self) -> int:
        """
        Load FAQs, generate embeddings, and store them.
        """

        chunks = self.ingestion.ingest()

        embedded_chunks = self.embedder.embed_chunks(chunks)

        indexed_count = self.vector_store.add_chunks(
            embedded_chunks
        )

        return indexed_count

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        category: str | None = None
    ) -> dict:
        """
        Retrieve the most relevant FAQs for a query.
        """

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must not be empty.")

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        query_embedding = self.embedder.embed_query(query)

        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=top_k,
            category=category
        )

        return results

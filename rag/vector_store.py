
from pathlib import Path

import chromadb


class FAQVectorStore:
    """
    Stores FAQ embeddings and metadata in persistent ChromaDB.
    """

    def __init__(
        self,
        persist_directory: str = "data/chroma_db",
        collection_name: str = "novadesk_faqs"
    ):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: list[dict]) -> int:
        """
        Insert or update FAQ chunks in ChromaDB.
        """

        if not chunks:
            return 0

        ids = []
        documents = []
        metadatas = []
        embeddings = []

        for chunk in chunks:
            content = chunk.get("content")
            metadata = chunk.get("metadata")
            embedding = chunk.get("embedding")

            if not isinstance(content, str) or not content.strip():
                raise ValueError("Chunk content must not be empty.")

            if not isinstance(metadata, dict):
                raise ValueError("Chunk metadata must be a dictionary.")

            if not isinstance(embedding, list) or not embedding:
                raise ValueError("Chunk must contain a valid embedding.")

            if not all(
                isinstance(value, (int, float))
                for value in embedding
            ):
                raise ValueError("Embedding must contain numeric values.")

            source = metadata.get("source")
            faq_number = metadata.get("faq_number")

            if not source or faq_number is None:
                raise ValueError(
                    "Metadata must contain source and faq_number."
                )

            ids.append(f"{source}_{faq_number}")
            documents.append(content)
            metadatas.append(metadata)
            embeddings.append(embedding)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        return len(ids)

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 3,
        category: str | None = None
    ) -> dict:
        """
        Find FAQs similar to the supplied query embedding.
        """

        if not query_embedding:
            raise ValueError("Query embedding must not be empty.")

        if n_results < 1:
            raise ValueError("n_results must be at least 1.")

        if self.collection.count() == 0:
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

        query_args = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, self.collection.count())
        }

        if category:
            query_args["where"] = {"category": category}

        return self.collection.query(**query_args)

    def count(self) -> int:
        """Return the number of stored FAQ records."""

        return self.collection.count()

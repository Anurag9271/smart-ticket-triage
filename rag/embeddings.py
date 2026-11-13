
from sentence_transformers import SentenceTransformer


class FAQEmbedder:
    """
    Converts FAQ chunks into numerical embeddings
    using a Sentence Transformers model.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu"
    ):
        self.model = SentenceTransformer(
            model_name,
            device=device
        )

    def embed_chunks(self, chunks: list[dict]) -> list[dict]:
        """
        Generate embeddings for FAQ chunks and
        attach them to their corresponding records.
        """

        if not chunks:
            return []

        texts = []

        for chunk in chunks:
            content = chunk.get("content", "")

            if not isinstance(content, str) or not content.strip():
                raise ValueError(
                    "Every chunk must contain non-empty text."
                )

            texts.append(content)

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Number of embeddings does not match number of chunks."
            )

        embedded_chunks = []

        for chunk, embedding in zip(chunks, embeddings):
            embedded_chunks.append({
                **chunk,
                "embedding": embedding.tolist()
            })

        return embedded_chunks


    def embed_query(self, query: str) -> list[float]:
        """
        Convert a user query into a numerical embedding.
        """

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must not be empty.")

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return embedding.tolist()

    

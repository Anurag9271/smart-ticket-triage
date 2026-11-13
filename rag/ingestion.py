
from pathlib import Path
import re


class DocumentIngestion:
    """
    Loads Markdown FAQ documents and converts them
    into structured FAQ chunks with metadata.
    """

    def __init__(self, documents_dir: str):
        self.documents_dir = Path(documents_dir)

    def load_documents(self) -> list[dict]:
        """Load all Markdown documents from the directory."""

        if not self.documents_dir.exists():
            raise FileNotFoundError(
                f"Knowledge base directory not found: {self.documents_dir}"
            )

        documents = []

        for file_path in sorted(self.documents_dir.glob("*.md")):
            content = file_path.read_text(encoding="utf-8")

            documents.append({
                "filename": file_path.name,
                "content": content
            })

        return documents

    def split_into_chunks(self, documents: list[dict]) -> list[dict]:
        """Split documents into individual FAQ chunks."""

        chunks = []

        for document in documents:
            filename = document["filename"]
            content = document["content"]

            category = filename.replace("_faq.md", "")

            sections = re.split(r"(?m)^##\s+", content)

            for section in sections[1:]:
                lines = section.strip().splitlines()

                if not lines:
                    continue

                heading = lines[0].strip()

                question_match = re.match(
                    r"^\d+\.\s*(.+)$", heading
                )

                if not question_match:
                    continue

                question = question_match.group(1).strip()

                answer = "\n".join(lines[1:]).strip()

                if not answer:
                    continue

                chunks.append({
                    "content": f"Question: {question}\n\nAnswer: {answer}",
                    "metadata": {
                        "source": filename,
                        "category": category,
                        "question": question,
                        "faq_number": int(
                            re.match(r"^(\d+)\.", heading).group(1)
                        )
                    }
                })

        return chunks

    def ingest(self) -> list[dict]:
        """Load documents and return structured FAQ chunks."""

        documents = self.load_documents()

        return self.split_into_chunks(documents)

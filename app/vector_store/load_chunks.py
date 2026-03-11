from typing import Optional, List

from langchain_core.documents import Document
from qdrant_client import QdrantClient


class QdrantChunkLoader:
    """
    从 Qdrant collection 中加载所有 chunk 文本
    并转换为 LangChain Document
    """

    def __init__(self, client: QdrantClient,
                 collection_name: str,
                 text_field: str = 'text',
                 batch_size: int = 1000):
        """
        参数
        ----
        client : QdrantClient
        collection_name : collection 名称
        text_field : payload 中存储文本的字段
        batch_size : 每次 scroll 数量
        """

        self.client = client
        self.collection_name = collection_name
        self.text_field = text_field
        self.batch_size = batch_size

    def load_chunks(self,
                    max_chunks: Optional[int] = None) -> List[Document]:
        """
        从 Qdrant 中加载所有 chunks

        Parameters
        ----------
        max_chunks : Optional[int]
            最大加载数量（用于调试）

        Returns
        -------
        List[Document]
        """

        documents: List[Document] = []
        offset = None

        while True:
            points, offset = self.client.scroll(
                collection_name=self.collection_name,
                limit=self.batch_size,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            if not points:
                break

            for point in points:
                payload = point.payload or {}
                text = payload.get(self.text_field)

                if not text:
                    continue
                meta=payload.get('metadata',{})
                documents.append(
                    Document(
                        page_content=text,
                        metadata=meta
                    )
                )

            if offset is None:
                break

        return documents

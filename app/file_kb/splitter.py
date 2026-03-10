from datetime import datetime
from app.file_kb.utils import md5

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_docs(docs):
    """
        Split documents into chunks and attach metadata.

        Metadata generated:
        - doc_id
        - chunk_index
        - chunk_id
        - chunk_hash
        """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=15,
        separators=["\n\n",
                    "\n",
                    "。",
                    ".",
                    "！",
                    "!",
                    "？",
                    "?",
                    ";",
                    "；",
                    " "])
    chunks = splitter.split_documents(docs)
    created_at = datetime.now().isoformat()

    # 存放处理后的chunks=[]
    processed_chunks = []
    # 记录每个文档的chunk编号
    doc_chunks_count = {}

    for chunk in chunks:

        text = chunk.page_content
        doc_id = chunk.metadata.get("doc_id")
        if not doc_id:
            source = chunk.metadata.get('source', 'unknown')
            doc_id = source.split('.')[0]

        if doc_id not in doc_chunks_count:
            doc_chunks_count[doc_id] = 0

        chunk_index = doc_chunks_count[doc_id]

        # 生成每个chunk的唯一ID
        chunk_id = f"{doc_id}_chunk_{chunk_index}"

        chunk_hash = md5(text)

        chunk.metadata['doc_id'] = doc_id
        chunk.metadata['chunk_index'] = chunk_index
        chunk.metadata['chunk_id'] = chunk_id
        chunk.metadata['chunk_hash'] = chunk_hash
        chunk.metadata['created_at'] = created_at

        doc_chunks_count[doc_id] += 1

        processed_chunks.append(chunk)

    return processed_chunks

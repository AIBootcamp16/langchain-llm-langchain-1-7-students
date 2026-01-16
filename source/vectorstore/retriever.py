# source/vectorstore/retriever.py
from typing import Optional
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client.http import models

from config.settings import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
    ALLOWED_INSURANCE_TYPES,
)


def get_retriever(insurance_type: Optional[str] = None):
    filters = None
    
    if insurance_type:
        print(f"  → 필터 적용: insurance_type = '{insurance_type}'")
        
        if insurance_type not in ALLOWED_INSURANCE_TYPES:
            raise ValueError(f"허용되지 않은 보험유형: {insurance_type}")

        filters = models.Filter(
            must=[
                # 1️⃣ 정확히 일치하는 보험유형
                # LangChain은 metadata를 중첩 딕셔너리로 저장하므로 "metadata.insurance_type" 경로 사용
                models.FieldCondition(
                    key="metadata.insurance_type",
                    match=models.MatchValue(value=insurance_type),
                ),
            ],
        )
    else:
        print(f"  → 필터 없음 (전체 검색)")

    # print("[DEBUG] qdrant filter:", filters)  # 너무 상세하므로 주석 처리

    client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
    )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )

    return vectorstore.as_retriever(
        search_kwargs={
            "k": TOP_K,
            "filter": filters
        }
    )


# def get_retriever(insurance_type: Optional[str] = None):
#     filters = None
#     print(repr(insurance_type))

#     if insurance_type:
#         print("🔍 retriever insurance_type:", insurance_type)
#         if insurance_type not in ALLOWED_INSURANCE_TYPES:
#             raise ValueError(f"허용되지 않은 보험유형: {insurance_type}")
        
#         filters = models.Filter(
#                 must=[
#                     models.FieldCondition(
#                         key="insurance_type",
#                         match=models.MatchValue(value=insurance_type),
#                     )
#                 ]
#             )

#     print("[DEBUG] qdrant filter:", filters)

#     client = QdrantClient(
#         host=QDRANT_HOST,
#         port=QDRANT_PORT,
#     )

#     embeddings = HuggingFaceEmbeddings(
#         model_name=EMBEDDING_MODEL
#     )

#     vectorstore = QdrantVectorStore(
#         client=client,
#         collection_name=COLLECTION_NAME,
#         embedding=embeddings,
#     )

#     return vectorstore.as_retriever(
#         search_kwargs={
#             "k": TOP_K,
#             "filter": filters
#         }
#     )
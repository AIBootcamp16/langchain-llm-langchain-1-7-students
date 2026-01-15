#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qdrant 벡터스토어 초기화 및 관리
"""
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient

def get_embeddings():
    """
    Hugging Face 임베딩 모델 초기화
    
    Returns:
        HuggingFaceEmbeddings 객체
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    return embeddings

def get_vectorstore(recreate: bool = False):
    """
    Qdrant 벡터스토어 초기화
    
    Args:
        recreate: True이면 기존 컬렉션 삭제 후 재생성
        
    Returns:
        QdrantVectorStore 객체
    """
    collection_name = "insurance_docs"
    
    # Qdrant 클라이언트
    client = QdrantClient("http://localhost:6333")
    
    # 임베딩 모델
    embeddings = get_embeddings()
    
    # 기존 컬렉션 삭제 (recreate=True인 경우)
    if recreate:
        try:
            client.delete_collection(collection_name)
            print(f"✓ 기존 '{collection_name}' 컬렉션 삭제됨")
        except:
            pass
    
    # 빈 벡터스토어 초기화
    vectorstore = QdrantVectorStore.from_documents(
        documents=[],
        embedding=embeddings,
        url="http://localhost:6333",
        collection_name=collection_name,
    )
    
    return vectorstore

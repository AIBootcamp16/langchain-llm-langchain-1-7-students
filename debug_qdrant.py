#!/usr/bin/env python3
"""
Qdrant에 저장된 insurance_type 값들을 확인하는 디버깅 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 경로 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "source"))

from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME, EMBEDDING_MODEL

def main():
    # Qdrant 클라이언트 생성
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # 컬렉션 정보 확인
    try:
        collection_info = client.get_collection(COLLECTION_NAME)
        print(f"📊 컬렉션: {COLLECTION_NAME}")
        print(f"   총 벡터 수: {collection_info.points_count}")
        print()
    except Exception as e:
        print(f"❌ 컬렉션 확인 실패: {e}")
        return
    
    # VectorStore 생성
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )
    
    # 샘플 검색으로 insurance_type 값들 확인
    print("🔍 샘플 검색으로 저장된 insurance_type 값 확인 중...\n")
    
    sample_queries = [
        "자동차",
        "상해",
        "질병",
        "화재",
        "보험"
    ]
    
    all_insurance_types = set()
    
    for query in sample_queries:
        print(f"검색어: '{query}'")
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(query)
        
        if docs:
            types_in_results = set()
            for doc in docs:
                ins_type = doc.metadata.get("insurance_type")
                if ins_type:
                    types_in_results.add(ins_type)
                    all_insurance_types.add(ins_type)
            print(f"  → 발견된 insurance_type 값들: {types_in_results}")
        else:
            print(f"  → 검색 결과 없음")
        print()
    
    print("=" * 50)
    print(f"📋 전체 발견된 insurance_type 값들 (repr 포함):")
    for ins_type in sorted(all_insurance_types):
        print(f"  - {repr(ins_type)} (길이: {len(ins_type)}, bytes: {ins_type.encode('utf-8')})")
    print()
    
    # 실제 Qdrant payload 구조 확인
    print("=" * 50)
    print("🔍 Qdrant payload 전체 구조 확인 (처음 10개 포인트):")
    try:
        result = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=10,
            with_payload=True,
            with_vectors=False
        )
        points, _ = result
        
        print(f"포인트 개수: {len(points)}\n")
        
        for i, point in enumerate(points[:5], 1):
            print(f"--- 포인트 {i} ---")
            print(f"ID: {point.id}")
            print(f"Payload 키들: {list(point.payload.keys()) if point.payload else 'None'}")
            if point.payload:
                print(f"Payload 내용:")
                for key, value in point.payload.items():
                    print(f"  {key}: {repr(value)} (타입: {type(value).__name__})")
                    if key == "insurance_type" or "insurance" in key.lower():
                        print(f"    ⭐ 이 필드가 insurance_type입니다!")
            print()
        
        # LangChain이 사용하는 메타데이터 키 확인
        print("=" * 50)
        print("🔍 LangChain 검색 결과와 Qdrant payload 비교:")
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke("보험")
        
        if docs:
            print(f"LangChain 문서 메타데이터 키들: {list(docs[0].metadata.keys())}")
            print(f"LangChain insurance_type 값: {repr(docs[0].metadata.get('insurance_type'))}")
            print()
            
            # 해당 문서의 실제 Qdrant 포인트 찾기
            print("LangChain에서 가져온 문서의 실제 Qdrant payload 확인:")
            # LangChain은 메타데이터에 특정 키를 사용할 수 있음
            # _id 또는 다른 키로 실제 포인트를 찾을 수 있는지 확인
            for i, doc in enumerate(docs[:3], 1):
                print(f"\n문서 {i}:")
                print(f"  LangChain metadata: {doc.metadata}")
                
    except Exception as e:
        print(f"❌ payload 확인 실패: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # 각 insurance_type별 정확한 개수 확인 (필터 사용)
    print("📊 insurance_type별 문서 개수 (필터로 정확히 확인):")
    from qdrant_client.http import models
    
    for ins_type in sorted(all_insurance_types):
        try:
            # 필터로 해당 insurance_type만 검색
            # LangChain은 metadata를 중첩 딕셔너리로 저장하므로 "metadata.insurance_type" 경로 사용
            filter_condition = models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.insurance_type",
                        match=models.MatchValue(value=ins_type),
                    )
                ]
            )
            
            # scroll을 사용해서 필터에 해당하는 모든 포인트 가져오기
            # limit을 크게 설정하여 모든 결과 가져오기
            result = client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=filter_condition,
                limit=10000,  # 충분히 큰 값
                with_payload=True,
                with_vectors=False
            )
            
            # 실제로 가져온 개수
            points, next_page = result
            count = len(points)
            
            # 다음 페이지가 있으면 계속 가져오기
            while next_page is not None:
                result = client.scroll(
                    collection_name=COLLECTION_NAME,
                    scroll_filter=filter_condition,
                    limit=10000,
                    offset=next_page,
                    with_payload=True,
                    with_vectors=False
                )
                points, next_page = result
                count += len(points)
            
            print(f"  - {repr(ins_type)}: {count:,}개")
        except Exception as e:
            print(f"  - {repr(ins_type)}: 확인 실패 ({e})")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

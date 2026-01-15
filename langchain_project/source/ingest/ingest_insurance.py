#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
보험 약관 데이터 수집 - 정확한 파싱
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
import sys

# UTF-8 출력 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("보험 약관 데이터 수집 시작")
print("=" * 60)

# 데이터 폴더
project_root = Path(__file__).resolve().parent.parent.parent
data_dir = project_root / ".files"

xml_files = sorted(data_dir.glob("*.xml"))
print(f"\n데이터 폴더: {data_dir}")
print(f"파일 수: {len(xml_files)}")

# XML 문서 파싱
print(f"\nXML 파일 파싱 중...\n")
all_documents = []

for i, xml_file in enumerate(xml_files, 1):
    print(f"[{i}/{len(xml_files)}] 처리 중: {xml_file.name}")
    try:
        tree = ET.parse(str(xml_file))
        root = tree.getroot()
        
        # root > file 찾기
        file_elem = root.find('file')
        if file_elem is None:
            print(f"     파일 요소 없음")
            continue
        
        # 메타데이터 추출
        category = (file_elem.findtext('category') or '').strip()
        name = (file_elem.findtext('name') or '').strip()
        cn_text = (file_elem.findtext('cn') or '').strip()
        
        # cn은 전체 약관 내용
        if cn_text and len(cn_text) > 20:
            # 긴 텍스트를 섹션으로 분할
            # 각 "제" 단위로 분할
            sections = cn_text.split('제')
            
            count = 0
            for section in sections:
                section = section.strip()
                if len(section) > 50:
                    # 섹션 텍스트 복구
                    if section and not section.startswith('제'):
                        section = '제' + section
                    
                    doc = Document(
                        page_content=section[:1000],  # 섹션별로 1000자 제한
                        metadata={
                            'source': xml_file.name,
                            'category': category,
                            'name': name,
                        }
                    )
                    all_documents.append(doc)
                    count += 1
            
            print(f"     {count}개 문서 파싱됨")
        else:
            print(f"     콘텐츠 없음")
    
    except Exception as e:
        print(f"     오류: {str(e)[:50]}")

print(f"\n{len(all_documents)}개 문서를 Qdrant에 저장 중...")

if all_documents:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    vectorstore = QdrantVectorStore.from_documents(
        documents=all_documents,
        embedding=embeddings,
        url="http://localhost:6333",
        collection_name="insurance_docs",
        force_recreate=True,
    )
    
    print("Qdrant 저장 완료")
    
    from qdrant_client import QdrantClient
    client = QdrantClient("http://localhost:6333")
    col_info = client.get_collection("insurance_docs")
    
    print("\n" + "=" * 60)
    print(f"총 {col_info.points_count}개 documents가 Qdrant에 적재되었습니다!")
    print("=" * 60)
else:
    print("파싱된 문서가 없습니다!")

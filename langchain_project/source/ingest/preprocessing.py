#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML 파일 전처리 및 문서 생성
"""
import xml.etree.ElementTree as ET
from langchain_core.documents import Document
from typing import List

def build_documents_from_xml(file_path: str) -> List[Document]:
    """
    XML 파일을 읽고 LangChain Document 리스트로 변환
    
    Args:
        file_path: XML 파일 경로
        
    Returns:
        Document 리스트
    """
    documents = []
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # root > file 찾기
        file_elem = root.find('file')
        if file_elem is None:
            return []
        
        # 메타데이터 추출
        category = (file_elem.findtext('category') or '').strip()
        name = (file_elem.findtext('name') or '').strip()
        cn_text = (file_elem.findtext('cn') or '').strip()
        
        # 메인 컨텐츠는 cn 요소
        if cn_text and len(cn_text) > 50:
            # 긴 텍스트를 "제" 단위로 분할 (청크 분리)
            sections = cn_text.split('제')
            
            for section in sections:
                section = section.strip()
                if len(section) > 100:  # 최소 길이 필터
                    # 섹션 복구
                    if section and not section.startswith('제'):
                        section = '제' + section
                    
                    # 최대 1000자로 제한
                    section = section[:1000]
                    
                    doc = Document(
                        page_content=section,
                        metadata={
                            'source': file_path,
                            'category': category,
                            'name': name,
                        }
                    )
                    documents.append(doc)
    
    except Exception as e:
        print(f"Error parsing {file_path}: {str(e)}")
        return []
    
    return documents

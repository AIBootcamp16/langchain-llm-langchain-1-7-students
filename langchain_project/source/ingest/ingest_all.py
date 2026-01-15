#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 보험 XML 파일을 Qdrant에 적재
"""
import sys
from pathlib import Path

# 부모 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from source.ingest.preprocessing import build_documents_from_xml
from source.ingest.vertorstore_ingest import get_vectorstore

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data_selected"

print("=" * 60)
print("🔥 보험 XML 파일 Qdrant 적재 시작")
print("=" * 60)

# 🔥 Qdrant vectorstore 초기화
print("\n🔄 Qdrant 벡터스토어 초기화 중...")
vectorstore = get_vectorstore(recreate=True)
print("✓ Qdrant 연결 성공")

# 데이터 폴더 확인
if not DATA_DIR.exists():
    print(f"\n❌ 오류: {DATA_DIR} 폴더가 없습니다!")
    print("   먼저 select_insurance_files.py를 실행하세요.")
    sys.exit(1)

xml_files = sorted(DATA_DIR.glob("*.xml"))
if not xml_files:
    print(f"\n❌ 오류: {DATA_DIR} 폴더에 XML 파일이 없습니다!")
    sys.exit(1)

print(f"\n📂 {len(xml_files)}개 XML 파일 처리 중...\n")

total_docs = 0
failed_files = []

for i, xml_file in enumerate(xml_files, 1):
    print(f"[{i}/{len(xml_files)}] 처리 중: {xml_file.name}")
    try:
        docs = build_documents_from_xml(str(xml_file))
        if docs:
            vectorstore.add_documents(docs)
            total_docs += len(docs)
            print(f"     ✓ {len(docs)}개 문서 추가됨")
        else:
            print(f"     ⚠️  문서 추출 실패")
            failed_files.append(xml_file.name)
    except Exception as e:
        print(f"     ❌ 오류: {str(e)[:50]}")
        failed_files.append(xml_file.name)

print("\n" + "=" * 60)
print(f"✅ 총 {total_docs}개 documents Qdrant에 적재 완료!")
print("=" * 60)

if failed_files:
    print(f"\n⚠️  처리 실패: {len(failed_files)}개")
    for f in failed_files[:5]:  # 처음 5개만 표시
        print(f"   - {f}")

print("\n🎉 데이터 적재 완료!")
print("   다음 단계: Streamlit 앱 실행")
print("   poetry run streamlit run source/app/app_streamlit.py")

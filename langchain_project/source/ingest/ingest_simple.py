"""
간단한 보험 약관 데이터 수집 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from source.ingest.preprocessing import build_documents_from_xml
from source.ingest.vertorstore_ingest import get_vectorstore

print("=" * 60)
print("🔥 보험 약관 데이터 수집 시작")
print("=" * 60)

# 데이터 폴더 찾기 (여러 경로 시도)
project_dir = Path(__file__).resolve().parent.parent
possible_paths = [
    project_dir.parent / ".files",  # 프로젝트 루트의 .files
    project_dir / ".files",  # source 디렉토리의 .files (백업)
    Path("C:\\Users\\MiniH\\Desktop\\Langchain-Project\\01.유리"),  # 원본 폴더
    Path("C:\\Users\\MiniH\\Desktop\\Langchain-Project\\git\\langchain-llm-langchain-1-7-students\\langchain_project\\.files"),
]

data_dir = None
for path in possible_paths:
    if path.exists():
        xml_files = list(path.glob("*.xml"))
        if xml_files:
            data_dir = path
            print(f"\n✓ 데이터 폴더 발견: {data_dir}")
            print(f"  파일 수: {len(xml_files)}")
            break

if not data_dir:
    print("\n❌ XML 파일을 찾을 수 없습니다!")
    print("다음 경로를 확인하세요:")
    for p in possible_paths:
        print(f"  - {p}")
    sys.exit(1)

# Qdrant 벡터스토어 초기화
print("\n🔄 Qdrant 벡터스토어 초기화 중...")
vectorstore = get_vectorstore(recreate=True)

# 데이터 수집
total_docs = 0
xml_files = sorted(data_dir.glob("*.xml"))

print(f"\n📂 {len(xml_files)}개 XML 파일 처리 중...\n")

for i, xml_file in enumerate(xml_files, 1):
    print(f"[{i}/{len(xml_files)}] 처리 중: {xml_file.name}")
    try:
        docs = build_documents_from_xml(str(xml_file))
        if docs:
            vectorstore.add_documents(docs)
            total_docs += len(docs)
            print(f"     ✓ {len(docs)}개 문서 추가됨")
        else:
            print(f"     ⚠️  문서 생성 실패")
    except Exception as e:
        print(f"     ❌ 오류: {str(e)}")

print("\n" + "=" * 60)
print(f"✅ 총 {total_docs}개 documents가 Qdrant에 적재되었습니다!")
print("=" * 60)

if total_docs > 0:
    print("\n🎉 데이터 수집 완료!")
    print("   이제 Streamlit 앱을 실행하세요:")
    print("   poetry run streamlit run source/app/app_streamlit.py")
else:
    print("\n⚠️  경고: 어떤 문서도 적재되지 않았습니다!")
    print("   XML 파일을 확인하세요.")

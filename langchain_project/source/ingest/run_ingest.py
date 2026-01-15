#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
전체 데이터 수집 및 적재 자동화 스크립트
1. select_insurance_files.py - 파일 선택
2. ingest_all.py - Qdrant 적재
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """명령어 실행"""
    print("\n" + "=" * 60)
    print(f"🔄 {description}")
    print("=" * 60 + "\n")
    
    try:
        result = subprocess.run(cmd, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} 실패!")
        print(f"   오류: {str(e)}")
        return False

def main():
    project_root = Path(__file__).resolve().parent.parent
    ingest_dir = project_root / "ingest"
    
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + "  📊 보험 데이터 Qdrant 적재 자동화".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    # 1. 보험 파일 선택
    print("\n✨ Step 1/2: 보험 파일 선택")
    cmd1 = f"cd \"{ingest_dir}\" && python select_insurance_files.py"
    if not run_command(cmd1, "보험 파일 선택 중..."):
        sys.exit(1)
    
    # 2. Qdrant 적재
    print("\n✨ Step 2/2: Qdrant 데이터 적재")
    cmd2 = f"cd \"{ingest_dir}\" && python ingest_all.py"
    if not run_command(cmd2, "Qdrant 적재 중..."):
        sys.exit(1)
    
    # 완료
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + "  ✅ 모든 작업 완료!".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    print("\n📌 다음 단계:")
    print("   1. Qdrant Web UI 확인: http://localhost:6333/dashboard")
    print("   2. Streamlit 앱 실행: poetry run streamlit run source/app/app_streamlit.py")
    print("   3. http://localhost:8501 에서 챗봇 사용 시작!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 중단했습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류: {str(e)}")
        sys.exit(1)

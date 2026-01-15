#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 보험 Q&A 챗봇 완벽 자동화 스크립트
1. Qdrant 컨테이너 실행 확인
2. 보험 파일 선택 및 적재
3. Streamlit 앱 실행
"""
import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, description, show_output=True):
    """명령어 실행"""
    print(f"\n🔄 {description}...")
    
    try:
        if show_output:
            result = subprocess.run(cmd, check=True, shell=True)
        else:
            result = subprocess.run(cmd, check=True, shell=True, 
                                  capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 실패!")
        if not show_output:
            print(f"   오류: {e.stderr}")
        return False

def check_qdrant():
    """Qdrant 서버 연결 확인"""
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient("http://localhost:6333")
        client.get_collections()
        return True
    except:
        return False

def start_qdrant():
    """Qdrant Docker 컨테이너 시작"""
    print("\n✨ Qdrant 시작 중...")
    
    # 기존 컨테이너 종료
    subprocess.run("docker stop qdrant 2>nul", shell=True, capture_output=True)
    time.sleep(1)
    
    # 새 컨테이너 시작
    cmd = "docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Qdrant 컨테이너 시작됨")
        time.sleep(3)  # 시작 대기
        return True
    else:
        print(f"❌ Qdrant 시작 실패")
        return False

def main():
    project_root = Path(__file__).resolve().parent
    
    print("\n╔" + "=" * 60 + "╗")
    print("║" + "🚀 보험 Q&A 챗봇 완벽 자동화".center(60) + "║")
    print("╚" + "=" * 60 + "╝")
    
    # Step 1: Qdrant 확인
    print("\n\n📌 Step 1/3: Qdrant 서버 확인")
    print("-" * 60)
    
    if not check_qdrant():
        print("⚠️  Qdrant 서버가 실행되지 않았습니다.")
        if not start_qdrant():
            print("\n❌ Qdrant를 시작할 수 없습니다!")
            print("   수동으로 시작: docker run -p 6333:6333 qdrant/qdrant")
            sys.exit(1)
    else:
        print("✓ Qdrant 서버 정상 실행 중")
    
    # Step 2: 데이터 적재
    print("\n\n📌 Step 2/3: 데이터 적재")
    print("-" * 60)
    
    run_ingest = project_root / "source" / "ingest" / "run_ingest.py"
    cmd = f"cd \"{project_root}\" && poetry run python \"{run_ingest}\""
    if not run_command(cmd, "데이터 적재 실행"):
        print("\n⚠️  데이터 적재 실패!")
        print("   수동으로 실행: poetry run python source/ingest/run_ingest.py")
    
    # Step 3: Streamlit 앱 실행
    print("\n\n📌 Step 3/3: Streamlit 앱 실행")
    print("-" * 60)
    
    streamlit_app = project_root / "source" / "app" / "app_streamlit.py"
    cmd = f"cd \"{project_root}\" && poetry run streamlit run \"{streamlit_app}\" --logger.level=error"
    
    print("\n" + "=" * 60)
    print("✅ 모든 준비 완료!")
    print("=" * 60)
    print("\n🌐 다음 URL에서 챗봇에 접속하세요:")
    print("   http://localhost:8501")
    print("\n📊 Qdrant 관리 화면:")
    print("   http://localhost:6333/dashboard")
    print("\n" + "=" * 60)
    
    # Streamlit 앱 실행 (포그라운드)
    print("\n🔄 Streamlit 앱 시작 중...")
    print("-" * 60)
    
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 중단했습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 오류: {str(e)}")
        sys.exit(1)

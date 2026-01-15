#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01.유리 폴더에서 보험 관련 XML 파일만 선택해서 data_selected 폴더로 복사
"""
from pathlib import Path
import shutil
import re
import unicodedata

# 원본 XML 폴더 (Windows/Mac/Linux 호환)
RAW_DIR = Path(r"c:\Users\MiniH\Desktop\Langchain-Project\01.유리")
# 선택된 파일 저장 폴더
TARGET_DIR = Path(__file__).resolve().parent.parent / "data_selected"

# 우리가 가져올 보험 유형
TARGET_INSURANCE_TYPES = [
    "상해보험",
    "손해보험",
    "연금보험",
    "자동차보험",
    "질병보험",
    "책임보험",
    "화재보험",
]

def extract_insurance_type_raw(filename: str) -> str | None:
    """
    파일명에서 보험 유형 추출
    예: 001_상해보험_가공.xml -> 상해보험
    """
    # Unicode 정규화(NFC)
    filename = unicodedata.normalize("NFC", filename)
    match = re.search(r"_(.+?)_가공", filename)
    if match:
        return match.group(1)
    return None

def select_files():
    TARGET_DIR.mkdir(exist_ok=True)
    
    # 기존 파일 정리
    for f in TARGET_DIR.glob("*.xml"):
        f.unlink()
    
    print("=" * 60)
    print("보험 XML 파일 선택 시작")
    print("=" * 60)
    print(f"\n원본 폴더: {RAW_DIR}")
    print(f"대상 폴더: {TARGET_DIR}")
    print("기존 data_selected 폴더 정리됨\n")
    
    if not RAW_DIR.exists():
        print(f"❌ 오류: {RAW_DIR} 폴더가 없습니다!")
        return 0
    
    copied = 0

    for xml_file in sorted(RAW_DIR.glob("*.xml")):
        insurance_type = extract_insurance_type_raw(xml_file.name)
        if insurance_type in TARGET_INSURANCE_TYPES:
            shutil.copy2(xml_file, TARGET_DIR / xml_file.name)
            copied += 1
            print(f"  ✓ {xml_file.name}")
    
    print("\n" + "=" * 60)
    print(f"✅ {copied}개 보험 XML 파일 선택 완료")
    print("=" * 60)
    
    return copied

    print("---- 완료 ----")
    print(f"총 {copied}개 파일 복사 완료")

if __name__ == "__main__":
    select_files()

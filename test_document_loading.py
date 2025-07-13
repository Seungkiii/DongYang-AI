#!/usr/bin/env python3
"""
문서 로딩 테스트 스크립트
"""
import os
import sys
from pathlib import Path

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.document_loader import load_pdf_documents, split_documents
from app.core.config import get_settings

def test_document_loading():
    """문서 로딩 테스트"""
    print("🔍 문서 로딩 테스트 시작")
    print("=" * 50)
    
    # 설정 로드
    settings = get_settings()
    
    # 문서 로드
    documents = load_pdf_documents(settings.documents_path)
    
    if not documents:
        print("❌ 문서를 로드할 수 없습니다.")
        return False
    
    print(f"✅ {len(documents)}개의 문서를 성공적으로 로드했습니다.")
    
    # 첫 번째 문서 정보 출력
    if documents:
        first_doc = documents[0]
        print(f"📄 첫 번째 문서:")
        print(f"   - 파일명: {first_doc.metadata.get('source', 'Unknown')}")
        print(f"   - 페이지 수: {first_doc.metadata.get('pages', 'Unknown')}")
        print(f"   - 텍스트 길이: {len(first_doc.page_content)} 문자")
        print(f"   - 첫 100자: {first_doc.page_content[:100]}...")
    
    # 문서 청크 분할 테스트
    print("\n🔪 문서 청크 분할 테스트")
    chunks = split_documents(documents, settings.chunk_size, settings.chunk_overlap)
    
    if chunks:
        print(f"✅ {len(chunks)}개의 청크를 생성했습니다.")
        print(f"📊 평균 청크 크기: {sum(len(chunk.page_content) for chunk in chunks) / len(chunks):.0f} 문자")
    else:
        print("❌ 청크를 생성할 수 없습니다.")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = test_document_loading()
        if success:
            print("\n🎉 문서 로딩 테스트 완료!")
        else:
            print("\n❌ 문서 로딩 테스트 실패!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 
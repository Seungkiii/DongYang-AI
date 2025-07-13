#!/usr/bin/env python3
"""
문서 벡터화 스크립트
PDF 문서를 로드하고 벡터 임베딩을 생성하여 ChromaDB에 저장합니다.
"""

import sys
import os
import logging
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.document_loader import load_pdf_documents, split_documents
from app.core.vector_store import VectorStore
from app.core.config import get_settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def vectorize_documents():
    """문서를 벡터화하여 ChromaDB에 저장합니다."""
    try:
        settings = get_settings()
        
        print("🔄 문서 벡터화 시작...")
        print(f"📁 문서 폴더: {settings.documents_path}")
        print(f"🗄️ 벡터 저장소: {settings.vector_store_path}")
        
        # 1. 문서 로드
        print("\n📖 PDF 문서 로드 중...")
        documents = load_pdf_documents(settings.documents_path)
        
        if not documents:
            print("❌ 로드된 문서가 없습니다!")
            return False
        
        print(f"✅ {len(documents)}개의 문서를 성공적으로 로드했습니다.")
        
        # 2. 문서 청크 분할
        print("\n✂️  문서 청크 분할...")
        chunks = split_documents(
            documents,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        
        if not chunks:
            print("❌ 청크를 생성할 수 없습니다!")
            return False
        
        print(f"✅ {len(chunks)}개의 청크를 생성했습니다.")
        
        # 3. 벡터 저장소 초기화
        print("\n🔄 벡터 저장소 초기화...")
        vector_store = VectorStore(
            openai_api_key=settings.openai_api_key,
            collection_name="insurance_docs"
        )
        
        # 4. 문서 벡터화 및 저장 (배치 처리)
        print("\n🔄 벡터 임베딩 및 ChromaDB 저장...")
        print("⏳ 이 과정은 시간이 오래 걸릴 수 있습니다...")
        
        # 배치 크기를 더 작게 설정 (토큰 제한 고려)
        batch_size = 25  # 50에서 25로 줄임
        vector_store.add_documents_batch(chunks, batch_size=batch_size)
        
        # 5. 결과 확인
        print("\n📊 벡터화 결과 확인...")
        collection_info = vector_store.get_collection_info()
        print(f"✅ 컬렉션: {collection_info['name']}")
        print(f"✅ 저장된 문서 수: {collection_info['count']}")
        print(f"✅ 상태: {collection_info['status']}")
        
        print("\n🎉 문서 벡터화 완료!")
        return True
        
    except Exception as e:
        logger.error(f"❌ 벡터화 중 오류 발생: {e}")
        print(f"❌ 벡터화 실패!")
        return False

if __name__ == "__main__":
    success = vectorize_documents()
    sys.exit(0 if success else 1) 
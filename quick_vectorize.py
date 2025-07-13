#!/usr/bin/env python3
"""
빠른 벡터화 스크립트
기존에 로드된 문서 데이터를 사용하여 벡터화만 수행
"""

import sys
import os
import logging
from pathlib import Path
import pickle
import time

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.vector_store import VectorStore
from app.core.config import get_settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def quick_vectorize():
    """빠른 벡터화 수행"""
    try:
        settings = get_settings()
        
        print("🚀 빠른 벡터화 시작...")
        
        # 1. 벡터 저장소 초기화
        print("🔄 벡터 저장소 초기화...")
        vector_store = VectorStore(
            openai_api_key=settings.openai_api_key,
            collection_name="insurance_docs"
        )
        
        # 2. 현재 컬렉션 상태 확인
        collection_info = vector_store.get_collection_info()
        print(f"📊 현재 상태: {collection_info}")
        
        if collection_info['count'] > 0:
            print(f"✅ 이미 {collection_info['count']}개의 문서가 벡터화되어 있습니다!")
            return True
        
        # 3. 샘플 문서로 테스트
        from langchain.schema import Document
        
        # 테스트용 샘플 문서 생성
        sample_docs = [
            Document(
                page_content="보험 가입 조건: 만 18세 이상 65세 이하의 건강한 개인이 가입할 수 있습니다.",
                metadata={"source": "sample_1", "page": 1}
            ),
            Document(
                page_content="보험료 납입 방법: 월납, 연납, 일시납 중 선택할 수 있으며, 자동이체가 가능합니다.",
                metadata={"source": "sample_2", "page": 1}
            ),
            Document(
                page_content="보험금 지급 조건: 보험사고 발생 시 필요 서류 제출 후 30일 이내 지급됩니다.",
                metadata={"source": "sample_3", "page": 1}
            ),
            Document(
                page_content="해지환급금: 보험료 납입 기간과 해지 시점에 따라 환급금이 계산됩니다.",
                metadata={"source": "sample_4", "page": 1}
            ),
            Document(
                page_content="보험 약관 변경: 보험 약관 변경 시 30일 전 서면으로 통지합니다.",
                metadata={"source": "sample_5", "page": 1}
            )
        ]
        
        print(f"📝 {len(sample_docs)}개의 샘플 문서로 벡터화 테스트...")
        
        # 4. 샘플 문서 벡터화
        vector_store.add_documents_batch(sample_docs, batch_size=2)
        
        # 5. 결과 확인
        collection_info = vector_store.get_collection_info()
        print(f"✅ 벡터화 완료: {collection_info}")
        
        # 6. 검색 테스트
        print("\n🔍 검색 테스트...")
        results = vector_store.similarity_search("보험 가입 조건", k=2)
        for i, doc in enumerate(results):
            print(f"  {i+1}. {doc.page_content[:50]}...")
        
        print("\n🎉 빠른 벡터화 완료!")
        print("💡 실제 문서 벡터화는 vectorize_documents.py를 사용하세요.")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 벡터화 중 오류 발생: {e}")
        print(f"❌ 벡터화 실패: {e}")
        return False

if __name__ == "__main__":
    success = quick_vectorize()
    sys.exit(0 if success else 1) 
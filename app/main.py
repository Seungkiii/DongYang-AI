import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .api import chat
from .core.config import get_settings

# 환경 변수 로드
load_dotenv()

settings = get_settings()

app = FastAPI(
    title="동양생명 보험 상담 AI API",
    description="보험 약관 기반 질의응답 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: 실제 배포 시 허용할 도메인 설정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router, prefix="/api")

@app.get("/", include_in_schema=False)
async def read_root():
    return FileResponse("chatbot_ui.html")

@app.get("/health")
async def health_check():
    """서버 상태 확인 엔드포인트"""
    return {"status": "healthy", "message": "동양생명 보험 상담 AI API가 정상 작동 중입니다."}

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 벡터 저장소 상태 확인"""
    try:
        print("=" * 60)
        print("🚀 동양생명 보험 상담 AI API 시작")
        print("=" * 60)
        
        # 벡터 저장소 디렉토리 확인
        vector_store_path = settings.vector_store_path
        if os.path.exists(vector_store_path):
            print(f"✅ 벡터 저장소 발견: {vector_store_path}")
            print("💡 기존 벡터 인덱스를 사용합니다.")
        else:
            print(f"⚠️  벡터 저장소가 없습니다: {vector_store_path}")
            print("📝 벡터화를 먼저 수행해주세요:")
            print("   python3 vectorize_documents.py")
        
        print("=" * 60)
        print("🎯 API 엔드포인트:")
        print("   GET  /health - 서버 상태 확인")
        print("   POST /api/chat/question - 질의응답")
        print("=" * 60)
        print("✅ 서버 시작 완료!")
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ 서버 시작 중 오류 발생: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc() 
#!/usr/bin/env python3
"""
간단한 API 테스트 스크립트
"""
import requests
import json
import time

def test_health():
    """Health check 테스트"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check 성공")
            print(f"📋 응답: {response.json()}")
            return True
        else:
            print(f"❌ Health check 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check 오류: {e}")
        return False

def test_chat(question):
    """Chat API 테스트"""
    try:
        payload = {"question": question, "context_count": 3}
        response = requests.post("http://localhost:8000/api/chat/question", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 질문: {question}")
            print(f"🤖 답변: {result.get('answer', '')[:200]}...")
            print(f"📚 컨텍스트 수: {len(result.get('contexts', []))}")
            return True
        else:
            print(f"❌ Chat API 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat API 오류: {e}")
        return False

if __name__ == "__main__":
    print("🔍 간단한 API 테스트 시작")
    print("=" * 40)
    
    # Health check
    if test_health():
        print("\n🤖 Chat API 테스트")
        test_chat("갑상선암은 일반암인가요?")
    
    print("\n테스트 완료") 
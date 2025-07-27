# 동양생명 보험 챗봇 배포 전략

## 배포 개요
3개의 분리된 컴포넌트(Frontend, Backend, AI)를 Docker Compose를 통해 통합 배포하는 전략입니다.

## 배포 아키텍처

```
EC2 Instance (Amazon Linux 2)
├── nginx/ (리버스 프록시)
├── docker-compose.yml (서비스 오케스트레이션)
├── .env (환경변수)
└── services/
    ├── frontend/ (React 앱)
    ├── backend/ (Spring Boot API)
    └── ai/ (FastAPI + RAG)
```

## Docker Compose 구성

### 1. 네트워크 구성
```yaml
networks:
  chatbot-network:
    driver: bridge
```

### 2. 서비스 간 통신
- **Frontend** → **Backend**: `http://backend:8080`
- **Backend** → **AI Server**: `http://ai:8000`
- **외부** → **Nginx**: `http://ec2-ip:80`

### 3. 볼륨 마운트
```yaml
volumes:
  vector_store: # AI 서버의 벡터 DB 영구 저장
  postgres_data: # 백엔드 DB 데이터 영구 저장
```

## 배포 순서 및 의존성

### 1단계: 인프라 준비
```bash
# EC2 인스턴스 접속
ssh -i your-key.pem ec2-user@ec2-3-38-100-135.ap-northeast-2.compute.amazonaws.com

# Docker 및 Docker Compose 설치
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2단계: 환경 설정
```bash
# 환경변수 파일 생성
cat > .env << EOF
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Database
POSTGRES_DB=chatbot
POSTGRES_USER=chatbot_user
POSTGRES_PASSWORD=secure_password

# Spring Boot
SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/chatbot
SPRING_DATASOURCE_USERNAME=chatbot_user
SPRING_DATASOURCE_PASSWORD=secure_password

# AI Server
AI_SERVER_URL=http://ai:8000
VECTOR_STORE_PATH=/app/vector_store

# Frontend
REACT_APP_API_URL=/api
EOF
```

### 3단계: 서비스 배포
```bash
# 모든 서비스 빌드 및 시작
docker-compose up -d --build

# 서비스 상태 확인
docker-compose ps
docker-compose logs -f
```

## CI/CD 파이프라인 통합

### GitHub Actions Workflow
각 저장소의 변경사항이 자동으로 배포되는 파이프라인:

```yaml
# .github/workflows/deploy.yml (각 저장소)
name: Deploy to EC2
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to EC2
        run: |
          # 1. EC2 접속
          # 2. 해당 서비스만 재빌드
          # 3. 무중단 배포 (rolling update)
```

### 배포 트리거 순서
1. **AI Server 변경** → AI 컨테이너만 재시작
2. **Backend 변경** → Backend 컨테이너 재시작 → AI 연결 테스트
3. **Frontend 변경** → Frontend 컨테이너 재시작 → Nginx 설정 리로드

## 서비스 헬스체크

### 1. AI Server 헬스체크
```bash
curl http://localhost:8000/
# 응답: {"status": "healthy", "service": "AI Server"}
```

### 2. Backend 헬스체크
```bash
curl http://localhost:8080/api/health
# 응답: {"status": "UP"}
```

### 3. Frontend 접근성 테스트
```bash
curl http://localhost:3000/
# 응답: React 앱 HTML
```

## 무중단 배포 전략

### Rolling Update 방식
```bash
# 1. 새 이미지 빌드
docker-compose build [service-name]

# 2. 서비스별 순차 업데이트
docker-compose up -d --no-deps [service-name]

# 3. 헬스체크 후 이전 컨테이너 제거
docker system prune -f
```

### Blue-Green 배포 (선택사항)
```bash
# 1. 새 환경 구성
docker-compose -f docker-compose.blue.yml up -d

# 2. 트래픽 전환 (Nginx 설정 변경)
# 3. 이전 환경 제거
```

## 모니터링 및 로깅

### 로그 수집
```bash
# 전체 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f ai backend frontend
```

### 리소스 모니터링
```bash
# 컨테이너 리소스 사용량
docker stats

# 디스크 사용량
df -h
du -sh /var/lib/docker/
```

## 백업 및 복구

### 데이터 백업
```bash
# 벡터 DB 백업
docker-compose exec ai tar -czf /tmp/vector_store_backup.tar.gz /app/vector_store

# PostgreSQL 백업
docker-compose exec postgres pg_dump -U chatbot_user chatbot > backup.sql
```

### 복구 절차
```bash
# 서비스 중단
docker-compose down

# 데이터 복구
# 서비스 재시작
docker-compose up -d
```

## 트러블슈팅

### 일반적인 문제들

1. **컨테이너 간 통신 실패**
   ```bash
   docker network ls
   docker network inspect dongyang-chatbot_chatbot-network
   ```

2. **포트 충돌**
   ```bash
   netstat -tulpn | grep :80
   sudo fuser -k 80/tcp
   ```

3. **메모리 부족**
   ```bash
   free -h
   docker system prune -a
   ```

4. **SSL 인증서 문제**
   ```bash
   sudo certbot renew
   sudo nginx -t && sudo nginx -s reload
   ```

## 성능 최적화

### 1. 이미지 최적화
- Multi-stage 빌드 사용
- 불필요한 패키지 제거
- 레이어 캐싱 활용

### 2. 리소스 제한
```yaml
services:
  ai:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

### 3. 캐싱 전략
- Nginx 정적 파일 캐싱
- Redis 세션 캐싱 (선택사항)
- AI 응답 캐싱 (선택사항)

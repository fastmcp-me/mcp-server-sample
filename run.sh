#!/bin/bash

# 2025년 세법 개정안 MCP 서버 실행 스크립트

set -e

echo "=== 2025년 세법 개정안 MCP 서버 시작 ==="

# 1. 의존성 설치 확인
echo "1. Python 패키지 설치 확인 중..."
if [ ! -d "venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# 2. ChromaDB 실행
echo "2. ChromaDB 실행 중..."
docker-compose up -d

# ChromaDB 시작 대기
echo "ChromaDB 시작 대기 중..."
sleep 10

# 3. 문서 인덱싱
echo "3. PDF 문서 인덱싱 중..."
python index_document.py

# 4. MCP 서버 실행
echo "4. MCP 서버 실행 중..."
echo "서버가 실행되었습니다. Ctrl+C로 중지할 수 있습니다."
python mcp_server.py

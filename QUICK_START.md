# 빠른 시작 가이드

## 🚀 1분 만에 시작하기

### 1. 시스템 실행
```bash
# 전체 시스템을 한 번에 실행
./run.sh
```

### 2. 수동 실행 (단계별)
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. ChromaDB 실행
docker-compose up -d

# 3. 문서 인덱싱
python index_document.py

# 4. MCP 서버 실행
python mcp_server.py
```

## 📋 시스템 상태 확인

### ChromaDB 상태 확인
```bash
docker ps
```

### 저장된 문서 확인
```bash
# ChromaDB UI 접속 (선택사항)
open http://localhost:8000
```

## 🔧 MCP 서버 설정

### Clode 설정
```json
{
  "mcpServers": {
    "tax-document-mcp": {
      "command": "python",
      "args": ["/Users/cheolminbae/workspace/document-mcp/mcp_server.py"],
      "env": {
        "CHROMA_HOST": "localhost",
        "CHROMA_PORT": "8000"
      }
    }
  }
}
```

### Cursor IDE 설정
```json
{
  "mcpServers": {
    "tax-document-mcp": {
      "command": "python",
      "args": ["/Users/cheolminbae/workspace/document-mcp/mcp_server.py"],
      "env": {
        "CHROMA_HOST": "localhost",
        "CHROMA_PORT": "8000"
      }
    }
  }
}
```

## 💡 사용 예시

### Clode/Cursor에서 사용하기
```
세법 개정안에서 소득세 관련 내용을 검색해줘
법인세 개정사항을 찾아줘
부가가치세 변경사항을 알려줘
문서 정보를 보여줘
```

## 🛠️ 문제 해결

### ChromaDB 연결 오류
```bash
# ChromaDB 재시작
docker-compose restart
```

### 의존성 오류
```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 문서 인덱싱 오류
```bash
# PDF 파일 확인
ls -la 2025_tax.pdf

# 인덱싱 재실행
python index_document.py
```

## 📊 시스템 정보

- **문서**: 2025년 세법 개정안 (422페이지)
- **저장된 청크**: 497개
- **벡터 DB**: ChromaDB
- **임베딩 모델**: jhgan/ko-sroberta-multitask (한국어 최적화)
- **검색 기능**: 자연어 쿼리 지원

## 🎯 주요 기능

1. **문서 검색**: 자연어로 세법 내용 검색
2. **정보 조회**: 저장된 문서 정보 확인
3. **컬렉션 관리**: ChromaDB 컬렉션 목록 조회

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. ChromaDB가 실행 중인지 확인
2. 문서 인덱싱이 완료되었는지 확인
3. MCP 서버 경로가 올바른지 확인

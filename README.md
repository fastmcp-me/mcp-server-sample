# 2025년 세법 개정안 MCP 서버

이 프로젝트는 2025년 세법 개정안 PDF 문서를 기반으로 한 MCP(Model Context Protocol) 서버입니다. Vector DB와 LangChain을 활용하여 문서 내용을 검색하고 관련 정보를 제공합니다.

## 기능

- PDF 문서 파싱 및 청크 분할
- ChromaDB를 이용한 벡터 저장 및 검색
- MCP 프로토콜을 통한 문서 검색 API
- 자연어 쿼리를 통한 세법 정보 검색

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. ChromaDB 실행
```bash
docker-compose up -d
```

### 3. 문서 인덱싱
```bash
python index_document.py
```

### 4. MCP 서버 실행
```bash
python mcp_server.py
```

## MCP 서버 설정

### Clode 클라이언트 설정
Clode에서 MCP 서버를 추가하려면:

1. Clode 설정에서 MCP 서버 추가
2. 서버 경로: `python /path/to/mcp_server.py`
3. 서버 이름: `tax-document-mcp`

### Cursor IDE 설정
Cursor에서 MCP 서버를 추가하려면:

1. Cursor 설정 파일에 MCP 서버 추가
2. 서버 경로: `python /path/to/mcp_server.py`
3. 서버 이름: `tax-document-mcp`

## API 사용법

MCP 서버는 다음 기능을 제공합니다:

- `search_document`: 문서 내용 검색
- `get_document_info`: 문서 정보 조회
- `list_collections`: 저장된 컬렉션 목록 조회

## 환경 변수

- `CHROMA_HOST`: ChromaDB 호스트 (기본값: localhost)
- `CHROMA_PORT`: ChromaDB 포트 (기본값: 8000)
- `PDF_PATH`: PDF 파일 경로 (기본값: 2025_tax.pdf)

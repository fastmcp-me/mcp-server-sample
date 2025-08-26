# MCP 서버 설정 가이드

이 가이드는 2025년 세법 개정안 MCP 서버를 Clode와 Cursor IDE에서 사용하는 방법을 설명합니다.

## 사전 준비

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **ChromaDB 실행**
   ```bash
   docker-compose up -d
   ```

3. **문서 인덱싱**
   ```bash
   python index_document.py
   ```

## Clode 클라이언트 설정

### 1. Clode 설정 파일 생성/수정

Clode의 설정 파일에 MCP 서버를 추가합니다:

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

### 2. Clode에서 사용하기

1. Clode를 재시작합니다.
2. 채팅에서 다음과 같이 사용할 수 있습니다:
   ```
   세법 개정안에서 소득세 관련 내용을 검색해줘
   ```

## Cursor IDE 설정

### 1. Cursor 설정 파일 생성/수정

Cursor의 설정 파일(`~/.cursor/settings.json`)에 MCP 서버를 추가합니다:

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

### 2. Cursor에서 사용하기

1. Cursor를 재시작합니다.
2. AI 채팅에서 다음과 같이 사용할 수 있습니다:
   ```
   2025년 세법 개정안에서 법인세 관련 내용을 찾아줘
   ```

## 사용 가능한 기능

### 1. 문서 검색 (`search_document`)
- **설명**: 2025년 세법 개정안 문서에서 관련 내용을 검색합니다.
- **매개변수**:
  - `query`: 검색할 쿼리 (예: '소득세', '법인세', '부가가치세' 등)
  - `max_results`: 최대 결과 수 (기본값: 5)

**사용 예시**:
```
세법 개정안에서 소득세 관련 내용을 검색해줘
법인세 개정사항을 찾아줘
부가가치세 변경사항을 알려줘
```

### 2. 문서 정보 조회 (`get_document_info`)
- **설명**: 저장된 문서의 정보를 조회합니다.
- **매개변수**: 없음

**사용 예시**:
```
문서 정보를 알려줘
저장된 문서의 상세 정보를 보여줘
```

### 3. 컬렉션 목록 조회 (`list_collections`)
- **설명**: ChromaDB에 저장된 컬렉션 목록을 조회합니다.
- **매개변수**: 없음

**사용 예시**:
```
저장된 컬렉션 목록을 보여줘
```

## 문제 해결

### 1. ChromaDB 연결 오류
```bash
# ChromaDB 상태 확인
docker ps

# ChromaDB 재시작
docker-compose restart
```

### 2. MCP 서버 실행 오류
```bash
# 의존성 재설치
pip install -r requirements.txt

# 서버 테스트
python test_mcp_server.py
```

### 3. 문서 인덱싱 오류
```bash
# PDF 파일 확인
ls -la 2025_tax.pdf

# 인덱싱 재실행
python index_document.py
```

## 환경 변수

- `CHROMA_HOST`: ChromaDB 호스트 (기본값: localhost)
- `CHROMA_PORT`: ChromaDB 포트 (기본값: 8000)
- `PDF_PATH`: PDF 파일 경로 (기본값: 2025_tax.pdf)

## 주의사항

1. **ChromaDB 실행**: MCP 서버를 사용하기 전에 반드시 ChromaDB가 실행되어야 합니다.
2. **문서 인덱싱**: PDF 파일이 변경되면 다시 인덱싱해야 합니다.
3. **메모리 사용량**: 임베딩 모델 로딩 시 메모리를 사용하므로 충분한 메모리가 필요합니다.
4. **한국어 지원**: 한국어 임베딩 모델을 사용하므로 한국어 쿼리가 최적화되어 있습니다.

## 성능 최적화

1. **청크 크기 조정**: `index_document.py`에서 `chunk_size`를 조정하여 검색 정확도를 개선할 수 있습니다.
2. **임베딩 모델 변경**: 다른 한국어 임베딩 모델로 변경하여 성능을 개선할 수 있습니다.
3. **결과 수 조정**: `max_results` 매개변수를 조정하여 검색 결과 수를 제어할 수 있습니다.

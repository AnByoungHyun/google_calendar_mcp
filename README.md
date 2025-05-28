# Google Calendar MCP stdio 서버

## 개요
Google Calendar와 연동되는 MCP stdio 서버입니다. Cursor 등에서 MCP 프로토콜로 일정을 조회, 생성, 상세 조회할 수 있습니다. 인증은 Google OAuth2를 사용합니다.

## 주요 기능
- Google Calendar API 연동
- MCP stdio 서버로 일정 조회, 생성, 상세 조회 기능 제공
- Google OAuth2 인증 처리

---

## 기술 스택
- **Python 3.13 이상 (권장: 3.13.3)**
- **패키지 매니저**: [uv](https://github.com/astral-sh/uv)
- **MCP 서버**: fastmcp
- **Google API 연동**: google-api-python-client, google-auth, google-auth-oauthlib
- **인증**: OAuth2 (Google)

---

## 구현 기능 및 MCP 메서드

| 기능                | MCP 메서드                  | 설명                                 |
|---------------------|-----------------------------|--------------------------------------|
| 1달 치 일정 보기    | list_month_events           | 지정한 연/월의 모든 일정 목록 조회   |
| 특정 일자 일정 보기 | list_day_events             | 지정한 날짜의 모든 일정 목록 조회    |
| 일정 상세 보기      | get_event_detail            | 일정 ID로 상세 정보 조회             |
| 일정 등록           | create_event                | 새로운 일정 생성 (참여자(이메일) 추가 가능)           |

---

## 설치 및 실행 방법 (uv 사용)

1. **uv 설치**
   ```bash
   pip install uv
   # 또는
   curl -Ls https://astral.sh/uv/install.sh | sh
   ```

2. **의존성 설치 및 가상환경 생성**
   ```bash
   uv pip install -r requirements.txt
   uv venv
   ```

3. **환경변수 파일(.env) 생성**
   프로젝트 루트에 아래와 같이 `.env` 파일을 만듭니다.
   ```env
   GOOGLE_CLIENT_SECRET_FILE=client_secret.json
   GOOGLE_API_SCOPES=https://www.googleapis.com/auth/calendar
   ```

4. **Google OAuth2 클라이언트 파일 준비**
   - Google Cloud Console에서 OAuth 동의 화면을 설정하고, OAuth 클라이언트 ID를 생성하여 `client_secret.json` 파일을 다운로드합니다.
   - [최신 발급 방법]
     1. Google Cloud Console 접속 → 프로젝트 선택/생성
     2. 좌측 메뉴에서 "API 및 서비스 > 사용자 인증 정보" 이동
     3. "OAuth 동의 화면"에서 사용자 유형 선택 및 필수 정보 입력 후 저장
     4. "사용자 인증 정보 만들기 > OAuth 클라이언트 ID" 선택
     5. 애플리케이션 유형은 "데스크톱 앱" 선택, 이름 입력 후 생성
     6. 생성된 클라이언트에서 `client_secret.json` 파일 다운로드 → 프로젝트 루트에 저장

5. **서버 실행**
   ```bash
   uv run python google_calendar_mcp/server.py
   # 또는 entry point 등록 시
   uv run google_calendar_mcp
   ```
   - 실행 시 별도 메시지는 출력되지 않으며, MCP stdio 프로토콜로만 통신합니다.

---

## MCP 서버 설치 방법

### 1. 깃허브에서 직접 설치
```bash
git clone https://github.com/AnByoungHyun/google_calendar_mcp.git
cd google_calendar_mcp
uv pip install -r requirements.txt
uv sync
```

### 2. uv로 바로 설치
```bash
uv pip install "git+https://github.com/AnByoungHyun/google_calendar_mcp.git"
uv sync
```

---

## Cursor MCP 등록 예시

`.cursor/mcp.json` 예시:
```json
{
  "google-calendar": {
    "command": "uv",
    "args": ["--directory", "<google_calendar_mcp_경로>", "run", "google_calendar_mcp"]
  }
}
```

---

## 참고 및 문의
- Google Calendar API 공식 문서: https://developers.google.com/calendar/api
- MCP/fastmcp 문서: https://github.com/anysphere/fastmcp

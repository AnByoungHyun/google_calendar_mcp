# Google Calendar MCP

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

## 1. uv 설치 (최초 1회만)
```bash
# macOS/Homebrew
brew install uv

# 또는 공식 설치 스크립트
curl -Ls https://astral.sh/uv/install.sh | sh
```

## 2. MCP 패키지 다운로드
```bash
git clone https://github.com/AnByoungHyun/google_calendar_mcp.git
cd google_calendar_mcp
```

## 3. 패키지 설치
```bash
uv sync
```
- 위 명령어 한 줄로 모든 패키지가 자동 설치됩니다.

## 4. Cursor MCP 등록 예시
`.cursor/mcp.json` 예시:
```json
{
  "mcpServers": {
    ...
    "google-calendar": {
      "command": "uv",
      "args": ["--directory", "<google_calendar_mcp_path>", "run", "google_calendar_mcp"]
    }
  }
}
```

---

## 참고 및 문의
- Google Calendar API 공식 문서: https://developers.google.com/calendar/api
- MCP/fastmcp 문서: https://github.com/anysphere/fastmcp

> 별도의 가상환경/venv 명령은 필요 없습니다. uv가 자동으로 안전한 환경을 만들어줍니다.
> 설치/실행 중 궁금한 점이 있으면 언제든 문의해 주세요!

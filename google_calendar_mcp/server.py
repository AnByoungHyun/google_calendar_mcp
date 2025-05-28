from mcp.server.fastmcp import FastMCP
from google_calendar_mcp.google_auth import get_calendar_service
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from typing import Optional, List, Any

mcp = FastMCP("google_calendar_mcp")

@mcp.tool()
def list_month_events(year: int, month: int) -> dict[str, Any]:
    """지정한 연/월의 모든 일정 목록 조회"""
    service = get_calendar_service()
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    time_min = start_date.isoformat() + 'Z'
    time_max = end_date.isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    return {"count": len(events), "events": events}

@mcp.tool()
def list_day_events(date: str) -> dict[str, Any]:
    """지정한 날짜(YYYY-MM-DD)의 모든 일정 목록 조회"""
    service = get_calendar_service()
    start_date = datetime.strptime(date, "%Y-%m-%d")
    end_date = start_date + timedelta(days=1)
    time_min = start_date.isoformat() + 'Z'
    time_max = end_date.isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    return {"count": len(events), "events": events}

@mcp.tool()
def get_event_detail(event_id: str) -> dict[str, Any]:
    """일정 ID로 상세 정보 조회"""
    service = get_calendar_service()
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    return event

@mcp.tool()
def create_event(summary: str, start: str, end: str, description: str = None, location: str = None, attendees: Optional[List[str]] = None) -> dict[str, Any]:
    """새로운 일정 생성 (attendees: 이메일 리스트)"""
    service = get_calendar_service()
    event_body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start},
        "end": {"dateTime": end},
    }
    if location:
        event_body["location"] = location
    if attendees:
        event_body["attendees"] = [{"email": email} for email in attendees]
    event = service.events().insert(calendarId='primary', body=event_body).execute()
    return {"message": "일정이 등록되었습니다.", "event": event}

if __name__ == "__main__":
    mcp.run() 
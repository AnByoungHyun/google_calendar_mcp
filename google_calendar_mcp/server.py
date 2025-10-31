from mcp.server.fastmcp import FastMCP
from google_calendar_mcp.google_auth import get_calendar_service
from datetime import datetime, timedelta
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

@mcp.tool()
def update_event(
    event_id: str,
    summary: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None
) -> dict[str, Any]:
    """일정 ID로 일정 정보 수정 (전달된 값만 반영)"""
    service = get_calendar_service()
    # 기존 이벤트 조회
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    # 전달된 값만 업데이트
    if summary is not None:
        event['summary'] = summary
    if description is not None:
        event['description'] = description
    if start is not None:
        event['start'] = {'dateTime': start}
    if end is not None:
        event['end'] = {'dateTime': end}
    if location is not None:
        event['location'] = location
    if attendees is not None:
        event['attendees'] = [{'email': email} for email in attendees]
    # patch로 업데이트
    updated_event = service.events().patch(calendarId='primary', eventId=event_id, body=event).execute()
    return {"message": "일정이 수정되었습니다.", "event": updated_event}

@mcp.tool()
def delete_event(event_id: str) -> dict[str, Any]:
    """일정 ID로 일정 삭제"""
    service = get_calendar_service()
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return {"message": "일정이 삭제되었습니다.", "event_id": event_id}
    except Exception as e:
        return {"error": f"일정 삭제 중 오류가 발생했습니다: {str(e)}"}

@mcp.tool()
def find_free_slots(
    date: str,
    duration_minutes: int = 60,
    work_start_hour: int = 9,
    work_end_hour: int = 18
) -> dict[str, Any]:
    """특정 날짜에서 N분 이상의 빈 시간대 찾기
    
    Args:
        date: 날짜 (YYYY-MM-DD 형식)
        duration_minutes: 찾고자 하는 최소 빈 시간 (분 단위, 기본값: 60분)
        work_start_hour: 업무 시작 시간 (0-23, 기본값: 9시)
        work_end_hour: 업무 종료 시간 (0-23, 기본값: 18시)
    
    Returns:
        빈 시간대 목록과 통계 정보
    """
    service = get_calendar_service()
    
    # 해당 날짜의 시작과 끝 시간 설정
    target_date = datetime.strptime(date, "%Y-%m-%d")
    work_start = target_date.replace(hour=work_start_hour, minute=0, second=0)
    work_end = target_date.replace(hour=work_end_hour, minute=0, second=0)
    
    # 해당 날짜의 모든 일정 조회
    time_min = target_date.isoformat() + 'Z'
    time_max = (target_date + timedelta(days=1)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    # 일정들의 시간대 추출 (업무 시간 범위 내만)
    busy_slots = []
    for event in events:
        start = event.get('start', {})
        end = event.get('end', {})
        
        # dateTime이 있으면 시간이 있는 일정, date만 있으면 종일 일정
        if 'dateTime' in start and 'dateTime' in end:
            event_start = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
            event_end = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
            
            # UTC를 로컬 시간으로 변환 (타임존 정보 제거)
            event_start = event_start.replace(tzinfo=None)
            event_end = event_end.replace(tzinfo=None)
            
            # 업무 시간 범위와 겹치는 부분만 추가
            actual_start = max(event_start, work_start)
            actual_end = min(event_end, work_end)
            
            if actual_start < actual_end:
                busy_slots.append({
                    'start': actual_start,
                    'end': actual_end,
                    'summary': event.get('summary', '제목 없음')
                })
        elif 'date' in start:
            # 종일 일정은 전체 업무 시간을 차지하는 것으로 간주
            busy_slots.append({
                'start': work_start,
                'end': work_end,
                'summary': event.get('summary', '제목 없음') + ' (종일)'
            })
    
    # 시작 시간 기준으로 정렬
    busy_slots.sort(key=lambda x: x['start'])
    
    # 빈 시간대 찾기
    free_slots = []
    current_time = work_start
    
    for busy in busy_slots:
        # 현재 시간과 다음 일정 사이에 빈 시간이 있는지 확인
        if current_time < busy['start']:
            gap_minutes = int((busy['start'] - current_time).total_seconds() / 60)
            if gap_minutes >= duration_minutes:
                free_slots.append({
                    'start': current_time.strftime('%H:%M'),
                    'end': busy['start'].strftime('%H:%M'),
                    'duration_minutes': gap_minutes,
                    'start_datetime': current_time.isoformat(),
                    'end_datetime': busy['start'].isoformat()
                })
        
        # 현재 시간을 이번 일정 종료 시간으로 업데이트
        current_time = max(current_time, busy['end'])
    
    # 마지막 일정 후 업무 종료 시간까지의 빈 시간 확인
    if current_time < work_end:
        gap_minutes = int((work_end - current_time).total_seconds() / 60)
        if gap_minutes >= duration_minutes:
            free_slots.append({
                'start': current_time.strftime('%H:%M'),
                'end': work_end.strftime('%H:%M'),
                'duration_minutes': gap_minutes,
                'start_datetime': current_time.isoformat(),
                'end_datetime': work_end.isoformat()
            })
    
    # 통계 정보 계산
    total_work_minutes = (work_end - work_start).total_seconds() / 60
    total_busy_minutes = sum(
        (busy['end'] - max(busy['start'], work_start)).total_seconds() / 60
        for busy in busy_slots
        if busy['end'] > work_start
    )
    total_free_minutes = sum(slot['duration_minutes'] for slot in free_slots)
    
    return {
        "date": date,
        "work_hours": f"{work_start_hour:02d}:00 ~ {work_end_hour:02d}:00",
        "requested_duration": f"{duration_minutes}분 이상",
        "free_slots_count": len(free_slots),
        "free_slots": free_slots,
        "busy_slots_count": len(busy_slots),
        "busy_slots": [
            {
                "start": busy['start'].strftime('%H:%M'),
                "end": busy['end'].strftime('%H:%M'),
                "summary": busy['summary']
            }
            for busy in busy_slots
        ],
        "statistics": {
            "total_work_minutes": int(total_work_minutes),
            "total_busy_minutes": int(total_busy_minutes),
            "total_free_minutes": int(total_free_minutes),
            "busy_percentage": round(total_busy_minutes / total_work_minutes * 100, 1) if total_work_minutes > 0 else 0,
            "free_percentage": round(total_free_minutes / total_work_minutes * 100, 1) if total_work_minutes > 0 else 0
        }
    }


if __name__ == "__main__":
    mcp.run()
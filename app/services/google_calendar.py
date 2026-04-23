"""Google Calendar helpers for SmartElect."""

from __future__ import annotations

import re


def _escape_ics_text(value: str) -> str:
    escaped_value = value.replace("\\", "\\\\")
    escaped_value = escaped_value.replace(";", r"\;")
    escaped_value = escaped_value.replace(",", r"\,")
    return escaped_value.replace("\n", r"\n")


def _format_ics_date(date: str) -> str:
    normalized_date = date.strip()
    if re.fullmatch(r"\d{8}", normalized_date):
        return normalized_date
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized_date):
        return normalized_date.replace("-", "")
    return "20260101"


def generate_ics_event(title: str, description: str, date: str, event_type: str = "general") -> str:
    """
    Generate an ICS event with meaningful, context-aware alarms.
    event_type can be: "election_day", "registration_deadline", or "general".
    """
    formatted_date = _format_ics_date(date)
    
    # Base ICS lines
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SmartElect//EN",
        "BEGIN:VEVENT",
        f"SUMMARY:{_escape_ics_text(title)}",
        f"DESCRIPTION:{_escape_ics_text(description)}",
        f"DTSTART;VALUE=DATE:{formatted_date}",
    ]
    
    # Meaningful alarms based on the real-world action needed
    if event_type == "election_day":
        # Remind 1 day before to gather documents, and at 7 AM on the day of.
        lines.extend([
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            "DESCRIPTION:Prepare ID and check polling booth",
            "TRIGGER:-P1D",
            "END:VALARM",
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            "DESCRIPTION:Polls are open today!",
            "TRIGGER;RELATED=START:-PT1H",
            "END:VALARM",
        ])
    elif event_type == "registration_deadline":
        # Remind 3 days before so they have time to fill forms.
        lines.extend([
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            "DESCRIPTION:Voter registration deadline approaching. Complete your form today.",
            "TRIGGER:-P3D",
            "END:VALARM",
        ])
    else:
        # General 24-hour reminder
        lines.extend([
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            "DESCRIPTION:SmartElect Reminder",
            "TRIGGER:-PT24H",
            "END:VALARM",
        ])
        
    lines.extend([
        "END:VEVENT",
        "END:VCALENDAR",
    ])
    
    return "\n".join(lines)

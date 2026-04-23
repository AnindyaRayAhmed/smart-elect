"""Decision engine for rule-based SmartElect responses."""

from __future__ import annotations

from app.services.civic_data import ELECTION_PROCESS, OFFICIAL_LINKS


def _format_numbered_lines(lines: list[str]) -> str:
    return "\n".join(f"{index}. {line}" for index, line in enumerate(lines, start=1))


def _format_bullets(lines: list[str]) -> str:
    return "\n".join(f"- {line}" for line in lines)


def _learn_process_response(persona: str) -> dict[str, str | float | bool]:
    if persona == "first_time_voter":
        steps = [
            "Verify baseline eligibility.",
            "Submit registration via the central portal.",
            "Confirm active status on the electoral roll.",
            "Identify assigned polling location.",
            "Present authorized identification at the designated booth.",
        ]
        return {
            "title": "Guide: First-Time Voter",
            "content": _format_numbered_lines(steps),
            "next_step": "Validate your registration status immediately.",
            "confidence": 0.95,
            "source": "Election Commission Guidelines",
            "calendar_option": True,
            "event_title": "Check Voter Registration Status",
            "event_description": "Review the official voter portal and confirm your registration details before election day.",
            "event_date": "2026-01-01",
            "event_type": "registration_deadline",
        }

    return {
        "title": "Guide: Electoral Lifecycle",
        "content": _format_numbered_lines(ELECTION_PROCESS),
        "next_step": "Verify registration status prior to election day.",
        "confidence": 0.98,
        "source": "Election Commission Portal",
        "calendar_option": True,
        "event_title": "Election Day Reminder",
        "event_description": "Go through the voting process steps and verify registration and polling details.",
        "event_date": "2026-01-01",
        "event_type": "election_day",
    }


def _timeline_info_response() -> dict[str, str | float | bool]:
    timeline_items = [
        f"Registration constraints: {OFFICIAL_LINKS['NVSP']}",
        f"Official schedules: {OFFICIAL_LINKS['ECI']}",
        f"Polling verification: {OFFICIAL_LINKS['electoral_search']}",
    ]
    return {
        "title": "Official Electoral Timelines",
        "content": _format_bullets(timeline_items),
        "next_step": "Lock registration deadlines into your calendar.",
        "confidence": 1.0,
        "source": "Official Timelines",
        "calendar_option": True,
        "event_title": "Voter Registration Deadline",
        "event_description": "Ensure you have submitted all registration forms before this date.",
        "event_date": "2026-01-01",
        "event_type": "registration_deadline",
    }


def _eligibility_response(context: dict[str, str]) -> dict[str, str | float | bool]:
    location = context.get("location", "the target constituency")
    checklist = [
        "Age >= 18 on the qualifying date.",
        "Verified Indian citizenship.",
        f"Primary residence established in {location}.",
    ]
    return {
        "title": "Eligibility Requirements",
        "content": _format_bullets(checklist),
        "next_step": "If criteria are met, initiate registration.",
        "confidence": 1.0,
        "source": "Voter Eligibility Act",
    }


def _registration_help_response() -> dict[str, str | float | bool]:
    steps = [
        "Access the NVSP portal.",
        "Select form for new registration or modification.",
        "Input personal data.",
        "Upload verified supporting documents.",
        "Submit and retain reference ID.",
    ]
    return {
        "title": "Registration Guide",
        "content": _format_numbered_lines(steps) + f"\n\nPortal: {OFFICIAL_LINKS['NVSP']}",
        "next_step": "Assemble identity documents before initiating process.",
        "confidence": 0.96,
        "source": "NVSP Portal",
    }


def _booth_lookup_response() -> dict[str, str | float | bool]:
    steps = [
        "Access the electoral search database.",
        "Query using EPIC or personal credentials.",
        "Extract assigned polling station location.",
        "Verify 48 hours prior to election day.",
    ]
    return {
        "title": "Polling Station Locator",
        "content": _format_numbered_lines(steps) + f"\n\nDatabase: {OFFICIAL_LINKS['electoral_search']}",
        "next_step": "You can search using your EPIC number.",
        "confidence": 0.99,
        "source": "Electoral Search",
    }


def _candidate_compare_response() -> dict[str, str | float | bool]:
    template = [
        "Candidate Legal Name",
        "Party Affiliation",
        "Constituency",
        "Public Record & Experience",
        "Declared Financials (Assets/Liabilities)",
        "Manifesto Commitments",
        "Legislative Performance Records",
    ]
    return {
        "title": "Candidate Evaluation Guide",
        "content": _format_bullets(template),
        "next_step": "Populate matrix using only official public disclosures.",
        "confidence": 0.92,
        "source": "Neutral Governance Best Practices",
    }


def _election_day_response() -> dict[str, str | float | bool]:
    steps = [
        "Verify polling station assignment.",
        "Procure authorized identification.",
        "Deploy to station within operational hours.",
        "Complete biometric/identity verification.",
        "Cast your vote at your assigned polling booth.",
    ]
    return {
        "title": "Election Day Steps",
        "content": _format_numbered_lines(steps),
        "next_step": "Ensure ID and polling details are secured T-minus 24 hours.",
        "confidence": 0.97,
        "source": "Election Day Guidelines",
        "calendar_option": True,
        "event_title": "Voting Day",
        "event_description": "Bring your ID and go to your designated polling booth to cast your vote.",
        "event_date": "2026-01-01",
        "event_type": "election_day",
    }


def _default_response(intent: str) -> dict[str, str | float | bool]:
    return {
        "title": "Ready to help",
        "content": f"I'm ready to help you. It looks like you're asking about: [{intent}].",
        "next_step": "What specific information do you need? (e.g., 'How do I verify my eligibility?')",
        "confidence": 0.5,
        "source": "SmartElect System",
    }


def generate_decision(intent: str, persona: str, context: dict[str, str]) -> dict[str, str | float | bool]:
    """Return a structured response based on intent, persona, and context."""
    if intent == "learn_process":
        return _learn_process_response(persona)
    if intent == "timeline_info":
        return _timeline_info_response()
    if intent == "eligibility_check":
        return _eligibility_response(context)
    if intent == "registration_help":
        return _registration_help_response()
    if intent == "booth_lookup":
        return _booth_lookup_response()
    if intent == "candidate_compare":
        return _candidate_compare_response()
    if intent == "election_day_preparation":
        return _election_day_response()
    return _default_response(intent)

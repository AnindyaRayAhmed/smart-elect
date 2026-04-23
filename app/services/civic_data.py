"""Minimal civic reference data for SmartElect."""

from __future__ import annotations


ELECTION_PROCESS: list[str] = [
    "Check voter eligibility based on age, citizenship, and ordinary residence.",
    "Register or update voter details through the official voter services portal.",
    "Verify your name in the electoral roll before election day.",
    "Locate your polling station using the official electoral search tools.",
    "Carry an accepted identity document and follow polling instructions on election day.",
]


DOCUMENTS_REQUIRED: list[str] = [
    "Proof of identity",
    "Proof of address",
    "Age proof when applicable",
    "Recent passport-size photograph if requested during registration",
]


OFFICIAL_LINKS: dict[str, str] = {
    "NVSP": "https://voters.eci.gov.in/",
    "ECI": "https://eci.gov.in/",
    "electoral_search": "https://electoralsearch.eci.gov.in/",
}

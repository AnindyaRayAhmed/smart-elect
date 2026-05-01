"""Firestore logging service for SmartElect interactions."""

import threading
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

db = None
try:
    from google.cloud import firestore
    # Initialize using default credentials
    db = firestore.Client()
except ImportError:
    logger.warning("google-cloud-firestore is not installed.")
except Exception as e:
    logger.warning(f"Could not initialize Firestore client: {e}")

def _log_interaction_sync(session_id: str, user_input: str, intent: str, decision_output: str) -> None:
    if db is None:
        return
    try:
        # Save interaction
        interaction_ref = db.collection("interactions").document()
        interaction_ref.set({
            "session_id": session_id,
            "input": user_input,
            "intent": intent,
            "decision_output": decision_output,
            "timestamp": datetime.now(timezone.utc)
        })
        
        # Update session
        session_ref = db.collection("sessions").document(session_id)
        session_ref.set({
            "last_intent": intent,
            "updated_at": datetime.now(timezone.utc)
        }, merge=True)
    except Exception as e:
        logger.error(f"Firestore write failed: {e}")

def log_interaction(session_id: str, user_input: str, intent: str, decision_output: str) -> None:
    """Non-blocking function to log interactions to Firestore."""
    try:
        thread = threading.Thread(
            target=_log_interaction_sync, 
            args=(session_id, user_input, intent, decision_output),
            daemon=True
        )
        thread.start()
    except Exception as e:
        logger.error(f"Failed to start Firestore logging thread: {e}")

import logging
import json
import re
import uuid
import time
import datetime
from typing import Any

# Basic regex for PII masking (email, phone number, SSN patterns)
PII_PATTERNS = [
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),
    (re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'), '[PHONE]'),
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[SSN]')
]

def mask_sensitive_data(text: Any) -> Any:
    if not isinstance(text, str):
        return text
    masked_text = text
    for pattern, replacement in PII_PATTERNS:
        masked_text = pattern.sub(replacement, masked_text)
    return masked_text

class GCLLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "gcl_payload"):
            # Merge payload into the top level for Cloud Logging
            log_record.update(record.gcl_payload)
            
        return json.dumps(log_record)

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("SmartElect-GCL")
    logger.setLevel(logging.INFO)
    
    # Prevent adding handlers multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(GCLLogFormatter())
        logger.addHandler(handler)
        # Stop propagation to avoid duplicate logs in uvicorn
        logger.propagate = False
        
    return logger

logger = setup_logger()

class RequestLogger:
    """Helper to log stages of a request lifecycle."""
    def __init__(self, session_id: str | None = None, request_id: str | None = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.session_id = session_id or self.request_id
        self.start_time = time.time()
        self.payload: dict[str, Any] = {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "timestamp": None,
            "component": None,
            "status": "success",
            "stage": None,
            "latency_ms": 0,
            "input": None,
            "intent": None,
            "entities": None,
            "decision_output": None,
        }

    def update_payload(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            if isinstance(v, str):
                self.payload[k] = mask_sensitive_data(v)
            elif isinstance(v, dict):
                # Basic 1-level masking for dicts like entities
                self.payload[k] = {
                    dk: mask_sensitive_data(dv) for dk, dv in v.items()
                }
            else:
                self.payload[k] = v

    def log_stage(self, stage: str, component: str = "system", status: str = "success", **kwargs: Any) -> None:
        self.update_payload(**kwargs)
        latency_ms = int((time.time() - self.start_time) * 1000)
        
        # Build the final dict to pass into the logger
        gcl_payload = self.payload.copy()
        gcl_payload["stage"] = stage
        gcl_payload["component"] = component
        gcl_payload["status"] = status
        gcl_payload["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        gcl_payload["latency_ms"] = latency_ms
        
        logger.info(f"[{self.request_id}] Stage: {stage}", extra={"gcl_payload": gcl_payload})

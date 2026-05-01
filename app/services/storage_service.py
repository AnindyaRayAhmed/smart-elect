import json
import uuid
import datetime
from google.cloud import storage

def export_voter_guide(decision_output: str) -> str:
    """
    Uploads the decision output to Google Cloud Storage and returns a signed URL.
    Returns an empty string if any error occurs.
    """
    try:
        client = storage.Client()
        bucket_name = "smartelect-user-exports"
        bucket = client.bucket(bucket_name)
        
        file_uuid = str(uuid.uuid4())
        blob_name = f"guide_{file_uuid}.json"
        blob = bucket.blob(blob_name)
        
        data = {
            "voter_guide": decision_output,
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
        }
        
        blob.upload_from_string(
            data=json.dumps(data, indent=2),
            content_type="application/json"
        )
        
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=10),
            method="GET"
        )
        return signed_url
    except Exception:
        # Silently fail if storage export doesn't work (e.g. no auth, no network, bucket not found)
        return ""

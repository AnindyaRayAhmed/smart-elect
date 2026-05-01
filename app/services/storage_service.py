import json
import uuid
import datetime
from google.cloud import storage

def export_voter_guide(decision_output: str) -> str:
    """
    Uploads the decision output to Google Cloud Storage and returns a signed URL.
    Returns a user-facing error message if any error occurs.
    """
    try:
        client = storage.Client()
        bucket = client.bucket("smartelect-user-exports")

        file_uuid = str(uuid.uuid4())
        blob = bucket.blob(f"guide_{file_uuid}.json")

        data = {
            "voter_guide": decision_output,
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
        }

        blob.upload_from_string(
            json.dumps(data, indent=2),
            content_type="application/json"
        )

        url = blob.generate_signed_url(
            version="v4",
            expiration=600,
            method="GET"
        )

        print("GCS_UPLOAD_SUCCESS:", blob.name)
        print("SIGNED_URL:", url)
        return url
    except Exception as e:
        print("GCS_ERROR:", str(e))
        return "File generation failed. Please try again."

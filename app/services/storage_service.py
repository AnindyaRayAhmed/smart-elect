import json
import uuid
import datetime
from google.cloud import storage

def export_voter_guide(decision_output: str) -> str:
    """
    Uploads the decision output to Google Cloud Storage and returns a public URL.
    Returns a user-facing error message if any error occurs.
    """
    try:
        bucket_name = "smartelect-user-exports"
        client = storage.Client()
        bucket = client.bucket(bucket_name)

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

        blob.make_public()

        url = f"https://storage.googleapis.com/{bucket_name}/{blob.name}"

        print("GCS_UPLOAD_SUCCESS:", blob.name)
        print("PUBLIC_URL:", url)
        return url
    except Exception as e:
        print("GCS_ERROR:", str(e))
        return "File generation failed. Please try again."

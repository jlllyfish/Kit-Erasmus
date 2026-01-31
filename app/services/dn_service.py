import requests
import hashlib
import base64
import os

def upload_file_to_dn(dossier_id, file_content, filename, message_body):
    """Upload complet : create + upload + message"""
    
    # Charger les variables d'environnement
    API_URL = os.getenv("DN_API_URL")
    TOKEN = os.getenv("DN_TOKEN")
    INSTRUCTEUR_ID = os.getenv("INSTRUCTEUR_ID")
    
    print(f"  ðŸ”‘ API_URL: {API_URL}")
    print(f"  ðŸ”‘ TOKEN: {'***' if TOKEN else 'None'}")
    print(f"  ðŸ”‘ INSTRUCTEUR_ID: {INSTRUCTEUR_ID}")
    
    if not API_URL or not TOKEN or not INSTRUCTEUR_ID:
        return {"success": False, "error": "Variables d'environnement manquantes"}
    
    # Calculer checksum
    file_size = len(file_content)
    md5_hash = hashlib.md5(file_content).digest()
    checksum = base64.b64encode(md5_hash).decode()
    
    # Ã‰tape 1: createDirectUpload
    mutation_upload = """
    mutation($input: CreateDirectUploadInput!) {
      createDirectUpload(input: $input) {
        directUpload {
          url
          headers
          signedBlobId
        }
      }
    }
    """
    
    variables = {
        "input": {
            "dossierId": dossier_id,
            "filename": filename,
            "byteSize": file_size,
            "checksum": checksum,
            "contentType": "application/pdf"
        }
    }
    
    response = requests.post(
        API_URL,
        json={"query": mutation_upload, "variables": variables},
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    if "errors" in response.json():
        return {"success": False, "error": "createDirectUpload failed"}
    
    upload_data = response.json()["data"]["createDirectUpload"]["directUpload"]
    
    # Ã‰tape 2: Upload fichier
    upload_headers = eval(upload_data["headers"])
    upload_response = requests.put(
        upload_data["url"],
        data=file_content,
        headers=upload_headers
    )
    
    if upload_response.status_code != 201:
        return {"success": False, "error": "Upload failed"}
    
    signed_blob_id = upload_data['signedBlobId']
    
    # Ã‰tape 3: Envoyer message
    mutation_message = """
    mutation($input: DossierEnvoyerMessageInput!) {
      dossierEnvoyerMessage(input: $input) {
        message {
          id
        }
        errors {
          message
        }
      }
    }
    """
    
    variables_message = {
        "input": {
            "dossierId": dossier_id,
            "instructeurId": INSTRUCTEUR_ID,
            "body": message_body,
            "attachment": signed_blob_id
        }
    }
    
    response_message = requests.post(
        API_URL,
        json={"query": mutation_message, "variables": variables_message},
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    if "errors" in response_message.json():
        return {"success": False, "error": "Message failed"}
    
    return {"success": True, "message_id": response_message.json()["data"]["dossierEnvoyerMessage"]["message"]["id"]}
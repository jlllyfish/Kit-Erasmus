import requests
import os
from datetime import datetime

def get_records_to_send():
    """RÃ©cupÃ¨re les PJ Ã  envoyer depuis Grist"""
    base_url = os.getenv("GRIST_BASE_URL")
    doc_id = os.getenv("GRIST_DOC_ID")
    api_key = os.getenv("GRIST_API_KEY")
    table = os.getenv("GRIST_TABLE")
    
    url = f"{base_url}/docs/{doc_id}/tables/{table}/records"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    response = requests.get(url, headers=headers)
    records = response.json()["records"]
    
    to_send = []
    for rec in records:
        fields = rec["fields"]
        kit_non_signe = fields.get("Kit_non_signe")
        
        if (fields.get("Validation_envoi") == True and 
            fields.get("Statut_envoi_DN") in [None, "", "Echec"] and
            kit_non_signe):
            
            if isinstance(kit_non_signe, list) and len(kit_non_signe) > 1:
                attachment_id = kit_non_signe[1]
                
                # RÃ©cupÃ©rer mÃ©tadonnÃ©es de l'attachment
                attachment_url = f"{base_url}/docs/{doc_id}/attachments/{attachment_id}"
                att_response = requests.get(attachment_url, headers=headers)
                
                if att_response.status_code == 200:
                    att_data = att_response.json()
                    filename = att_data.get("fileName", "document.pdf")
                    
                    to_send.append({
                        "id": rec["id"],
                        "dossier_id": fields.get("Ref_dossier_dossier_id"),
                        "pj_url": f"{base_url}/docs/{doc_id}/attachments/{attachment_id}/download",
                        "pj_filename": filename
                    })
    
    return to_send

def update_status(record_id, status, date_envoi=None):
    """Met Ã  jour le statut d'envoi dans Grist"""
    base_url = os.getenv("GRIST_BASE_URL")
    doc_id = os.getenv("GRIST_DOC_ID")
    api_key = os.getenv("GRIST_API_KEY")
    table = os.getenv("GRIST_TABLE")
    
    url = f"{base_url}/docs/{doc_id}/tables/{table}/records"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    data = {
        "records": [{
            "id": record_id,
            "fields": {
                "Statut_envoi_DN": status,
                "Date_envoi_DN": date_envoi or datetime.now().isoformat()
            }
        }]
    }
    
    response = requests.patch(url, json=data, headers=headers)
    return response.status_code == 200
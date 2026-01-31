import os
import requests
from dotenv import load_dotenv
from app.services.grist_service import get_records_to_send, update_status
from app.services.dn_service import upload_file_to_dn

load_dotenv()

def download_file_from_grist(url):
    """Télécharge la PJ depuis Grist"""
    headers = {"Authorization": f"Bearer {os.getenv('GRIST_API_KEY')}"}
    response = requests.get(url, headers=headers)
    return response.content

def main():
    records = get_records_to_send()
    print(f"🔍 {len(records)} PJ à envoyer")
    
    for rec in records:
        print(f"\n📤 Traitement dossier {rec['dossier_id']}")
        
        try:
            # Télécharger la PJ depuis Grist
            file_content = download_file_from_grist(rec['pj_url'])
            
            # Upload vers DN
            result = upload_file_to_dn(
                dossier_id=rec['dossier_id'],
                file_content=file_content,
                filename=rec['pj_filename'],
                message_body="Document transmis automatiquement"
            )
            
            if result["success"]:
                update_status(rec['id'], "Succès")
                print(f"✅ Envoyé avec succès")
            else:
                update_status(rec['id'], "Echec")
                print(f"❌ Echec: {result['error']}")
                
        except Exception as e:
            update_status(rec['id'], "Echec")
            print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    main()
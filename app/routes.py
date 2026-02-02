from flask import Blueprint, render_template, jsonify, request
import requests
import os
from datetime import datetime

bp = Blueprint('main', __name__)

def get_grist_stats():
    """Récupère les statistiques depuis Grist"""
    base_url = os.getenv("GRIST_BASE_URL")
    doc_id = os.getenv("GRIST_DOC_ID")
    api_key = os.getenv("GRIST_API_KEY")
    table = os.getenv("GRIST_TABLE")
    
    url = f"{base_url}/docs/{doc_id}/tables/{table}/records"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        records = response.json()["records"]
        
        total = len(records)
        
        # A générer : Kit_non_signe vide ou False
        a_generer = sum(1 for r in records 
                       if not r["fields"].get("Kit_non_signe"))
        
        # A valider : Validation_envoi = False ET Kit_non_signe non vide
        a_valider = sum(1 for r in records 
                       if r["fields"].get("Validation_envoi") == False
                       and r["fields"].get("Kit_non_signe"))
        
        # A envoyer : Validation_envoi = True ET (Statut vide ou Echec) ET Kit_non_signe non vide
        a_envoyer = sum(1 for r in records 
                       if r["fields"].get("Validation_envoi") == True 
                       and r["fields"].get("Statut_envoi_DN") in [None, "", "Echec"]
                       and r["fields"].get("Kit_non_signe"))
        
        envoyes = sum(1 for r in records if r["fields"].get("Statut_envoi_DN") == "Succès")
        
        return {
            "total": total,
            "a_generer": a_generer,
            "a_valider": a_valider,
            "a_envoyer": a_envoyer,
            "envoyes": envoyes
        }
    except Exception as e:
        return {
            "total": 0,
            "a_generer": 0,
            "a_valider": 0,
            "a_envoyer": 0,
            "envoyes": 0,
            "error": str(e)
        }

@bp.route('/')
def index():
    stats = get_grist_stats()
    return render_template('dashboard.html', stats=stats, active_tab='kite')

@bp.route('/etablissements')
def etablissements():
    """Page de gestion par établissement"""
    # Récupérer la liste des établissements
    etablissements_list = get_etablissements_list()
    
    # Récupérer l'établissement sélectionné (par défaut le premier)
    selected = request.args.get('etab', etablissements_list[0] if etablissements_list else None)
    
    # Récupérer les participants de cet établissement
    participants = get_participants_by_etablissement(selected) if selected else []
    
    return render_template('etablissements.html', 
                         etablissements=etablissements_list,
                         selected_etab=selected,
                         participants=participants,
                         active_tab='etablissements')

@bp.route('/statistiques')
def statistiques():
    """Page de statistiques"""
    # Récupérer la liste des établissements
    etablissements_list = get_etablissements_list()
    
    # Récupérer l'établissement sélectionné (par défaut "Tous")
    selected = request.args.get('etab', 'Tous')
    
    return render_template('stats.html', 
                         etablissements=etablissements_list,
                         selected_etab=selected,
                         active_tab='statistiques')

def get_etablissements_list():
    """Récupère la liste unique des établissements"""
    base_url = os.getenv("GRIST_BASE_URL")
    doc_id = os.getenv("GRIST_DOC_ID")
    api_key = os.getenv("GRIST_API_KEY")
    table = os.getenv("GRIST_TABLE")
    
    url = f"{base_url}/docs/{doc_id}/tables/{table}/records"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        records = response.json()["records"]
        
        # Extraire les établissements uniques
        etablissements = set()
        for r in records:
            etab = r["fields"].get("ref_champs_votre_eplefpa")
            if etab:
                etablissements.add(etab)
        
        return sorted(list(etablissements))
    except Exception as e:
        return []

def get_participants_by_etablissement(etablissement):
    """Récupère les participants d'un établissement donné"""
    base_url = os.getenv("GRIST_BASE_URL")
    doc_id = os.getenv("GRIST_DOC_ID")
    api_key = os.getenv("GRIST_API_KEY")
    table = os.getenv("GRIST_TABLE")
    
    url = f"{base_url}/docs/{doc_id}/tables/{table}/records"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        records = response.json()["records"]
        
        participants = []
        for r in records:
            fields = r["fields"]
            if fields.get("ref_champs_votre_eplefpa") == etablissement:
                # Déterminer le statut du kit
                kit_status = "À valider"
                if fields.get("Validation_envoi") == True:
                    if fields.get("Statut_envoi_DN") == "Succès":
                        kit_status = "Envoyé"
                    else:
                        kit_status = "Validé"
                
                # Prendre uniquement le 1er prénom et enlever les virgules
                prenoms = fields.get("prenom_s_participant", "")
                premier_prenom = prenoms.split()[0] if prenoms else ""
                premier_prenom = premier_prenom.replace(",", "").strip()
                
                # Convertir les timestamps Unix en dates
                date_debut_raw = fields.get("ref_champs_date_debut_activite_hors_jours_de_voyage", "")
                date_fin_raw = fields.get("ref_champs_date_fin_activite_hors_jours_de_voyage", "")
                
                date_debut = ""
                date_fin = ""
                
                if date_debut_raw:
                    try:
                        date_debut = datetime.fromtimestamp(date_debut_raw).strftime("%d/%m/%Y")
                    except:
                        date_debut = str(date_debut_raw)
                
                if date_fin_raw:
                    try:
                        date_fin = datetime.fromtimestamp(date_fin_raw).strftime("%d/%m/%Y")
                    except:
                        date_fin = str(date_fin_raw)
                
                participants.append({
                    "numero_dossier": fields.get("dossier_number", ""),
                    "prenom": premier_prenom,
                    "nom": fields.get("nom_participant", ""),
                    "pays": fields.get("ref_champs_pays_d_accueil", ""),
                    "date_debut": date_debut,
                    "date_fin": date_fin,
                    "kit_status": kit_status
                })
        
        return participants
    except Exception as e:
        return []

@bp.route('/api/stats')
def api_stats():
    """API pour récupérer les stats en temps réel"""
    stats = get_grist_stats()
    return jsonify(stats)

@bp.route('/api/send_conventions', methods=['POST'])
def send_conventions():
    """Lance l'envoi des conventions"""
    from app.services.grist_service import get_records_to_send
    import requests
    import os
    
    try:
        # Vérifier combien il y a à envoyer
        records = get_records_to_send()
        count = len(records)
        
        if count == 0:
            return jsonify({
                "success": True, 
                "message": "Aucune convention à envoyer",
                "count": 0
            })
        
        # Exécuter le script d'upload
        from app.services.upload_service import main as run_upload
        run_upload()
        
        return jsonify({
            "success": True, 
            "message": f"{count} convention(s) traitée(s)",
            "count": count
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/api/chart_data')
def chart_data():
    """API pour récupérer les données des graphiques"""
    etab = request.args.get('etab', 'Tous')
    
    base_url = os.getenv("GRIST_BASE_URL")
    doc_id = os.getenv("GRIST_DOC_ID")
    api_key = os.getenv("GRIST_API_KEY")
    table = os.getenv("GRIST_TABLE")
    
    url = f"{base_url}/docs/{doc_id}/tables/{table}/records"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        records = response.json()["records"]
        
        # Filtrer par établissement si nécessaire
        if etab != 'Tous':
            records = [r for r in records if r["fields"].get("ref_champs_votre_eplefpa") == etab]
        
        # 1. Big Number : Total mobilités
        total = len(records)
        
        # 2. Somme des jours d'activité
        total_jours = sum(r["fields"].get("Nbre_jours_activite", 0) for r in records)
        
        # 3. Récupérer les prévisions
        url_previsions = f"{base_url}/docs/{doc_id}/tables/Previsions/records"
        response_prev = requests.get(url_previsions, headers=headers)
        previsions = response_prev.json()["records"]
        
        # Calculer le total prévu
        if etab != 'Tous':
            # Chercher la prévision pour cet établissement
            prev_etab = [p for p in previsions if p["fields"].get("Etablissement") == etab]
            total_prevu = sum(p["fields"].get("Nombre_jours", 0) for p in prev_etab)
        else:
            # Somme de toutes les prévisions
            total_prevu = sum(p["fields"].get("Nombre_jours", 0) for p in previsions)
        
        # Calculer le %
        pct_consommation = round((total_jours / total_prevu * 100), 1) if total_prevu > 0 else 0
        
        # 4. Donut : Répartition par pays
        pays_count = {}
        for r in records:
            pays = r["fields"].get("ref_champs_pays_d_accueil", "Non défini")
            pays_count[pays] = pays_count.get(pays, 0) + 1
        
        # Top 10 pays + Autres
        sorted_pays = sorted(pays_count.items(), key=lambda x: x[1], reverse=True)
        top_10 = sorted_pays[:10]
        autres = sum([count for _, count in sorted_pays[10:]])
        
        donut_labels = [pays for pays, _ in top_10]
        donut_values = [count for _, count in top_10]
        
        if autres > 0:
            donut_labels.append("Autres")
            donut_values.append(autres)
        
        # 5. Courbe : Mobilités par mois depuis 2026
        monthly_count = {}
        for r in records:
            date_debut = r["fields"].get("ref_champs_date_debut_activite_hors_jours_de_voyage")
            if date_debut:
                try:
                    dt = datetime.fromtimestamp(date_debut)
                    if dt.year >= 2026:
                        month_key = dt.strftime("%Y-%m")
                        monthly_count[month_key] = monthly_count.get(month_key, 0) + 1
                except:
                    pass
        
        # Trier par mois
        sorted_months = sorted(monthly_count.items())
        line_labels = [month for month, _ in sorted_months]
        line_values = [count for _, count in sorted_months]
        
        return jsonify({
            "total": total,
            "total_jours": total_jours,
            "pct_consommation": pct_consommation,
            "donut": {
                "labels": donut_labels,
                "series": donut_values
            },
            "line": {
                "labels": line_labels,
                "series": line_values
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
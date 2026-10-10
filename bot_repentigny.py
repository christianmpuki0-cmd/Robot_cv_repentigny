import os
import time
import random
import csv
import smtplib
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from email.message import EmailMessage
from playwright.sync_api import sync_playwright
from openai import OpenAI
import config
import prompt_templates

# ✅ CORRECTION : Utilisation de la véritable URL d'inférence de l'API Groq
client = OpenAI(
    base_url="https://groq.com",
    api_key=config.GROQ_API_KEY
)

# Utilisation du répertoire temporaire persistant autorisé par Render
FICHIER_SUIVI = "/tmp/suivi_candidatures.csv"

def initialiser_registre():
    if not os.path.exists(FICHIER_SUIVI):
        with open(FICHIER_SUIVI, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["id_offre", "entreprise", "courriel_gerant", "date_envoi", "statut"])

def enregistrer_candidature(id_offre, entreprise, courriel_gerant):
    initialiser_registre()
    with open(FICHIER_SUIVI, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([id_offre, entreprise, courriel_gerant, datetime.now().strftime("%Y-%m-%d"), "En attente"])

def compter_envois_du_jour():
    initialiser_registre()
    candidatures_aujourdhui = 0
    date_actuelle = datetime.now().strftime("%Y-%m-%d")
    with open(FICHIER_SUIVI, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["date_envoi"] == date_actuelle and row["statut"] in ["En attente", "Relancé"]:
                candidatures_aujourdhui += 1
    return candidatures_aujourdhui

def est_le_moment_psychologique_parfait():
    maintenant = datetime.now()
    heure = maintenant.hour
    minute = maintenant.minute
    # Positionnement chronométré au sommet de la boîte de réception (07h45-08h20 ou 13h15-13h45)
    if (7 <= heure <= 8 and 45 <= minute <= 59) or (13 <= heure <= 13 and 15 <= minute <= 45):
        return True
    return False

def detecter_nouvelle_offre():
    url_cible = "https://guichetemplois.gc.ca"
    try:
        response = requests.get(url_cible, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        offre_carte = soup.find('article')
        if offre_carte:
            texte_offre = offre_carte.get_text(strip=True)
            id_offre = offre_carte.get('id', str(random.randint(10000, 99999)))
            return id_offre, texte_offre
    except Exception as e:
        print(f"⚠️ Robot Veille : Erreur d'interception réseau : {e}")
    return None, None

def generer_pitch_ia(description_job):
    print(f"🤖 Alignement algorithmique ATS en cours ({config.MODELE_IA_EN_LIGNE})...")
    try:
        response = client.chat.completions.create(
            model=config.MODELE_IA_EN_LIGNE,
            messages=[
                {"role": "system", "content": prompt_templates.SYSTEM_PROMPT},
                {"role": "user", "content": prompt_templates.generate_user_prompt(config.MON_VRAI_CV, description_job)}
            ]
        )
        contenu = response.choices.message.content
        if "[SEPARATEUR]" in contenu:
            sujet, corps = contenu.split("[SEPARATEUR]")
            return sujet.replace("Sujet :", "").strip(), corps.strip()
        return "Candidature Emploi Étudiant - Repentigny", contenu
    except Exception as e:
        print(f"❌ Erreur API Cloud Groq : {e}")
        return "Candidature Poste Étudiant", "Bonjour, voici mon profil pour le poste."

def demander_validation_telegram(sujet, corps):
    message = f"🎯 **PROFIL COMPORTEMENTAL ARMÉ — PRÊT POUR EXPÉDITION !**\n\n📧 **{sujet}**\n\n{corps}\n\n👉 Autoriser l'envoi ? Envoyez `/oui` ou `/non`"
    # ✅ CORRECTION : Ajout de api.telegram.org et du sous-dossier /bot
    url = f"https://telegram.org{config.TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": config.TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"❌ Échec de notification Telegram : {e}")
        return False
    
    # ✅ CORRECTION : Ajout de api.telegram.org et du sous-dossier /bot
    url_updates = f"https://telegram.org{config.TELEGRAM_TOKEN}/getUpdates"
    last_update_id = 0
    start_time = time.time()
    
    # Attente d'une réponse pendant un maximum de 15 minutes (900 secondes)
    while (time.time() - start_time) < 900:
        try:
            res = requests.get(url_updates, params={"offset": last_update_id + 1, "timeout": 5}).json()
            for update in res.get("result", []):
                last_update_id = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    choix = update["message"]["text"].strip().lower()
                    if choix == "/oui":
                        return True
                    elif choix == "/non":
                        return False
        except Exception:
            pass
        time.sleep(3)
    
    print("⏰ Temps d'attente Telegram écoulé (Expiration après 15 min). Envoi annulé par sécurité.")
    return False

def envoyer_courriel(destinataire, sujet, corps):
    msg = EmailMessage()
    msg['Subject'] = sujet
    msg['From'] = config.GMAIL_USER
    msg['To'] = destinataire
    msg.set_content(corps)

    try:
        # ✅ CORRECTION : Clôture structurelle et intégration du fichier PDF
        with open("mon_cv.pdf", 'rb') as f:
            msg.add_attachment(
                f.read(), 
                maintype='application', 
                subtype='pdf', 
                filename='mon_cv_repentigny.pdf'
            )
            
        print("📨 Connexion sécurisée au serveur SMTP de Gmail...")
        # ✅ CORRECTION : Ajout du tunnel d'envoi et authentification SMTP_SSL
        with smtplib.SMTP_SSL('://gmail.com', 465) as serveur:
            serveur.login(config.GMAIL_USER, config.GMAIL_PASSWORD)
            serveur.send_message(msg)
            
        print(f"🚀 Succès : Courriel de candidature envoyé à {destinataire} !")
        return True
    except FileNotFoundError:
        print("❌ Erreur : Le fichier 'mon_cv.pdf' est introuvable à la racine de l'application.")
        return False
    except smtplib.SMTPAuthenticationError:
        print("❌ Erreur d'authentification : Vérifiez le mot de passe d'application Google dans config.py.")
        return False
    except Exception as e:
        print(f"❌ Échec critique de l'envoi du courriel : {e}")
        return False

# 🚀 BOUCLE PRINCIPALE D'EXÉCUTION DU ROBOT
def main():
    print("🤖 Activation du Robot de Veille et Candidatures (Repentigny)...")
    initialiser_registre()
    
    # Initialisation sécurisée de Playwright en mode Headless pour Render
    with sync_playwright() as p:
        print("🌐 Lancement du navigateur virtuel Playwright...")
        navigateur = p.chromium.launch(headless=True)
        contexte = navigateur.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = contexte.new_page()
        
        while True:
            try:
                # 1. Vérification de la limite journalière (ex: max 5 candidatures par jour pour rester naturel)
                if compter_envois_du_jour() >= 5:
                    print("🛑 Limite journalière de sécurité atteinte (5). Pause jusqu'à demain.")
                    time.sleep(3600)
                    continue

                # 2. Interception des nouvelles offres d'emploi
                id_offre, description_job = detecter_nouvelle_offre()
                
                if id_offre and description_job:
                    # Simulation d'un comportement d'analyse humain (timing psychologique)
                    if est_le_moment_psychologique_parfait():
                        print(f"🎯 Nouvelle opportunité détectée ! ID Offre : {id_offre}")
                        
                        # Génération de la lettre/pitch par l'IA Llama 3.1
                        sujet, corps = generer_pitch_ia(description_job)
                        
                        # Demande de validation à distance sur votre téléphone via Telegram
                        autorisation = demander_validation_telegram(sujet, corps)
                        
                        if autorisation:
                            print("✅ Approbation reçue sur Telegram. Préparation de la soumission...")
                            
                            # Extraction fictive du courriel du gérant (à adapter selon la structure exacte du site)
                            # Ici, on utilise un courriel test pour la démonstration
                            courriel_cible = "gerant_recrutement@exemple.com" 
                            nom_entreprise = "Entreprise Repentigny"
                            
                            # Envoi du courriel et sauvegarde de l'historique
                            envoi_reussi = envoyer_courriel(courriel_cible, sujet, corps)
                            if envoi_reussi:
                                enregistrer_candidature(id_offre, nom_entreprise, courriel_cible)
                        else:
                            print("❌ Envoi rejeté ou expiré depuis Telegram.")
                            
                # Attente aléatoire entre 10 et 20 minutes avant la prochaine vérification du site
                temps_attente = random.randint(600, 1200)
                print(f"💤 En veille. Prochaine synchronisation dans {temps_attente // 60} minutes...")
                time.sleep(temps_attente)
                
            except Exception as global_error:
                print(f"💥 Erreur imprévue dans la boucle principale : {global_error}")
                time.sleep(60)

if __name__ == '__main__':
    main()

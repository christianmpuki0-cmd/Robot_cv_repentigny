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

# Connexion à l'API Cloud Gratuite de Groq (Modèle Llama 3.1 70B d'élite)
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
    url = f"https://telegram.org{config.TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": config.TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except Exception:
        return False
    
    url_updates = f"https://telegram.org{config.TELEGRAM_TOKEN}/getUpdates"
    last_update_id = 0
    while True:
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
        time.sleep(2)

def envoyer_courriel(destinataire, sujet, corps):
    msg = EmailMessage()
    msg['Subject'] = sujet
    msg['From'] = config.GMAIL_USER
    msg['To'] = destinataire
    msg.set_content(corps)

    try:
        with open("mon_cv.pdf", 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="CV_Etudiant.pdf")
    except FileNotFoundError:
        print("⚠️ Alerte Critique : Fichier matériel 'mon_cv.pdf' manquant à la racine du dépôt GitHub.")

    try:
        with smtplib.SMTP_SSL('://gmail.com', 465) as smtp:
            smtp.login(config.GMAIL_USER, config.GMAIL_PASS)
            smtp.send_message(msg)
        print("✉️ Courriel d'élite expédié avec succès.")
    except Exception as e:
        print(f"❌ Blocage du serveur de messagerie : {e}")

def simuler_navigation_humaine(url_offre):
    """Contre les radars comportementaux des plateformes (Indeed, LinkedIn)."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            page = context.new_page()
            page.goto(url_offre)
            # Entropie temporelle asynchrone (Simulation de lecture et mouvements de souris)
            time.sleep(random.uniform(3.5, 7.0))
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(random.uniform(2.0, 5.0))
            browser.close()
    except Exception as e:
        print(f"⚠️ Alerte algorithme anti-bot de navigation : {e}")

def executer_relances_automatiques():
    """Biais de rareté et urgence inversée à J+4 exact sans action de l'employeur."""
    initialiser_registre()
    lignes_mises_a_jour = []
    modifie = False
    
    with open(FICHIER_SUIVI, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_envoi = datetime.strptime(row["date_envoi"], "%Y-%m-%d")
            if row["statut"] == "En attente" and datetime.now() >= date_envoi + timedelta(days=4):
                prompt_relance = f"Rédige un courriel de suivi très courtois, direct et ultra-court (40 mots max) pour le poste chez {row['entreprise']}. Rappelle ma proximité à Repentigny et spécifie poliment que j'ai d'autres opportunités en cours d'évaluation cette semaine."
                try:
                    response = client.chat.completions.create(model=config.MODELE_IA_EN_LIGNE, messages=[{"role": "user", "content": prompt_relance}])
                    envoyer_courriel(row["courriel_gerant"], f"Suivi d'intérêt - Candidature Étudiante - [Votre Nom]", response.choices.message.content)
                    row["statut"] = "Relancé"
                    modifie = True
                except Exception:
                    pass
            lignes_mises_a_jour.append(row)
            
    if modifie:
        with open(FICHIER_SUIVI, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["id_offre", "entreprise", "courriel_gerant", "date_envoi", "statut"])
            writer.writeheader()
            writer.writerows(lignes_mises_a_jour)

def executer_robot():
    deja_postule = set()
    print("🚀 Moteur d'hyper-domination activé sur Render (Docker). Scan actif 24h/24...")
    
    while True:
        if compter_envois_du_jour() >= config.LIMITE_JOURNALIERE:
            print("🛑 Seuil de sécurité journalier atteint pour protéger la boîte et la réputation d'envoi. Pause...")
            time.sleep(1800)
            continue
            
        executer_relances_automatiques()
        id_offre, texte_offre = detecter_nouvelle_offre()
        
        if id_offre and id_offre not in deja_postule:
            sujet, corps = generer_pitch_ia(texte_offre)
            
            # Indexation et ancrage territorial chirurgical (Analyse par zone)
            if "brien" in texte_offre.lower():
                corps = corps.replace("Bonjour,", "Bonjour,\n\nÉtant basé à proximité immédiate du Boulevard Brien, ma flexibilité horaire et ma ponctualité sont optimales.")
            elif "notre-dame" in texte_offre.lower():
                corps = corps.replace("Bonjour,", "Bonjour,\n\nHabitant tout près du secteur de la rue Notre-Dame, je garantis une assiduité et une réactivité complètes pour vos quarts de travail.")
                
            if demander_validation_telegram(sujet, corps):
                # Rétention intelligente jusqu'à la réouverture de la fenêtre psychologique
                while not est_le_moment_psychologique_parfait():
                    print("⏳ Candidature validée sur Telegram. Rétention active jusqu'au pic d'attention humaine (07h45 ou 13h15)...")
                    time.sleep(300)
                
                courriel_cible = "gerant_repentigny@example.com"  # À coupler avec votre méthode de scraping
                envoyer_courriel(courriel_cible, sujet, corps)
                enregistrer_candidature(id_offre, "Commerce Local Repentigny", courriel_cible)
            
            deja_postule.add(id_offre)
            
        time.sleep(60)



if name == "main":
executer_robot()

---


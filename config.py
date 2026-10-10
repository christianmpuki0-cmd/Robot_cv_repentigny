import os

# --- PARAMÈTRES DE SÉCURITÉ ET ACCÈS (À configurer dans les variables d'environnement de Render) ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_APP_PASSWORD")  # Mot de passe d'application Google (16 caractères)

# --- CONFIGURATION DE L'IA D'ÉLITE OPEN-SOURCE EN LIGNE (100% GRATUITE VIA GROQ) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODELE_IA_EN_LIGNE = "llama-3.1-70b-versatile"

# --- COMPTEUR DE BRIDAGE COMPORTEMENTAL (DÉJOUE LES ALERTES ANTI-BOTS) ---
LIMITE_JOURNALIERE = 25  

# --- MATIÈRE PREMIÈRE DU PROFIL (Optimisée au sommet absolu pour le parsing ATS et les gérants) ---
MON_VRAI_CV = """
Nom complet: [Votre Nom]
Téléphone: [Votre Numéro de Téléphone]
Courriel: [Votre Courriel]
Ville: Repentigny, QC
Statut: Étudiant autonome, ponctuel et disponible immédiatement.

DISPONIBILITÉS CRITIQUES (L'atout majeur pour l'embauche étudiante) :
- Soirs de semaine : Disponible dès 16h00 jusqu'à la fermeture complète des commerces.
- Fins de semaine : Flexibilité absolue (Disponibilité pour ouvertures, quarts de jour ou fermetures).
- Congés scolaires, jours fériés et période estivale : Disponible à temps plein.

COMPÈTENCES TRANSFÉRABLES STRUCTURÉES (Sémantique ATS validée) :
- Service à la clientèle : Approche humaine, entregent, communication courtoise et résolution active de problèmes.
- Fiabilité et efficacité : Rapidité d'exécution sous pression, rigueur opérationnelle et solide esprit d'équipe.
- Normes de travail : Respect strict des consignes opérationnelles, de la propreté et des règles de la CNESST.
- Logistique locale : Résident de Repentigny avec mobilité 100 % autonome (Zéro enjeu de transport ou de retard).

EXPÉRIENCES DE VIE ET ENGAGEMENTS (Scolaire / Sportif / Communautaire) :
- [Exemple : Sport compétitif ou bénévolat à Repentigny] -> Développement de l'éthique de travail, ponctualité et constance.
- [Exemple : Projets scolaires complexes de groupe] -> Gestion rigoureuse des priorités, respect d'échéanciers stricts et polyvalence.
"""



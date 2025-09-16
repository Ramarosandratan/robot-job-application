# Robot d'Application Automatisée aux Emplois

Un système intelligent et automatisé pour la recherche d'emploi qui utilise l'IA pour scraper des offres d'emploi, les filtrer selon vos critères, générer des lettres de motivation personnalisées et envoyer des candidatures automatiquement.

## 🚀 Fonctionnalités

### Scraping Intelligent
- **Scraping automatique** des offres d'emploi sur LinkedIn et autres plateformes
- **Extraction précise** des détails de poste : titre, description, compétences, entreprise, localisation
- **Navigation multi-pages** pour une couverture complète des résultats de recherche

### Filtrage et Scoring IA
- **Filtrage personnalisé** basé sur vos critères préférés (poste, salaire, localisation, etc.)
- **Scoring de pertinence** utilisant l'IA pour évaluer la correspondance avec votre profil
- **Détection de doublons** pour éviter les candidatures répétées

### Génération Automatisée d'Applications
- **Lettres de motivation personnalisées** générées par IA selon le poste et votre profil
- **Adaptation automatique** au style et aux exigences de chaque entreprise
- **Génération de CV** optimisés pour chaque candidature

### Gestion Complète des Candidatures
- **Envoi automatique d'emails** avec pièces jointes (CV, lettre de motivation)
- **Suivi des candidatures** avec mise à jour des statuts
- **Système de relance** intelligent pour les candidatures non répondues

### Dashboard et Analytics
- **Interface web Streamlit** pour visualiser vos candidatures
- **Rapports quotidiens** par email avec statistiques détaillées
- **Analyse de marché** pour identifier les tendances d'embauche

### Apprentissage Machine
- **Entraînement de modèles** pour améliorer la précision du matching
- **Analyse prédictive** des chances de succès des candidatures
- **Optimisation continue** basée sur les retours

## 🛠️ Technologies Utilisées

- **Python** - Langage principal
- **Playwright** - Scraping web automatisé
- **OpenAI GPT** - Génération de contenu IA
- **Supabase** - Base de données et authentification
- **Streamlit** - Interface utilisateur web
- **Scikit-learn** - Apprentissage machine
- **PostgreSQL** - Base de données relationnelle

## 📋 Prérequis

- Python 3.8+
- Compte Supabase
- Clé API OpenAI
- Navigateur Chromium (installé automatiquement avec Playwright)

## 🚀 Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/votre-username/robot-job-application.git
cd robot-job-application
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -p requirements.txt
playwright install
```

### 4. Configuration des variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
# Supabase
SUPABASE_URL=votre_supabase_url
SUPABASE_ANON_KEY=votre_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=votre_supabase_service_role_key

# OpenAI
OPENAI_API_KEY=votre_openai_api_key

# Email (optionnel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=votre_email@gmail.com
EMAIL_PASSWORD=votre_mot_de_passe_app

# Rapport quotidien
REPORT_RECIPIENT_EMAIL=votre_email_pour_rapports@exemple.com
```

## 📖 Utilisation

### Configuration initiale
1. **Créer un profil utilisateur** dans Supabase avec vos informations :
   - Résumé professionnel
   - Compétences
   - Liens LinkedIn/GitHub/Portfolio
   - Critères préférés (poste, salaire, localisation)

2. **Configurer les URLs de recherche** pour les plateformes d'emploi

### Lancement du système
```bash
# Exécution complète (scraping + applications)
python orchestrator.py

# Scraping seulement
python scraper.py

# Dashboard
streamlit run dashboard.py

# Entraînement du modèle ML
python ml_matcher_trainer.py
```

### Exemple d'utilisation basique
```python
import asyncio
from orchestrator import run_daily_scraping

# Lancer le scraping quotidien pour un utilisateur
result = asyncio.run(run_daily_scraping(
    user_id=1,
    search_url="https://www.linkedin.com/jobs/search/?keywords=software%20engineer",
    max_pages=5,
    relevance_threshold=50
))
print(result)
```

## 🏗️ Architecture du Projet

```
robot-job-application/
├── orchestrator.py          # Coordination principale du système
├── scraper.py               # Scraping des offres d'emploi
├── filter_jobs.py           # Filtrage des jobs selon critères
├── ai_matcher.py            # Matching IA avancé
├── relevance_scorer.py      # Calcul du score de pertinence
├── application_generator.py # Génération de lettres de motivation
├── application_bot.py       # Automatisation des candidatures
├── email_sender.py          # Envoi d'emails
├── follow_up_manager.py     # Gestion des relances
├── dashboard.py             # Interface web Streamlit
├── database.py              # Connexion et requêtes Supabase
├── market_analyzer.py       # Analyse de marché
├── ml_matcher_trainer.py    # Entraînement modèles ML
├── duplicate_detector.py    # Détection de doublons
├── migrate.py               # Scripts de migration base de données
├── requirements.txt         # Dépendances Python
└── README.md               # Documentation
```

## 🔧 Modules Principaux

### Orchestrator (`orchestrator.py`)
- Coordonne l'ensemble du processus d'application
- Gère le workflow quotidien
- Génère des rapports détaillés

### Scraper (`scraper.py`)
- Utilise Playwright pour naviguer sur les sites d'emploi
- Extrait les données structurées des offres
- Gère la pagination et les erreurs

### AI Matcher (`ai_matcher.py`)
- Utilise des modèles de langage pour le matching
- Compare les profils utilisateurs avec les descriptions de poste
- Améliore continuellement la précision

### Application Generator (`application_generator.py`)
- Génère des lettres de motivation personnalisées
- Adapte le contenu selon l'entreprise et le poste
- Utilise des templates optimisés

## 📊 Dashboard

Lancez le dashboard avec :
```bash
streamlit run dashboard.py
```

Fonctionnalités du dashboard :
- Visualisation des candidatures en cours
- Statistiques de succès
- Gestion des profils utilisateurs
- Configuration des paramètres

## 🔒 Sécurité et Confidentialité

- **Stockage sécurisé** des données sensibles (clés API, mots de passe)
- **Chiffrement** des communications avec Supabase
- **Gestion des permissions** pour l'accès aux données
- **Audit logging** des actions du système

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Guidelines de développement
- Respecter PEP 8 pour le style de code
- Ajouter des tests pour les nouvelles fonctionnalités
- Documenter les fonctions et classes
- Utiliser des commits descriptifs

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🐛 Signaler un Bug

Si vous trouvez un bug, veuillez ouvrir une issue sur GitHub avec :
- Description détaillée du problème
- Étapes pour reproduire
- Environnement (OS, version Python)
- Logs d'erreur si disponibles

## 💡 Fonctionnalités Futures

- [ ] Support multi-plateformes (Indeed, Glassdoor, etc.)
- [ ] Interface mobile
- [ ] Intégration LinkedIn API
- [ ] Analyse prédictive des entretiens
- [ ] Recommandations personnalisées
- [ ] Mode collaboratif pour équipes RH

## 📞 Support

Pour toute question ou support :
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement

---

**Note :** Ce système est conçu pour automatiser le processus de candidature mais respecte les termes de service des plateformes d'emploi. Utilisez-le de manière responsable et éthique.

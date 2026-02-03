The Over-Engineered Guestbook

App utilisateur : http://localhost

Adminer (dev only) : http://localhost:8080

Serveur : db

Base : guestbook

Utilisateur / Mot de passe : ceux de .env

📝 Fonctionnalités

Affichage du nombre de visites via Redis.

Lecture / écriture de messages dans PostgreSQL via l’API Flask.

Interface web simple pour afficher les messages.

Persistance des données grâce aux volumes Docker.

Reverse proxy Nginx pour sécuriser l’accès au backend.

🔒 Sécurité

Aucun mot de passe en clair dans le dépôt.

Redis et PostgreSQL non exposés à l’extérieur.

Nginx est le seul point d’accès externe.

Adminer accessible uniquement en local pour debug.

Volumes pour la persistance des données.

Flask en mode debug désactivé en prod.

⚙️ Structure des fichiers
.
├─ app.py                 # API Flask
├─ Dockerfile             # Build de l’API
├─ docker-compose.yml     # Orchestration de tous les services
├─ nginx.conf             # Configuration du reverse proxy
├─ init.sql               # SQL initial pour la base Postgres
├─ templates/             # HTML du front
├─ static/                # CSS / JS
├─ .env.example           # Variables d’environnement fictives
└─ README.md

Le projet peut être cloné et lancé en une seule commande : docker-compose up -d --build.

La persistance est assurée via un volume Docker nommé.

Multi-stage build pour l’image Flask (taille optimisée).

Isolation réseau : l’utilisateur n’accède qu’à Nginx, Nginx ne parle pas directement à la base.

📌 Bonnes pratiques

Ne pas exposer Adminer en prod.

Toujours utiliser .env pour secrets.

HTTPS recommandé pour déploiement réel.

Vérifier les logs et limiter le trafic si nécessaire.

🔑 Commandes utiles
# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Lister les conteneurs
docker ps

# Se connecter à Postgres
docker exec -it projetgold_book_db_1 psql -U marie -d guestbook

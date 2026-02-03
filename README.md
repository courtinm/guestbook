# 🖊️ The Over-Engineered Guestbook

Un projet de **guestbook** moderne et sécurisé, utilisant Docker, Flask, PostgreSQL, Redis et Nginx.  
Cette application a été créée comme excuse pour manipuler docker. Elle permet de poster des messages et de les visualiser, comme sur un livre d'or.

- Cloner et lancer le projet en une seule commande (après avoir modifier le fichier .env.place_holder en .env avec les variables de votre choix) :
docker-compose up -d

---

## 🌐 Accès

- **App utilisateur** : [http://localhost](http://localhost)  
- **Adminer (dev only)** : [http://localhost:8080](http://localhost:8080)  
- **Serveur de base de données** : `db`  
- **Base de données** : `guestbook`  
- **Utilisateur / Mot de passe** : définis dans le fichier `.env`

---

## 📝 Fonctionnalités

- Affichage du nombre de visites via **Redis**.  
- Lecture et écriture de messages dans **PostgreSQL** via l’**API Flask**.  
- Interface web simple pour afficher les messages.  
- **Persistance** des données grâce aux volumes Docker.  
- **Reverse proxy Nginx** pour sécuriser l’accès au backend.  

---

## 🔒 Sécurité

- Aucun mot de passe en clair dans le dépôt.  
- **Redis** et **PostgreSQL** non exposés à l’extérieur.  
- **Nginx** est le seul point d’accès externe.  
- **Adminer** accessible uniquement en local pour debug.  
- Volumes Docker pour la persistance des données.  
- **Flask** en mode debug désactivé en production.  

---

## ⚙️ Structure des fichiers

.

├─ app.py # API Flask

├─ Dockerfile # Build de l’API

├─ docker-compose.yml # Orchestration de tous les services

├─ nginx.conf # Configuration du reverse proxy

├─ init.sql # SQL initial pour PostgreSQL

├─ templates/ # HTML du front

├─ .env.example # Variables d’environnement fictives à modifier

└─ README.md

---

## 📌 Bonnes pratiques

Ne pas exposer Adminer en production.

Toujours utiliser .env pour gérer les secrets.

HTTPS recommandé pour tout déploiement réel.

Vérifier régulièrement les logs et limiter le trafic si nécessaire.

## 🔑 Commandes utiles
# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Lister les conteneurs
docker ps

# Se connecter à PostgreSQL
docker exec -it projetgold_book_db_1 psql -U marie -d guestbook


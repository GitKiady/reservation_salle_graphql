# Réservation de Salle — API GraphQL

Système de réservation de salles de réunion avec vérification atomique de disponibilité, rappels automatiques par e-mail et API GraphQL optimisée avec DataLoader.

---

## Table des matières

- [Présentation](#présentation)
- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancement](#lancement)
- [API GraphQL](#api-graphql)
  - [Queries](#queries)
  - [Mutations](#mutations)
- [Fonctionnalités clés](#fonctionnalités-clés)
- [Structure du projet](#structure-du-projet)

---

## Présentation

Cette API permet à des utilisateurs authentifiés de **réserver des créneaux horaires sur des salles** avec les garanties suivantes :

- **Pas de double réservation** : vérification atomique via un script Lua exécuté dans Redis.
- **Rappels automatiques** : un e-mail de confirmation est envoyé avant le début de la réservation, suivi d'une annulation automatique si l'utilisateur ne confirme pas.
- **Performance** : les relations N+1 sont évitées grâce à l'intégration de DataLoader dans le contexte GraphQL.
- **Sécurité** : authentification JWT avec séparation des rôles utilisateur / admin.

---

## Architecture

```
Client (GraphQL)
      │
      ▼
FastAPI + Strawberry (GraphQL Router)
      │
      ├── Middleware / Context (JWT → User / Admin)
      │
      ├── GraphQL Layer
      │     ├── Query  (lecture, paginée)
      │     └── Mutation (écriture, vérification Redis)
      │
      ├── CRUD Layer (SQLModel + AsyncSession → PostgreSQL)
      │
      ├── Redis
      │     └── Lua Script (vérification atomique des créneaux)
      │
      └── TaskIQ (broker Redis)
            ├── send_email_confirmation (planifié avant le début)
            └── cancel_reservation (annulation si non confirmé)
```

---

## Stack technique

| Composant         | Technologie                                                      |
|-------------------|------------------------------------------------------------------|
| Framework web     | [FastAPI](https://fastapi.tiangolo.com/)                         |
| API GraphQL       | [Strawberry](https://strawberry.rocks/)                          |
| ORM               | [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy async)    |
| Base de données   | PostgreSQL (via `asyncpg`)                                       |
| Cache / atomicité | Redis (Lua scripting)                                            |
| Tâches planifiées | [TaskIQ](https://taskiq-python.github.io/) + Redis backend       |
| Authentification  | JWT (PyJWT + bcrypt)                                             |
| E-mails           | SMTP                                                             |
| Variables d'env   | `python-dotenv`                                                  |

---

## Prérequis

- Python **3.11+**
- PostgreSQL **14+** (avec un schéma dédié)
- Redis **6+**
- Un compte SMTP (Gmail ou autre) pour l'envoi d'e-mails

---

## Installation

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd API_QL_reservation_salle

# 2. Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
# .venv\Scripts\activate   # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditez le fichier .env avec vos propres valeurs
```

---

## Configuration

Toutes les variables sont chargées depuis un fichier `.env` à la racine du projet (voir [`.env.example`](.env.example)).

| Variable                   | Description                                                      | Exemple                  |
|----------------------------|------------------------------------------------------------------|--------------------------|
| `DATABASE`                 | Dialecte de base de données                                      | `postgresql`             |
| `DATABASE_USERNAME`        | Utilisateur PostgreSQL                                           | `ressalle`               |
| `DATABASE_PASSWORD`        | Mot de passe PostgreSQL                                          | `motdepasse`             |
| `DATABASE_HOST`            | Hôte PostgreSQL                                                  | `localhost`              |
| `DATABASE_PORT`            | Port PostgreSQL                                                  | `5432`                   |
| `DATABASE_NAME`            | Nom de la base de données                                        | `ressalle`               |
| `DATABASE_SCHEMA`          | Schéma PostgreSQL                                                | `ressalle`               |
| `SECRET_KEY`               | Clé secrète pour la signature JWT                                | *(chaîne aléatoire)*     |
| `ALGORITHM`                | Algorithme JWT                                                   | `HS256`                  |
| `TOKEN_EXPIRATION_MINUTES` | Durée de validité du token en minutes                            | `300`                    |
| `REDIS_HOST`               | Hôte Redis                                                       | `localhost`              |
| `REDIS_PORT`               | Port Redis                                                       | `6379`                   |
| `SMTP_SERVER`              | Serveur SMTP                                                     | `smtp.gmail.com`         |
| `SMTP_PORT`                | Port SMTP                                                        | `587`                    |
| `EMAIL_SENDER`             | Adresse e-mail expéditrice                                       | `monapp@gmail.com`       |
| `EMAIL_PASSWORD`           | Mot de passe d'application SMTP                                  | *(mot de passe d'app)*   |
| `MINUTE_CONFIRMATION`      | Minutes avant la réservation pour envoyer l'e-mail               | `30`                     |
| `MINUTE_CANCEL`            | Minutes avant la réservation limite de confirmation              | `15`                     |

> **Gmail** : utilisez un [mot de passe d'application](https://myaccount.google.com/apppasswords), pas votre mot de passe principal.

---

## Lancement

```bash
uvicorn main:app --reload
```

L'API GraphQL est disponible sur `http://localhost:8000/graphql`. Le playground GraphiQL est accessible directement depuis le navigateur.

---

## API GraphQL

L'endpoint unique est : `POST /graphql`

Les opérations protégées nécessitent un header `Authorization` :

```
Authorization: Bearer <votre_token_jwt>
```

### Queries

#### Utilisateurs

| Query         | Rôle requis | Description                            |
|---------------|-------------|----------------------------------------|
| `users`       | Admin       | Liste paginée de tous les utilisateurs |
| `user`        | Admin       | Récupère un utilisateur par son ID     |
| `currentUser` | Utilisateur | Infos de l'utilisateur connecté        |

#### Salles

| Query   | Rôle requis | Description                        |
|---------|-------------|------------------------------------|
| `rooms` | Admin       | Liste paginée de toutes les salles |
| `room`  | Admin       | Récupère une salle par son ID      |

#### Réservations

| Query          | Rôle requis | Description                                          |
|----------------|-------------|------------------------------------------------------|
| `bookings`     | Admin       | Liste paginée de toutes les réservations             |
| `booking`      | Admin       | Récupère une réservation par son ID                  |
| `bookingUser`  | Utilisateur | Récupère une réservation appartenant à l'utilisateur |
| `bookingsUser` | Utilisateur | Liste paginée des réservations de l'utilisateur      |

```graphql
query {
  bookingsUser(page: 1, limit: 10) {
    id
    roomId
    startTime
    endTime
    status
  }
}
```

---

### Mutations

#### Utilisateurs

| Mutation     | Rôle requis | Description                         |
|--------------|-------------|-------------------------------------|
| `createUser` | Public      | Inscription d'un nouvel utilisateur |
| `loginUser`  | Public      | Connexion (retourne un JWT)         |
| `updateUser` | Utilisateur | Mise à jour du profil               |
| `deleteUser` | Admin       | Suppression d'un utilisateur        |

#### Salles

| Mutation     | Rôle requis | Description         |
|--------------|-------------|---------------------|
| `createRoom` | Admin       | Créer une salle     |
| `updateRoom` | Admin       | Modifier une salle  |
| `deleteRoom` | Admin       | Supprimer une salle |

#### Réservations

| Mutation        | Rôle requis | Description                                        |
|-----------------|-------------|----------------------------------------------------|
| `createBooking` | Utilisateur | Créer une réservation (vérification Redis atomique) |
| `updateBooking` | Utilisateur | Modifier une réservation existante                 |
| `deleteBooking` | Utilisateur | Annuler une réservation                            |

```graphql
mutation {
  createBooking(booking: {
    userId: 1,
    roomId: 2,
    startTime: "2026-09-01T09:00:00",
    endTime: "2026-09-01T11:00:00"
  }) {
    id
    status
    startTime
    endTime
  }
}
```

---

## Fonctionnalités clés

### Vérification atomique des créneaux (Redis + Lua)

Pour éviter les conditions de course (*race conditions*) lors de réservations simultanées sur la même salle, la vérification et l'écriture sont effectuées **dans un seul script Lua exécuté atomiquement par Redis**.

Les créneaux réservés sont stockés comme une liste de timestamps (début/fin) sous la clé `bkrm:{room_id}`. Le script détecte tout chevauchement avant d'accepter une nouvelle réservation.

### Rappels automatiques (TaskIQ + Redis)

Lors de chaque création de réservation, deux tâches sont planifiées :

1. **`send_email_confirmation`** — Envoi d'un e-mail de confirmation `MINUTE_CONFIRMATION` minutes avant le début du créneau.
2. **`cancel_reservation`** — Annulation automatique si l'utilisateur ne confirme pas avant la limite (`MINUTE_CANCEL` minutes avant le début).

### DataLoader (N+1 Prevention)

Le contexte GraphQL expose un objet `Loader` qui regroupe les requêtes de relations en un seul appel base de données par requête GraphQL, évitant ainsi le problème N+1.

---

## Structure du projet

```
API_QL_reservation_salle/
│
├── main.py                   # Point d'entrée FastAPI (lifespan, schema, router)
│
├── graphQL/
│   ├── query.py              # Agrégation des queries
│   ├── mutation.py           # Agrégation des mutations
│   ├── loaders/              # DataLoader (optimisation N+1)
│   ├── user/                 # Queries, mutations, types, inputs — Utilisateurs
│   ├── room/                 # Queries, mutations, types, inputs — Salles
│   └── booking/              # Queries, mutations, types, inputs — Réservations
│
├── data/
│   ├── models/               # Modèles SQLModel (User, Room, Booking)
│   ├── crud/                 # Fonctions CRUD asynchrones
│   └── database/             # Connexion et session SQLModel/AsyncPG
│
├── middleware/
│   ├── context.py            # Contexte GraphQL (session, loaders, auth)
│   ├── security/             # Authentification JWT
│   └── sort/                 # Utilitaires de pagination
│
├── utils/
│   ├── cache/                # Client Redis et script Lua de réservation
│   ├── mailing/              # Envoi d'e-mails SMTP
│   ├── planning/             # Configuration TaskIQ (broker, tâches planifiées)
│   └── security/             # Hachage de mots de passe (bcrypt)
│
├── .env.example              # Template des variables d'environnement
├── requirements.txt          # Dépendances Python
└── LICENSE
```

---

## Licence

Ce projet est distribué sous licence [MIT](LICENSE).

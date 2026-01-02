# Assistant Intelligent (RAG + Mistral AI)

Une application d'assistant intelligent contextuel basée sur **RAG (Retrieval-Augmented Generation)**, utilisant **Mistral AI** pour la génération de réponses et **Chroma** pour la recherche dans vos documents.

---

## Table des matières

1. [Présentation](#présentation)
2. [Fonctionnalités](#fonctionnalités)
3. [Architecture](#architecture)
4. [Flux de données RAG](#flux-de-données-rag)
5. [Installation & Lancement](#installation--lancement)
6. [Utilisation](#utilisation)
7. [Endpoints API](#endpoints-api)
8. [Frontend Streamlit](#frontend-streamlit)
9. [Intégration n8n](#intégration-n8n)
10. [Bonnes pratiques](#bonnes-pratiques)
11. [Extensions possibles](#extensions-possibles)


---

## Présentation

L'**Assistant Intelligent** permet de poser des questions à une intelligence artificielle qui répond **en se basant sur vos documents**.

Il combine :

- **Recherche contextuelle** via **Chroma Vector Store**.
- **Génération de texte** via **Mistral AI**.
- **RAG (Retrieval-Augmented Generation)** pour fournir des réponses fiables et contextualisées.

Domaines possibles : médical, juridique, RH, support client, éducation, technique…

---

## Fonctionnalités

- Pose des questions et reçoit des réponses contextuelles.
- Historique des conversations sauvegardé.
- Ingestion de documents PDF/TXT en chunks.
- Recherche intelligente dans la base vectorielle.
- Automatisation via **n8n** pour ingérer des documents automatiquement.

---

## Architecture

```text
                 +----------------+
                 |    Utilisateur |
                 +-------+--------+
                         |
                         v
                 +-------+--------+
                 |   Frontend     | Streamlit
                 +-------+--------+
                         |
               HTTP POST /ask
                         |
                         v
                 +-------+--------+
                 |   Backend      | FastAPI
                 | - RAG Chain    |
                 | - Mistral AI   |
                 | - Chroma DB    |
                 +-------+--------+
                         |
               Recherche & Génération
                         |
                         v
                 +-------+--------+
                 | Base Vectorielle|
                 |   Chroma DB     |
                 +----------------+
```

### Composants principaux

| Composant           | Description |
|--------------------|------------|
| Backend FastAPI     | Fournit les endpoints `/ask`, `/ingest-pdf`, `/health`. |
| Frontend Streamlit  | Interface utilisateur pour poser des questions et visualiser l'historique. |
| Mistral AI (LLM)    | Génère les réponses naturelles à partir du contexte. |
| Chroma Vector Store | Stocke les embeddings pour recherche intelligente. |
| n8n                 | Automatisation des flux et ingestion des documents. |

---

## Flux de données RAG

```text
[Document PDF/TXT] 
       |
       v
+------------------+
| Chunking Text    | <- Découpe les documents en morceaux
+------------------+
       |
       v
+------------------+
| Chroma Vector DB |
+------------------+
       |
       v
[Question utilisateur] --> [Backend FastAPI]
       |
       v
+------------------+
| RAG Chain        | --> Sélection des k documents pertinents
| (Mistral AI)     |
+------------------+
       |
       v
[Réponse générée et renvoyée à Streamlit]
```
---

## Installation & Lancement

### Prérequis

- Docker & Docker Compose
- Python 3.10+ (si exécution locale sans Docker)
- Clé API Mistral AI (`MISTRAL_API_KEY`)

### Lancer avec Docker Compose

```bash
# Cloner le projet
git clone <repo-url>
cd assistant-ia

# Ajouter votre clé API
echo "MISTRAL_API_KEY=votre_cle_api" > .env

# Lancer tous les services
docker-compose up -d
```

**Services disponibles :**

- Backend : http://localhost:8000
- Streamlit : http://localhost:8501
- n8n : http://localhost:5678

---

## Utilisation

1. Déposer vos documents PDF/TXT dans `./data`.
2. Ingestion via n8n ou manuellement via `/ingest-pdf`.
3. Poser vos questions dans Streamlit.
4. Visualiser réponses et historique.

---

## Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Vérifie l'état du backend et le nombre de documents indexés. |
| `/ask` | POST | Pose une question et reçoit une réponse. |
| `/ingest-pdf` | POST | Ajoute des documents en chunks à la base vectorielle. |

---

## Frontend Streamlit

- Affiche les réponses générées par Mistral AI.

---

## Intégration n8n

- Automatisation de l'ingestion des documents.
- Exemple de workflow :
  1. Détecter un nouveau PDF dans `./data`.
  2. Appeler `/ingest-pdf` du backend.
  3. Optionnel : notifier via Slack ou email.

---

## Bonnes pratiques

- Chunker les documents pour améliorer la pertinence.
- Vérifier que `MISTRAL_API_KEY` est configurée.
- Ne pas utiliser la télémétrie Chroma.
- Toujours ingérer les documents avant de poser des questions.

---


## Auteur

⚡ **Chihab** – Software Engineer

---

**⭐ Si ce projet vous a été utile, n'hésitez pas à lui donner une étoile !**

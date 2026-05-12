# Nistula Guest Message Handler

A unified webhook service and database schema for managing multi-channel guest communications. Built with FastAPI and PostgreSQL, and fully containerized for a one-click developer setup.

## Prerequisites

You only need two things installed to run this project:
- **Docker** 
- An **Anthropic API Key** (Claude)

## Setup Guide

1. **Clone this repository** and navigate into the directory.
2. **Set up your environment variables:**
   Copy the example environment file and add your Anthropic API key:
   ```bash
   cp .env.example .env
# Webhook API Setup & Testing Guide

## Prerequisites

Edit `.env` and paste your actual key in `ANTHROPIC_API_KEY`.

## Starting the System

Run the following command to build the API, initialize the PostgreSQL database, and load the schema:

```bash
docker-compose up -d --build
```

The system is now running!

- The Webhook API is live at `http://localhost:8000`
- The PostgreSQL database is running on `localhost:5433` (mapped to 5433 to avoid local conflicts)

---

## Testing the Webhook

You can test the application using the built-in interactive Swagger UI or your terminal.

### Option A: Interactive Dashboard (Recommended)

FastAPI automatically generates a testing dashboard.

1. Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser
2. Expand the `POST /webhook/message` endpoint and click "Try it out"
3. Paste a test payload and click "Execute"

### Option B: cURL Tests

#### Test 1: Standard Pre-Sales Query (Happy Path)

```bash
curl -X POST http://localhost:8000/webhook/message \
-H "Content-Type: application/json" \
-d '{
   "source": "whatsapp",
   "guest_name": "Rahul Sharma",
   "message": "Is the villa available from April 20 to 24? What is the base rate?",
   "timestamp": "2026-05-05T10:30:00Z",
   "booking_ref": "NIS-2024-0891",
   "property_id": "villa-b1"
}'
```

#### Test 2: The Complaint Escalation (Guardrail Check)

```bash
curl -X POST http://localhost:8000/webhook/message \
-H "Content-Type: application/json" \
-d '{
   "source": "airbnb",
   "guest_name": "Sarah Connor",
   "message": "The AC is broken and we are sweating. I want a refund right now.",
   "timestamp": "2026-05-05T14:15:00Z",
   "booking_ref": "NIS-2024-0999",
   "property_id": "villa-b1"
}'
```

---

## Viewing the Database

The Docker Compose file automatically provisions the database and executes `schema.sql` on startup. Data is persisted using a Docker Volume.

### Verify Tables via CLI

```bash
docker exec -it nistula-db psql -U postgres -d nistula_db -c "\dt"
```

### Connect via GUI

If you prefer using a GUI (like DBeaver or TablePlus), use these credentials:

- **Host:** `localhost`
- **Port:** `5433`
- **Database:** `nistula_db`
- **User:** `postgres`
- **Password:** `admin123`

---

## Confidence Scoring & Action Logic

The confidence score (0.0 to 1.0) is a hybrid calculation combining LLM Self-Evaluation and Rule-Based Guardrails.

### LLM Self-Evaluation

Claude evaluates its own drafted reply against the provided "Property Context":

- **High (0.9–1.0):** The query is entirely covered by the context
- **Medium (0.6–0.8):** The query is partially covered or requires minor assumptions
- **Low (<0.6):** The query is out of context (e.g., custom requests)

### Rule-Based Guardrails

The system intercepts the LLM's raw score to enforce safety constraints.

- **Complaint Override:** If the `query_type` is classified as `complaint`, the confidence score is artificially capped at `0.5` regardless of the LLM's certainty, forcing human review

### Action Mapping

- **`auto_send`:** Confidence > 0.85 AND query type is not `complaint`
- **`agent_review`:** Confidence between 0.60 and 0.85 AND query type is not `complaint`
- **`escalate`:** Confidence < 0.60 OR query type is `complaint`

---

## Shutting Down

To stop the application and clean up the containers (while keeping your database data safely stored in the volume), run:

```bash
docker-compose down
```
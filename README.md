# Senin Masalın

Senin Masalın is a local MVP for a Turkish AI-powered personalized bedtime story platform for children.

Current scope: local backend and frontend MVP. Authentication, payments, image generation, PDF generation, audio and video features are intentionally not implemented yet.

## Stack

- Python 3.13
- FastAPI
- SQLModel
- Alembic
- MySQL 5.7
- NVIDIA Llama 3.3 70B through chat completions
- React + Vite + TypeScript
- Axios

## Project structure

```text
senin-masalin/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   ├── research/
│   ├── rules/
│   ├── tests/
│   ├── .env
│   └── requirements.txt
├── frontend/
├── README.md
└── .gitignore
```

## Local backend setup

From the project root:

```bash
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env`:

```env
DATABASE_URL=mysql+pymysql://root@127.0.0.1:3306/senin_masalin
NVIDIA_API_KEY=your_nvidia_api_key
NVIDIA_MODEL=meta/llama-3.3-70b-instruct
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions
```

Create the local MySQL database in DBngin or PyCharm:

```sql
CREATE DATABASE senin_masalin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Open the interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### Health check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### Generate story

```http
POST /api/stories/generate
Content-Type: application/json
```

Request:

```json
{
  "child_name": "Elif",
  "age": 5,
  "animal": "kedi",
  "themes": ["orman", "gokkusagi"],
  "favorite_color": "mor"
}
```

Response:

```json
{
  "title": "...",
  "baslangic": "...",
  "macera": "...",
  "sonuc": "...",
  "moral": "..."
}
```

Validation rules:

- `age` must be between 2 and 12.
- `child_name`, `animal` and `favorite_color` are required and cannot be blank.
- `themes` must contain 1 to 3 controlled theme keys.

## Pedagogical Story Engine

The backend includes a research-backed rule layer that converts the PDFs in `backend/research/` into structured YAML rules under `backend/rules/`.

Rule files:

- `age_rules.yaml`
- `language_rules.yaml`
- `story_rules.yaml`
- `learning_goals.yaml`
- `emotion_rules.yaml`
- `culture_rules.yaml`
- `theme_rules.yaml`
- `forbidden_content.yaml`
- `references.yaml`
- `developmental_outcomes.yaml`

`app/services/pedagogical_story_engine.py` loads these files and selects the target age group from the request age:

- `age_2_3`
- `age_4_5`
- `age_6_8`
- `age_9_12`

`PromptBuilder` injects the selected age group, developmental outcomes and YAML rules into the story prompt before calling NVIDIA Llama 3.3 70B. This keeps pedagogical rules editable outside the application code while preserving the same API response shape.

Theme options are controlled by `backend/rules/theme_rules.yaml`. The frontend displays 20 emoji themes and lets parents select up to 3.

The rule sources are the three PDFs in `backend/research/`:

- Aliye Yılmaz, `Çocuk Eğitiminde Masalın Yeri (Binbir Gece Masalları Örneği)`
- Bernard R. Robin, `The Power of Digital Storytelling to Support Teaching and Learning`
- Bernard R. Robin, `The Educational Uses of Digital Storytelling`

## Alembic

Generate a migration after model changes:

```bash
alembic revision --autogenerate -m "create stories table"
```

Apply migrations:

```bash
alembic upgrade head
```

## Notes

- All prompt construction lives in `PromptBuilder`.
- The story endpoint uses NVIDIA chat completions with Llama 3.3 70B and validates the returned JSON against the response schema.
- The current MVP does not persist generated stories yet; the SQLModel model and Alembic setup are ready for the next milestone.

## Local frontend setup

In a second terminal, from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The Vite dev server proxies `/api` requests to the FastAPI backend at `http://127.0.0.1:8000`, so keep the backend running while using the frontend.

Build the frontend:

```bash
npm run build
```

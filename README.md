# Blog API

A RESTful blog post API built with Flask and SQLite.

## Stack

- **Flask** — web framework
- **Flask-SQLAlchemy** — ORM with SQLite backend
- **python-dotenv** — environment variable loading

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/Coos-Wolff/blog-api.git
cd blog-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install flask flask-sqlalchemy python-dotenv
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set a secure `SECRET_KEY`.

### 5. Run the app

```bash
python run.py
```

The API will be available at `http://localhost:5003`.

## API Endpoints

All endpoints are prefixed with `/post`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/post/` | List all posts (paginated) |
| `GET` | `/post/<id>` | Get a single post by ID |
| `POST` | `/post/add` | Create a new post |
| `PATCH` | `/post/update` | Update fields on an existing post |
| `DELETE` | `/post/<id>` | Delete a post by ID |

### Query parameters — `GET /post/`

| Param | Default | Description |
|-------|---------|-------------|
| `page` | `1` | Page number |
| `per_page` | `5` | Results per page |

### Request body — `POST /post/add`

```json
{
  "title": "My First Post",
  "subtitle": "A brief intro",
  "data": "June 30, 2026",
  "body": "Post content here.",
  "author": "Jane Doe",
  "img_url": "https://example.com/image.jpg"
}
```

### Request body — `PATCH /post/update`

```json
{
  "id": 1,
  "title": "Updated Title",
  "subtitle": "Updated subtitle",
  "body": "Updated content."
}
```

Only `title`, `subtitle`, and `body` are patchable. Include `id` plus any subset of those fields.

## Project Structure

```
.
├── blogapp/
│   ├── __init__.py     # App factory
│   ├── models.py       # BlogPost model
│   ├── repository.py   # Database access layer
│   ├── service.py      # Business logic layer
│   └── routes.py       # Route definitions
├── http/               # HTTP test files (JetBrains / VS Code REST Client)
├── .env.example        # Environment variable template
├── run.py              # Entry point
└── README.md
```
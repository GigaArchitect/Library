# Library API

A RESTful library management API built with Django & Django REST Framework.

## Features

- Custom user model with email-based auth and **Patron** / **Author** roles
- Token authentication via **Django Knox**
- **Book CRUD** with author ownership enforcement
- **Borrow / return** flow with atomic stock management
- **Due-date tracking** and overdue detection via `BorrowRecord`
- **Search** books by title, ISBN, category, and author name
- **Pagination** (20 per page, no count query)
- **Role-based permissions** (Authors create/manage books, Patrons borrow/return)
- **Swagger** docs at `/swagger/`
- **CORS** configured for local frontend development
- **MySQL** development, **SQLite** Docker deployment
- **54 tests** covering models, auth, CRUD, borrow/return, search, and permissions

## Docker Image

Image hosted on Docker Hub at `consumedking/library_api`:

```sh
docker run -p 8080:8080 consumedking/library_api
```

## Local Setup

```sh
git clone <repo-url> library_api
cd library_api
python3 -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

## Models

- **User** — custom model with `PATRON` / `AUTHOR` roles
- **AuthorProfile** / **PatronProfile** — auto-created via signals
- **Book** — ISBN (PK), name, year, authors, categories, stock, borrowed_by
- **Category** — book categorization
- **BorrowRecord** — tracks borrowed_at, due_date, returned_at, overdue status

## Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/signup` | — | — | Create account |
| POST | `/login` | — | — | Login, get Knox token |
| POST | `/logout` | ✓ | — | Invalidate token |
| POST | `/logoutall` | ✓ | — | Invalidate all tokens |
| GET | `/users` | ✓ | Admin | List all users |
| GET | `/user/<id>` | ✓ | — | Get user details |
| PUT | `/user/<id>/update` | ✓ | Owner | Update own profile |
| DELETE | `/user/<id>/delete` | ✓ | Admin | Delete user |
| GET | `/books` | ✓ | — | List books (?search=...) |
| POST | `/books/create` | ✓ | Author | Create book |
| GET | `/books/<isbn>` | ✓ | — | Get single book |
| PUT | `/books/<isbn>/update` | ✓ | Author | Update own book |
| DELETE | `/books/<isbn>/delete` | ✓ | Author | Delete own book |
| POST | `/books/<isbn>/borrow` | ✓ | Patron | Borrow a copy |
| POST | `/books/<isbn>/return` | ✓ | Patron | Return a copy |
| GET | `/categories` | ✓ | — | List categories |
| POST | `/categories/create` | ✓ | Admin | Create category |
| PUT | `/categories/<id>/update` | ✓ | Admin | Update category |
| DELETE | `/categories/<id>/delete` | ✓ | Admin | Delete category |
| GET | `/swagger/` | — | — | Swagger UI docs |

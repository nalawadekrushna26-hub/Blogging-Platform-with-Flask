# 🪶 BlogCraft — Modern Blogging & Publishing Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite%203-003B57.svg?logo=sqlite&logoColor=white)](https://sqlite.org/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-red.svg)](https://www.sqlalchemy.org/)
[![Quill.js](https://img.shields.io/badge/Rich_Editor-Quill.js-orange.svg)](https://quilljs.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A full-stack, industry-standard blogging web application built with Python Flask, SQLite, and modern responsive frontend design. Features secure authentication, Quill.js rich text editing, reader comments with author moderation, multi-field search, topic filtering, and a dedicated author analytics dashboard.

---

## 🌟 Key Features

### 1. 🔐 Secure User Authentication & Profiles
- **User Registration & Login**: Handled via Flask-WTF forms with real-time uniqueness validation and CSRF token protection.
- **Cryptographic Security**: Password hashing using Werkzeug (`scrypt`/`pbkdf2`).
- **Session Management**: Persistent remember-me cookies managed by Flask-Login.
- **User Profiles**: Custom bio, display names, and randomized avatar image uploads.

### 2. ✍️ Blog Post CRUD with Rich Text Editor
- **Quill.js Editor Integration**: Compose articles with rich formatting (H1/H2/H3, bold, italics, blockquotes, code blocks, bullet/numbered lists, links, and inline images).
- **SEO-Friendly Slugs**: Automatic URL slug generation from titles (e.g., `/posts/mastering-flask-in-2026`).
- **Publish & Draft Modes**: Authors can publish immediately or save work-in-progress drafts.
- **Categories & Hashtags**: Primary category selection with comma-separated many-to-many tag relationships (`post_tags`).
- **Cover Image Uploads**: Dedicated featured photo uploader with secure file handling.

### 3. 💬 Discussion & Commenting System
- **Threaded Comment Feed**: Displays reader avatars, formatted timestamps, and an **Author** badge for creator replies.
- **Dual-Authorization Moderation**: Comment authors can delete their own remarks, and article creators can moderate any comment under their posts.

### 4. 🔍 Search & Filtering Engine
- **Multi-Field Search**: Real-time query matching across article titles, summaries, and body content using SQLAlchemy `ilike` and `or_`.
- **Category Filtering**: Horizontal filter chips to explore stories by topic.
- **Tag Filtering**: Dedicated `/tag/<slug>` discovery feed with hashtag pills.

### 5. 📊 Creator Studio Dashboard
- **Analytics Metric Cards**: Real-time tracking of Total Stories, Published count, Drafts, and Reader Comments.
- **Article Management Table**: Direct actions to View, Edit, or permanently Delete articles.

### 6. 🛡️ Production Security & Quality Assurance
- **HTTP Security Headers**: `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`.
- **Session Hardening**: `HttpOnly`, `SameSite=Lax` cookies.
- **Custom Error Pages**: Branded 404, 403, and 500 pages with transaction rollback.
- **Automated Test Suite**: Complete unit and integration test suite (`tests/test_app.py`) running against an isolated in-memory SQLite database.

---

## 🏗️ Project Architecture & Folder Structure

Built using the **Application Factory Pattern** and modular **Flask Blueprints**:

```text
blogging platform/
│
├── app/
│   ├── __init__.py          # Application Factory (create_app) & Security Headers
│   ├── extensions.py        # SQLAlchemy, LoginManager, Migrate instances
│   ├── models.py            # User, Post, Category, Tag, Comment models
│   ├── utils.py             # Secure randomized image uploader
│   ├── errors.py            # Custom HTTP 403, 404, 500 error handlers
│   │
│   ├── auth/                # Authentication Blueprint
│   │   ├── __init__.py
│   │   ├── forms.py         # Registration, Login, and Profile WTForms
│   │   └── routes.py        # Register, Login, Logout, Profile endpoints
│   │
│   ├── posts/               # Blog Post & Discussion Blueprint
│   │   ├── __init__.py
│   │   ├── forms.py         # PostForm & CommentForm
│   │   └── routes.py        # CRUD routes, Quill handler, Comments
│   │
│   ├── main/                # Public & Dashboard Blueprint
│   │   ├── __init__.py
│   │   └── routes.py        # Homepage, Dashboard, Search, Tag routes
│   │
│   ├── templates/           # Jinja2 Modular Templates
│   │   ├── base.html        # Master layout with Navbar & Search
│   │   ├── auth/            # login.html, register.html, profile.html
│   │   ├── posts/           # create_post.html, edit_post.html, post_detail.html, list_posts.html
│   │   ├── main/            # index.html, dashboard.html, search.html
│   │   └── errors/          # 404.html, 403.html, 500.html
│   │
│   └── static/              # Static Assets
│       ├── css/style.css    # Modern Untitled UI design system
│       ├── js/main.js
│       └── images/uploads/  # User-uploaded covers and avatars
│
├── tests/
│   ├── __init__.py
│   └── test_app.py          # Automated Test Suite (unittest)
│
├── instance/
│   └── app.db               # SQLite Database File
│
├── config.py                # Environment configurations (Dev, Test, Prod)
├── run.py                   # Development Server Entry Point
├── wsgi.py                  # Production WSGI Server Entry Point
├── seed.py                  # Database Seeder (Categories & Tags)
├── requirements.txt         # Project Dependencies
├── .env                     # Local Environment Secrets
└── README.md                # Documentation
```

---

## 🚀 Quickstart & Installation (Windows PowerShell)

### Prerequisites
- Python 3.10+
- Git

### 1. Clone or Open Project
```powershell
cd "c:\Users\HP\Downloads\blogging platform"
```

### 2. Activate Virtual Environment
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Seed Categories and Tags
Populate initial categories (*Technology*, *Web Development*, *Python & Flask*, etc.):
```powershell
python seed.py
```

### 5. Start the Development Server
```powershell
python run.py
```
Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 Running the Automated Test Suite

Run the complete test suite against an isolated in-memory SQLite database:

```powershell
python -m unittest tests/test_app.py -v
```

All 8 test suites should pass with `OK`:
- ✅ Password Hashing & Security Verification
- ✅ SEO Slug Generation
- ✅ User Registration & Duplicate Email Defense
- ✅ Login Credentials & Session Establishment
- ✅ Blog Post Creation, Publishing, and Quill Sync
- ✅ Post Updating & Permanent Deletion
- ✅ Reader Commenting & Dual Moderation
- ✅ Multi-Field Search Engine Accuracy
- ✅ Security Headers & 404 Error Handling

---

## 🌐 Production Deployment

### Windows Production (Waitress WSGI)
```powershell
waitress-serve --port=5000 wsgi:app
```

### Linux / Cloud Production (Render, Railway, Heroku, AWS)
```bash
gunicorn wsgi:app
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).

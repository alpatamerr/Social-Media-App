# Simple Social - FastAPI + Streamlit Social Media App

A lightweight social media application built with FastAPI backend and Streamlit frontend, featuring user authentication, media uploads with ImageKit integration, and a real-time feed.

## 🚀 Features

- **User Authentication**: Secure JWT-based authentication with FastAPI-Users
- **Media Uploads**: Support for images and videos with ImageKit CDN integration
- **Social Feed**: Real-time feed displaying posts from all users
- **Image Transformation**: Dynamic image transformations with caption overlays using ImageKit
- **User Management**: Register, login, password reset, and account verification
- **Post Management**: Create and delete your own posts
- **Async Database**: SQLite with async support (aiosqlite)

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **FastAPI-Users**: Ready-to-use authentication and user management
- **SQLAlchemy**: Async ORM with SQLite database
- **Uvicorn**: ASGI server for running FastAPI
- **ImageKit**: Cloud-based image and video storage/transformation service
- **Python-dotenv**: Environment variable management

### Frontend
- **Streamlit**: Fast way to build data apps and web interfaces
- **Requests**: HTTP library for API communication

## 📋 Prerequisites

- Python 3.14+
- ImageKit account (for media storage)
- UV package manager (recommended) or pip

## 🔧 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd fast-api-project
```

2. **Create environment variables**

Copy `.env.example` to `.env` and fill in your actual values:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# ImageKit Configuration
IMAGEKIT_PRIVATE_KEY=your_actual_private_key
IMAGEKIT_PUBLIC_KEY=your_actual_public_key
IMAGEKIT_URL=your_actual_url_endpoint

# Security
SECRET_KEY=your_secure_random_secret_key

# Database
DATABASE_URL=sqlite+aiosqlite:///./test.db

# API
API_URL=http://localhost:8000
```

**Note:** `.env` is gitignored and will never be committed. `.env.example` is committed to show required variables.

3. **Install dependencies**

Using UV:
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

## 🚀 Running the Application

### Start the Backend (FastAPI)

```bash
uv run ./main.py
```

The API will be available at `http://localhost:8000`

### Start the Frontend (Streamlit)

In a separate terminal:
```bash
uv run streamlit run frontend.py
```

The web interface will be available at `http://localhost:8501`

## 📁 Project Structure

```
fast-api-project/
├── app/
│   ├── app.py          # Main FastAPI application and endpoints
│   ├── db.py           # Database models and session management
│   ├── images.py       # ImageKit configuration
│   ├── schemas.py      # Pydantic schemas for validation
│   └── users.py        # User authentication and management
├── frontend.py         # Streamlit frontend application
├── main.py             # FastAPI server entry point
├── pyproject.toml      # Project dependencies and metadata
└── README.md           # This file
```

## 🔑 API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/jwt/login` - Login and get JWT token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token
- `POST /auth/request-verify-token` - Request email verification

### Users
- `GET /users/me` - Get current user information
- `PATCH /users/me` - Update current user

### Posts
- `POST /upload` - Upload a new image/video post with caption
- `GET /feed` - Get all posts in chronological order
- `DELETE /post/{post_id}` - Delete a post (owner only)

## 💾 Database Schema

### User Table
- `id` (UUID): Primary key
- `email` (String): User email (unique)
- `hashed_password` (String): Securely hashed password
- `is_active` (Boolean): Account status
- `is_superuser` (Boolean): Admin privileges
- `is_verified` (Boolean): Email verification status

### Post Table
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User
- `caption` (Text): Post caption
- `url` (String): ImageKit URL
- `file_type` (String): "image" or "video"
- `file_name` (String): Original filename
- `created_at` (DateTime): Timestamp

## 🎨 Frontend Features

### Login/Signup Page
- Simple email/password authentication
- Combined login and registration interface

### Feed Page
- Displays all posts in reverse chronological order
- Shows user email and post date
- Image transformations with caption overlays
- Delete button for own posts
- Uniform media display sizing

### Upload Page
- File upload for images (PNG, JPG, JPEG) and videos (MP4, AVI, MOV, MKV, WEBM)
- Caption input field
- Real-time upload feedback

## 🔒 Security Features

- JWT-based authentication with bearer tokens
- Password hashing with bcrypt
- Environment-based configuration (secrets in `.env`, never committed)
- Session state management in Streamlit
- Protected API endpoints requiring authentication
- Post ownership verification for delete operations
- Separation of `.env` (secrets) and `.env.example` (public reference)

## ⚙️ Configuration

### Environment Variables
All sensitive configuration is managed through environment variables in `.env`:

| Variable | Purpose | Example |
|----------|---------|---------|
| `IMAGEKIT_PRIVATE_KEY` | ImageKit API authentication | Get from ImageKit dashboard |
| `IMAGEKIT_PUBLIC_KEY` | ImageKit public identifier | Get from ImageKit dashboard |
| `IMAGEKIT_URL` | ImageKit URL endpoint | https://ik.imagekit.io/your_id |
| `SECRET_KEY` | JWT secret key | Generate: `openssl rand -hex 32` |
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./test.db` |
| `API_URL` | Backend API URL | `http://localhost:8000` |

### ImageKit Setup
1. Sign up at [ImageKit.io](https://imagekit.io)
2. Go to Settings → Developer Options
3. Copy your Private Key, Public Key, and URL Endpoint
4. Add them to your `.env` file

### Database
The application uses SQLite by default for development. The database file `test.db` will be created automatically on first run.


## 📝 Development

### Auto-reload
Both FastAPI and Streamlit support auto-reload during development:
- FastAPI: `reload=True` is enabled in main.py
- Streamlit: Auto-reloads on file changes by default

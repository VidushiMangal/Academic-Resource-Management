
# Academic Resource Management (ARM) 📚

A FastAPI-based backend system designed for managing academic research records of students and faculty. The system supports secure login, and CRUD operations for users and research publications. It features JWT-based authentication and uses a hybrid data storage model.

---

## 🚀 Features

- 🔐 **Authentication**
  - OAuth2 Password Flow
  - JWT Bearer Token for securing endpoints

- 📄 **CRUD Operations**
  - Manage user profiles (stored in JSON)
  - Manage research publications (stored in PostgreSQL)

- ✅ **Data Validation**
  - Ensured by Pydantic models

- 🧪 **Interactive API Docs**
  - Swagger UI at `/docs`
  - ReDoc UI at `/redoc`

---

## 🛠️ Tech Stack

| Tool             | Purpose                              |
|------------------|--------------------------------------|
| FastAPI          | Backend framework                    |
| Pydantic         | Data validation                      |
| PostgreSQL       | Database for research publications   |
| JSON File        | Lightweight storage for user data    |
| OAuth2 + JWT     | Authentication and authorization     |
| Uvicorn          | ASGI server                          |
| Python venv      | Virtual environment                  |

---

## 📂 Project Structure

```
My_project/
├── main.py              # FastAPI app entry point
├── login.py             # Auth logic (OAuth2 + JWT)
├── user.py              # User data handling (JSON)
├── publishey.py         # Publication handling (PostgreSQL)
├── Database/
│   ├── user.json        # JSON file for user data
│   └── publication.json # (Optional: Legacy/sample data)
├── requirements.txt
├── .env                 # Secrets & config (not committed)
└── README.md
```

---

## ⚙️ Installation & Running the Project

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/academic-resource-management.git
cd academic-resource-management
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL

Ensure PostgreSQL is installed and a database is created for storing publication data. Example connection:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/your_db_name
```

### 5. Run the FastAPI Application

```bash
uvicorn main:app --reload
```

Now visit: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔐 Authentication Guide

This API uses **OAuth2 Password Flow** and **JWT tokens** for authentication.

### Steps:

1. **Login** using your credentials (`/login`)
2. Copy the returned `access_token`
3. Use this token in the `Authorization` header for protected endpoints:

```http
Authorization: Bearer <your-token>
```



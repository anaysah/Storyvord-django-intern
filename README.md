

# Task Management API

This is a Django-based RESTful API for managing tasks, built with Django Rest Framework (DRF) and JWT authentication. It supports CRUD operations, filtering, pagination, and custom permissions, designed as part of a Backend Developer Intern assignment.

## Features
- **User Authentication**: Register and log in with JWT tokens.
- **Task Management**: Create, read, update, and delete tasks.
- **Permissions**: Normal users manage their own tasks; admins can manage all tasks.
- **Filtering**: Filter tasks by status, priority, and date ranges.
- **Pagination**: 10 tasks per page.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/anaysah/Storyvord-django-intern
cd Storyvord-django-intern
```

### 2. Set Up a Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: You can install these manually:
```bash
pip install django djangorestframework djangorestframework-simple-jwt django-filter
```

### 4. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser (Optional)
For admin access:
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/`.

## API Endpoints

### Authentication
- **Register**: `POST /api/register/`
  - Payload: `{"username": "user", "email": "user@example.com", "password": "pass123"}`
  - Response: JWT tokens and user info
- **Login**: `POST /api/token/`
  - Payload: `{"username": "user", "password": "pass123"}`
  - Response: `{"access": "<token>", "refresh": "<token>"}`
- **Refresh Token**: `POST /api/token/refresh/`
  - Payload: `{"refresh": "<refresh-token>"}`

### Tasks
Include the `Authorization: Bearer <access-token>` header for all task endpoints.
- **List Tasks**: `GET /api/tasks/`
  - Normal users see their tasks; admins see all.
  - Filters: `?status=completed`, `?priority=high`, `?created_at__gte=2024-01-01`
- **Create Task**: `POST /api/tasks/`
  - Payload: `{"title": "New Task", "description": "Do something", "status": "pending", "priority": "medium"}`
- **Retrieve Task**: `GET /api/tasks/<id>/`
- **Update Task**: `PUT /api/tasks/<id>/`
  - Payload: `{"title": "Updated Task", "status": "completed"}`
- **Delete Task**: `DELETE /api/tasks/<id>/`

## Running Tests
To run the unit tests:
```bash
python manage.py test tasks
```

## Project Structure
- `task_manager/`: Main project settings and URLs.
- `tasks/`: App containing models, views, serializers, and tests.
- `requirements.txt`: List of dependencies (create with `pip freeze > requirements.txt`).

- Use a tool like Postman for easier API testing.
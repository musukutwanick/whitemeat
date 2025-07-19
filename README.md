# Whitemeat - Django Backend with Frontend Integration

A Django web application that integrates with your existing HTML, CSS, and JavaScript frontend.

## Project Structure

```
whitemeat/
├── whitemeat_backend/      # Django project settings
├── frontend/               # Django app for frontend integration
├── static/                 # Static files (CSS, JS, images)
│   ├── css/               # CSS files
│   └── js/                # JavaScript files
├── templates/             # HTML templates
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Setup Instructions

### 1. Activate Virtual Environment
```bash
# The virtual environment is already created and activated
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Start Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see your application.

## Integrating Your Existing Frontend

### 1. Copy Your Files
- Copy your CSS files to `static/css/`
- Copy your JavaScript files to `static/js/`
- Copy any images to `static/images/` (create this directory if needed)

### 2. Update the Template
- Edit `templates/index.html` to include your existing HTML content
- Use Django's `{% load static %}` and `{% static 'path/to/file' %}` tags to reference your static files

### 3. Create API Endpoints
- Add new views in `frontend/views.py` for your backend functionality
- Add corresponding URLs in `frontend/urls.py`

## Available Endpoints

- `/` - Main frontend page
- `/api/example/` - Example API endpoint
- `/admin/` - Django admin interface

## Development Features

- **CORS Headers**: Configured for frontend-backend communication
- **Static Files**: Automatic serving of CSS, JS, and images
- **Template System**: Django templates with static file integration
- **SQLite Database**: Ready for your data models
- **Debug Mode**: Enabled for development

## Next Steps

1. Replace the sample content in `templates/index.html` with your existing HTML
2. Move your CSS files to `static/css/` and update the template references
3. Move your JavaScript files to `static/js/` and update the template references
4. Create Django models for your data in `frontend/models.py`
5. Add API endpoints in `frontend/views.py` for your frontend to communicate with

## Creating API Endpoints

Example of creating a new API endpoint:

```python
# In frontend/views.py
@csrf_exempt
def your_api_endpoint(request):
    if request.method == 'POST':
        # Handle POST data
        data = json.loads(request.body)
        # Process the data
        return JsonResponse({'status': 'success', 'data': result})
```

```python
# In frontend/urls.py
urlpatterns = [
    path('', views.index, name='index'),
    path('api/your-endpoint/', views.your_api_endpoint, name='your_api'),
]
```

## Database Models

To create database models for your application:

1. Define models in `frontend/models.py`
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`

## Admin Interface

To use Django's admin interface:

1. Create a superuser: `python manage.py createsuperuser`
2. Visit `http://127.0.0.1:8000/admin/`

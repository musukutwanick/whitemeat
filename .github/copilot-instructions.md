<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Whitemeat Project - Django Backend with Frontend Integration

This is a Django web application project that serves a frontend built with HTML, CSS, and JavaScript.

## Project Structure
- `whitemeat_backend/` - Django project configuration
- `frontend/` - Django app for handling frontend views and API endpoints
- `static/` - Static files (CSS, JavaScript, images)
- `templates/` - HTML templates
- `manage.py` - Django management script

## Development Guidelines
- Use Django's template system to serve HTML pages
- Static files (CSS, JS) should be placed in the `static/` directory
- API endpoints should be created in the `frontend/views.py` file
- Use Django's CSRF protection for forms
- CORS is configured for frontend-backend communication

## Key Features
- Django backend with SQLite database
- Static file serving for CSS/JavaScript
- CORS headers enabled for API communication
- Template system for HTML rendering
- RESTful API endpoints

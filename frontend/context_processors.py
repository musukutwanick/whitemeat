"""Template context processors for the frontend app."""
from .models import SiteSettings


def admin_nav(request):
    """Expose the dashboard section list to every admin template so the
    sidebar in admin/base.html renders consistently on all pages, not just
    the generic CRUD ones."""
    if not request.path.startswith("/dashboard/"):
        return {}
    try:
        from .dashboard import _nav_sections
        return {"sections": _nav_sections()}
    except Exception:
        return {"sections": []}


def site_settings(request):
    """Expose the singleton SiteSettings row to every template as `site`.

    Falls back to an unsaved instance (which carries the field defaults) if
    the table isn't ready yet - e.g. during the first migrate - so template
    rendering never crashes.
    """
    try:
        settings_obj = SiteSettings.load()
    except Exception:
        settings_obj = SiteSettings()
    return {"site": settings_obj}

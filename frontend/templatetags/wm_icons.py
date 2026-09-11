"""Inline SVG icon set for the White Meat Company site.

Usage in templates:
    {% load wm_icons %}
    {% wm_icon "masterclass" %}
    {% wm_icon "masterclass" size=40 class="svc-icon" %}

Icons are stroke-based (currentColor), 24x24 viewBox, so they inherit
text colour and match the project's existing hand-drawn SVG style.
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_PATHS = {
    # Equipment / cage
    "equipment": (
        '<rect x="3" y="4" width="18" height="16" rx="1"/>'
        '<path d="M3 9h18M3 14h18M9 4v16M15 4v16"/>'
    ),
    # Outgrower / partnership
    "outgrower": (
        '<path d="M8 13l2 2 4-4"/>'
        '<path d="M20.5 12a8.5 8.5 0 1 1-4.9-7.7"/>'
        '<path d="M16 3l4 1-1 4"/>'
    ),
    # Breeding stock / rabbit
    "breeding": (
        '<path d="M9 12c-2 0-3 1.5-3 4v3h12v-3c0-2.5-1-4-3-4"/>'
        '<path d="M9 12c0-2-1-4-1-6 0-1.5 1-2 2-1s1 3 1 5"/>'
        '<path d="M15 12c0-2 1-4 1-6 0-1.5-1-2-2-1s-1 3-1 5"/>'
        '<circle cx="10" cy="16" r="0.5"/><circle cx="14" cy="16" r="0.5"/>'
    ),
    # Masterclass / graduation cap
    "masterclass": (
        '<path d="M22 10L12 5 2 10l10 5 10-5z"/>'
        '<path d="M6 12v5c0 1 2.7 2.5 6 2.5s6-1.5 6-2.5v-5"/>'
        '<path d="M22 10v6"/>'
    ),
    # Restaurant / cutlery
    "restaurant": (
        '<path d="M4 3v7a2 2 0 0 0 4 0V3M6 10v11"/>'
        '<path d="M17 3c-1.7 0-3 2-3 5s1.3 4 3 4v9"/>'
    ),
    # Butchery / cleaver
    "butchery": (
        '<path d="M3 21L14 10"/>'
        '<path d="M13 3h7v7a1 1 0 0 1-1 1h-4a2 2 0 0 1-2-2V3z"/>'
    ),
    # Shop / bag
    "shop": (
        '<path d="M6 8h12l1 12H5L6 8z"/>'
        '<path d="M9 8V6a3 3 0 0 1 6 0v2"/>'
    ),
    # Leaf / health
    "leaf": (
        '<path d="M11 20A7 7 0 0 1 4 13c0-6 8-9 16-9 0 8-3 16-9 16z"/>'
        '<path d="M4 20c4-4 8-6 12-7"/>'
    ),
    # Utility icons
    "phone": (
        '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6'
        'A19.8 19.8 0 0 1 2 4.2 2 2 0 0 1 4 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0'
        '1-.5 2.1L7.1 9.9a16 16 0 0 0 6 6l1.4-1.1a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.7.7A2 2 0'
        '0 1 22 16.9z"/>'
    ),
    "mail": (
        '<rect x="2" y="4" width="20" height="16" rx="2"/>'
        '<path d="M22 7l-10 6L2 7"/>'
    ),
    "pin": (
        '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>'
        '<circle cx="12" cy="10" r="3"/>'
    ),
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "whatsapp": (
        '<path d="M21 11.5a8.4 8.4 0 0 1-12.5 7.3L3 20l1.3-5.4A8.5 8.5 0 1 1 21 11.5z"/>'
        '<path d="M8.5 9c0 3 2.5 5.5 5.5 5.5.5 0 1-.5 1-1l-1.5-1-1 .8A4 4 0 0 1 9.7 10l.8-1L9.5 7.5c-.5 0-1 .5-1 1z"/>'
    ),
    "arrow-right": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "chevron-down": '<path d="M6 9l6 6 6-6"/>',
}


@register.simple_tag
def wm_icon(name, size=24, **attrs):
    paths = _PATHS.get(name, _PATHS["leaf"])
    css_class = attrs.get("class", "wm-icon")
    return mark_safe(
        f'<svg class="{css_class}" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true" focusable="false">{paths}</svg>'
    )

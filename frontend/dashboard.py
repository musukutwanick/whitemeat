"""Generic content-management CRUD for the staff dashboard.

One registry (SECTIONS) + three views (list / edit / delete) drive the
management pages for every image-bearing content type on the site, so
adding a new managed model is a one-line registry entry rather than a
fresh set of views and templates.

Menus (branch-scoped) and the Masterclass schedule editor keep their own
bespoke views - they don't fit the flat one-model-per-page shape.
"""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    CageForm, ShedForm, AccessoryForm, BreedForm, ButcheryProductForm, HeroSlideForm,
    MasterclassDateForm,
)
from .models import Cage, Shed, Accessory, Breed, ButcheryProduct, HeroSlide, MasterclassDate


SECTIONS = {
    "cages": {
        "model": Cage, "form": CageForm,
        "label": "Cages", "singular": "cage", "icon": "fa-warehouse",
        "columns": [("name", "Name"), ("get_category_display", "Type"),
                    ("price", "Price"), ("order", "Order")],
        "image_attr": "image_url", "flag": "is_available", "flag_label": "Available",
    },
    "sheds": {
        "model": Shed, "form": ShedForm,
        "label": "Sheds", "singular": "shed", "icon": "fa-house-chimney",
        "columns": [("name", "Name"), ("get_category_display", "Type"),
                    ("price", "Price"), ("order", "Order")],
        "image_attr": "image_url", "flag": "is_available", "flag_label": "Available",
    },
    "accessories": {
        "model": Accessory, "form": AccessoryForm,
        "label": "Accessories", "singular": "accessory", "icon": "fa-screwdriver-wrench",
        "columns": [("name", "Name"), ("price", "Price")],
        "image_attr": "image_url", "flag": "is_available", "flag_label": "Available",
    },
    "breeding": {
        "model": Breed, "form": BreedForm,
        "label": "Breeding Stock", "singular": "breed", "icon": "fa-paw",
        "columns": [("name", "Name"), ("price", "Price"), ("order", "Order")],
        "image_attr": "image_url", "flag": "is_available", "flag_label": "Available",
    },
    "butchery": {
        "model": ButcheryProduct, "form": ButcheryProductForm,
        "label": "Butchery", "singular": "product", "icon": "fa-drumstick-bite",
        "columns": [("name", "Name"), ("get_category_display", "Category"),
                    ("price", "Price"), ("unit", "Unit")],
        "image_attr": "image_url", "flag": "is_available", "flag_label": "Available",
    },
    "hero-slides": {
        "model": HeroSlide, "form": HeroSlideForm,
        "label": "Hero Slides", "singular": "slide", "icon": "fa-images",
        "columns": [("get_page_display", "Page"), ("heading", "Heading"),
                    ("order", "Order")],
        "image_attr": "image_url", "flag": "is_active", "flag_label": "Active",
    },
    "masterclass-dates": {
        "model": MasterclassDate, "form": MasterclassDateForm,
        "label": "Masterclass Dates", "singular": "date", "icon": "fa-calendar-day",
        "columns": [("date", "Date"), ("capacity", "Capacity"),
                    ("booked_count", "Booked"), ("location", "Location")],
        "image_attr": None, "flag": "is_active", "flag_label": "Active",
    },
}

# Order the nav/landing tiles are shown in.
SECTION_ORDER = ["cages", "sheds", "accessories", "breeding", "butchery",
                 "hero-slides", "masterclass-dates"]


def get_section(slug):
    cfg = SECTIONS.get(slug)
    if not cfg:
        from django.http import Http404
        raise Http404(f"Unknown content section: {slug}")
    return cfg


def _resolve(obj, attr):
    """Read attr off obj, calling it if it's a method (e.g. get_x_display)."""
    value = getattr(obj, attr, "")
    return value() if callable(value) else value


@staff_member_required
def content_list(request, section):
    cfg = get_section(section)
    objects = cfg["model"].objects.all()
    rows = []
    for obj in objects:
        rows.append({
            "obj": obj,
            "pk": obj.pk,
            "image": _resolve(obj, cfg["image_attr"]) if cfg["image_attr"] else None,
            "cells": [_resolve(obj, attr) for attr, _ in cfg["columns"]],
            "flag": getattr(obj, cfg["flag"]) if cfg["flag"] else None,
        })
    return render(request, "admin/content_list.html", {
        "section": section, "cfg": cfg, "rows": rows,
        "headers": [label for _, label in cfg["columns"]],
        "sections": _nav_sections(),
    })


@staff_member_required
def content_edit(request, section, pk=None):
    cfg = get_section(section)
    instance = get_object_or_404(cfg["model"], pk=pk) if pk else None
    if request.method == "POST":
        form = cfg["form"](request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save()
            messages.success(
                request,
                f'{cfg["singular"].capitalize()} "{obj}" '
                f'{"updated" if pk else "added"} successfully.'
            )
            return redirect("content_list", section=section)
        messages.error(request, "Please fix the errors below.")
    else:
        form = cfg["form"](instance=instance)
    return render(request, "admin/content_form.html", {
        "section": section, "cfg": cfg, "form": form, "instance": instance,
        "image": _resolve(instance, cfg["image_attr"]) if (instance and cfg["image_attr"]) else None,
        "sections": _nav_sections(),
    })


@staff_member_required
@require_POST
def content_delete(request, section, pk):
    cfg = get_section(section)
    obj = get_object_or_404(cfg["model"], pk=pk)
    label = str(obj)
    obj.delete()
    messages.success(request, f'"{label}" deleted.')
    return redirect("content_list", section=section)


def _nav_sections():
    """[(slug, label, icon), ...] for the sidebar - shared by every page."""
    return [(slug, SECTIONS[slug]["label"], SECTIONS[slug]["icon"])
            for slug in SECTION_ORDER]


def dashboard_counts():
    """{slug: count} for the landing tiles."""
    return {slug: SECTIONS[slug]["model"].objects.count() for slug in SECTION_ORDER}

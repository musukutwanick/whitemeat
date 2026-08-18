from django.contrib import admin
from .models import MasterclassEvent, MasterclassSession

class MasterclassSessionInline(admin.TabularInline):
    model = MasterclassSession
    extra = 1
    fields = ("day", "time", "title", "description")
    show_change_link = True
    verbose_name = "Session"
    verbose_name_plural = "Sessions"
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "day":
            formfield.label = "Day (1 = First day, 2 = Second day)"
        if db_field.name == "time":
            formfield.widget.attrs["placeholder"] = "e.g. 8:00 AM"
        if db_field.name == "title":
            formfield.widget.attrs["placeholder"] = "Session title (e.g. Registration & Welcome)"
        if db_field.name == "description":
            formfield.widget.attrs["placeholder"] = "Short description of the session"
        return formfield

@admin.register(MasterclassEvent)
class MasterclassEventAdmin(admin.ModelAdmin):
    list_display = ("title", "date_range")
    search_fields = ("title", "date_range")
    inlines = [MasterclassSessionInline]

@admin.register(MasterclassSession)
class MasterclassSessionAdmin(admin.ModelAdmin):
    list_display = ("event", "day", "time", "title")
    list_filter = ("event", "day")
    search_fields = ("title", "description")

from .models import (
    MenuCategory, MenuItem, RestaurantBranch, HowDidYouHearAboutUs, 
    Accessory, RestaurantLocation, Reservation, ContactMessage, 
    NewsletterSubscriber, Notice
)

@admin.register(RestaurantBranch)
class RestaurantBranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'address', 'phone', 'email']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_available', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['is_available', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'price', 'image', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    class Media:
        css = {
            'all': ('css/admin-accessory.css',)
        }

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    list_editable = ['order']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'category', 'price', 'is_available', 'is_featured', 'created_at']
    list_filter = ['branch', 'category', 'is_available', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'ingredients', 'allergens']
    list_editable = ['price', 'is_available', 'is_featured']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(RestaurantLocation)
class RestaurantLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'is_open']
    list_filter = ['is_open']
    search_fields = ['name', 'address', 'description']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['confirmation_number', 'name', 'phone', 'date', 'time', 'guests', 'location', 'status', 'created_at']
    list_filter = ['status', 'location', 'date']
    search_fields = ['confirmation_number', 'name', 'email', 'phone', 'special_requests']
    readonly_fields = ['confirmation_number', 'created_at']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'notice_type', 'is_active', 'is_featured', 'created_by', 'created_at', 'expires_at']
    list_filter = ['notice_type', 'is_active', 'is_featured']
    search_fields = ['title', 'content']

@admin.register(HowDidYouHearAboutUs)
class HowDidYouHearAboutUsAdmin(admin.ModelAdmin):
    list_display = ['choice', 'other_text', 'submitted_at']
    list_filter = ['choice', 'submitted_at']
    search_fields = ['other_text']
    readonly_fields = ['choice', 'other_text', 'submitted_at']

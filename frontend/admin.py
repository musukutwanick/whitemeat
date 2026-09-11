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
    list_display = ("title", "date_range", "price", "door_fee")
    search_fields = ("title", "date_range")
    inlines = [MasterclassSessionInline]

@admin.register(MasterclassSession)
class MasterclassSessionAdmin(admin.ModelAdmin):
    list_display = ("event", "day", "time", "title")
    list_filter = ("event", "day")
    search_fields = ("title", "description")


from .models import MasterclassDate, MasterclassBooking


@admin.register(MasterclassDate)
class MasterclassDateAdmin(admin.ModelAdmin):
    list_display = ("date", "capacity", "booked_count", "spaces_left", "is_active", "is_past")
    list_editable = ("capacity", "is_active")
    list_filter = ("is_active",)
    date_hierarchy = "date"
    ordering = ("date",)
    search_fields = ("location", "notes")

    @admin.display(boolean=True)
    def is_past(self, obj):
        return obj.is_past


@admin.register(MasterclassBooking)
class MasterclassBookingAdmin(admin.ModelAdmin):
    list_display = ("name", "masterclass_date", "attendees", "status", "has_proof", "created_at")
    list_filter = ("status", "masterclass_date")
    list_editable = ("status",)
    search_fields = ("name", "email", "phone")
    readonly_fields = ("created_at", "updated_at", "proof_preview")
    fieldsets = (
        (None, {"fields": ("masterclass_date", "name", "email", "phone", "attendees", "notes")}),
        ("Payment", {"fields": ("payment_proof", "proof_preview", "status", "admin_notes")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(boolean=True, description="Proof")
    def has_proof(self, obj):
        return bool(obj.payment_proof)

    @admin.display(description="Proof preview")
    def proof_preview(self, obj):
        if not obj.payment_proof:
            return "No file uploaded."
        from django.utils.html import format_html
        url = obj.payment_proof.url
        if url.lower().endswith((".pdf",)):
            return format_html('<a href="{}" target="_blank" rel="noopener">View PDF proof</a>', url)
        return format_html(
            '<a href="{}" target="_blank" rel="noopener"><img src="{}" style="max-height:220px;border:1px solid #ddd;"></a>',
            url, url,
        )

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


# ---------------------------------------------------------------------------
#  Site-wide content (Phase 1)
# ---------------------------------------------------------------------------
from django.utils.html import format_html
from .models import SiteSettings, HeroSlide, HomeServiceCard


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Brand", {"fields": ("company_name", "tagline", "brand_slogan")}),
        ("Contact", {"fields": (
            "whatsapp_number", "phone_primary", "phone_secondary", "email",
            "office_address", "restaurant_address", "business_hours",
            "map_embed_url",
        )}),
        ("Social links", {"fields": (
            "facebook_url", "instagram_url", "twitter_url", "youtube_url",
            "tiktok_url", "whatsapp_channel_url",
        )}),
        ("Payment (shown at checkout)", {"fields": (
            "payment_instructions", "payment_ecocash_number", "payment_ecocash_name",
            "payment_bank_details",
        )}),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        # Singleton: only ever one row.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("order", "thumb", "page", "heading", "is_active")
    list_display_links = ("heading",)
    list_editable = ("order", "is_active")
    list_filter = ("page", "is_active")
    search_fields = ("heading", "subheading")
    fieldsets = (
        (None, {"fields": ("page", "heading", "subheading", "is_active", "order")}),
        ("Image", {"fields": (
            "background_image", "background_image_filename", "image_alt", "overlay",
        )}),
        ("Video (optional - plays instead of the image above)", {"fields": (
            "background_video", "background_video_filename",
        )}),
        ("Call to action", {"fields": (
            "cta_primary_label", "cta_primary_url",
            "cta_secondary_label", "cta_secondary_url",
        )}),
    )

    @admin.display(description="Preview")
    def thumb(self, obj):
        try:
            return format_html(
                '<img src="{}" style="height:44px;width:78px;object-fit:cover;'
                'border-radius:4px;">', obj.image_url,
            )
        except Exception:
            return "-"


@admin.register(HomeServiceCard)
class HomeServiceCardAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "icon", "url", "is_active")
    list_display_links = ("title",)
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "icon")


from .models import Breed


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ("order", "thumb", "name", "price", "is_available", "is_featured")
    list_display_links = ("name",)
    list_editable = ("order", "price", "is_available", "is_featured")
    list_filter = ("is_available", "is_featured")
    search_fields = ("name", "description", "characteristics")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "slug", "tagline", "is_available", "is_featured", "order")}),
        ("Content", {"fields": ("description", "characteristics")}),
        ("Pricing & stock", {"fields": ("price", "stock_quantity")}),
        ("Image", {"fields": ("image", "image_filename", "image_alt")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Preview")
    def thumb(self, obj):
        try:
            return format_html(
                '<img src="{}" style="height:44px;width:60px;object-fit:cover;">', obj.image_url,
            )
        except Exception:
            return "-"


from .models import ButcheryProduct, Cage, Shed


class _ProductImageAdmin(admin.ModelAdmin):
    """Shared admin config for Cage / Shed (identical shape)."""
    list_display = ("order", "thumb", "name", "category", "price", "is_available", "is_featured")
    list_display_links = ("name",)
    list_editable = ("order", "price", "is_available", "is_featured")
    list_filter = ("category", "is_available", "is_featured")
    search_fields = ("name", "description", "features")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "slug", "category", "is_available", "is_featured", "order")}),
        ("Content", {"fields": ("description", "features", "price", "capacity")}),
        ("Image", {"fields": ("image", "image_filename", "image_alt")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Preview")
    def thumb(self, obj):
        try:
            return format_html('<img src="{}" style="height:44px;width:60px;object-fit:cover">', obj.image_url)
        except Exception:
            return "-"


@admin.register(Cage)
class CageAdmin(_ProductImageAdmin):
    pass


@admin.register(Shed)
class ShedAdmin(_ProductImageAdmin):
    pass


@admin.register(ButcheryProduct)
class ButcheryProductAdmin(admin.ModelAdmin):
    list_display = ("order", "thumb", "name", "category", "price", "unit", "is_available", "is_featured")
    list_display_links = ("name",)
    list_editable = ("order", "price", "is_available", "is_featured")
    list_filter = ("category", "is_available", "is_featured")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "category", "is_available", "is_featured", "order")}),
        ("Content", {"fields": ("description", "price", "unit", "stock_note")}),
        ("Image", {"fields": ("image", "image_filename", "image_alt")}),
    )

    @admin.display(description="Preview")
    def thumb(self, obj):
        from django.utils.html import format_html
        try:
            return format_html('<img src="{}" style="height:44px;width:60px;object-fit:cover">', obj.image_url)
        except Exception:
            return "-"


from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("created_at", "source", "customer_name", "customer_phone", "total", "payment_method", "status", "has_proof")
    list_filter = ("source", "payment_method", "status")
    list_editable = ("status",)
    search_fields = ("customer_name", "customer_phone", "items_summary", "notes")
    readonly_fields = ("created_at", "proof_preview")
    fieldsets = (
        (None, {"fields": ("source", "status", "created_at")}),
        ("Customer", {"fields": ("customer_name", "customer_phone", "notes")}),
        ("Order", {"fields": ("items_summary", "total")}),
        ("Payment", {"fields": ("payment_method", "proof_of_payment", "proof_preview")}),
    )

    @admin.display(boolean=True, description="Proof")
    def has_proof(self, obj):
        return bool(obj.proof_of_payment)

    @admin.display(description="Proof preview")
    def proof_preview(self, obj):
        if not obj.proof_of_payment:
            return "No file uploaded (cash order)."
        url = obj.proof_of_payment.url
        if url.lower().endswith(".pdf"):
            return format_html('<a href="{}" target="_blank" rel="noopener">View PDF proof</a>', url)
        return format_html(
            '<a href="{}" target="_blank" rel="noopener"><img src="{}" style="max-height:220px;border:1px solid #ddd;"></a>',
            url, url,
        )

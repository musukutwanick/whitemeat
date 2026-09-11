from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from datetime import datetime
from whitemeat_backend.supabase_storage import get_menu_storage, get_equipment_storage, get_masterclass_storage, get_order_storage

# Accessory model for cages/equipment accessories
class Accessory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='equipment/', storage=get_equipment_storage, blank=True, null=True, help_text="Upload accessory image")
    # Keep alongside `image` for backward compatibility: a code-managed
    # static image (bypasses admin upload / Supabase entirely). Mirrors
    # MenuItem.image_filename.
    image_filename = models.CharField(max_length=200, blank=True, help_text="Alternative: Image filename in static/images/")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', 'name']

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        elif self.image_filename:
            return f'/static/images/{self.image_filename}'
        return '/static/images/default-accessory.jpg'

class MasterclassEvent(models.Model):
    title = models.CharField(max_length=200, default="Upcoming Masterclass")
    date_range = models.CharField(max_length=100, help_text="e.g. August 2nd & 3rd, 2025")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=140,
                                 help_text="Standard course fee, per attendee.")
    certification_fee = models.DecimalField(max_digits=8, decimal_places=2, default=20, blank=True, null=True,
                                              help_text="Optional add-on certification fee. Leave blank to hide.")
    door_fee = models.DecimalField(max_digits=8, decimal_places=2, default=10,
                                    help_text="Extra late-registration fee for booking on the day, at the door.")

    def __str__(self):
        return self.title

class MasterclassSession(models.Model):
    event = models.ForeignKey(MasterclassEvent, on_delete=models.CASCADE, related_name='sessions')
    day = models.PositiveSmallIntegerField(choices=[(1, 'Day 1'), (2, 'Day 2')])
    time = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['day', 'time']

    def __str__(self):
        return f"Day {self.day} {self.time} - {self.title}"
class RestaurantBranch(models.Model):
    """Model representing restaurant branches"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Restaurant Branches"

    def __str__(self):
        return self.name

class MenuCategory(models.Model):
    """Model representing menu categories"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Menu Categories"
        ordering = ['order', 'name']

class MenuItem(models.Model):
    """Model representing menu items for different branches"""
    branch = models.ForeignKey(RestaurantBranch, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE)
    # Updated to support actual file uploads to Supabase menu/ folder
    image = models.ImageField(upload_to='menu/', storage=get_menu_storage, blank=True, null=True, help_text="Upload menu item image")
    # Keep old field for backward compatibility
    image_filename = models.CharField(max_length=200, blank=True, help_text="Alternative: Image filename in static/images/")
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    ingredients = models.TextField(blank=True, help_text="List of ingredients")
    allergens = models.TextField(blank=True, help_text="Allergen information")
    preparation_time = models.IntegerField(null=True, blank=True, help_text="Preparation time in minutes")
    calories = models.IntegerField(null=True, blank=True, help_text="Calories per serving")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        unique_together = ['branch', 'name']  # Prevent duplicate menu items per branch
    
    def __str__(self):
        return f"{self.name} - {self.branch.name}"
    
    @property
    def image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        elif self.image_filename:
            return f'/static/images/{self.image_filename}'
        return '/static/images/default-menu-item.jpg'

class RestaurantLocation(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    description = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    map_embed_url = models.URLField(help_text="Google Maps embed URL")
    is_open = models.BooleanField(default=True)
    opening_hours = models.TextField(blank=True, help_text="Store opening hours")
    
    def __str__(self):
        return self.name

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    guests = models.PositiveIntegerField()
    location = models.ForeignKey(RestaurantLocation, on_delete=models.CASCADE)
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmation_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.date} {self.time}"
    
    class Meta:
        ordering = ['-created_at']

class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject[:50]}"
    
    class Meta:
        ordering = ['-created_at']

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class Notice(models.Model):
    NOTICE_TYPES = [
        ('general', 'General Notice'),
        ('menu', 'Menu Update'),
        ('event', 'Event Announcement'),
        ('promotion', 'Promotion'),
        ('alert', 'Important Alert'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    notice_type = models.CharField(max_length=20, choices=NOTICE_TYPES, default='general')
    image = models.ImageField(upload_to='notices/', blank=True, null=True, help_text="Optional notice image")
    document = models.FileField(upload_to='notices/documents/', blank=True, null=True, help_text="Optional document attachment")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Display prominently on homepage")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True, help_text="Leave blank for no expiration")
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    class Meta:
        ordering = ['-created_at']

class HowDidYouHearAboutUs(models.Model):
    CHOICES = [
        ('search_engine', 'Search Engine (Google, Bing)'),
        ('facebook', 'Facebook'),
        ('twitter', 'X (Twitter)'),
        ('friend', 'Friend or Colleague'),
        ('radio', 'Radio'),
        ('blog', 'Blog/Article'),
        ('ad', 'Online Advertisement'),
        ('other', 'Other'),
    ]
    choice = models.CharField(max_length=32, choices=CHOICES)
    other_text = models.CharField(max_length=255, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_choice_display()} ({self.submitted_at:%Y-%m-%d %H:%M})"


# =========================================================================
#  SITE-WIDE CONTENT  (Phase 1 - design system, base layout, homepage)
# =========================================================================

class SiteSettings(models.Model):
    """Single row holding contact details, WhatsApp number and social links
    that were previously hard-coded into every template. Edited in the
    Django admin; exposed to all templates as `site` via a context
    processor (frontend.context_processors.site_settings).
    """
    company_name = models.CharField(max_length=120, default="The White Meat Company")
    tagline = models.CharField(
        max_length=160, blank=True,
        default="Pioneering Zimbabwe's white meat revolution.",
    )
    brand_slogan = models.CharField(
        max_length=60, default="EAT | LIVE | HEALTHY",
        help_text="Recurring brand philosophy shown in banners and dividers.",
    )

    # Contact
    whatsapp_number = models.CharField(
        max_length=20, default="263772333369",
        help_text="International format, digits only, no + (used for wa.me links).",
    )
    phone_primary = models.CharField(max_length=30, blank=True, default="+263 772 333 369")
    phone_secondary = models.CharField(max_length=30, blank=True, default="+263 779 521 665")
    email = models.EmailField(blank=True, default="rabbitholezim@gmail.com")
    office_address = models.CharField(
        max_length=255, blank=True,
        default="17793 Tredgold Avenue, Belvedere, Harare",
    )
    restaurant_address = models.CharField(
        max_length=255, blank=True,
        default="Golden Quarry Road & Bulawayo Road, Harare",
    )
    business_hours = models.TextField(
        blank=True,
        default="Mon-Fri 08:00-17:00\nSat 08:00-15:00",
    )
    map_embed_url = models.URLField(
        blank=True, max_length=1000,
        help_text="Google Maps 'embed' src URL for the footer/contact map.",
    )

    # Social links (blank = hidden)
    facebook_url = models.URLField(blank=True, default="https://www.facebook.com/thewhitemeatco")
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True, default="https://x.com/WhiteMeatCompa1")
    youtube_url = models.URLField(blank=True, default="https://www.youtube.com/@brightt.makuchete2875")
    tiktok_url = models.URLField(blank=True, default="https://www.tiktok.com/@thewhitemeatco")
    whatsapp_channel_url = models.URLField(
        blank=True, default="https://whatsapp.com/channel/0029VaMwhvvEKyZDkNNk5H21",
    )

    # Payment details - shown to customers in the checkout modal before they
    # upload proof of payment or choose to pay cash. All optional/blank = hidden.
    payment_instructions = models.TextField(
        blank=True,
        help_text="Short note shown above the payment details, e.g. 'Pay 50% deposit to confirm your order.'",
    )
    payment_ecocash_number = models.CharField(
        max_length=30, blank=True, help_text="EcoCash / mobile money number customers should pay to.",
    )
    payment_ecocash_name = models.CharField(
        max_length=120, blank=True, help_text="Registered name on the EcoCash/mobile money account.",
    )
    payment_bank_details = models.TextField(
        blank=True,
        help_text="Bank name, account name, account number, branch - shown to customers exactly as typed.",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def whatsapp_link(self):
        digits = "".join(ch for ch in self.whatsapp_number if ch.isdigit())
        return f"https://wa.me/{digits}" if digits else ""

    @property
    def slogan_parts(self):
        """['EAT', 'LIVE', 'HEALTHY'] - so templates can put a coloured
        separator between the words instead of a plain '|' character."""
        return [p.strip() for p in (self.brand_slogan or "").split("|") if p.strip()]


class HeroSlide(models.Model):
    """A slide in the homepage hero slider. Fully admin-managed.

    Image handling mirrors `Accessory`: an uploaded `background_image`
    (Supabase in production) OR a `background_image_filename` pointing at a
    file in static/images/ as a code-managed fallback.
    """
    OVERLAY_CHOICES = [
        ("dark", "Dark overlay (light text)"),
        ("light", "Light overlay (dark text)"),
        ("none", "No overlay"),
    ]
    PAGE_CHOICES = [
        ("home", "Homepage"),
        ("equipment", "Rabbit Farm Equipment"),
        ("breeding", "Breeding Stock"),
        ("masterclass", "Masterclass"),
        ("rabbithole", "Rabbit Hole"),
        ("butchery", "Whitemeat Butchery"),
        ("outgrowers", "Outgrower Initiatives"),
    ]

    page = models.CharField(
        max_length=20, choices=PAGE_CHOICES, default="home",
        help_text="Which page's slider this slide belongs to.",
    )
    heading = models.CharField(max_length=120)
    subheading = models.TextField(blank=True)
    background_image = models.ImageField(
        upload_to="hero/", storage=get_equipment_storage, blank=True, null=True,
        help_text="Recommended 2400x1200px, < 400 KB.",
    )
    background_image_filename = models.CharField(
        max_length=200, blank=True,
        help_text="Alternative: filename in static/images/ (e.g. home.jpeg).",
    )
    image_alt = models.CharField(max_length=200, blank=True)

    background_video = models.FileField(
        upload_to="hero/", storage=get_equipment_storage, blank=True, null=True,
        help_text="Optional: an MP4 that autoplays instead of the image above "
                   "(the image is still used as the poster while it loads).",
    )
    background_video_filename = models.CharField(
        max_length=200, blank=True,
        help_text="Alternative: filename in static/videos/ (e.g. but.mp4).",
    )

    cta_primary_label = models.CharField(max_length=40, blank=True)
    cta_primary_url = models.CharField(max_length=300, blank=True)
    cta_secondary_label = models.CharField(max_length=40, blank=True)
    cta_secondary_url = models.CharField(max_length=300, blank=True)

    overlay = models.CharField(max_length=10, choices=OVERLAY_CHOICES, default="dark")
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first.")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["page", "order", "id"]

    def __str__(self):
        return f"[{self.get_page_display()}] {self.order}. {self.heading}"

    @property
    def image_url(self):
        if self.background_image:
            try:
                return self.background_image.url
            except Exception:
                pass
        if self.background_image_filename:
            return f"/static/images/{self.background_image_filename}"
        return "/static/images/home.jpeg"

    @property
    def video_url(self):
        if self.background_video:
            try:
                return self.background_video.url
            except Exception:
                pass
        if self.background_video_filename:
            return f"/static/videos/{self.background_video_filename}"
        return ""


class HomeServiceCard(models.Model):
    """One item in the icon strip shown across the bottom of the homepage hero."""
    ICON_CHOICES = [
        ("breeding", "Breeding stock (paw)"),
        ("equipment", "Equipment (tools)"),
        ("masterclass", "Masterclass (graduation cap)"),
        ("outgrower", "Outgrower (handshake)"),
        ("restaurant", "Rabbit Hole (utensils)"),
        ("butchery", "Butchery (drumstick)"),
        ("shop", "Shop (bag)"),
        ("leaf", "Health (leaf)"),
        ("truck", "Delivery (truck)"),
        ("phone", "Contact (phone)"),
    ]

    # Icon key -> Font Awesome 6 (free) class.
    FA_ICONS = {
        "breeding": "fa-solid fa-paw",
        "equipment": "fa-solid fa-screwdriver-wrench",
        "masterclass": "fa-solid fa-graduation-cap",
        "outgrower": "fa-solid fa-handshake",
        "restaurant": "fa-solid fa-utensils",
        "butchery": "fa-solid fa-drumstick-bite",
        "shop": "fa-solid fa-bag-shopping",
        "leaf": "fa-solid fa-leaf",
        "truck": "fa-solid fa-truck-fast",
        "phone": "fa-solid fa-phone",
    }

    title = models.CharField(max_length=80)
    description = models.CharField(max_length=200, blank=True)
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default="leaf")
    url = models.CharField(
        max_length=300,
        help_text="Where the item links to, e.g. /equipment/ or a named path.",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    @property
    def fa_class(self):
        return self.FA_ICONS.get(self.icon, "fa-solid fa-leaf")


class Breed(models.Model):
    """A rabbit breed on the Breeding Stock page. Fully admin-managed:
    price, description and characteristics can all be edited without
    touching a template. Image handling mirrors Accessory/HeroSlide.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-filled from the name if left blank.")
    tagline = models.CharField(max_length=200, blank=True, help_text="Short eyebrow, e.g. 'The gold standard of commercial rabbit farming'.")
    description = models.TextField()
    characteristics = models.TextField(
        blank=True,
        help_text="One characteristic per line, e.g. 'Mature weight: 4-5.5 kg'.",
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(
        null=True, blank=True, help_text="Optional. Leave blank if stock isn't tracked.",
    )
    image = models.ImageField(
        upload_to="breeds/", storage=get_equipment_storage, blank=True, null=True,
        help_text="Upload a breed photo.",
    )
    image_filename = models.CharField(
        max_length=200, blank=True,
        help_text="Alternative: filename in static/images/ (e.g. new.jpg).",
    )
    image_alt = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while Breed.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.image_filename:
            return f"/static/images/{self.image_filename}"
        return "/static/images/new.jpg"

    @property
    def characteristics_list(self):
        return [c.strip() for c in (self.characteristics or "").splitlines() if c.strip()]


class MasterclassDate(models.Model):
    """One bookable date on the Masterclass calendar. Admin creates these
    for the whole year; the calendar and booking form are both driven
    entirely from this table - no dates are hardcoded in templates.
    """
    event = models.ForeignKey(
        MasterclassEvent, on_delete=models.CASCADE, related_name="calendar_dates",
        null=True, blank=True, help_text="Optional link back to the main event/schedule.",
    )
    date = models.DateField(unique=True)
    capacity = models.PositiveIntegerField(default=20)
    is_active = models.BooleanField(default=True, help_text="Untick to cancel/hide this date.")
    location = models.CharField(max_length=200, blank=True, default="Belvedere, Harare")
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.date:%d %b %Y}"

    @property
    def booked_count(self):
        return self.bookings.exclude(status="cancelled").aggregate(
            total=models.Sum("attendees")
        )["total"] or 0

    @property
    def spaces_left(self):
        return max(self.capacity - self.booked_count, 0)

    @property
    def is_full(self):
        return self.spaces_left <= 0

    @property
    def is_past(self):
        return self.date < timezone.localdate()

    @property
    def is_bookable(self):
        return self.is_active and not self.is_past and not self.is_full


class MasterclassBooking(models.Model):
    STATUS_CHOICES = [
        ("pending_payment", "Pending Payment"),
        ("proof_submitted", "Payment Proof Submitted"),
        ("verified", "Payment Verified"),
        ("rejected", "Payment Rejected"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    masterclass_date = models.ForeignKey(MasterclassDate, on_delete=models.CASCADE, related_name="bookings")
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    attendees = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    payment_proof = models.FileField(
        upload_to="masterclass_proofs/%Y/%m/", storage=get_masterclass_storage, blank=True, null=True,
        help_text="Screenshot/PDF of proof of payment.",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending_payment")
    admin_notes = models.TextField(blank=True, help_text="Internal notes, not shown to the customer.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.masterclass_date} ({self.get_status_display()})"


class ButcheryProduct(models.Model):
    """A product in the Whitemeat Butchery. Admin-managed: price, unit,
    description and availability all editable without touching a template.
    """
    CATEGORY_CHOICES = [
        ("fish", "Fish"),
        ("chicken", "Chicken"),
        ("rabbit", "Rabbit Meat"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="portions")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(
        max_length=40, default="each",
        help_text="e.g. 'each', 'per kg', '500g pack'.",
    )
    stock_note = models.CharField(
        max_length=60, blank=True,
        help_text="e.g. 'Fresh daily', 'Frozen', 'Pre-order only'.",
    )
    image = models.ImageField(
        upload_to="butchery/", storage=get_equipment_storage, blank=True, null=True,
    )
    image_filename = models.CharField(
        max_length=200, blank=True,
        help_text="Alternative: filename in static/images/.",
    )
    image_alt = models.CharField(max_length=200, blank=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while ButcheryProduct.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.image_filename:
            return f"/static/images/{self.image_filename}"
        return "/static/images/default-menu-item.jpg"


class Cage(models.Model):
    """A rabbit cage system on the /cages/ page. Admin-managed, mirrors
    Accessory/Breed/ButcheryProduct: price, description, features and
    availability all editable without touching a template.
    """
    CATEGORY_CHOICES = [
        ("breeders", "Breeders"),
        ("weaners", "Weaners"),
        ("growers", "Growers"),
        ("complete", "Complete system"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-filled from the name if left blank.")
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="breeders",
        help_text="Shown as the tag on the product card.",
    )
    description = models.TextField()
    features = models.TextField(
        blank=True,
        help_text="One feature per line, e.g. '12 compartments: 1 buck + 11 does'.",
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.CharField(
        max_length=120, blank=True,
        help_text="e.g. 'Houses 1 buck + 11 does' or 'Up to 90 weaners'.",
    )
    image = models.ImageField(
        upload_to="cages/", storage=get_equipment_storage, blank=True, null=True,
        help_text="Upload a cage photo.",
    )
    image_filename = models.CharField(
        max_length=200, blank=True,
        help_text="Alternative: filename in static/images/ (e.g. cage3.jpg).",
    )
    image_alt = models.CharField(max_length=200, blank=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while Cage.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.image_filename:
            return f"/static/images/{self.image_filename}"
        return "/static/images/cage3.jpg"

    @property
    def features_list(self):
        return [f.strip() for f in (self.features or "").splitlines() if f.strip()]


class Shed(models.Model):
    """A rabbit shed / housing structure on the /sheds/ page. Admin-managed,
    mirrors Cage: price, description, features and availability all editable
    without touching a template.
    """
    CATEGORY_CHOICES = [
        ("colony", "Colony shed"),
        ("breeding", "Breeding shed"),
        ("grower", "Grower shed"),
        ("complete", "Complete unit"),
        ("custom", "Custom build"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-filled from the name if left blank.")
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="colony",
        help_text="Shown as the tag on the product card.",
    )
    description = models.TextField()
    features = models.TextField(
        blank=True,
        help_text="One feature per line, e.g. 'Treated timber frame, IBR roof'.",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.CharField(
        max_length=120, blank=True,
        help_text="e.g. 'Fits 4 x 12Sdx breeder cages' or '12m x 3m footprint'.",
    )
    image = models.ImageField(
        upload_to="sheds/", storage=get_equipment_storage, blank=True, null=True,
        help_text="Upload a shed photo.",
    )
    image_filename = models.CharField(
        max_length=200, blank=True,
        help_text="Alternative: filename in static/images/ (e.g. house.jpg).",
    )
    image_alt = models.CharField(max_length=200, blank=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while Shed.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.image_filename:
            return f"/static/images/{self.image_filename}"
        return "/static/images/house.jpg"

    @property
    def features_list(self):
        return [f.strip() for f in (self.features or "").splitlines() if f.strip()]


class Order(models.Model):
    """A checkout submission from any of the site's shopping carts (cages,
    sheds, accessories, breeding stock, or a restaurant order/reservation).

    One shared model + one shared checkout form (see frontend/forms.py
    OrderForm and the /api/place-order/ view) so every cart on the site
    ends the same way: payment details shown, proof of payment attached OR
    pay-cash chosen, then the order is handed to WhatsApp to confirm.
    """
    SOURCE_CHOICES = [
        ("cages", "Cages"),
        ("sheds", "Sheds"),
        ("accessories", "Accessories"),
        ("breeding", "Breeding Stock"),
        ("butchery", "Whitemeat Butchery"),
        ("rabbithole", "Rabbit Hole"),
        ("pagomo", "Rabbit Hole Pagomo"),
        ("mixed", "Mixed cart"),
    ]
    PAYMENT_CHOICES = [
        ("proof", "Paid - proof of payment attached"),
        ("cash", "Pay in cash on collection/delivery"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending review"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=30)
    items_summary = models.TextField(help_text="Human-readable order lines, one per line.")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cash")
    proof_of_payment = models.FileField(
        upload_to="order_proofs/%Y/%m/", storage=get_order_storage, blank=True, null=True,
        help_text="Screenshot/PDF of proof of payment. Required unless paying cash.",
    )
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer_name} - {self.get_source_display()} (${self.total})"

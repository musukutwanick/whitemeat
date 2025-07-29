from django.db import models

# Accessory model for cages/equipment accessories
class Accessory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='accessory_images/', blank=True, null=True, help_text="Upload accessory image")
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
            return self.image.url
        return '/static/images/default-accessory.jpg'

class MasterclassEvent(models.Model):
    title = models.CharField(max_length=200, default="Upcoming Masterclass")
    date_range = models.CharField(max_length=100, help_text="e.g. August 2nd & 3rd, 2025")
    description = models.TextField(blank=True)

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
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime

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
    # Updated to support actual file uploads
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True, help_text="Upload menu item image")
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
            return self.image.url
        elif self.image_filename:
            return f'/static/images/{self.image_filename}'
        return '/static/images/default-menu-item.jpg'

class Notice(models.Model):
    """Model for admin notices/announcements"""
    NOTICE_TYPES = [
        ('general', 'General Notice'),
        ('promotion', 'Promotion'),
        ('event', 'Event'),
        ('announcement', 'Announcement'),
        ('maintenance', 'Maintenance'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    notice_type = models.CharField(max_length=20, choices=NOTICE_TYPES, default='general')
    image = models.ImageField(upload_to='notice_images/', blank=True, null=True)
    document = models.FileField(upload_to='notice_documents/', blank=True, null=True)
    branch = models.ForeignKey(RestaurantBranch, on_delete=models.CASCADE, null=True, blank=True, 
                              help_text="Leave blank for system-wide notices")
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_current(self):
        """Check if notice is currently active"""
        now = timezone.now()
        if self.end_date:
            return self.start_date <= now <= self.end_date
        return self.start_date <= now

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

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from .models import (
    MenuItem, MenuCategory, RestaurantBranch, HowDidYouHearAboutUs,
    MasterclassEvent, MasterclassSession, Accessory,
    HeroSlide, HomeServiceCard, Breed,
    MasterclassDate, MasterclassBooking, SiteSettings, ButcheryProduct, Cage, Shed,
    Order,
)
from .forms import HowDidYouHearAboutUsForm, MasterclassBookingForm, OrderForm
import json
import calendar as cal_module
from datetime import date
from urllib.parse import quote
from django.utils import timezone
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)

# Page Views
def index(request):
    """Serve the main homepage and handle 'How Did You Hear About Us' form"""
    submitted = False
    if request.method == 'POST' and 'how_hear_submit' in request.POST:
        form = HowDidYouHearAboutUsForm(request.POST)
        if form.is_valid():
            form.save()
            submitted = True
            form = HowDidYouHearAboutUsForm()  # reset form after submit
    else:
        form = HowDidYouHearAboutUsForm()
    context = {
        'form': form,
        'how_hear_submitted': submitted,
        'hero_slides': HeroSlide.objects.filter(is_active=True, page='home'),
        'service_cards': HomeServiceCard.objects.filter(is_active=True),
    }
    return render(request, 'index.html', context)


def equipment(request):
    """Rabbit Farm Equipment landing page (catalogue arrives in a later phase)."""
    context = {
        'hero_slides': HeroSlide.objects.filter(is_active=True, page='equipment'),
    }
    return render(request, 'equipment.html', context)


def outgrowers(request):
    """Outgrower Initiatives page (fleshed out in a later phase)."""
    return render(request, 'outgrowers.html')


def butchery(request):
    """Whitemeat Butchery: products + WhatsApp ordering."""
    products = ButcheryProduct.objects.filter(is_available=True)
    present = [c for c in products.values_list('category', flat=True).distinct()]
    categories = [(k, v) for k, v in ButcheryProduct.CATEGORY_CHOICES if k in present]
    return render(request, 'butchery.html', {'products': products, 'categories': categories})


def cart(request):
    """Shopping cart placeholder (server-side cart arrives in a later phase)."""
    return render(request, 'cart.html')

def masterclass(request):
    """Serve the masterclass page: dynamic content, a year-round admin-managed
    calendar of dates, and a booking form (with proof-of-payment upload) that
    hands off to WhatsApp to confirm."""
    event = MasterclassEvent.objects.order_by('-id').first()
    sessions_by_day = {1: [], 2: []}
    days = [1, 2]
    if event:
        sessions = MasterclassSession.objects.filter(event=event)
        for session in sessions:
            sessions_by_day.get(session.day, []).append(session)

    today = timezone.localdate()
    try:
        month = int(request.GET.get('month', today.month))
        year = int(request.GET.get('year', today.year))
    except (TypeError, ValueError):
        month, year = today.month, today.year
    if month < 1:
        month, year = 12, year - 1
    elif month > 12:
        month, year = 1, year + 1

    dates_this_month = MasterclassDate.objects.filter(is_active=True, date__year=year, date__month=month)
    dates_by_day = {d.date.day: d for d in dates_this_month}

    month_weeks = cal_module.Calendar(firstweekday=6).monthdayscalendar(year, month)
    calendar_weeks = []
    for week in month_weeks:
        row = []
        for day_num in week:
            if day_num == 0:
                row.append(None)
            else:
                d = date(year, month, day_num)
                row.append({
                    'day': day_num,
                    'is_today': d == today,
                    'is_past': d < today,
                    'mc_date': dates_by_day.get(day_num),
                })
        calendar_weeks.append(row)

    prev_month, prev_year = (12, year - 1) if month == 1 else (month - 1, year)
    next_month, next_year = (1, year + 1) if month == 12 else (month + 1, year)
    upcoming_dates = MasterclassDate.objects.filter(is_active=True, date__gte=today).order_by('date')[:12]

    booking_success = False
    whatsapp_url = None

    if request.method == 'POST':
        form = MasterclassBookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking = form.save()
            proof_url = None
            if booking.payment_proof:
                try:
                    proof_url = request.build_absolute_uri(booking.payment_proof.url)
                except Exception:
                    proof_url = None

            lines = [
                f"Hi! I'd like to confirm my Masterclass booking (Ref #{booking.id}).",
                "",
                f"Name: {booking.name}",
                f"Email: {booking.email}",
                f"Phone: {booking.phone}",
                f"Date: {booking.masterclass_date.date:%A, %d %B %Y}",
                f"Attendees: {booking.attendees}",
            ]
            if event:
                lines.append(f"Course fee: ${event.price} per attendee")
            lines.append(f"Payment proof: {proof_url}" if proof_url else "Payment proof: (will send separately)")
            lines.append("")
            lines.append("Please confirm my booking. Thank you!")
            message = "\n".join(lines)

            site = SiteSettings.load()
            digits = "".join(ch for ch in site.whatsapp_number if ch.isdigit())
            whatsapp_url = f"https://wa.me/{digits}?text={quote(message)}"
            booking_success = True
            form = MasterclassBookingForm()  # fresh form for a follow-up booking
    else:
        form = MasterclassBookingForm()

    context = {
        'event': event,
        'sessions_by_day': sessions_by_day,
        'days': days,
        'calendar_weeks': calendar_weeks,
        'calendar_month': month,
        'calendar_year': year,
        'calendar_month_name': cal_module.month_name[month],
        'prev_month': prev_month, 'prev_year': prev_year,
        'next_month': next_month, 'next_year': next_year,
        'upcoming_dates': upcoming_dates,
        'booking_form': form,
        'booking_success': booking_success,
        'whatsapp_url': whatsapp_url,
    }
    return render(request, 'masterclass.html', context)

def cages(request):
    """Serve the cage products page (admin-managed via the Cage model)."""
    cages = Cage.objects.filter(is_available=True)
    return render(request, 'cages.html', {'cages': cages})


def sheds(request):
    """Serve the rabbit shed / housing page (admin-managed via the Shed model)."""
    sheds = Shed.objects.filter(is_available=True)
    return render(request, 'sheds.html', {'sheds': sheds})


def accessories(request):
    """Serve the accessories catalogue page (split out from /cages/)"""
    accessories = Accessory.objects.filter(is_available=True).order_by('-created_at')
    return render(request, 'accessories.html', {'accessories': accessories})

# Accessories are managed from the staff dashboard's generic content CRUD
# (section='accessories' - see frontend/dashboard.py) alongside cages, sheds,
# breeding stock and butchery. The old bespoke add_accessory view/template
# was a duplicate, unlinked UI left over from before that existed.

def breeding(request):
    """Serve the breeding stock page with dynamic breeds"""
    breeds = Breed.objects.filter(is_available=True)
    return render(request, 'breeding.html', {'breeds': breeds})

def rabbithole(request):
    """Serve the rabbit hole restaurant page with dynamic menu items"""
    # Look for Pagomo branch or any active branch
    branch = RestaurantBranch.objects.filter(slug__in=['rabbit-hole-pagomo', 'pagomo'], is_active=True).first()
    if not branch:
        branch = RestaurantBranch.objects.filter(is_active=True).first()
    
    if branch:
        menu_items = MenuItem.objects.filter(
            branch=branch, 
            is_available=True
        ).select_related('category').order_by('category__order', 'name')
    else:
        menu_items = MenuItem.objects.filter(
            is_available=True
        ).select_related('category').order_by('category__order', 'name')

    # If the specific branch has no items, fallback to any available menu items
    if not menu_items.exists():
        menu_items = MenuItem.objects.filter(
            is_available=True
        ).select_related('category').order_by('category__order', 'name')

    categories = MenuCategory.objects.all().order_by('order')
    context = {
        'branch': branch,
        'menu_items': menu_items,
        'categories': categories,
    }
    return render(request, 'rabbithole.html', context)

def pagomo(request):
    """Serve the pagomo branch page with dynamic menu items"""
    branch = RestaurantBranch.objects.filter(slug__in=['rabbit-hole-pagomo', 'pagomo'], is_active=True).first()
    if not branch:
        branch = RestaurantBranch.objects.filter(is_active=True).first()
    
    if branch:
        menu_items = MenuItem.objects.filter(
            branch=branch, 
            is_available=True
        ).select_related('category').order_by('category__order', 'name')
    else:
        menu_items = MenuItem.objects.filter(
            is_available=True
        ).select_related('category').order_by('category__order', 'name')
    
    if not menu_items.exists():
        menu_items = MenuItem.objects.filter(
            is_available=True
        ).select_related('category').order_by('category__order', 'name')

    categories = MenuCategory.objects.all().order_by('order')
    context = {
        'branch': branch,
        'menu_items': menu_items,
        'categories': categories,
    }
    return render(request, 'pagomo.html', context)

def debug_static(request):
    """Debug view to test static file loading"""
    return render(request, 'debug.html')

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to authenticate with username first
        user = authenticate(request, username=username, password=password)
        
        # If that fails and the input looks like an email, try to find user by email
        if user is None and '@' in username:
            try:
                from django.contrib.auth.models import User
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username/email or password.')
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('index')

# Admin Dashboard Views
@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard"""
    from .dashboard import SECTIONS, SECTION_ORDER
    branches = RestaurantBranch.objects.filter(is_active=True)
    recent_menu_items = MenuItem.objects.select_related('branch', 'category').order_by('-created_at')[:5]

    stats = {
        'total_branches': branches.count(),
        'total_menu_items': MenuItem.objects.count(),
    }

    # Live counts for each managed content section, for the landing tiles.
    content_tiles = [
        {
            'slug': slug,
            'label': SECTIONS[slug]['label'],
            'icon': SECTIONS[slug]['icon'],
            'count': SECTIONS[slug]['model'].objects.count(),
        }
        for slug in SECTION_ORDER
    ]
    pending_bookings = MasterclassBooking.objects.exclude(
        status__in=['confirmed', 'cancelled']
    ).count()
    pending_orders = Order.objects.filter(status='pending').count()

    # Get latest 10 survey responses
    from .models import HowDidYouHearAboutUs
    recent_how_hear = HowDidYouHearAboutUs.objects.order_by('-submitted_at')[:10]

    # Statistics for each choice
    how_hear_stats = (
        HowDidYouHearAboutUs.objects.values('choice')
        .annotate(count=Count('id')).order_by('-count')
    )
    # Map choice to display name
    CHOICE_LABELS = dict(HowDidYouHearAboutUs.CHOICES)
    for stat in how_hear_stats:
        stat['label'] = CHOICE_LABELS.get(stat['choice'], stat['choice'])

    context = {
        'branches': branches,
        'recent_menu_items': recent_menu_items,
        'stats': stats,
        'content_tiles': content_tiles,
        'pending_bookings': pending_bookings,
        'pending_orders': pending_orders,
        'total_branches': branches.count(),
        'total_menu_items': MenuItem.objects.count(),
        'total_responses': HowDidYouHearAboutUs.objects.count(),
        'recent_how_hear': recent_how_hear,
        'how_hear_stats': how_hear_stats,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def branch_selection(request):
    """Select branch for menu management"""
    branches = RestaurantBranch.objects.filter(is_active=True)
    return render(request, 'admin/branch_selection.html', {'branches': branches})

@login_required
def branch_menu_items(request, branch_id):
    """Display menu items for a specific branch"""
    branch = get_object_or_404(RestaurantBranch, id=branch_id, is_active=True)
    menu_items = MenuItem.objects.filter(branch=branch).select_related('category').order_by('category__order', 'name')
    categories = MenuCategory.objects.all().order_by('order')
    
    # Calculate category item counts specific to this branch
    categories_with_counts = []
    for cat in categories:
        cat_count = menu_items.filter(category=cat).count()
        categories_with_counts.append({
            'name': cat.name,
            'slug': cat.slug,
            'count': cat_count,
        })
    
    context = {
        'branch': branch,
        'menu_items': menu_items,
        'categories': categories,
        'categories_with_counts': categories_with_counts,
    }
    return render(request, 'admin/branch_menu_items.html', context)

@login_required
def add_menu_item(request, branch_id):
    """Add new menu item to a specific branch"""
    branch = get_object_or_404(RestaurantBranch, id=branch_id, is_active=True)
    categories = MenuCategory.objects.all().order_by('order')
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            price = request.POST.get('price', '').strip()
            description = request.POST.get('description', '').strip()
            category_id = request.POST.get('category')
            
            if not name or not price or not category_id:
                messages.error(request, 'Please fill in all required fields.')
            else:
                menu_item = MenuItem.objects.create(
                    branch=branch,
                    name=name,
                    description=description,
                    price=price,
                    category_id=category_id,
                    image=request.FILES.get('image') if 'image' in request.FILES else None,
                    ingredients=request.POST.get('ingredients', '').strip(),
                    allergens=request.POST.get('allergens', '').strip(),
                    preparation_time=request.POST.get('preparation_time') or None,
                    calories=request.POST.get('calories') or None,
                    is_available=request.POST.get('is_available') == 'on' or 'is_available' in request.POST,
                    is_featured=request.POST.get('is_featured') == 'on',
                )
                messages.success(request, f'Menu item "{menu_item.name}" added successfully!')
                return redirect('branch_menu_items', branch_id=branch.id)
        except Exception as e:
            logger.exception("Error adding menu item")
            messages.error(request, f'Error adding menu item: {str(e)}')
    
    context = {
        'branch': branch,
        'categories': categories,
    }
    return render(request, 'admin/add_menu_item.html', context)

@login_required
def edit_menu_item(request, branch_id, item_id):
    """Edit existing menu item"""
    branch = get_object_or_404(RestaurantBranch, id=branch_id, is_active=True)
    menu_item = get_object_or_404(MenuItem, id=item_id, branch=branch)
    categories = MenuCategory.objects.all().order_by('order')
    
    if request.method == 'POST':
        try:
            menu_item.name = request.POST.get('name', '').strip()
            menu_item.description = request.POST.get('description', '').strip()
            menu_item.price = request.POST.get('price', '').strip()
            menu_item.category_id = request.POST.get('category')
            menu_item.ingredients = request.POST.get('ingredients', '').strip()
            menu_item.allergens = request.POST.get('allergens', '').strip()
            menu_item.preparation_time = request.POST.get('preparation_time') or None
            menu_item.calories = request.POST.get('calories') or None
            menu_item.is_available=request.POST.get('is_available') == 'on'
            menu_item.is_featured = request.POST.get('is_featured') == 'on'
            
            if 'image' in request.FILES:
                menu_item.image = request.FILES['image']
            
            menu_item.save()
            messages.success(request, f'Menu item "{menu_item.name}" updated successfully!')
            return redirect('branch_menu_items', branch_id=branch.id)
        except Exception as e:
            logger.exception("Error updating menu item")
            messages.error(request, f'Error updating menu item: {str(e)}')
    
    context = {
        'branch': branch,
        'menu_item': menu_item,
        'categories': categories,
    }
    return render(request, 'admin/edit_menu_item.html', context)

@login_required
def delete_menu_item(request, branch_id, item_id):
    """Delete menu item"""
    branch = get_object_or_404(RestaurantBranch, id=branch_id, is_active=True)
    menu_item = get_object_or_404(MenuItem, id=item_id, branch=branch)
    
    if request.method == 'POST':
        name = menu_item.name
        menu_item.delete()
        messages.success(request, f'Menu item "{name}" deleted successfully!')
        return redirect('branch_menu_items', branch_id=branch.id)
    
    return render(request, 'admin/confirm_delete.html', {
        'item': menu_item,
        'branch': branch,
        'item_type': 'menu item'
    })

@login_required
def admin_logout(request):
    """Admin logout"""
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('login')

@login_required
def how_hear_responses(request):
    stats = (
        HowDidYouHearAboutUs.objects.values('choice')
        .order_by('choice')
        .annotate(count=Count('id'))
    )
    responses = HowDidYouHearAboutUs.objects.order_by('-submitted_at')[:50]
    CHOICE_LABELS = dict(HowDidYouHearAboutUs.CHOICES)
    for stat in stats:
        stat['label'] = CHOICE_LABELS.get(stat['choice'], stat['choice'])
    return render(request, 'admin/how_hear_responses.html', {
        'stats': stats,
        'responses': responses,
    })

# API Endpoints
@csrf_exempt
def api_menu_items(request):
    """API endpoint to get menu items"""
    if request.method == 'GET':
        menu_items = [
            {
                'id': 1,
                'name': 'Full Rabbit',
                'price': 12.00,
                'category': 'goch-goch',
                'description': 'Our signature dish featuring a whole rabbit prepared to perfection with special herbs and spices.',
                'image': 'images/full-rabbit.jpg'
            },
            {
                'id': 2,
                'name': 'Half Rabbit',
                'price': 6.00,
                'category': 'goch-goch',
                'description': 'Half portion of our delicious rabbit, perfect for lighter appetites.',
                'image': 'images/half-rabbit.jpg'
            },
            {
                'id': 3,
                'name': 'Tsuro',
                'price': 6.00,
                'category': 'stews',
                'description': 'Traditional rabbit stew served with sadza and fresh vegetables.',
                'image': 'images/tsuro.jpg'
            }
        ]
        return JsonResponse({'menu_items': menu_items})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_restaurant_locations(request):
    """API endpoint to get restaurant locations"""
    if request.method == 'GET':
        locations = [
            {
                'id': 1,
                'name': 'Rabbit hole Pagomo',
                'address': 'Pagomo, Harare, Zimbabwe',
                'description': 'Our flagship location offering the complete Rabbit Hole experience with a vibrant atmosphere and extensive menu.',
                'map_embed': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d30387.108017334933!2d30.952801010839856!3d-17.8204137!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x1931a5005ab9857b%3A0x64e4ebc8d391f6a4!2sRabbit%20Hole%20PaGomo!5e0!3m2!1sen!2szw!4v1752682566421!5m2!1sen!2szw'
            },
            {
                'id': 2,
                'name': 'Rabbit hole Premium',
                'address': 'Premium Location, Harare, Zimbabwe',
                'description': 'Experience our premium dining location with an elevated atmosphere and exclusive menu offerings.',
                'map_embed': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d30387.108017334933!2d30.952801010839856!3d-17.8204137!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x1931a5625e2989af%3A0x5e54f2f976050108!2sThe%20Rabbit%20Hole%20Bar%20%26%20Grill!5e0!3m2!1sen!2szw!4v1752683185081!5m2!1sen!2szw'
            }
        ]
        return JsonResponse({'locations': locations})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_contact_form(request):
    """API endpoint to handle contact form submissions"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')
            
            # Here you could save to database or send email
            # For now, we'll just return success
            
            response_data = {
                'status': 'success',
                'message': f'Thank you {name}! Your message has been received. We will get back to you soon.',
                'data': {
                    'name': name,
                    'email': email,
                    'received_at': '2025-07-18'
                }
            }
            return JsonResponse(response_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_reservation(request):
    """API endpoint to handle restaurant reservations"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            phone = data.get('phone')
            date = data.get('date')
            time = data.get('time')
            guests = data.get('guests')
            location = data.get('location')
            
            # Here you could save to database
            # For now, we'll just return success
            
            response_data = {
                'status': 'success',
                'message': f'Reservation confirmed for {name} on {date} at {time}',
                'reservation_details': {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'date': date,
                    'time': time,
                    'guests': guests,
                    'location': location,
                    'confirmation_number': f'RH{hash(name + email + date) % 10000:04d}'
                }
            }
            return JsonResponse(response_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_newsletter_signup(request):
    """API endpoint to handle newsletter signups"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            name = data.get('name', '')
            
            # Here you could save to database or integrate with email service
            # For now, we'll just return success
            
            response_data = {
                'status': 'success',
                'message': f'Successfully subscribed {email} to our newsletter!',
                'subscriber': {
                    'email': email,
                    'name': name,
                    'subscribed_at': '2025-07-18'
                }
            }
            return JsonResponse(response_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def debug_menu_data(request):
    """Debug view to check menu items and branch data"""
    html = ["<h1>Debug Menu Data</h1>"]
    
    # Check branches
    html.append("<h2>Branches:</h2><ul>")
    for branch in RestaurantBranch.objects.all():
        html.append(f"<li>ID: {branch.id}, Name: {branch.name}, Slug: {branch.slug}, Active: {branch.is_active}</li>")
    html.append("</ul>")
    
    # Check categories
    html.append("<h2>Categories:</h2><ul>")
    for cat in MenuCategory.objects.all():
        html.append(f"<li>ID: {cat.id}, Name: {cat.name}, Slug: {cat.slug}, Order: {cat.order}</li>")
    html.append("</ul>")
    
    # Check menu items
    html.append("<h2>All Menu Items:</h2><ul>")
    for item in MenuItem.objects.select_related('branch', 'category').all():
        html.append(f"<li>ID: {item.id}, Name: {item.name}, Branch: {item.branch.name}, Category: {item.category.name}, Available: {item.is_available}, Price: ${item.price}</li>")
    html.append("</ul>")
    
    # Check Pagomo specific items
    try:
        pagomo_branch = RestaurantBranch.objects.get(slug='pagomo', is_active=True)
        html.append(f"<h2>Pagomo Branch (ID: {pagomo_branch.id}) Menu Items:</h2><ul>")
        pagomo_items = MenuItem.objects.filter(branch=pagomo_branch, is_available=True).select_related('category')
        for item in pagomo_items:
            html.append(f"<li>Name: {item.name}, Category: {item.category.name}, Price: ${item.price}, Available: {item.is_available}</li>")
        html.append("</ul>")
        html.append(f"<p><strong>Total available items for Pagomo: {pagomo_items.count()}</strong></p>")
    except RestaurantBranch.DoesNotExist:
        html.append("<p><strong>ERROR: Pagomo branch not found!</strong></p>")
    
    return HttpResponse("".join(html))

def how_hear_about_us(request):
    """Handle the 'How Did You Hear About Us' form submission"""
    submitted = False
    if request.method == 'POST':
        form = HowDidYouHearAboutUsForm(request.POST)
        if form.is_valid():
            form.save()
            submitted = True
    else:
        form = HowDidYouHearAboutUsForm()
    return render(request, 'how_hear_about_us.html', {'form': form, 'submitted': submitted})

@staff_member_required
def edit_masterclass_schedule(request):
    event = MasterclassEvent.objects.order_by('-id').first()
    if not event:
        event = MasterclassEvent.objects.create(
            title="Rabbitry Masterclass",
            date_range="August 2025",
            description="Pioneering Zimbabwe's white meat revolution. Join our comprehensive 2-day intensive program."
        )
    sessions = MasterclassSession.objects.filter(event=event).order_by('day', 'time')
    
    # Serialize sessions for front-end JS table
    sessions_data = [
        {
            'id': s.id,
            'day': s.day,
            'time': s.time,
            'title': s.title,
            'description': s.description or '',
        }
        for s in sessions
    ]
    
    return render(request, 'admin/edit_masterclass_schedule.html', {
        'event': event,
        'sessions': sessions,
        'sessions_json': json.dumps(sessions_data),
    })

def masterclass_sessions_api(request):
    """API endpoint to get masterclass sessions JSON"""
    event = MasterclassEvent.objects.order_by('-id').first()
    if not event:
        return JsonResponse({'event': None, 'sessions': []})
    sessions = MasterclassSession.objects.filter(event=event).order_by('day', 'time')
    sessions_data = [
        {
            'id': s.id,
            'day': s.day,
            'time': s.time,
            'title': s.title,
            'description': s.description or '',
        }
        for s in sessions
    ]
    return JsonResponse({
        'event': {
            'title': event.title,
            'date_range': event.date_range,
            'description': event.description,
        },
        'sessions': sessions_data
    })

@csrf_exempt
@staff_member_required
def save_masterclass_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event = MasterclassEvent.objects.order_by('-id').first()
            if not event:
                event = MasterclassEvent.objects.create(
                    title=data.get('event_title', 'Rabbitry Masterclass'),
                    date_range=data.get('event_date', 'August 2025'),
                    description=data.get('description', '')
                )
            
            # Save event info if requested
            if data.get('save_event'):
                event.title = data.get('event_title', event.title).strip()
                event.date_range = data.get('event_date', event.date_range).strip()
                if 'description' in data:
                    event.description = data.get('description', '').strip()
                event.save()
                return JsonResponse({'success': True, 'message': 'Event details updated!'})
            
            # Remove all existing sessions and replace with updated ones
            MasterclassSession.objects.filter(event=event).delete()
            sessions = data.get('sessions', [])
            for s in sessions:
                title = (s.get('title') or '').strip()
                time_str = (s.get('time') or '').strip()
                if title:  # Only save rows that have a title
                    MasterclassSession.objects.create(
                        event=event,
                        day=int(s.get('day', 1)),
                        time=time_str,
                        title=title,
                        description=(s.get('description') or '').strip(),
                    )
            return JsonResponse({'success': True, 'message': 'Schedule saved successfully!'})
        except Exception as e:
            logger.exception("Error saving masterclass schedule")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@require_POST
def place_order(request):
    """Unified checkout endpoint for every cart on the site (cages, sheds,
    accessories, breeding stock, restaurant orders/reservations). Saves the
    Order (with proof of payment if attached), then hands off to WhatsApp -
    same pattern as the masterclass booking flow."""
    form = OrderForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    order = form.save()

    proof_url = None
    if order.proof_of_payment:
        try:
            proof_url = request.build_absolute_uri(order.proof_of_payment.url)
        except Exception:
            proof_url = None

    lines = [
        f"New order - {order.get_source_display()}",
        "",
        "Items:",
        order.items_summary,
        "",
        f"Total: ${order.total}",
        "",
        f"Name: {order.customer_name}",
        f"Phone: {order.customer_phone}",
    ]
    if order.payment_method == 'cash':
        lines.append("Payment: Cash on collection/delivery")
    else:
        lines.append("Payment: EcoCash/bank transfer - proof attached")
        lines.append(f"Proof of payment: {proof_url}" if proof_url else "Proof of payment: (attached, link unavailable)")
    if order.notes:
        lines.append(f"Notes: {order.notes}")
    lines.append("")
    lines.append(f"Order ref #{order.id}. Please confirm my order. Thank you!")
    message = "\n".join(lines)

    site = SiteSettings.load()
    digits = ''.join(ch for ch in site.whatsapp_number if ch.isdigit())
    whatsapp_url = f"https://wa.me/{digits}?text={quote(message)}"

    return JsonResponse({'success': True, 'whatsapp_url': whatsapp_url, 'order_id': order.id})


def health_check(request):
    return HttpResponse("OK")



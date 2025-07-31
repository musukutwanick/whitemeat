from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from .models import MenuItem, MenuCategory, RestaurantBranch, HowDidYouHearAboutUs, MasterclassEvent, MasterclassSession, Accessory
from .forms import HowDidYouHearAboutUsForm, AccessoryForm
import json
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required

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
    return render(request, 'index.html', {'form': form, 'how_hear_submitted': submitted})

def masterclass(request):
    """Serve the masterclass training page dynamically from DB"""
    # Get the latest event (or the only one)
    event = MasterclassEvent.objects.order_by('-id').first()
    sessions_by_day = {1: [], 2: []}
    days = [1, 2]
    if event:
        sessions = MasterclassSession.objects.filter(event=event)
        for session in sessions:
            sessions_by_day.get(session.day, []).append(session)
    context = {
        'event': event,
        'sessions_by_day': sessions_by_day,
        'days': days,
    }
    return render(request, 'masterclass.html', context)

def cages(request):
    """Serve the cages and accessories page with dynamic accessories"""
    accessories = Accessory.objects.filter(is_available=True).order_by('-created_at')
    return render(request, 'cages.html', {'accessories': accessories})


# Admin: Add Accessory/Equipment
@staff_member_required
def add_accessory(request):

    # Handle add/edit/delete
    if request.method == 'POST':
        if 'accessory_id' in request.POST:
            # Edit existing accessory
            accessory = get_object_or_404(Accessory, pk=request.POST['accessory_id'])
            form = AccessoryForm(request.POST, request.FILES, instance=accessory)
            if form.is_valid():
                form.save()
                messages.success(request, 'Accessory updated successfully!')
                return redirect('add_accessory')
        elif 'delete_accessory_id' in request.POST:
            # Delete accessory
            accessory = get_object_or_404(Accessory, pk=request.POST['delete_accessory_id'])
            accessory.delete()
            messages.success(request, 'Accessory deleted successfully!')
            return redirect('add_accessory')
        else:
            # Add new accessory
            form = AccessoryForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Accessory added successfully!')
                return redirect('add_accessory')
    else:
        form = AccessoryForm()

    accessories = Accessory.objects.order_by('-created_at')
    return render(request, 'admin/add_accessory.html', {'form': form, 'accessories': accessories})

def breeding(request):
    """Serve the breeding stock page"""
    return render(request, 'breeding.html')

def rabbithole(request):
    """Serve the rabbit hole restaurant page with dynamic menu items"""
    try:
        # Get the Pagomo branch (since rabbithole.html shows menu from Pagomo branch)
        branch = RestaurantBranch.objects.get(slug='rabbit-hole-pagomo', is_active=True)
        # Get all available menu items for this branch, ordered by category
        menu_items = MenuItem.objects.filter(
            branch=branch, 
            is_available=True
        ).select_related('category').order_by('category__order', 'name')
        # Get all categories to display filter buttons
        categories = MenuCategory.objects.all().order_by('order')
        
        context = {
            'branch': branch,
            'menu_items': menu_items,
            'categories': categories,
        }
        return render(request, 'rabbithole.html', context)
    except RestaurantBranch.DoesNotExist:
        # If Pagomo branch doesn't exist, render with empty data
        context = {
            'branch': None,
            'menu_items': [],
            'categories': MenuCategory.objects.all().order_by('order'),
        }
        return render(request, 'rabbithole.html', context)

def pagomo(request):
    """Serve the pagomo branch page with dynamic menu items"""
    try:
        # Get the Pagomo branch (using the actual slug from database)
        branch = RestaurantBranch.objects.get(slug='rabbit-hole-pagomo', is_active=True)
        # Get all available menu items for this branch, ordered by category
        menu_items = MenuItem.objects.filter(
            branch=branch, 
            is_available=True
        ).select_related('category').order_by('category__order', 'name')
        # Get all categories to display filter buttons
        categories = MenuCategory.objects.all().order_by('order')
        
        context = {
            'branch': branch,
            'menu_items': menu_items,
            'categories': categories,
        }
        return render(request, 'pagomo.html', context)
    except RestaurantBranch.DoesNotExist:
        # If Pagomo branch doesn't exist, render with empty data
        context = {
            'branch': None,
            'menu_items': [],
            'categories': MenuCategory.objects.all().order_by('order'),
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
@login_required
def admin_dashboard(request):
    """Main admin dashboard"""
    branches = RestaurantBranch.objects.filter(is_active=True)
    recent_menu_items = MenuItem.objects.select_related('branch', 'category').order_by('-created_at')[:5]
    
    stats = {
        'total_branches': branches.count(),
        'total_menu_items': MenuItem.objects.count(),
    }

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
    
    context = {
        'branch': branch,
        'menu_items': menu_items,
        'categories': categories,
    }
    return render(request, 'admin/branch_menu_items.html', context)

@login_required
def add_menu_item(request, branch_id):
    """Add new menu item to a specific branch"""
    branch = get_object_or_404(RestaurantBranch, id=branch_id, is_active=True)
    categories = MenuCategory.objects.all().order_by('order')
    
    if request.method == 'POST':
        try:
            menu_item = MenuItem.objects.create(
                branch=branch,
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                price=request.POST.get('price'),
                category_id=request.POST.get('category'),
                image=request.FILES.get('image') if 'image' in request.FILES else None,
                ingredients=request.POST.get('ingredients', ''),
                allergens=request.POST.get('allergens', ''),
                preparation_time=request.POST.get('preparation_time') or None,
                calories=request.POST.get('calories') or None,
                is_available=request.POST.get('is_available') == 'on',
                is_featured=request.POST.get('is_featured') == 'on',
            )
            messages.success(request, f'Menu item "{menu_item.name}" added successfully!')
            return redirect('branch_menu_items', branch_id=branch.id)
        except Exception as e:
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
            menu_item.name = request.POST.get('name')
            menu_item.description = request.POST.get('description')
            menu_item.price = request.POST.get('price')
            menu_item.category_id = request.POST.get('category')
            menu_item.ingredients = request.POST.get('ingredients', '')
            menu_item.allergens = request.POST.get('allergens', '')
            menu_item.preparation_time = request.POST.get('preparation_time') or None
            menu_item.calories = request.POST.get('calories') or None
            menu_item.is_available = request.POST.get('is_available') == 'on'
            menu_item.is_featured = request.POST.get('is_featured') == 'on'
            
            if 'image' in request.FILES:
                menu_item.image = request.FILES['image']
            
            menu_item.save()
            messages.success(request, f'Menu item "{menu_item.name}" updated successfully!')
            return redirect('branch_menu_items', branch_id=branch.id)
        except Exception as e:
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
    sessions = MasterclassSession.objects.filter(event=event) if event else []
    return render(request, 'admin/edit_masterclass_schedule.html', {
        'event': event,
        'sessions': sessions,
    })

@csrf_exempt
@staff_member_required
def save_masterclass_schedule(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        event = MasterclassEvent.objects.order_by('-id').first()
        if not event:
            return JsonResponse({'success': False, 'error': 'No event found.'}, status=400)
        # Save event info if requested
        if data.get('save_event'):
            event.title = data.get('event_title', event.title)
            event.date_range = data.get('event_date', event.date_range)
            event.save()
            return JsonResponse({'success': True})
        # Remove all existing sessions for this event
        MasterclassSession.objects.filter(event=event).delete()
        # Add new sessions
        sessions = data.get('sessions', [])
        for s in sessions:
            MasterclassSession.objects.create(
                event=event,
                day=int(s.get('day', 1)),
                time=s.get('time', ''),
                title=s.get('title', ''),
                description=s.get('description', ''),
            )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

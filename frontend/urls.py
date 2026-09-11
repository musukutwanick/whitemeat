from django.urls import path
from . import views
from . import dashboard

urlpatterns = [
    # Page URLs
    path('', views.index, name='index'),
    path('masterclass/', views.masterclass, name='masterclass'),
    path('equipment/', views.equipment, name='equipment'),
    path('cages/', views.cages, name='cages'),
    path('sheds/', views.sheds, name='sheds'),
    path('accessories/', views.accessories, name='accessories'),
    path('outgrowers/', views.outgrowers, name='outgrowers'),
    path('breeding/', views.breeding, name='breeding'),
    path('butchery/', views.butchery, name='butchery'),
    path('cart/', views.cart, name='cart'),
    path('rabbithole/', views.rabbithole, name='rabbithole'),
    path('pagomo/', views.pagomo, name='pagomo'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    
    # Admin Dashboard URLs
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/branch-selection/', views.branch_selection, name='branch_selection'),
    path('dashboard/branch/<int:branch_id>/menu/', views.branch_menu_items, name='branch_menu_items'),
    path('dashboard/branch/<int:branch_id>/menu/add/', views.add_menu_item, name='add_menu_item'),
    path('dashboard/branch/<int:branch_id>/menu/<int:item_id>/edit/', views.edit_menu_item, name='edit_menu_item'),
    path('dashboard/branch/<int:branch_id>/menu/<int:item_id>/delete/', views.delete_menu_item, name='delete_menu_item'),
    path('dashboard/responses/', views.how_hear_responses, name='how_hear_responses'),
    path('dashboard/masterclass-schedule/', views.edit_masterclass_schedule, name='edit_masterclass_schedule'),
    path('dashboard/masterclass-schedule/sessions/', views.masterclass_sessions_api, name='masterclass_sessions_api'),
    path('dashboard/masterclass-schedule/save/', views.save_masterclass_schedule, name='save_masterclass_schedule'),

    # Generic content management (cages, accessories, breeding, butchery,
    # hero slides, masterclass dates) - see frontend/dashboard.py
    path('dashboard/c/<slug:section>/', dashboard.content_list, name='content_list'),
    path('dashboard/c/<slug:section>/new/', dashboard.content_edit, name='content_add'),
    path('dashboard/c/<slug:section>/<int:pk>/', dashboard.content_edit, name='content_edit'),
    path('dashboard/c/<slug:section>/<int:pk>/delete/', dashboard.content_delete, name='content_delete'),

    # API URLs
    path('api/menu-items/', views.api_menu_items, name='api_menu_items'),
    path('api/locations/', views.api_restaurant_locations, name='api_locations'),
    path('api/contact/', views.api_contact_form, name='api_contact'),
    path('api/reservation/', views.api_reservation, name='api_reservation'),
    path('api/newsletter/', views.api_newsletter_signup, name='api_newsletter'),
    path('api/place-order/', views.place_order, name='place_order'),
    
    # Debug URL
    path('debug/', views.debug_static, name='debug_static'),
    path('debug-menu/', views.debug_menu_data, name='debug_menu_data'),

    # Payment URLs
    # Paynow payment endpoint removed

    # Health Check URL
    path('health/', views.health_check, name='health_check'),
]

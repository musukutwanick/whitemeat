from django.urls import path
from . import views

urlpatterns = [
    # Page URLs
    path('', views.index, name='index'),
    path('masterclass/', views.masterclass, name='masterclass'),
    path('cages/', views.cages, name='cages'),
    path('breeding/', views.breeding, name='breeding'),
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
    path('dashboard/masterclass-schedule/save/', views.save_masterclass_schedule, name='save_masterclass_schedule'),
    path('dashboard/add-accessory/', views.add_accessory, name='add_accessory'),
    
    # API URLs
    path('api/menu-items/', views.api_menu_items, name='api_menu_items'),
    path('api/locations/', views.api_restaurant_locations, name='api_locations'),
    path('api/contact/', views.api_contact_form, name='api_contact'),
    path('api/reservation/', views.api_reservation, name='api_reservation'),
    path('api/newsletter/', views.api_newsletter_signup, name='api_newsletter'),
    
    # Debug URL
    path('debug/', views.debug_static, name='debug_static'),
    path('debug-menu/', views.debug_menu_data, name='debug_menu_data'),
]

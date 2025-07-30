# URL patterns for EcoEchoes club website
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Admin-approved password reset URLs
    path('password_reset/', views.request_password_reset, name='password_reset'),
    path('password_reset/status/', views.password_reset_status, name='password_reset_status'),
    
    # User profile URLs
    path('profile/', views.profile, name='profile'),
    path('history/', views.user_history, name='user_history'),
    
    # Article URLs
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/category/<str:category>/', views.articles_by_category, name='articles_by_category'),
    path('articles/<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    
    # Event URLs
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/type/<str:event_type>/', views.events_by_type, name='events_by_type'),
    path('events/<slug:slug>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<slug:event_slug>/register/', views.register_for_event, name='register_for_event'),
    
    # Search URLs
    path('search/', views.search, name='search'),
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
    
    # Other pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Membership application URLs
    path('apply/', views.apply_membership, name='apply_membership'),
    path('application-success/', views.application_success, name='application_success'),
    path('application-status/', views.application_status, name='application_status'),
    
    # AJAX URLs
    path('ajax/like-article/<int:article_id>/', views.like_article, name='like_article'),
] 
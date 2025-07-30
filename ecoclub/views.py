from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .models import Article, Event, EventRegistration, UserProfile, FileUpload, ContactMessage, UserHistory, MembershipApplication, PasswordResetRequest
from .forms import (CustomUserCreationForm, CustomAuthenticationForm, ArticleForm, EventForm, 
                   EventRegistrationForm, FileUploadForm, ContactForm, SearchForm, JoinClubForm, 
                   UserProfileForm, MembershipApplicationForm, PasswordResetRequestForm, PasswordResetStatusForm)

# Generate unique slugs for articles and events
def generate_unique_slug(model_class, title, exclude_id=None):
    """Generate a unique slug for a model"""
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    
    queryset = model_class.objects.filter(slug=slug)
    if exclude_id:
        queryset = queryset.exclude(pk=exclude_id)
    
    while queryset.exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
        queryset = model_class.objects.filter(slug=slug)
        if exclude_id:
            queryset = queryset.exclude(pk=exclude_id)
    
    return slug

# Track user activity for analytics
def track_user_history(request, page_visited):
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key
    
    # Get IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Track visit
    UserHistory.objects.create(
        user=user,
        session_key=session_key,
        ip_address=ip,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        page_visited=page_visited
    )

# Main homepage with recent content
def home(request):
    track_user_history(request, 'home')
    
    # Get recent articles and events
    recent_articles = Article.objects.filter(published=True)[:6]
    upcoming_events = Event.objects.filter(start_date__gte=timezone.now(), is_active=True)[:6]
    
    # Get visit count from cookies
    visit_count = request.session.get('visit_count', 0)
    visit_count += 1
    request.session['visit_count'] = visit_count
    
    context = {
        'recent_articles': recent_articles,
        'upcoming_events': upcoming_events,
        'visit_count': visit_count,
    }
    return render(request, 'home.html', context)

# User registration - restricted to club members only
def register(request):
    # Redirect to home page since public registration is not available
    messages.info(request, 'Registration is not available for the general public. Please contact us if you\'re interested in joining our club.')
    return redirect('home')

# Club member login system
def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Allow superusers to login regardless of club membership
            if user.is_superuser:
                login(request, user)
                messages.success(request, f'Welcome back, Admin!')
                return redirect('home')
            else:
                # Check if user is a club member
                try:
                    profile = UserProfile.objects.get(user=user)
                    if profile.is_club_member:
                        login(request, user)
                        messages.success(request, f'Welcome back, {user.first_name}!')
                        return redirect('home')
                    else:
                        messages.error(request, 'This login is for club members only. Please contact us if you\'re interested in joining our club.')
                except UserProfile.DoesNotExist:
                    messages.error(request, 'This login is for club members only. Please contact us if you\'re interested in joining our club.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

# User logout
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

# Display all published articles with filtering
class ArticleListView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Article.objects.filter(published=True).select_related('author')
        # Filter by category if specified
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add categories to context
        context['categories'] = Article.CATEGORY_CHOICES
        # Add current category filter if any
        context['current_category'] = self.request.GET.get('category', '')
        return context

# Individual article detail view with view tracking
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'
    
    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.views += 1
        obj.save()
        # Track user history
        track_user_history(self.request, f'article: {obj.title}')
        return obj

# Create new articles - club members only
class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'
    success_url = reverse_lazy('article_list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.slug = generate_unique_slug(Article, form.instance.title)
        messages.success(self.request, 'Article created successfully!')
        return super().form_valid(form)

# Edit existing articles - authors only
class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'
    success_url = reverse_lazy('article_list')
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Article updated successfully!')
        return super().form_valid(form)

# Display all active events
class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10
    
    def get_queryset(self):
        return Event.objects.filter(is_active=True).select_related('organizer')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_types'] = Event.EVENT_TYPES
        return context

# Individual event detail with registration status
class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Check if user is a club member and registered
        if self.request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=self.request.user)
                if profile.is_club_member:
                    context['is_registered'] = EventRegistration.objects.filter(
                        user=self.request.user, event=event
                    ).exists()
                    context['registration_form'] = EventRegistrationForm()
                    context['can_register'] = True
                else:
                    context['can_register'] = False
            except UserProfile.DoesNotExist:
                context['can_register'] = False
        else:
            context['is_registered'] = False
            context['can_register'] = False
        
        # Track user history
        track_user_history(self.request, f'event: {event.title}')
        return context

# Create new events - club members only
class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')
    
    def form_valid(self, form):
        form.instance.organizer = self.request.user
        form.instance.slug = generate_unique_slug(Event, form.instance.title)
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)

# Edit existing events - organizers only
class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)

# Register for events - club members only
@login_required
def register_for_event(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    
    # Check if user is a club member
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.is_club_member:
            messages.error(request, 'Event registration is available to club members only.')
            return redirect('event_detail', slug=event_slug)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Event registration is available to club members only.')
        return redirect('event_detail', slug=event_slug)
    
    if request.method == 'POST':
        # Check if user is already registered
        if EventRegistration.objects.filter(user=request.user, event=event).exists():
            messages.error(request, 'You are already registered for this event.')
            return redirect('event_detail', slug=event_slug)
        
        # Check if event is open for registration
        if not event.is_registration_open():
            messages.error(request, 'Registration for this event is closed.')
            return redirect('event_detail', slug=event_slug)
        
        # Check if there are available spots
        if not event.has_available_spots():
            messages.error(request, 'This event is full.')
            return redirect('event_detail', slug=event_slug)
        
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.event = event
            registration.save()
            messages.success(request, 'Successfully registered for the event!')
            return redirect('event_detail', slug=event_slug)
    
    return redirect('event_detail', slug=event_slug)

# User profile management - club members only
@login_required
def profile(request):
    # Check if user is a club member
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.is_club_member:
            messages.error(request, 'This feature is available to club members only.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'This feature is available to club members only.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    # Get user's articles and events
    user_articles = Article.objects.filter(author=request.user)
    user_events = Event.objects.filter(organizer=request.user)
    registered_events = EventRegistration.objects.filter(user=request.user).select_related('event')
    
    context = {
        'form': form,
        'profile': profile,
        'user_articles': user_articles,
        'user_events': user_events,
        'registered_events': registered_events,
    }
    return render(request, 'users/profile.html', context)

# Join club application - redirects to home
@login_required
def join_club(request):
    # Redirect to home page since self-joining is not available
    messages.info(request, 'Club membership is by invitation only. Please contact us if you\'re interested in joining our club.')
    return redirect('home')

# Search functionality across articles and events
def search(request):
    form = SearchForm(request.GET or None)
    results = []
    query = None
    
    if form.is_valid():
        query = form.cleaned_data['query']
        search_type = form.cleaned_data['search_type']
        
        if search_type == 'all' or search_type == 'articles':
            articles = Article.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query),
                published=True
            )
            results.extend([{'type': 'article', 'object': article} for article in articles])
        
        if search_type == 'all' or search_type == 'events':
            events = Event.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query),
                is_active=True
            )
            results.extend([{'type': 'event', 'object': event} for event in events])
        
        # Track search
        track_user_history(request, f'search: {query}')
    
    # Paginate results
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'results': page_obj,
        'query': query,
    }
    return render(request, 'search.html', context)

# AJAX search suggestions API
@csrf_exempt
def search_suggestions(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('query', '')
        
        if len(query) >= 2:
            article_titles = Article.objects.filter(
                title__icontains=query, published=True
            ).values_list('title', flat=True)[:5]
            
            event_titles = Event.objects.filter(
                title__icontains=query, is_active=True
            ).values_list('title', flat=True)[:5]
            
            suggestions = list(article_titles) + list(event_titles)
            return JsonResponse({'suggestions': suggestions})
    
    return JsonResponse({'suggestions': []})

# File upload system - club members only
@login_required
def upload_file(request):
    # Check if user is a club member
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.is_club_member:
            messages.error(request, 'This feature is available to club members only.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'This feature is available to club members only.')
        return redirect('home')
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_upload = form.save(commit=False)
            file_upload.user = request.user
            file_upload.save()
            messages.success(request, 'File uploaded successfully!')
            return redirect('profile')
    else:
        form = FileUploadForm()
    
    return render(request, 'users/upload_file.html', {'form': form})

# Contact form handling
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message. We will get back to you soon!')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

# About page
def about(request):
    track_user_history(request, 'about')
    return render(request, 'about.html')

# User activity history - club members only
@login_required
def user_history(request):
    # Check if user is a club member
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.is_club_member:
            messages.error(request, 'This feature is available to club members only.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'This feature is available to club members only.')
        return redirect('home')
    
    history = UserHistory.objects.filter(user=request.user)
    
    # Get visit statistics
    total_visits = history.count()
    today_visits = history.filter(timestamp__date=timezone.now().date()).count()
    
    # Paginate history
    paginator = Paginator(history, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'history': page_obj,
        'total_visits': total_visits,
        'today_visits': today_visits,
    }
    return render(request, 'users/history.html', context)

# Article like functionality - club members only
@login_required
@require_POST
def like_article(request, article_id):
    # Check if user is a club member
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.is_club_member:
            return JsonResponse({'error': 'This feature is available to club members only.'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'This feature is available to club members only.'})
    
    article = get_object_or_404(Article, id=article_id)
    
    if request.user in article.likes.all():
        article.likes.remove(request.user)
        liked = False
    else:
        article.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'like_count': article.likes.count()
    })

# Filter articles by category
def articles_by_category(request, category):
    articles = Article.objects.filter(category=category, published=True)
    
    # Paginate articles
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'articles': page_obj,
        'category': category,
        'category_display': dict(Article.CATEGORY_CHOICES).get(category, category)
    }
    return render(request, 'articles/articles_by_category.html', context)

# Filter events by type
def events_by_type(request, event_type):
    events = Event.objects.filter(event_type=event_type, is_active=True)
    
    # Paginate events
    paginator = Paginator(events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj,
        'event_type': event_type,
        'event_type_display': dict(Event.EVENT_TYPES).get(event_type, event_type)
    }
    return render(request, 'events/events_by_type.html', context)

# Membership application form
def apply_membership(request):
    if request.method == 'POST':
        form = MembershipApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            messages.success(request, 'Your membership application has been submitted successfully! We will review it and contact you soon.')
            return redirect('home')
    else:
        form = MembershipApplicationForm()
    
    return render(request, 'membership/apply.html', {'form': form})

# Application success page
def application_success(request):
    return render(request, 'membership/success.html')

# Check application status
def application_status(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            application = MembershipApplication.objects.get(email=email)
            return render(request, 'membership/status.html', {'application': application})
        except MembershipApplication.DoesNotExist:
            messages.error(request, 'No application found with this email address.')
    
    return render(request, 'membership/check_status.html')

# Admin-approved password reset request
def request_password_reset(request):
    """View for requesting password reset via admin approval"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            reason = form.cleaned_data['reason']
            desired_password = form.cleaned_data['desired_password']
            
            # Create password reset request
            PasswordResetRequest.objects.create(
                user=user,
                desired_password=desired_password,
                reason=reason,
                admin_notes=f"Reason: {reason}"
            )
            
            messages.success(request, 'Your password reset request has been submitted and is pending admin approval. You can check the status using the form below.')
            return redirect('password_reset_status')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'registration/password_reset_request.html', {'form': form})

# Check password reset request status
def password_reset_status(request):
    """View for checking password reset request status"""
    status_info = None
    
    if request.method == 'POST':
        form = PasswordResetStatusForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            
            try:
                user = User.objects.get(username=username, email=email)
                reset_request = PasswordResetRequest.objects.filter(user=user).order_by('-requested_at').first()
                
                if reset_request:
                    status_info = {
                        'request': reset_request,
                        'user': user
                    }
                else:
                    messages.warning(request, 'No password reset request found for this user.')
            except User.DoesNotExist:
                messages.error(request, 'No user found with this username and email combination.')
    else:
        form = PasswordResetStatusForm()
    
    return render(request, 'registration/password_reset_status.html', {
        'form': form,
        'status_info': status_info
    })

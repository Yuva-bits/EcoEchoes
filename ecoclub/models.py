from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

# Extended user profile with club membership status
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_club_member = models.BooleanField(default=False)
    join_date = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Environmental articles with categories and engagement tracking
class Article(models.Model):
    CATEGORY_CHOICES = [
        ('environment', 'Environment'),
        ('renewable_energy', 'Renewable Energy'),
        ('waste_management', 'Waste Management'),
        ('sustainable_living', 'Sustainable Living'),
        ('climate_change', 'Climate Change'),
        ('conservation', 'Conservation'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    content = models.TextField()
    excerpt = models.TextField(max_length=300, help_text="Brief description of the article")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='environment')
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_articles', blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('article_detail', args=[self.slug])

# Club events with registration management
class Event(models.Model):
    EVENT_TYPES = [
        ('competition', 'Competition'),
        ('cleaning_campaign', 'Cleaning Campaign'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('awareness_drive', 'Awareness Drive'),
        ('tree_planting', 'Tree Planting'),
        ('recycling_drive', 'Recycling Drive'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, default='workshop')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    max_participants = models.PositiveIntegerField(default=50)
    registration_deadline = models.DateTimeField()
    event_image = models.ImageField(upload_to='events/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['start_date']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('event_detail', args=[self.slug])
    
    def is_registration_open(self):
        return timezone.now() < self.registration_deadline and self.is_active
    
    def get_registered_count(self):
        return self.registrations.filter(is_confirmed=True).count()
    
    def has_available_spots(self):
        return self.get_registered_count() < self.max_participants

# Event registration tracking
class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=True)
    additional_notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'event']
        
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

# User activity tracking for analytics
class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history', null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    page_visited = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        user_info = self.user.username if self.user else "Anonymous"
        return f"{user_info} - {self.page_visited} - {self.timestamp}"

# File upload system for club members
class FileUpload(models.Model):
    FILE_TYPES = [
        ('document', 'Document'),
        ('image', 'Image'),
        ('certificate', 'Certificate'),
        ('id_proof', 'ID Proof'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='uploads/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='document')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.title} by {self.user.username}"
    
    def get_file_size(self):
        return self.file.size
    
    def get_file_extension(self):
        return self.file.name.split('.')[-1].lower()

# Contact form submissions
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - {self.subject}"

# Membership application system
class MembershipApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    location = models.CharField(max_length=100)
    bio = models.TextField(help_text="Tell us about yourself and why you want to join our club")
    motivation = models.TextField(help_text="What motivates you to care about environmental issues?")
    experience = models.TextField(help_text="Any relevant experience or skills you'd like to share?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_applications')
    admin_notes = models.TextField(blank=True, help_text="Notes from admin")
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='membership_applications')
    
    class Meta:
        ordering = ['-applied_at']
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_status_display()}"

# Admin-approved password reset system
class PasswordResetRequest(models.Model):
    """Model for handling password reset requests that require admin approval"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ], default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_resets')
    processed_at = models.DateTimeField(null=True, blank=True)
    desired_password = models.CharField(max_length=128, blank=True, null=True, help_text="User's desired new password")
    reason = models.TextField(blank=True, null=True, help_text="User's reason for password reset")
    
    class Meta:
        ordering = ['-requested_at']
        verbose_name = 'Password Reset Request'
        verbose_name_plural = 'Password Reset Requests'
    
    def __str__(self):
        return f"Password reset for {self.user.username} - {self.status}"
    
    def is_expired(self):
        """Check if the request is older than 24 hours"""
        from django.utils import timezone
        from datetime import timedelta
        return self.requested_at < timezone.now() - timedelta(hours=24)

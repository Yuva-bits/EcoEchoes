from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, Article, Event, EventRegistration, UserHistory, FileUpload, ContactMessage, MembershipApplication, PasswordResetRequest

# User profile inline for admin interface
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'

# Extended user admin with profile integration
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Article management in admin
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'published', 'views', 'created_at']
    list_filter = ['category', 'published', 'created_at', 'author']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at']
    filter_horizontal = ['likes']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')

# Event management in admin
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'organizer', 'start_date', 'location', 'get_registered_count', 'is_active']
    list_filter = ['event_type', 'is_active', 'start_date', 'organizer']
    search_fields = ['title', 'description', 'location', 'organizer__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'get_registered_count']
    date_hierarchy = 'start_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organizer')

# Event registration management
@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'registered_at', 'is_confirmed']
    list_filter = ['is_confirmed', 'registered_at', 'event__event_type']
    search_fields = ['user__username', 'event__title']
    readonly_fields = ['registered_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'event')

# User activity tracking management
@admin.register(UserHistory)
class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'page_visited', 'ip_address', 'timestamp']
    list_filter = ['timestamp', 'page_visited']
    search_fields = ['user__username', 'page_visited', 'ip_address']
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# File upload management
@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'file_type', 'uploaded_at', 'is_public']
    list_filter = ['file_type', 'is_public', 'uploaded_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['uploaded_at', 'get_file_size', 'get_file_extension']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Contact message management with actions
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"

# Membership application management with auto-user creation
@admin.register(MembershipApplication)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'status', 'applied_at', 'processed_at', 'processed_by']
    list_filter = ['status', 'applied_at', 'processed_at']
    search_fields = ['first_name', 'last_name', 'email', 'location']
    readonly_fields = ['applied_at', 'processed_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'location')
        }),
        ('Application Details', {
            'fields': ('bio', 'motivation', 'experience')
        }),
        ('Status', {
            'fields': ('status', 'applied_at', 'processed_at', 'processed_by', 'admin_notes', 'created_user')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('processed_by', 'created_user')
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            obj.processed_by = request.user
            obj.processed_at = timezone.now()
            
            # If approved, create user account
            if obj.status == 'approved' and not obj.created_user:
                from django.contrib.auth.models import User
                import random
                import string
                
                username = f"{obj.first_name.lower()}{obj.last_name.lower()}"
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=obj.email,
                    first_name=obj.first_name,
                    last_name=obj.last_name,
                    password=password
                )
                
                # Create user profile
                profile = UserProfile.objects.create(
                    user=user,
                    bio=obj.bio,
                    location=obj.location,
                    birth_date=obj.date_of_birth,
                    phone_number=obj.phone_number,
                    is_club_member=True
                )
                
                obj.created_user = user
                obj.admin_notes = f"User account created. Username: {username}, Password: {password}"
                
        super().save_model(request, obj, form, change)

# Password reset request management
@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'username', 'email', 'status', 'requested_at', 'processed_at']
    list_filter = ['status', 'requested_at', 'processed_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['user', 'requested_at', 'processed_at', 'processed_by', 'desired_password', 'reason']
    list_editable = ['status']
    ordering = ['-requested_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'requested_at')
        }),
        ('Request Details', {
            'fields': ('desired_password', 'reason')
        }),
        ('Admin Action', {
            'fields': ('status', 'processed_by', 'processed_at', 'admin_notes')
        }),
    )
    
    def username(self, obj):
        return obj.user.username
    username.short_description = 'Username'
    
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            obj.processed_by = request.user
            obj.processed_at = timezone.now()
            
            if obj.status == 'approved':
                # Use the user's desired password
                if obj.desired_password:
                    # Update the user's password with their desired password
                    obj.user.set_password(obj.desired_password)
                    obj.user.save()
                    
                    obj.admin_notes = f"Password reset approved. User's desired password has been set."
                else:
                    obj.admin_notes = f"Password reset approved but no desired password was provided."
                
            elif obj.status == 'rejected':
                obj.admin_notes = f"Password reset request rejected by {request.user.username}"
        
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'processed_by')

# Custom admin site branding
admin.site.site_header = "EcoEchoes Admin"
admin.site.site_title = "EcoEchoes Admin Portal"
admin.site.index_title = "Welcome to EcoEchoes Administration"

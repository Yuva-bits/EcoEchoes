# EcoEchoes - Environmental Awareness Club Website

A Django-based web application for managing an environmental awareness club. The platform provides a comprehensive system for club members to share articles, organize events, and engage with environmental content.

## Features

### Public Features
- **Article Browsing**: Read environmental articles across multiple categories
- **Event Discovery**: View upcoming environmental events and activities
- **Search Functionality**: Search across articles and events with real-time suggestions
- **Contact System**: Submit inquiries and feedback
- **Membership Applications**: Apply to join the club with detailed application forms

### Club Member Features
- **Content Creation**: Write and publish environmental articles
- **Event Management**: Create and organize club events
- **Event Registration**: Register for club events with capacity management
- **Profile Management**: Update personal information and view activity history
- **File Upload System**: Share documents and media files
- **Article Engagement**: Like and interact with articles
- **Activity Tracking**: View personal browsing history and statistics

### Administrative Features
- **User Management**: Manage club members and their profiles
- **Content Moderation**: Approve articles and manage event registrations
- **Membership Processing**: Review and approve membership applications
- **Password Reset System**: Admin-approved password reset requests
- **Analytics Dashboard**: Track user activity and engagement metrics

## Technology Stack

- **Backend**: Django 5.2.4
- **Database**: SQLite (development)
- **Frontend**: Bootstrap 5.3.0, Font Awesome 6.4.0
- **Image Processing**: Pillow 11.3.0
- **Python**: 3.8+

## Project Structure

```
EcoEchoes Website/
├── ecoechoes_website/          # Main Django project
│   ├── settings.py            # Project configuration
│   ├── urls.py               # Main URL routing
│   └── wsgi.py               # WSGI configuration
├── ecoclub/                   # Main application
│   ├── models.py             # Database models
│   ├── views.py              # View logic
│   ├── forms.py              # Form definitions
│   ├── admin.py              # Admin interface
│   ├── urls.py               # App URL patterns
│   └── migrations/           # Database migrations
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── home.html             # Homepage
│   ├── articles/             # Article templates
│   ├── events/               # Event templates
│   ├── users/                # User profile templates
│   ├── membership/           # Membership templates
│   └── registration/         # Authentication templates
├── static/                   # Static files
│   └── images/               # Images and assets
├── media/                    # User uploaded files
├── requirements.txt           # Python dependencies
└── manage.py                 # Django management script
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EcoEchoes-Website
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Database Models

### Core Models
- **UserProfile**: Extended user profiles with club membership status
- **Article**: Environmental articles with categories and engagement tracking
- **Event**: Club events with registration management
- **EventRegistration**: Event participation tracking
- **UserHistory**: User activity analytics
- **FileUpload**: File sharing system for members
- **ContactMessage**: Public contact form submissions
- **MembershipApplication**: Club membership applications
- **PasswordResetRequest**: Admin-approved password reset system

## Authentication & Permissions

### Access Levels
1. **Public Users**: Can browse articles, events, and submit contact forms
2. **Club Members**: Can create content, register for events, and access member features
3. **Administrators**: Full access to all features and admin panel

### Security Features
- Club membership verification for protected features
- Admin-approved password reset system
- CSRF protection on all forms
- Input validation and sanitization

## User Interface

### Design Features
- **Dark Theme**: Modern dark interface with green accent colors
- **Responsive Design**: Mobile-friendly Bootstrap layout
- **Interactive Elements**: Hover effects, animations, and smooth transitions
- **Search Functionality**: Real-time search suggestions
- **User Experience**: Intuitive navigation and clear call-to-actions

### Key Pages
- **Homepage**: Featured articles and upcoming events
- **Article Pages**: Detailed article views with engagement features
- **Event Pages**: Event details with registration capabilities
- **User Profile**: Personal dashboard with activity tracking
- **Admin Panel**: Comprehensive management interface

## Configuration

### Environment Variables
The application uses Django's default settings for development. For production, consider:

- Setting `DEBUG = False`
- Configuring a production database (PostgreSQL recommended)
- Setting up proper email backend
- Configuring static file serving
- Setting secure `SECRET_KEY`

### Customization
- **Branding**: Update site title, logo, and colors in templates
- **Categories**: Modify article and event categories in models
- **Features**: Enable/disable features through admin panel
- **Styling**: Customize CSS in base template

## Features in Detail

### Article System
- **Categories**: Environment, Renewable Energy, Waste Management, etc.
- **Engagement**: View tracking, likes, and author attribution
- **Content Management**: Rich text editing with image support
- **Publishing**: Draft/published status with admin approval

### Event System
- **Event Types**: Competitions, Workshops, Cleaning Campaigns, etc.
- **Registration**: Capacity management and deadline tracking
- **Organizer Tools**: Event creation and management for members
- **Participant Management**: Registration tracking and confirmation

### Membership System
- **Application Process**: Detailed application forms with validation
- **Admin Review**: Comprehensive application review system
- **Auto-Account Creation**: Automatic user account creation upon approval
- **Status Tracking**: Application status checking for applicants

## Deployment

### Development
```bash
python manage.py runserver
```

### Production Considerations
1. **Database**: Use PostgreSQL for production
2. **Static Files**: Configure proper static file serving
3. **Media Files**: Set up media file storage (AWS S3 recommended)
4. **Security**: Configure HTTPS and security headers
5. **Performance**: Enable caching and optimize database queries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Darshini Balamurali
- Eshwara Pandiyan
- Joel Thomas Joe
- Yuvashree Senthilmurugan

---

**EcoEchoes** - Creating a sustainable future through environmental awareness and community action. 

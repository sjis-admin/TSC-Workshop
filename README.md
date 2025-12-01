# Titanium Science Club - Workshop Registration System

A modern, responsive Django-based workshop registration platform with SSLCommerz payment integration for St. Joseph International School's Titanium Science Club.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- ✨ **Modern, Vibrant UI** - Beautiful gradient design with smooth animations
- 📱 **Fully Responsive** - Works perfectly on mobile, tablet, and desktop
- 💳 **SSLCommerz Integration** - Secure online payment gateway for Bangladesh
- 📧 **Email Notifications** - Automatic confirmation emails
- 📄 **PDF Receipts** - Professional receipts with QR codes
- 📊 **Excel Exports** - Export registrations, payments, and workshop data
- 🔒 **Data Validation** - Comprehensive form and business logic validation
- 🎨 **Admin Panel** - Enhanced Django admin with custom actions

## Workshops

### 1. PROJECT DISPLAY & PRESENTATION Workshop
- **Date**: 10 & 11 December 2025
- **Time**: 10:30 AM - 1:30 PM
- **Venue**: New building, St Joseph International School
- **Fee**: ৳200 (Paid)

### 2. PHYSICS OLYMPIAD Workshop
- **Date**: Saturday, 13 December 2025
- **Time**: 9:45 AM - 12:30 PM
- **Venue**: New building, St Joseph International School
- **Fee**: FREE
- **Trainers**: Fayez Ahmed Jahangir Masud & Dr Arshad Momen (BDPhO)

### 3. ARDUINO ROBOTICS BOOTCAMP
- **Date**: Monday, 15 Dec & Wednesday, 17 Dec 2025
- **Time**: 9:45 AM - 12:30 PM
- **Venue**: New building, St Joseph International School
- **Fee**: FREE
- **Organizer**: 2 teams from Zan Tech

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- PostgreSQL (for production) / SQLite (for development)

## Installation & Setup

### 1. Clone or Download the Project

```bash
cd /Volumes/Drive\ A/SJIS/workshop
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and configure:

```env
# For Development (using SQLite)
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# SSLCommerz Credentials (Add your credentials here)
SSLCOMMERZ_STORE_ID=your-store-id-here
SSLCOMMERZ_STORE_PASSWORD=your-store-password-here
SSLCOMMERZ_IS_SANDBOX=True

# For Production (using PostgreSQL)
# Uncomment and configure these when deploying:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=workshop_db
# DB_USER=postgres
# DB_PASSWORD=your-password
# DB_HOST=localhost
# DB_PORT=5432
# DOMAIN=https://titanium.sjis.edu.bd
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Populate Workshops

```bash
python manage.py populate_workshops
```

This will create the three workshops in the database.

### 8. Collect Static Files (for production)

```bash
python manage.py collectstatic
```

### 9. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## SSLCommerz Configuration

### Getting Sandbox Credentials

1. Visit [SSLCommerz](https://www.sslcommerz.com/)
2. Register for a sandbox account
3. Get your Store ID and Store Password
4. Add them to your `.env` file

### Testing Payments

Use SSLCommerz sandbox test cards:
- Card Number: `4242424242424242`
- CVV: Any 3 digits
- Expiry: Any future date

## Admin Panel

Access the admin panel at: http://127.0.0.1:8000/admin/

### Admin Features

- ✅ View all workshops, registrations, and payments
- ✅ Export data to Excel (registrations, payments, workshops)
- ✅ Filter by payment status, workshop, date
- ✅ Search by registration number, email, student name
- ✅ View payment details inline with registrations
- ✅ Color-coded status indicators

### Excel Export

In the admin panel:
1. Select items you want to export
2. Choose "Export selected to Excel" from actions dropdown
3. Click "Go"
4. Excel file will be downloaded

## Email Configuration

### Development (Console Backend)

By default, emails are printed to the console. No configuration needed.

### Production (SMTP)

Edit your `.env` file:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Then update `workshop_registration/settings.py`:

```python
if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

## Database Configuration

### Development (SQLite)

Default configuration. No action needed.

### Production (PostgreSQL)

1. Install PostgreSQL
2. Create database:

```sql
CREATE DATABASE workshop_db;
CREATE USER workshop_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE workshop_db TO workshop_user;
```

3. Update `.env`:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=workshop_db
DB_USER=workshop_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

## Project Structure

```
workshop/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── workshop_registration/      # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── workshops/                  # Main app
│   ├── models.py              # Database models
│   ├── views.py               # View logic
│   ├── forms.py               # Form validation
│   ├── admin.py               # Admin configuration
│   ├── urls.py                # URL routing
│   ├── payment_gateway.py     # SSLCommerz integration
│   ├── utils.py               # Helper functions
│   └── management/
│       └── commands/
│           └── populate_workshops.py
├── templates/                  # HTML templates
│   ├── base.html
│   └── workshops/
│       ├── workshop_list.html
│       ├── register.html
│       ├── payment_confirmation.html
│       ├── payment_success.html
│       ├── registration_success.html
│       └── receipt.html
└── static/                     # Static files
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Key Features Explained

### 1. Workshop Registration

- Students can register for free or paid workshops
- Grade validation (2-12 only)
- Email validation
- Bangladesh phone number validation
- Prevent duplicate registrations

### 2. Payment Flow

For paid workshops:
1. Student fills registration form
2. Redirected to payment confirmation page
3. SSLCommerz payment gateway integration
4. Payment success/fail handling
5. Email confirmation
6. Receipt generation

For free workshops:
1. Student fills registration form
2. Immediate confirmation
3. Email notification
4. Receipt generation

### 3. Receipt System

- PDF generation with QR code
- Professional letterhead design
- Complete registration details
- View in browser or download
- Print-optimized styling

### 4. Admin Features

- Comprehensive dashboard
- Excel exports for all data
- Color-coded status indicators
- Advanced filtering and search
- Inline payment details

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure PostgreSQL database
- [ ] Set up production SMTP email
- [ ] Add production domain to `ALLOWED_HOSTS`
- [ ] Configure SSLCommerz production credentials
- [ ] Set strong `SECRET_KEY`
- [ ] Run `python manage.py collectstatic`
- [ ] Set up SSL certificate (HTTPS)
- [ ] Configure web server (Nginx/Apache)
- [ ] Set up WSGI server (Gunicorn/uWSGI)

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name titanium.sjis.edu.bd;
    
    location /static/ {
        alias /path/to/workshop/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/workshop/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Support & Contact

- **Email**: info@titanium.sjis.edu.bd
- **Website**: https://titanium.sjis.edu.bd
- **School**: St. Joseph International School

## License

Copyright © 2025 Titanium Science Club, St. Joseph International School. All rights reserved.

## Acknowledgments

- SSLCommerz for payment gateway services
- BDPhO for Physics Olympiad trainers
- Zan Tech for Arduino Robotics instruction
- All participating students and parents

---

**Made with ❤️ by Titanium Science Club**

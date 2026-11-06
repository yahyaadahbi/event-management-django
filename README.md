# 🎟 EventHub — Django Event Management Platform

A production-ready, beautifully designed event management web application.

---

## ✨ Features

- **Role-based access**: Participants (register for events) & Organizers (create/manage events)
- **Event CRUD** with image upload, categories, ticket types
- **PDF Tickets** with QR codes generated on registration
- **Analytics Dashboard** with Chart.js (registrations over time, events by category)
- **Dark mode** toggle with persistence
- **Bookmarks/Favorites** (AJAX, no page reload)
- **QR Scan validation** page for organizers
- **CSV & Excel exports** for registrations
- **Toast notifications** and in-app notification center
- **Trending events** algorithm
- **Responsive, mobile-first** modern UI (Syne + DM Sans fonts)

---

## 🚀 Quick Start

### 1. Clone / place the project
```bash
cd event_management/
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment
```bash
cp .env.example .env
# Edit .env — set SECRET_KEY, DB credentials if using PostgreSQL
```

### 5. Apply migrations
```bash
python manage.py makemigrations accounts events registrations
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Load sample data (optional)
```bash
python manage.py shell < seed_data.py
```

### 8. Collect static files (production)
```bash
python manage.py collectstatic
```

### 9. Run the development server
```bash
python manage.py runserver
```

Open http://127.0.0.1:8000

---

## 🗂 Project Structure

```
event_management/
│
├── event_management/       ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/               ← Auth, profiles, notifications
├── events/                 ← Event CRUD, categories, reviews
├── registrations/          ← Tickets, QR, PDF generation
├── dashboard/              ← Analytics, exports
│
├── templates/              ← All HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── events/
│   ├── registrations/
│   ├── dashboard/
│   └── partials/
│
├── static/
│   ├── css/main.css
│   └── js/
│
├── media/                  ← Uploaded files (gitignored)
├── requirements.txt
└── .env.example
```

---

## 👤 User Roles

| Role        | Capabilities |
|-------------|-------------|
| Participant | Browse events, register, download ticket PDF, leave reviews, save bookmarks |
| Organizer   | All of above + create/edit/delete events, view analytics, export data, scan QR codes |
| Admin       | Full Django admin panel access |

---

## 🔧 Key Settings

- **Database**: SQLite by default. Uncomment PostgreSQL block in `settings.py` for production.
- **Email**: Console backend for development (emails print to terminal).
- **Media files**: Stored in `media/` directory locally.

---

## 🎨 Tech Stack

- **Backend**: Django 4.2, python-decouple, django-filter
- **Frontend**: Bootstrap 5 (heavily customized), Syne + DM Sans (Google Fonts), Bootstrap Icons
- **Charts**: Chart.js 4
- **PDF**: ReportLab
- **QR Codes**: qrcode + Pillow
- **Exports**: openpyxl (Excel), Python csv (CSV)

---

## 📄 API / AJAX Endpoints

| URL | Method | Description |
|-----|--------|-------------|
| `/registrations/register/<event_pk>/` | POST | Register for event (AJAX-ready) |
| `/registrations/cancel/<pk>/` | POST | Cancel registration |
| `/events/<pk>/bookmark/` | POST | Toggle bookmark |
| `/accounts/notifications/read/` | POST | Mark all notifications read |
| `/dashboard/chart-data/?type=monthly` | GET | Monthly registration data (JSON) |
| `/registrations/scan/` | POST | Validate QR ticket code |

---

## 📸 Screenshots

After running the server:
- **Home**: `/` — Hero, featured events, stats counters
- **Events**: `/events/` — Filterable grid with sidebar
- **Dashboard**: `/dashboard/` — Analytics with Chart.js
- **Ticket**: `/registrations/ticket/<pk>/` — Beautiful ticket with QR

---

## 🔐 Security Notes

- CSRF protection on all POST forms
- `login_required` on all protected views
- Role checks (organizer-only views reject participants)
- File uploads restricted by type/path

---

## 📝 License

MIT — Free for educational and commercial use.

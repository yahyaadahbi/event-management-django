"""
Seed script to populate the database with sample data.
Run with: python manage.py shell < seed_data.py
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')

from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from events.models import Category, Event, TicketType

# ── Categories ──────────────────────────────────────────────────────────────
categories_data = [
    ('Technology', '#6366f1', 'bi-cpu'),
    ('Music', '#ec4899', 'bi-music-note-beamed'),
    ('Business', '#f59e0b', 'bi-briefcase'),
    ('Arts', '#8b5cf6', 'bi-palette'),
    ('Sports', '#10b981', 'bi-trophy'),
    ('Food & Drink', '#ef4444', 'bi-cup-hot'),
    ('Education', '#3b82f6', 'bi-book'),
    ('Health', '#14b8a6', 'bi-heart-pulse'),
]

cats = {}
for name, color, icon in categories_data:
    cat, _ = Category.objects.get_or_create(name=name, defaults={'color': color, 'icon': icon})
    cats[name] = cat
    print(f'Category: {name}')

# ── Organizer ──────────────────────────────────────────────────────────────
organizer, _ = CustomUser.objects.get_or_create(
    username='organizer1',
    defaults={
        'email': 'organizer@example.com',
        'role': 'organizer',
        'first_name': 'hiba',
        'last_name': 'korimy',
    }
)
organizer.set_password('demo1234')
organizer.save()
print(f'Organizer: {organizer.username}')

# ── Participant ────────────────────────────────────────────────────────────
participant, _ = CustomUser.objects.get_or_create(
    username='participant1',
    defaults={
        'email': 'participant@example.com',
        'role': 'participant',
        'first_name': 'walid',
        'last_name': 'elakrch',
    }
)
participant.set_password('demo1234')
participant.save()
print(f'Participant: {participant.username}')

# ── Events ─────────────────────────────────────────────────────────────────
now = timezone.now()
friday = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
saturday = friday + timedelta(days=1)

events_data = [
    {
        'title': 'La nuit spirituelle cherkaoui',
        'description': 'Une soiree spirituelle animee par la troupe Cherkaoui.',
        'event_date': friday.replace(hour=20, minute=0),
        'location': 'Zenith Center, Rabat',
        'capacity_max': 500,
        'price': 0,
        'status': 'full',
        'category': 'Music',
        'image': 'events/la_nuit_spirituelle_cherkaoui.jpg',
    },
    {
        'title': 'OUM en concert exceptionnel a Casablanca',
        'description': 'Concert live de OUM dans une ambiance artistique unique.',
        'event_date': friday.replace(hour=20, minute=30),
        'location': 'Megarama, Casablanca',
        'capacity_max': 400,
        'price': 250,
        'status': 'open',
        'category': 'Music',
        'image': 'events/oum_casablanca.jpg',
    },
    {
        'title': 'Soiree inaugurale FMMA 2026',
        'description': 'Ceremonie d ouverture du Festival Marocain de Musique Andalouse.',
        'event_date': friday.replace(hour=20, minute=30),
        'location': "Theatre l'Hermitage, Casablanca",
        'capacity_max': 450,
        'price': 300,
        'status': 'open',
        'category': 'Music',
        'image': 'events/fmma_inaugurale_2026.jpg',
    },
    {
        'title': 'Hanane Fadili - 30 ans de rire a Marrakech',
        'description': 'One woman show celebrant 30 ans de carriere de Hanane Fadili.',
        'event_date': friday.replace(hour=20, minute=0),
        'location': 'Meydene, Marrakech',
        'capacity_max': 350,
        'price': 200,
        'status': 'open',
        'category': 'Arts',
        'image': 'events/hanane_fadili_marrakech.jpg',
    },
    {
        'title': "SPECTACLE DE DANSE ST'ART STUDIO 2026",
        'description': 'Spectacle choregraphique contemporain presente par ST ART Studio.',
        'event_date': saturday.replace(hour=18, minute=0),
        'location': 'Theatre Mohammed V, Rabat',
        'capacity_max': 420,
        'price': 150,
        'status': 'open',
        'category': 'Arts',
        'image': 'events/start_studio_danse_2026.jpg',
    },
    {
        'title': 'Soiree du patrimoine soufi marocain authentique',
        'description': 'Hommage au patrimoine soufi marocain dans un cadre musical traditionnel.',
        'event_date': saturday.replace(hour=20, minute=0),
        'location': 'Zenith Center, Rabat',
        'capacity_max': 500,
        'price': 0,
        'status': 'full',
        'category': 'Music',
        'image': 'events/patrimoine_soufi_authentique.jpg',
    },
    {
        'title': 'Soiree de cloture du FMMA 2026',
        'description': 'Grande soiree de cloture du festival FMMA 2026.',
        'event_date': saturday.replace(hour=20, minute=30),
        'location': "Theatre l'Hermitage, Casablanca",
        'capacity_max': 450,
        'price': 300,
        'status': 'open',
        'category': 'Music',
        'image': 'events/fmma_cloture_2026.jpg',
    },
    {
        'title': 'EKO en comedie musicale - Fes',
        'description': 'Comedie musicale familiale presentee par la troupe EKO.',
        'event_date': saturday.replace(hour=20, minute=30),
        'location': 'Megarama, Fes',
        'capacity_max': 380,
        'price': 200,
        'status': 'open',
        'category': 'Arts',
        'image': 'events/eko_comedie_musicale_fes.jpg',
    },
    {
        'title': 'Deploying Secure AI Agents on GKE',
        'description': 'Session Build with AI sur le deploiement securise des agents IA sur GKE par Mohammed Sanbouli.',
        'event_date': now.replace(year=2026, month=5, day=25, hour=21, minute=0, second=0, microsecond=0),
        'location': 'EMSI Casablanca',
        'capacity_max': 250,
        'price': 0,
        'status': 'open',
        'category': 'Technology',
        'image': 'events/deploying_secure_ai_agents_gke.jpg',
    },
    {
        'title': 'Inside the Mind of Machines: Neural Networks Uncovered',
        'description': 'Session Build with AI animee par Adam Ghzaouni autour des reseaux neuronaux.',
        'event_date': now.replace(year=2026, month=5, day=20, hour=15, minute=0, second=0, microsecond=0),
        'location': 'EMSI Casablanca',
        'capacity_max': 250,
        'price': 0,
        'status': 'open',
        'category': 'Technology',
        'image': 'events/inside_mind_machines_neural_networks.jpg',
    },
    {
        'title': 'ADK Crash Course - From Beginner To Expert',
        'description': 'Crash course Build with AI sur ADK presente par Abdel Ghiouar.',
        'event_date': now.replace(year=2026, month=5, day=14, hour=17, minute=0, second=0, microsecond=0),
        'location': 'EMSI Moulay Youssef, Casablanca',
        'capacity_max': 300,
        'price': 0,
        'status': 'open',
        'category': 'Education',
        'image': 'events/adk_crash_course_beginner_expert.jpg',
    },
    {
        'title': 'From Linkedin to CV: Build and Deploy a Smart Resume Generator with GADK',
        'description': 'Session pratique avec Aya Hafri pour creer et deployer un generateur de CV intelligent avec GADK.',
        'event_date': now.replace(year=2026, month=5, day=28, hour=21, minute=0, second=0, microsecond=0),
        'location': 'EMSI Casablanca',
        'capacity_max': 220,
        'price': 0,
        'status': 'open',
        'category': 'Education',
        'image': 'events/linkedin_to_cv_gadks.jpg',
    },
    {
        'title': 'The AI Assembly Line: MLOps on Google Cloud',
        'description': 'Masterclass Build with AI sur MLOps et Google Cloud avec Walid Kassimi.',
        'event_date': now.replace(year=2026, month=5, day=22, hour=18, minute=30, second=0, microsecond=0),
        'location': 'EMSI Moulay Youssef, Casablanca',
        'capacity_max': 260,
        'price': 0,
        'status': 'open',
        'category': 'Technology',
        'image': 'events/ai_assembly_line_mlops_google_cloud.jpg',
    },
    {
        'title': 'The Ultimate DevOps Crash Course',
        'description': 'Session Build with AI animee par Haitham El Abdioui et Ali Bourak sur les fondamentaux DevOps.',
        'event_date': now.replace(year=2026, month=5, day=21, hour=15, minute=0, second=0, microsecond=0),
        'location': 'EMSI Moulay Youssef, Casablanca',
        'capacity_max': 260,
        'price': 0,
        'status': 'open',
        'category': 'Technology',
        'image': 'events/ultimate_devops_crash_course.jpg',
    },
    {
        'title': 'Journee Mondiale de la Sante',
        'description': 'Evenement de sensibilisation organise a l\'occasion de la Journee Mondiale de la Sante. Participation gratuite avec activites et conferences sur la sante et le bien-etre.',
        'event_date': now.replace(year=2027, month=4, day=7, hour=9, minute=0, second=0, microsecond=0),
        'location': 'Hassan II University Hospital, Fes',
        'capacity_max': 500,
        'price': 0,
        'status': 'open',
        'category': 'Health',
        'image': 'events/journee_mondiale_sante.jpg',
    },
    {
        'title': 'FOOD FESTIVAL',
        'description': 'Festival gastronomique avec stands de nourriture, boissons, animations et loisirs. Decouvrez les saveurs locales et internationales dans une ambiance festive au bord de la mer.',
        'event_date': now.replace(year=2026, month=4, day=11, hour=15, minute=0, second=0, microsecond=0),
        'location': 'Front de Mer, Saint-Paul',
        'capacity_max': 500,
        'price': 0,
        'status': 'open',
        'category': 'Food & Drink',
        'image': 'events/food_festival_saint_paul.jpg',
    },
]

for data in events_data:
    cat = cats.get(data.pop('category'))
    event, created = Event.objects.get_or_create(
        title=data['title'],
        defaults={**data, 'organizer': organizer, 'category': cat}
    )
    if created:
        # Add ticket types for paid events
        if event.price > 0:
            TicketType.objects.create(event=event, name='Early Bird', price=event.price * 0.7, quantity=20)
            TicketType.objects.create(event=event, name='Standard', price=event.price, quantity=int(event.capacity_max * 0.7))
            TicketType.objects.create(event=event, name='VIP', price=event.price * 2, quantity=int(event.capacity_max * 0.1))
        print(f'Created event: {event.title}')
    else:
        print(f'Skipped (exists): {event.title}')

print('\n✅ Seed complete!')
print('Demo accounts:')
print('  Organizer: organizer1 / demo1234')
print('  Participant: participant1 / demo1234')
print('  Admin: (python manage.py createsuperuser)')

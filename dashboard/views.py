"""
Dashboard views: analytics, charts, CSV/Excel export.
"""

import csv
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta

from events.models import Event, Category
from registrations.models import Registration
from accounts.models import Notification


@method_decorator(login_required, name='dispatch')
class DashboardHomeView(View):
    """Main analytics dashboard for organizers and admins."""

    def get(self, request):
        user = request.user

        if user.is_organizer or user.is_staff:
            # Organizer: show stats for their events
            if user.is_staff:
                events_qs = Event.objects.all()
                regs_qs = Registration.objects.all()
            else:
                events_qs = Event.objects.filter(organizer=user)
                regs_qs = Registration.objects.filter(event__organizer=user)

            total_events = events_qs.count()
            total_registrations = regs_qs.filter(status='confirmed').count()
            total_revenue = regs_qs.filter(status='confirmed').aggregate(
                total=Sum('event__price')
            )['total'] or 0

            # Monthly registrations (last 6 months)
            monthly_data = []
            for i in range(5, -1, -1):
                month_start = (timezone.now() - timedelta(days=30 * i)).replace(
                    day=1, hour=0, minute=0, second=0
                )
                month_end = (month_start + timedelta(days=32)).replace(day=1)
                count = regs_qs.filter(
                    status='confirmed',
                    created_at__gte=month_start,
                    created_at__lt=month_end
                ).count()
                monthly_data.append({
                    'month': month_start.strftime('%b %Y'),
                    'count': count
                })

            # Top events by registrations
            top_events = events_qs.annotate(
                reg_count=Count('registrations', filter=Q(registrations__status='confirmed'))
            ).order_by('-reg_count')[:5]

            # Events per category
            category_data = Category.objects.annotate(
                count=Count('events', filter=Q(events__organizer=user) if not user.is_staff else Q())
            ).filter(count__gt=0).values('name', 'color', 'count')

            cancelled_regs = []
            if user.is_staff:
                cancelled_regs = regs_qs.filter(status='cancelled').select_related(
                    'participant', 'event'
                ).order_by('-updated_at')[:20]

            context = {
                'total_events': total_events,
                'total_registrations': total_registrations,
                'total_revenue': total_revenue,
                'open_events': events_qs.filter(status='open').count(),
                'monthly_data_json': json.dumps(monthly_data),
                'top_events': top_events,
                'category_data_json': json.dumps(list(category_data)),
                'cancelled_regs': cancelled_regs,
                'cancelled_regs_count': regs_qs.filter(status='cancelled').count() if user.is_staff else 0,
            }
        else:
            # Participant dashboard
            regs = Registration.objects.filter(participant=user)
            recent_registrations = regs.select_related('event').order_by('-created_at')[:10]
            saved_notifications = Notification.objects.filter(
                user=user,
                message__startswith='Saved event:'
            ).order_by('-created_at')[:10]

            recent_activity = []
            for reg in recent_registrations:
                recent_activity.append({
                    'title': reg.event.title,
                    'created_at': reg.created_at,
                    'label': reg.get_status_display(),
                    'icon_bg': 'bg-success' if reg.status == 'confirmed' else 'bg-danger',
                    'link': '',
                })

            for item in saved_notifications:
                recent_activity.append({
                    'title': item.message.replace('Saved event: ', '', 1),
                    'created_at': item.created_at,
                    'label': 'Saved',
                    'icon_bg': 'bg-warning',
                    'link': item.link,
                })

            recent_activity.sort(key=lambda x: x['created_at'], reverse=True)
            context = {
                'total_registrations': regs.count(),
                'confirmed': regs.filter(status='confirmed').count(),
                'cancelled': regs.filter(status='cancelled').count(),
                'bookmarks': user.bookmarks.count(),
                'recent_activity': recent_activity[:5],
            }

        return render(request, 'dashboard/dashboard.html', context)


@method_decorator(login_required, name='dispatch')
class ExportRegistrationsCSV(View):
    """Export registrations as CSV (organizer only)."""

    def get(self, request):
        user = request.user
        if user.is_staff:
            regs = Registration.objects.all()
        elif user.is_organizer:
            regs = Registration.objects.filter(event__organizer=user)
        else:
            return redirect('home')

        regs = regs.select_related('participant', 'event', 'ticket_type')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="registrations_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Participant', 'Email', 'Event', 'Ticket Type',
                         'Status', 'Ticket Code', 'Registered At', 'Price'])

        for reg in regs:
            writer.writerow([
                reg.pk,
                reg.participant.get_full_name() or reg.participant.username,
                reg.participant.email,
                reg.event.title,
                reg.ticket_type.name if reg.ticket_type else 'General',
                reg.status,
                str(reg.ticket_code),
                reg.created_at.strftime('%Y-%m-%d %H:%M'),
                reg.get_ticket_price(),
            ])

        return response


@method_decorator(login_required, name='dispatch')
class ExportRegistrationsExcel(View):
    """Export registrations as Excel (organizer only)."""

    def get(self, request):
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter

        user = request.user
        if user.is_staff:
            regs = Registration.objects.all()
        elif user.is_organizer:
            regs = Registration.objects.filter(event__organizer=user)
        else:
            return redirect('home')

        regs = regs.select_related('participant', 'event', 'ticket_type')

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Registrations'

        # Header styling
        header_fill = PatternFill(start_color='6366F1', end_color='6366F1', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF', size=11)

        headers = ['ID', 'Participant', 'Email', 'Event', 'Ticket Type',
                   'Status', 'Ticket Code', 'Registered At', 'Price']

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')

        # Data rows
        for row, reg in enumerate(regs, 2):
            ws.cell(row=row, column=1, value=reg.pk)
            ws.cell(row=row, column=2, value=reg.participant.get_full_name() or reg.participant.username)
            ws.cell(row=row, column=3, value=reg.participant.email)
            ws.cell(row=row, column=4, value=reg.event.title)
            ws.cell(row=row, column=5, value=reg.ticket_type.name if reg.ticket_type else 'General')
            ws.cell(row=row, column=6, value=reg.status)
            ws.cell(row=row, column=7, value=str(reg.ticket_code))
            ws.cell(row=row, column=8, value=reg.created_at.strftime('%Y-%m-%d %H:%M'))
            ws.cell(row=row, column=9, value=float(reg.get_ticket_price()))

        # Auto-size columns
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].auto_size = True

        from io import BytesIO
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="registrations_export.xlsx"'
        return response


@method_decorator(login_required, name='dispatch')
class ChartDataView(View):
    """JSON endpoint for Chart.js data."""

    def get(self, request):
        chart_type = request.GET.get('type', 'monthly')
        user = request.user

        if user.is_staff:
            regs_qs = Registration.objects.filter(status='confirmed')
        else:
            regs_qs = Registration.objects.filter(event__organizer=user, status='confirmed')

        if chart_type == 'monthly':
            data = []
            for i in range(5, -1, -1):
                start = (timezone.now() - timedelta(days=30 * i)).replace(
                    day=1, hour=0, minute=0, second=0
                )
                end = (start + timedelta(days=32)).replace(day=1)
                data.append({
                    'label': start.strftime('%b'),
                    'value': regs_qs.filter(created_at__gte=start, created_at__lt=end).count()
                })
            return JsonResponse({'data': data})

        elif chart_type == 'category':
            data = list(
                Category.objects.annotate(count=Count('events__registrations')).values('name', 'color', 'count')
            )
            return JsonResponse({'data': data})

        return JsonResponse({'error': 'Unknown chart type'}, status=400)

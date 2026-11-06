"""
Context processors for global template context.
"""


def notifications_processor(request):
    """Inject unread notification count into all templates."""
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(read=False).count()
        notifications = request.user.notifications.filter(read=False)[:5]
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': notifications,
        }
    return {}

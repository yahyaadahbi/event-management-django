from .models import Category

def categories_processor(request):
    # Avoid running in admin (important fix)
    if request.path.startswith('/admin/'):
        return {}

    return {
        'all_categories': Category.objects.all()
    }
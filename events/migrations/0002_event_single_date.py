from django.db import migrations, models
from django.utils import timezone


def copy_start_to_event_date(apps, schema_editor):
    Event = apps.get_model('events', 'Event')
    for event in Event.objects.all().iterator():
        event.event_date = event.start_date or timezone.now()
        event.save(update_fields=['event_date'])


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.RunPython(copy_start_to_event_date, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='event',
            name='event_date',
            field=models.DateTimeField(),
        ),
        migrations.RemoveField(
            model_name='event',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='event',
            name='end_date',
        ),
    ]

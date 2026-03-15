from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtask',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, related_name='children', to='tasks.subtask'),
        ),
        migrations.AddIndex(
            model_name='subtask',
            index=models.Index(fields=['task', 'parent', 'sort_order'], name='tasks_subta_task_id_5250d2_idx'),
        ),
    ]
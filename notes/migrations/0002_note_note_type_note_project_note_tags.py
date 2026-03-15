from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
        ('tasks', '0001_initial'),
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='note_type',
            field=models.CharField(choices=[('note', 'Note'), ('documentation', 'Documentation'), ('plan', 'Plan')], default='note', max_length=20),
        ),
        migrations.AddField(
            model_name='note',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, related_name='notes', to='projects.project'),
        ),
        migrations.AddField(
            model_name='note',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='notes', to='tasks.tag'),
        ),
        migrations.AddIndex(
            model_name='note',
            index=models.Index(fields=['project', 'note_type'], name='notes_note_project_2088fe_idx'),
        ),
    ]
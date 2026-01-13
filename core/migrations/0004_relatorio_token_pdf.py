                                               

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_relatorio_tipo_discurso'),
    ]

    operations = [
        migrations.AddField(
            model_name='relatorio',
            name='token_pdf',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]

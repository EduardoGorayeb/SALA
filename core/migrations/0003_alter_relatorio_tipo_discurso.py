                                               

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_relatorio_tipo_discurso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relatorio',
            name='tipo_discurso',
            field=models.CharField(choices=[('tcc', 'TCC / Defesa acadêmica'), ('palestra_tecnica', 'Palestra técnica'), ('palestra_motivacional', 'Palestra motivacional'), ('pitch_comercial', 'Pitch comercial'), ('pitch_startup', 'Pitch startup'), ('videoaula', 'Videoaula'), ('explicacao_escolar', 'Explicação escolar'), ('apresentacao_comercial_detalhada', 'Apresentação comercial detalhada'), ('livre', 'Livre')], default='livre', max_length=50),
        ),
    ]

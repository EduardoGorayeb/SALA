                                               

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='relatorio',
            name='tipo_discurso',
            field=models.CharField(choices=[('tcc', 'Trabalho de Conclusão de Curso'), ('palestra', 'Palestra'), ('explicativo', 'Explicativo / Didático'), ('comercial', 'Apresentação Comercial')], default='tcc', max_length=50),
        ),
    ]

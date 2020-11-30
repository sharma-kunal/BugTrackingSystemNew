# Generated by Django 3.1.2 on 2020-11-30 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20201126_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tickets',
            name='status',
            field=models.CharField(choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Additional Info Required', 'Additional Info Required'), ('Closed', 'Closed')], max_length=50),
        ),
    ]
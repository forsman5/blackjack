# Generated by Django 2.0 on 2018-05-20 17:25

from django.db import migrations, models
import game.fields


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_auto_20180520_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='id',
            field=models.BigIntegerField(default=game.fields.makeId, primary_key=True, serialize=False),
        ),
    ]

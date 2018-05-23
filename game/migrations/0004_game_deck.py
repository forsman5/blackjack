# Generated by Django 2.0 on 2018-05-21 00:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_auto_20180520_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='deck',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='deck', to='game.Hand'),
            preserve_default=False,
        ),
    ]
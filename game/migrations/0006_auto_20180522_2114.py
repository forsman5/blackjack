# Generated by Django 2.0 on 2018-05-23 01:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_game_bet'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='complete',
        ),
        migrations.AlterField(
            model_name='game',
            name='deck',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deck', to='game.Hand'),
        ),
    ]
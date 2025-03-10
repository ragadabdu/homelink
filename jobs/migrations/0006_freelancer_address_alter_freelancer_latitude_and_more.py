# Generated by Django 4.2.19 on 2025-02-21 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='freelancer',
            name='address',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='freelancer',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='freelancer',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='freelancer',
            name='profile_pic',
            field=models.ImageField(blank=True, upload_to='profiles/'),
        ),
    ]

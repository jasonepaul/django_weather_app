# Generated by Django 3.1.2 on 2020-10-29 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentWx',
            fields=[
                ('date', models.DateField(primary_key=True, serialize=False)),
                ('month_day', models.CharField(max_length=5)),
                ('min_temp', models.FloatField(blank=True, null=True)),
                ('max_temp', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WxStats',
            fields=[
                ('month_day', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('last_date', models.DateField()),
                ('stats_count', models.IntegerField()),
                ('record_min_temp', models.FloatField()),
                ('avg_min_temp', models.FloatField()),
                ('avg_max_temp', models.FloatField()),
                ('record_max_temp', models.FloatField()),
            ],
        ),
    ]
from django.db import models

# Create your models here.


class WxStats(models.Model):
    """ Model representing the temperature stats (temperatures in °C)"""
    month_day = models.CharField(primary_key=True, max_length=5, null=False, blank=False)
    last_date = models.DateField(null=False, blank=False)
    stats_count = models.IntegerField(null=False, blank=False)
    record_min_temp = models.FloatField(null=False, blank=False)
    avg_min_temp = models.FloatField(null=False, blank=False)
    avg_max_temp = models.FloatField(null=False, blank=False)
    record_max_temp = models.FloatField(null=False, blank=False)


class CurrentWx(models.Model):
    """ Model representing the recent min and max temperatures (temperatures in °C)"""
    date = models.DateField(primary_key=True, null=False, blank=False)
    month_day = models.CharField(max_length=5, null=False, blank=False)
    min_temp = models.FloatField(null=True, blank=True)
    max_temp = models.FloatField(null=True, blank=True)


class Info(models.Model):
    """ Model to store the time of last tables update date"""
    last_update = models.DateField(null=False, blank=False)

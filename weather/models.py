from django.db import models

# Create your models here.


class WxStats(models.Model):
    """ Model representing the temperature stats"""
    month_day = models.TextField(primary_key=True, max_length=5, null=False, blank=False, help_text="month and day")
    last_date = models.DateField(null=False, blank=False)
    record_min_temp = models.FloatField(null=False, blank=False)
    avg_min_temp = models.FloatField(null=False, blank=False)
    avg_max_temp = models.FloatField(null=False, blank=False)
    record_max_temp = models.FloatField(null=False, blank=False)
    stats_count = models.IntegerField(null=False, blank=False)


class CurrentWx(models.Model):
    """ Model representing the recent min and max temperatures"""
    date = models.DateField(primary_key=True, null=False, blank=False, help_text="month and day")
    min_temp = models.FloatField(null=True, blank=True)
    max_temp = models.FloatField(null=True, blank=True)
    month_day = models.ForeignKey(WxStats, null=False, blank=False)

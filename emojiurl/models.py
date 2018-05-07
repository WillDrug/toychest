# -*- coding: utf-8 -*-
import re
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
import re
from barnum import gen_data
import random
from math import ceil, floor
import time


# Create your models here.
class Link(models.Model):
    emoji = models.CharField(max_length=50, primary_key=True, unique=True)
    link = models.URLField()
    keep_alive = models.IntegerField()

    def __str__(self):
        return '<Link(' + self.emoji + ':' + self.link + ')>'

    def __unicode__(self):
        return '<Link(' + self.emoji + ':' + self.link + ')>'


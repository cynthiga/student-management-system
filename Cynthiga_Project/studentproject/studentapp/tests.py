from django.test import TestCase

# for unique to identify(modify):
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.IntegerField(unique=True)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name

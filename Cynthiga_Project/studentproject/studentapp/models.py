from django.db import models
class Student(models.Model):
    name=models.CharField(max_length=100)
    roll_no = models.IntegerField(unique=True)
    department=models.CharField(max_length=100)
    year=models.IntegerField()
    total_marks = models.IntegerField(default=100)
    obtained_marks = models.IntegerField(default=0)
    
    def percentage(self):
        if self.total_marks > 0:
            return (self.obtained_marks / self.total_marks) * 100
        return 0
    # new field
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    graduation_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.name
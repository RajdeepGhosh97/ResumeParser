from django.db import models

class resumes(models.Model):
    resname = models.CharField(max_length=100)
    respdf = models.FileField(upload_to='resumes')
    

    def __str__(self):
        return self.resname


class resume_data(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=100)
    mobile = models.CharField(max_length=12)
    skills = models.CharField(max_length=500)

    def __str__(self):
        return self.name
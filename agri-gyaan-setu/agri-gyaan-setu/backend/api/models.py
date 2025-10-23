from django.db import models

# Existing Post model (you can keep this if it's being used elsewhere)
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title

# Farmer model to store farmer details
class Farmer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Crop model to define crop and required soil/environmental parameters
class Crop(models.Model):
    name = models.CharField(max_length=100)
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    ph = models.FloatField()
    rainfall = models.FloatField()

    def __str__(self):
        return self.name

# Recommendation model to relate farmers with recommended crops
class Recommendation(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    recommended_crop = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmer.name} - {self.recommended_crop}"

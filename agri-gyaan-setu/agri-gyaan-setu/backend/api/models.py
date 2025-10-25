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
    # store hashed password
    password = models.CharField(max_length=128, blank=True)

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


# ImportantDate model: per-farmer or global events like sowing/harvest
class ImportantDate(models.Model):
    EVENT_TYPES = [
        ('sowing', 'Sowing'),
        ('harvest', 'Harvest'),
        ('other', 'Other'),
    ]

    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, null=True, blank=True,
                               help_text='If blank, this event is global')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text='Optional end date for a window')
    notes = models.TextField(blank=True)
    # Optional recurrence rule (RFC RRULE or a simple text) to support recurring events
    recurrence = models.CharField(max_length=512, blank=True, help_text='Optional recurrence rule (RRULE)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        who = self.farmer.name if self.farmer else 'Global'
        crop_name = self.crop.name if self.crop else 'Any crop'
        return f"{who} - {crop_name} - {self.event_type} on {self.date}"

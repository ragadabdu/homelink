from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

import requests

class Freelancer(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to="profiles/", blank=True)
    name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)  # Add this line
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.id} | {self.name}"

    def save(self, *args, **kwargs):
        # Geocode the address if it's provided and latitude/longitude are not set
        if self.address and (not self.latitude or not self.longitude):
            self.geocode_address()
        super().save(*args, **kwargs)

    def geocode_address(self):
        """
        Use OpenStreetMap Nominatim API to convert the address into latitude and longitude.
        """
        try:
            # Nominatim API endpoint
            url = f"https://nominatim.openstreetmap.org/search?q={self.address}&format=json"
            response = requests.get(url)
            data = response.json()

            if data:
                # Use the first result (most relevant)
                self.latitude = float(data[0]['lat'])
                self.longitude = float(data[0]['lon'])
            else:
                print(f"No results found for address: {self.address}")
        except Exception as e:
            print(f"Error geocoding address: {e}")

class Business(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to="'profiles/", blank=True)
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.id} | {self.name}"
    
from django.db import models

class WorkerCategory(models.Model):
    name = models.CharField(max_length=100)
    demand_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

from django.conf import settings
from django.db import models

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.amount} - {self.status}"



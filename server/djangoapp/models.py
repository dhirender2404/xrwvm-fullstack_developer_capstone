from django.db import models

# CarMake model
class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)  # optional

    def __str__(self):
        return self.name


# CarModel model
class CarModel(models.Model):
    SEDAN = 'Sedan'
    SUV = 'SUV'
    WAGON = 'Wagon'
    CAR_TYPE_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
    ]

    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name='models')
    dealer_id = models.IntegerField()
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=CAR_TYPE_CHOICES)
    year = models.IntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.car_make.name} - {self.name} ({self.year})"

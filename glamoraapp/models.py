from django.db import models

class AdminTable(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=100)

class UserRegister(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=50)
    is_blocked = models.BooleanField(default=False)
   

class BeautyService(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add default
    duration = models.PositiveIntegerField(default=60)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Appointment(models.Model):
    user = models.ForeignKey(UserRegister, on_delete=models.CASCADE)
    service = models.ForeignKey(BeautyService, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, default="Pending")
class Booking(models.Model):
    user = models.ForeignKey(UserRegister, on_delete=models.CASCADE)
    service = models.ForeignKey(BeautyService, on_delete=models.CASCADE)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')  # pending → confirmed after payment

    def __str__(self):
        return f"{self.user.name} - {self.service.name} - {self.booking_date}"
from .models import UserRegister

class Feedback(models.Model):
    user = models.ForeignKey(UserRegister, on_delete=models.CASCADE)
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    rating = models.IntegerField(choices=[(1,'1★'),(2,'2★'),(3,'3★'),(4,'4★'),(5,'5★')], blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.message[:20]}"
    
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('service', 'New Service'),
        ('offer', 'Special Offer'),
        ('booking', 'Booking Update'),
        ('general', 'General'),
    )
    
    user = models.ForeignKey(UserRegister, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
    title = models.CharField(max_length=200, default='Notification')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.name}: {self.title}"
    
    def mark_as_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
class Payment(models.Model):
    PAYMENT_CHOICES = (
        ('COD', 'Cash On Delivery'),
        ('CARD', 'Card Payment'),
        ('UPI', 'UPI Payment'),
    )

    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='completed')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking #{self.booking.id}"
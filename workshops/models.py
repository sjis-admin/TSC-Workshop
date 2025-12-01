from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
import uuid
from datetime import datetime


class Workshop(models.Model):
    """Model for workshop details"""
    
    name = models.CharField(max_length=200, help_text="Workshop name")
    description = models.TextField(help_text="Workshop description")
    workshop_date = models.CharField(max_length=200, help_text="Workshop date(s)")
    venue = models.CharField(max_length=200, help_text="Workshop venue")
    time = models.CharField(max_length=100, help_text="Workshop time")
    duration = models.CharField(max_length=100, help_text="Workshop duration")
    fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Workshop fee in BDT (0 for free workshops)"
    )
    capacity = models.PositiveIntegerField(
        default=100,
        help_text="Maximum number of participants"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether workshop is accepting registrations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields for organizers/trainers
    organizer = models.CharField(max_length=200, blank=True, help_text="Workshop organizer/trainer")
    
    class Meta:
        ordering = ['workshop_date', 'name']
        verbose_name = "Workshop"
        verbose_name_plural = "Workshops"
    
    def __str__(self):
        return f"{self.name} - {self.workshop_date}"
    
    @property
    def is_free(self):
        """Check if workshop is free"""
        return self.fee == 0
    
    @property
    def current_registrations(self):
        """Get current number of confirmed registrations"""
        return self.registrations.filter(
            models.Q(payment_status='completed') | 
            models.Q(payment_status='free', workshop__fee=0)
        ).count()
    
    @property
    def is_full(self):
        """Check if workshop is at capacity"""
        return self.current_registrations >= self.capacity
    
    @property
    def available_slots(self):
        """Get number of available slots"""
        return max(0, self.capacity - self.current_registrations)



class School(models.Model):
    """Model for schools"""
    name = models.CharField(max_length=200, unique=True, help_text="School name")
    is_active = models.BooleanField(default=True, help_text="Whether school is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "School"
        verbose_name_plural = "Schools"

    def __str__(self):
        return self.name


class Registration(models.Model):
    """Model for student registrations"""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('free', 'Free Workshop'),
    ]

    GRADE_CHOICES = [(i, str(i)) for i in range(2, 13)]
    
    # Unique registration number
    registration_number = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False,
        help_text="Auto-generated registration number"
    )
    
    # Workshop reference
    workshop = models.ForeignKey(
        Workshop, 
        on_delete=models.PROTECT,
        related_name='registrations',
        help_text="Workshop to register for"
    )
    
    # Student Information
    student_name = models.CharField(max_length=200, help_text="Full name of the student")
    grade = models.IntegerField(
        choices=GRADE_CHOICES,
        validators=[MinValueValidator(2), MaxValueValidator(12)],
        help_text="Grade (2-12)"
    )
    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        related_name='registrations',
        help_text="School of the student",
        null=True, # Allow null temporarily for migration
        blank=True
    )
    school_name = models.CharField(max_length=200, help_text="Name of the school", blank=True) # Keep for migration
    contact_number = models.CharField(max_length=20, help_text="Contact number")
    email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Email address"
    )
    
    # Payment Status
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        help_text="Payment status"
    )
    
    # Timestamps
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-registered_at']
        verbose_name = "Registration"
        verbose_name_plural = "Registrations"
        unique_together = ['email', 'workshop']  # Prevent duplicate registrations
    
    def __str__(self):
        return f"{self.registration_number} - {self.student_name}"
    
    def save(self, *args, **kwargs):
        """Override save to generate registration number"""
        if not self.registration_number:
            # Generate registration number: REG-YYYYMMDD-XXXXX
            date_str = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4().hex[:5]).upper()
            self.registration_number = f"REG-{date_str}-{unique_id}"
        
        # If workshop is free, set payment status to 'free'
        if self.workshop.is_free:
            self.payment_status = 'free'
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate registration"""
        super().clean()
        
        # Check if workshop is active
        if not self.workshop.is_active:
            raise ValidationError("This workshop is not accepting registrations.")
        
        # Check if workshop is full
        if self.workshop.is_full and not self.pk:  # Only for new registrations
            raise ValidationError("This workshop is already full.")
        
        # Validate grade
        if self.grade < 2 or self.grade > 12:
            raise ValidationError("Grade must be between 2 and 12.")


class Payment(models.Model):
    """Model for payment transactions"""
    
    PAYMENT_METHOD_CHOICES = [
        ('sslcommerz', 'SSLCommerz'),
        ('free', 'Free'),
    ]
    
    # One-to-one relationship with registration
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='payment',
        help_text="Related registration"
    )
    
    # Transaction details
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="SSLCommerz transaction ID"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Payment amount"
    )
    currency = models.CharField(max_length=3, default='BDT')
    
    # Payment status
    payment_status = models.CharField(max_length=50, default='pending')
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='sslcommerz'
    )
    
    # SSLCommerz response data (stored as JSON)
    sslcommerz_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Complete SSLCommerz response data"
    )
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-initiated_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount} {self.currency}"
    
    def mark_completed(self):
        """Mark payment as completed"""
        self.payment_status = 'completed'
        self.completed_at = datetime.now()
        self.registration.payment_status = 'completed'
        self.registration.save()
        self.save()
    
    def mark_failed(self):
        """Mark payment as failed"""
        self.payment_status = 'failed'
        self.registration.payment_status = 'failed'
        self.registration.save()
        self.save()

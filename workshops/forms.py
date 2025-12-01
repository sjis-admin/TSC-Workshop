from django import forms
from django.core.validators import RegexValidator
from .models import Registration, Workshop, School


class RegistrationForm(forms.ModelForm):
    """Form for workshop registration"""
    
    # Phone number validator for Bangladesh
    phone_regex = RegexValidator(
        regex=r'^(\+8801|01)[3-9]\d{8}$',
        message="Phone number must be a valid Bangladesh number (e.g., 01712345678 or +8801712345678)"
    )
    
    contact_number = forms.CharField(
        validators=[phone_regex],
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '01712345678',
            'pattern': r'(\+8801|01)[3-9]\d{8}',
        })
    )
    
    student_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter full name',
        })
    )
    
    grade = forms.ChoiceField(
        choices=Registration.GRADE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        empty_label="Select your school"
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
        })
    )
    
    # Terms and conditions agreement
    terms_agreed = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label="I agree to the terms and conditions"
    )
    
    class Meta:
        model = Registration
        fields = ['student_name', 'grade', 'school', 'contact_number', 'email']
    
    def __init__(self, *args, **kwargs):
        self.workshop = kwargs.pop('workshop', None)
        super().__init__(*args, **kwargs)
        if self.workshop:
            self.instance.workshop = self.workshop
    
    def clean_grade(self):
        """Validate grade is between 2 and 12"""
        grade = self.cleaned_data.get('grade')
        if grade:
            try:
                grade = int(grade) # Convert to integer
            except ValueError:
                raise forms.ValidationError("Invalid grade value.")
            
            if grade < 2 or grade > 12:
                raise forms.ValidationError("Grade must be between 2 and 12.")
        return grade
    
    def clean_email(self):
        """Check for duplicate registration with same email for this workshop"""
        email = self.cleaned_data.get('email')
        
        if self.workshop and email:
            # Check if this email is already registered for this workshop
            existing = Registration.objects.filter(
                email=email,
                workshop=self.workshop
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise forms.ValidationError(
                    "This email is already registered for this workshop. "
                    "Please use a different email or contact support."
                )
        
        return email
    
    def clean(self):
        """Additional form-level validation"""
        cleaned_data = super().clean()
        
        # Check if workshop is available
        if self.workshop:
            if not self.workshop.is_active:
                raise forms.ValidationError("This workshop is not accepting registrations.")
            
            if self.workshop.is_full:
                raise forms.ValidationError(
                    f"This workshop is full. Only {self.workshop.capacity} slots were available."
                )
        
        return cleaned_data

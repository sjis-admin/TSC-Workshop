// Main JavaScript for Titanium Science Club Workshop Registration

document.addEventListener('DOMContentLoaded', function() {
    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });
    
    // Card hover effects enhancement
    const cards = document.querySelectorAll('.workshop-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });
    
    // Smooth scroll for navigation
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Field validation function
function validateField(field) {
    const value = field.value.trim();
    const fieldType = field.type;
    let isValid = true;
    
    // Remove previous error states
    field.classList.remove('is-invalid');
    const errorElement = field.parentElement.querySelector('.form-error');
    if (errorElement) {
        errorElement.remove();
    }
    
    // Check if required field is empty
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        showError(field, 'This field is required');
    }
    
    // Email validation
    if (fieldType === 'email' && value) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(value)) {
            isValid = false;
            showError(field, 'Please enter a valid email address');
        }
    }
    
    // Phone number validation (Bangladesh)
    if (field.name === 'contact_number' && value) {
        const phonePattern = /^(\+8801|01)[3-9]\d{8}$/;
        if (!phonePattern.test(value)) {
            isValid = false;
            showError(field, 'Please enter a valid Bangladesh phone number');
        }
    }
    
    // Grade validation
    if (field.name === 'grade' && value) {
        const grade = parseInt(value);
        if (grade < 2 || grade > 12) {
            isValid = false;
            showError(field, 'Grade must be between 2 and 12');
        }
    }
    
    return isValid;
}

// Show error message
function showError(field, message) {
    field.classList.add('is-invalid');
    field.style.borderColor = 'var(--error-500)';
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.textContent = message;
    field.parentElement.appendChild(errorDiv);
}

// Loading spinner for form submissions
function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    button.disabled = true;
    
    return function() {
        button.innerHTML = originalText;
        button.disabled = false;
    };
}

// Confirm before leaving page with unsaved form data
let formModified = false;

document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                formModified = true;
            });
        });
        
        form.addEventListener('submit', function() {
            formModified = false;
        });
    });
});

window.addEventListener('beforeunload', function(e) {
    if (formModified) {
        e.preventDefault();
        e.returnValue = '';
    }
});

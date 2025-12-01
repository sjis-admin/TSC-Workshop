"""
SSLCommerz Payment Gateway Integration
"""

import requests
import uuid
from django.conf import settings
from django.urls import reverse
from decimal import Decimal


class SSLCommerzPayment:
    """Handler for SSLCommerz payment gateway"""
    
    def __init__(self):
        self.store_id = settings.SSLCOMMERZ_STORE_ID
        self.store_password = settings.SSLCOMMERZ_STORE_PASSWORD
        self.api_url = settings.SSLCOMMERZ_API_URL
        self.validation_url = settings.SSLCOMMERZ_VALIDATION_URL
        self.is_sandbox = settings.SSLCOMMERZ_IS_SANDBOX
    
    def initiate_payment(self, registration, request):
        """
        Initiate payment session with SSLCommerz
        
        Args:
            registration: Registration object
            request: Django request object for building absolute URLs
            
        Returns:
            dict: Response from SSLCommerz API with GatewayPageURL
        """
        
        # Generate unique transaction ID
        tran_id = f"TXN-{registration.registration_number}-{uuid.uuid4().hex[:8].upper()}"
        
        # Build absolute URLs for callbacks
        success_url = request.build_absolute_uri(reverse('payment_success'))
        fail_url = request.build_absolute_uri(reverse('payment_fail'))
        cancel_url = request.build_absolute_uri(reverse('payment_cancel'))
        
        # Prepare payment data
        payment_data = {
            # Store Information
            'store_id': self.store_id,
            'store_passwd': self.store_password,
            
            # Transaction Information
            'total_amount': str(registration.workshop.fee),
            'currency': settings.CURRENCY,
            'tran_id': tran_id,
            
            # Payment Success/Fail/Cancel URLs
            'success_url': success_url,
            'fail_url': fail_url,
            'cancel_url': cancel_url,
            
            # Customer Information
            'cus_name': registration.student_name,
            'cus_email': registration.email,
            'cus_add1': registration.school_name,
            'cus_city': 'Dhaka',
            'cus_country': 'Bangladesh',
            'cus_phone': registration.contact_number,
            
            # Product Information
            'product_name': registration.workshop.name,
            'product_category': 'Workshop Registration',
            'product_profile': 'general',
            
            # Shipping Information (required but not used)
            'shipping_method': 'NO',
            'num_of_item': 1,
            
            # Additional Information
            'value_a': registration.registration_number,  # Store registration number
            'value_b': registration.workshop.id,  # Store workshop ID
        }
        
        try:
            # Make API request to SSLCommerz
            response = requests.post(
                self.api_url,
                data=payment_data,
                timeout=30
            )
            
            response_data = response.json()
            print(f"SSLCommerz Response: {response_data}")  # Debug logging
            
            # Check if payment initiation was successful
            if response_data.get('status') == 'SUCCESS':
                return {
                    'success': True,
                    'gateway_url': response_data.get('GatewayPageURL'),
                    'transaction_id': tran_id,
                    'response_data': response_data
                }
            else:
                error_reason = response_data.get('failedreason', 'Payment initiation failed')
                print(f"SSLCommerz Error: {error_reason}")  # Debug logging
                return {
                    'success': False,
                    'error': error_reason,
                    'response_data': response_data
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Connection error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def validate_payment(self, val_id, transaction_id):
        """
        Validate payment with SSLCommerz
        
        Args:
            val_id: Validation ID from SSLCommerz
            transaction_id: Transaction ID
            
        Returns:
            dict: Validation response
        """
        
        validation_data = {
            'val_id': val_id,
            'store_id': self.store_id,
            'store_passwd': self.store_password,
        }
        
        try:
            response = requests.get(
                self.validation_url,
                params=validation_data,
                timeout=30
            )
            
            validation_response = response.json()
            
            # Check if validation was successful
            if validation_response.get('status') == 'VALID' or \
               validation_response.get('status') == 'VALIDATED':
                return {
                    'success': True,
                    'transaction_id': validation_response.get('tran_id'),
                    'amount': validation_response.get('amount'),
                    'currency': validation_response.get('currency_type'),
                    'card_type': validation_response.get('card_type'),
                    'response_data': validation_response
                }
            else:
                return {
                    'success': False,
                    'error': 'Payment validation failed',
                    'response_data': validation_response
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Connection error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def verify_payment_amount(self, received_amount, expected_amount):
        """
        Verify that the received payment amount matches expected amount
        
        Args:
            received_amount: Amount received from SSLCommerz
            expected_amount: Expected amount from workshop
            
        Returns:
            bool: True if amounts match
        """
        try:
            received = Decimal(str(received_amount))
            expected = Decimal(str(expected_amount))
            return received == expected
        except:
            return False

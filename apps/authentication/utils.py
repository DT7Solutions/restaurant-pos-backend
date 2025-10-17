import random
from django.core.mail import send_mail
import requests
import json
from core import settings

def generate_otp(length=6):
    """
    Generates a random OTP of the specified length. Default is 6 digits.
    """
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp

def send_otp_email(user_email, otp_code):
    """
    Sends an OTP email to the user.
    """
    subject = "Your OTP Code"
    message = f"Your OTP code is {otp_code}"
    from_email = "gsa32476@gmail.com"  
    recipient_list = [user_email]

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )


def send_mobial_otp(mobile, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        
        "route" : "otp",
        "variables_values" : "123456",
        "numbers" : "9985462090",
        # "route": "otp",
        # "variables_values": otp,
        # "numbers":mobile
    }

    headers = {
        
       "authorization":"LOZC9VFJiSaMe2DGE4uzkXngTqv07d1xwjh5BW3Uo86RysAtQNIw4OVfF57D6rySmh12sRLqYWdcl0ni",
        # "authorization": settings.FAST2SMS_API_KEY, 
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print(response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return str(e)
    
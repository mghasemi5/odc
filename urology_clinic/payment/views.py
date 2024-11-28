import requests  # For sending HTTP requests to Zarinpal
from django.conf import settings  # To access settings like ZARINPAL_MERCHANT_ID
from django.shortcuts import render, redirect  # For rendering templates and redirections
from .models import Payment  # Import the Payment model to track transactions



# Create your views here.
def start_payment(request):
    if request.method == "POST":
        amount = int(request.POST['amount'])  # Amount in Rials
        description = "Appointment Payment"  # Payment description
        callback_url = settings.ZARINPAL_CALLBACK_URL
        metadata = {"mobile": request.POST.get('mobile', ""), "email": request.POST.get('email', "")}

        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": amount,
            "callback_url": callback_url,
            "description": description,
            "metadata": metadata,
        }

        # Send request to Zarinpal
        response = requests.post(f"{settings.ZARINPAL_API_BASE}/payment/request.json", json=data)

        if response.status_code == 200 and response.json().get('data', {}).get('code') == 100:
            authority = response.json()['data']['authority']

            # Save payment record
            Payment.objects.create(authority=authority, amount=amount)

            # Redirect to Zarinpal payment gateway
            return redirect(f"{settings.ZARINPAL_START_PAY}/{authority}")

        else:
            return render(request, "payment_failed.html", {"message": "Failed to initiate payment."})

    return render(request, "start_payment.html")

def verify_payment(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')

    try:
        payment = Payment.objects.get(authority=authority)

        if status == "OK":
            data = {
                "merchant_id": settings.ZARINPAL_MERCHANT_ID,
                "amount": payment.amount,
                "authority": authority,
            }

            response = requests.post(f"{settings.ZARINPAL_API_BASE}/payment/verify.json", json=data)

            if response.status_code == 200:
                res_data = response.json().get('data', {})
                if res_data.get('code') == 100:
                    payment.status = "success"
                    payment.ref_id = res_data.get('ref_id')
                    payment.save()

                    return render(request, "payment_success.html", {"ref_id": payment.ref_id})

        payment.status = "failed"
        payment.save()
        return render(request, "payment_failed.html", {"message": "Payment failed or canceled."})

    except Payment.DoesNotExist:
        return render(request, "payment_failed.html", {"message": "Invalid payment authority."})


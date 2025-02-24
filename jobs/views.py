from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from config import settings

from .models import Freelancer, Business

from django.db.models import Q
from .models import Freelancer, WorkerCategory

import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect

import uuid
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from .models import Payment


class FreelancerListView(ListView):
    model = Freelancer

class FreelancerDetailView(LoginRequiredMixin, DetailView):
    model = Freelancer

class FreelancerCreateView(LoginRequiredMixin, CreateView):
    model = Freelancer
    fields = ['name', 'profile_pic', 'tagline', 'bio']
    success_url = reverse_lazy('freelancer-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(FreelancerCreateView, self).form_valid(form)

class BusinessCreateView(LoginRequiredMixin, CreateView):
    model = Business
    fields = ['name', 'profile_pic', 'bio']
    success_url = reverse_lazy('freelancer-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(BusinessCreateView, self).form_valid(form)

@login_required
def handle_login(request):
    # if the user has a freelance/biz acct -> take them to home
    print(request.user)
    print(request.user.get_freelancer())
    if request.user.get_freelancer() or request.user.get_business():
        return redirect(reverse_lazy('freelancer-list'))

    return render(request, 'jobs/choose_account.html', {})

def FreelancerFilterView(request):
    keywords = request.GET.get('keywords', '')
    freelancers = Freelancer.objects.all()

    if keywords:
        # Filter freelancers based on keywords
        freelancers = freelancers.filter(
            Q(tagline__icontains=keywords) | Q(bio__icontains=keywords)
        )

        # Track demand by category
        try:
            category = WorkerCategory.objects.get(name__icontains=keywords)
            category.demand_count += 1
            category.save()
        except WorkerCategory.DoesNotExist:
            # Optional: Handle the case where the keyword doesn't match any category
            pass

    return render(request, 'jobs/freelancer_list.html', {'object_list': freelancers})

def freelancer_detail(request, pk):
    error_message = None
    success_message = None

    if request.method == 'POST':
        amount = request.POST.get('amount')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Validate form data
        if not amount or not email or not first_name or not last_name:
            error_message = "All fields are required."
        elif not email.strip() or '@' not in email:
            error_message = "Please enter a valid email address."
        elif not amount.isdigit() or float(amount) <= 0:
            error_message = "Please enter a valid positive amount."
        else:
            headers = {
                'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
                'Content-Type': 'application/json',
            }

            data = {
                'amount': amount,
                'currency': 'ETB',
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'tx_ref': str(uuid.uuid4()),  # Generate a unique transaction reference
                'callback_url': 'https://mywebsite.com/chapa-webhook/',  # Replace with your actual callback URL
            }

            response = requests.post('https://api.chapa.co/v1/transaction/initialize', headers=headers, json=data)
            response_data = response.json()

            if response_data.get('status') == 'success':
                success_message = "Payment initialized successfully! Please check your email for further instructions."
            else:
                error_message = response_data.get('message', 'An error occurred. Please try again.')

    freelancer = get_object_or_404(Freelancer, pk=pk)

    return render(request, 'freelancer_detail.html', {
        'freelancer': freelancer,
        'error': error_message,
        'success': success_message
    })


# views.py
from django.http import JsonResponse
from .models import Freelancer

from django.views.decorators.csrf import csrf_exempt
import requests

import json
import requests

@csrf_exempt
def freelancer_map(request):
    if request.method == 'POST':
        try:
            # Parse the request data
            data = json.loads(request.body)
            address = data.get('address')
            service = data.get('service')

            # Geocode the address using Nominatim API
            geocode_url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json"
            response = requests.get(geocode_url)
            geocode_data = response.json()

            if not geocode_data:
                return JsonResponse({'status': 'error', 'message': 'Address not found'}, status=400)

            # Get the first result (most relevant)
            latitude = float(geocode_data[0]['lat'])
            longitude = float(geocode_data[0]['lon'])

            # Save the freelancer profile (replace with your actual model logic)
            freelancer = Freelancer.objects.create(
                address=address,
                service=service,
                latitude=latitude,
                longitude=longitude
            )

            return JsonResponse({'status': 'success', 'message': 'Profile saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



logger = logging.getLogger(__name__)

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user
            amount = data.get('amount')
            transaction_id = data.get('transaction_id')
            status = data.get('status')

            logger.info(f"Payment data received: {data}")

            Payment.objects.create(user=user, amount=amount, transaction_id=transaction_id, status=status)

            return redirect('payment_success')  # Replace 'payment_success' with your success page URL
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return redirect('payment_error')  # Replace 'payment_error' with your error page URL
    return redirect('payment_error')  # Replace 'payment_error' with your error page URL



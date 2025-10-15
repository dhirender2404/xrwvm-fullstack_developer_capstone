from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import logging
import json
import random
from datetime import datetime

from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review
from .populate import initiate  # optional

logger = logging.getLogger(__name__)

# -------------------- LOGIN --------------------
@csrf_exempt
def login_user(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get('userName')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
        else:
            return JsonResponse({"userName": username, "status": "Failed"})
    return JsonResponse({"error": "Invalid request method"}, status=400)


# -------------------- LOGOUT --------------------
@csrf_exempt
def logout_request(request):
    if request.method == "GET":
        logout(request)
        return JsonResponse({"userName": ""})
    return JsonResponse({"error": "Invalid request method"}, status=400)


# -------------------- REGISTRATION --------------------
@csrf_exempt
def registration(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get('userName')
        password = data.get('password')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')

        if User.objects.filter(username=username).exists():
            return JsonResponse({"userName": username, "error": "Already Registered"})

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})

    return JsonResponse({"error": "Invalid request method"}, status=400)


# -------------------- GET CARS --------------------
def get_cars(request):
    if CarMake.objects.count() == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = [{"CarModel": cm.name, "CarMake": cm.car_make.name} for cm in car_models]
    return JsonResponse({"CarModels": cars})


# -------------------- DEALERS LIST --------------------
@csrf_exempt
def get_dealerships(request, state="All"):
    if CarMake.objects.count() == 0:
        initiate()

    dealers = [
        {"id": 1, "full_name": "Dealer One", "city": "CityA", "state": "StateX", "address": "Addr1", "zip": "12345"},
        {"id": 2, "full_name": "Dealer Two", "city": "CityB", "state": "StateY", "address": "Addr2", "zip": "67890"},
    ]

    if state != "All":
        dealers = [d for d in dealers if d['state'] == state]

    return JsonResponse({"status": 200, "dealers": dealers})


# -------------------- MOCK DATA --------------------
MOCK_REVIEWS = [
    {"review": "Great service, very professional!", "user": "Alice", "rating": 5},
    {"review": "Average experience, car delivery was late.", "user": "Bob", "rating": 3},
    {"review": "Excellent deals and friendly staff.", "user": "Charlie", "rating": 4},
    {"review": "Not satisfied, poor communication.", "user": "Dave", "rating": 2}
]

MOCK_DEALERS = [
    {"id": 1, "full_name": "Dealer One"},
    {"id": 2, "full_name": "Dealer Two"},
]


# -------------------- DEALER REVIEWS --------------------
def get_dealer_reviews(request, dealer_id):
    dealer = next((d for d in MOCK_DEALERS if d["id"] == int(dealer_id)), None)
    if not dealer:
        return JsonResponse({"status": 404, "message": "Dealer not found"})

    reviews = random.sample(MOCK_REVIEWS, k=random.randint(1, 3))
    for r in reviews:
        r["sentiment"] = "positive" if r["rating"] >= 4 else "negative"

    return JsonResponse({"status": 200, "reviews": reviews})


# -------------------- DEALER DETAILS --------------------
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    return JsonResponse({"status": 400, "message": "Bad Request"})


# -------------------- ADD REVIEW --------------------
@csrf_exempt
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 403, "message": "Unauthorized"})

    data = json.loads(request.body)
    try:
        response = post_review(data)
        return JsonResponse({"status": 200})
    except Exception as e:
        logger.error(f"Error posting review: {e}")
        return JsonResponse({"status": 401, "message": "Error in posting review"})

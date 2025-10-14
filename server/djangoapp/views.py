# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime
from .restapis import get_request, analyze_review_sentiments, post_review

from .models import CarMake, CarModel
from django.http import JsonResponse
from .populate import initiate  # optional, if using populate.py


from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
# from .populate import initiate


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
@csrf_exempt
def logout_request(request):
    if request.method == "GET":
        logout(request)  # Terminate user session
        data = {"userName": ""}  # Return empty username
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)
# ...

# Create a `registration` view to handle sign up request
# @csrf_exempt

def get_cars(request):
    count = CarMake.objects.count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = [{"CarModel": cm.name, "CarMake": cm.car_make.name} for cm in car_models]
    return JsonResponse({"CarModels": cars})



@csrf_exempt
def registration(request):
    context = {}

    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)
# ...

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    # Serve directly from your local database or fixture
    from .populate import initiate
    if CarMake.objects.count() == 0:
        initiate()

    # Here you can return mock dealers if needed
    dealers = [
        {"id": 1, "full_name": "Dealer One", "city": "CityA", "state": "StateX", "address": "Addr1", "zip": "12345"},
        {"id": 2, "full_name": "Dealer Two", "city": "CityB", "state": "StateY", "address": "Addr2", "zip": "67890"},
        # Add more if needed
    ]

    MOCK_REVIEWS = [
    {"review": "Great service, very professional!", "user": "Alice", "rating": 5},
    {"review": "Average experience, car delivery was late.", "user": "Bob", "rating": 3},
    {"review": "Excellent deals and friendly staff.", "user": "Charlie", "rating": 4},
    {"review": "Not satisfied, poor communication.", "user": "Dave", "rating": 2}
]


    if state != "All":
        dealers = [d for d in dealers if d['state'] == state]

    return JsonResponse({"status": 200, "dealers": dealers})

# ...

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    dealer = next((d for d in MOCK_DEALERS if d["id"] == int(dealer_id)), None)
    if not dealer:
        return JsonResponse({"status": 404, "message": "Dealer not found"})

    # Return 1-3 random reviews for the dealer
    reviews = random.sample(MOCK_REVIEWS, k=random.randint(1, 3))
    for r in reviews:
        # Add sentiment for demonstration
        r["sentiment"] = "positive" if r["rating"] >= 4 else "negative"
    return JsonResponse({"status": 200, "reviews": reviews})
# ...

# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})
# ...

# Create a `add_review` view to submit a review
def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})
# ...

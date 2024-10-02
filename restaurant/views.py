from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
import random
import datetime

items = [
    {"name": "Pho", "price": 12.99},
    {"name": "Cha Gio (Fried Spring Rolls)", "price": 5.99},
    {"name": "Banh Xeo (Vietnamese Pancake)", "price": 8.99},
    {"name": "Banh Mi (Sandwich)", "price": 7.99},
]



special = random.choice(items)

def main(request):
    context = {
        "restaurant_name": "Pho King",
        "location": "420 baked street",
        "hours": [
            {"day": "Monday-Friday", "time": "9 AM - 10 PM"},
            {"day": "Saturday-Sunday", "time": "11 AM - 11 PM"}
        ],
        "photos": ["main_photo.jpg", "dining_area.jpg"]
    }
    return render(request, 'restaurant/main.html', context)

def order(request):
    
    discounted_price = round(special["price"] * 0.8, 2)
    discount = {
        "name": special["name"],
        "price": discounted_price
    }
    context = {
        "items": items,
        "special": discount
    }
    return render(request, 'restaurant/order.html', context)

def confirmation(request):
    if request.method =="POST":
        name = request.POST.get("name")
        number = request.POST.get("number")
        email = request.POST.get("email")
        itemsOrdered = []
        total = 0
        
        for item in items:
            if request.POST.get(item["name"]):
                itemsOrdered.append(item["name"])
                total += item["price"]
        time = datetime.datetime.now() + datetime.timedelta(minutes=random.randint(30, 60))
        context = {
            "name": name,
            "number": number,
            "email": email,
            "total": total,
            "itemsOrdered": itemsOrdered,
            "time": time.strftime("%I:%M %p")
        }
        return render(request, 'restaurant/confirmation.html', context) 
    else:
        return HttpResponse("Error 400")

    
        
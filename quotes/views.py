from django.shortcuts import render
import random
# Create your views here.
# views.py

quotes = [
    "Don't tell me what you value. Show me your budget, and I'll tell you what you value.- Joe Biden",
    "Anyone who can throw a punch and take a punch, that’s a Biden. - Joe Biden",
    "If we do everything right, if we do it with absolute certainty, there's still a 30% chance we're going to get it wrong. - Joe Biden"
]

images = [
    "/static/joe1.png",
    "/static/joe2.png",
    "/static/joe3.png"
]

def quote(request):
    selected_quote = random.choice(quotes)
    selected_image = random.choice(images)
    
    context = {
        'quote': selected_quote,
        'image': selected_image,
        'show': True
    }
    
    return render(request, 'base.html', context)

def show_all(request):
    quotes_with_images = zip(quotes, images)
    context = {
        'quotes_with_images': quotes_with_images,
        'show': False,
    }
    return render(request, 'show_all.html', context)

def about(request):
    context = {
        'name': "Joe Biden",
        'biography': """
            Joe Biden is the 46th and current president of the United States. Prior to his presidency, he served as 
            the 47th vice president of the United States from 2009 to 2017 under President Barack Obama. Biden 
            also represented Delaware in the U.S. Senate from 1973 to 2009. He has been involved in American 
            politics for over five decades, making significant contributions to various legislations, and advocating 
            for issues such as healthcare reform, environmental protection, and economic recovery.
        """,
        'achievements': [
            "Elected as the 46th President of the United States in 2020",
            "Served as Vice President of the United States from 2009 to 2017",
            "Played a key role in passing the Affordable Care Act",
        ],
        'me' : """
            A BU Computer Science Major created this site.
            Link to About page: https://cs-people.bu.edu/longluu2/cs412/Assign1/index.html
        """,
        'show': False,
    }
    return render(request, 'about.html', context)

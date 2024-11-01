from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from .models import User
from .forms import ListingForm
from django.contrib import messages
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.shortcuts import render
from .models import Listing, Bid, Watchlist, Comment
from django.core.paginator import Paginator
from django.db.models import Max
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Max
from .models import Listing, Bid, Watchlist


from django.core.serializers import serialize
from django.http import JsonResponse
from django.core.paginator import Paginator
import json

def index(request):
    category = request.GET.get('category')
    if category:
        all_listings = Listing.objects.filter(category=category, live=True)
    else:
        all_listings = Listing.objects.filter(live=True)

    # Retrieve unique categories from the Listing model
    categories = Listing.objects.values_list('category', flat=True).distinct()
    items_per_page = 6  # Adjust this as needed
    paginator = Paginator(all_listings, items_per_page)
    page_number = request.GET.get('page')
    listings = paginator.get_page(page_number)

    # Create a dictionary to store the bid status for each listing
    user_bid_status = {}
    user_watchlist = set()  # Store listing IDs in user's watchlist

    # Retrieve the user's watchlist items if they are authenticated
    if request.user.is_authenticated:
        watchlist = Watchlist.objects.filter(user=request.user).first()
        if watchlist:
            user_watchlist = set(watchlist.listings.values_list('id', flat=True))

    # Loop through each listing to determine bid status and watchlist status
    for listing in all_listings:
        highest_bid = listing.bids.aggregate(Max('amount'))['amount__max']
        user_bid = listing.bids.filter(user=request.user).first() if request.user.is_authenticated else None

        if user_bid:
            if user_bid.amount == highest_bid:
                user_bid_status[listing.id] = "Highest Bidder"
            else:
                user_bid_status[listing.id] = "Bid Placed"
        else:
            user_bid_status[listing.id] = "No Bid"

    context = {
        'listings': listings,
        'category': category,
        'categories': categories,
        'user_bid_status': user_bid_status,
        'user_watchlist': user_watchlist,  # Pass the watchlist to the context
    }

    return render(request, 'auctions/index.html', context)




@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('auctions:index')
        else:
            return render(request, 'auctions/login.html', {'message': 'Your login is incorrect.  Try again.'})
    return render(request, 'auctions/login.html')


@csrf_exempt
def logout_view(request):
    logout(request)
    return render(request, 'auctions/index.html' )


@csrf_exempt
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create a new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })

        # Authenticate and log in the user
        login(request, user)

        # Redirect to the index page (assuming the name of the URL pattern is "index")
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")



def all_listings(request):
    # Assuming you have a model named 'Listing' that represents your listings
    listings_list = Listing.objects.all()
    paginator = Paginator(listings_list, 10) # Show 6 listings per page
    page_number = request.GET.get('page')
    page_listings = paginator.get_page(page_number)

    context = {"listings": page_listings}

    return render(request, 'auctions/index.html', context)


@login_required
def create_auction(request):

    categories = ListingForm.CATEGORIES  # Define your categories here
    if not request.user.is_authenticated:
        messages.success(request, 'You need to be logged in to view this page.')
        # return redirect('login.html')

    elif request.method == 'POST':
        form = ListingForm(request.POST)
        print(form.errors)
        if form.is_valid():

            listing = form.save(commit=False)
            listing.user = request.user  # Set the created_by field to the current user
            listing.save()

            # Redirect to your_listing.html after creating the auction
            return redirect('auctions:your_listing')
        else:
            messages.error(request, 'Your submission did not go through. Try again.')
            return render(request, 'auctions/create_auction.html', {'form': form, 'categories': categories})
    else:
        form = ListingForm()

    # Query and pass the user's listings to the template
    user_listings = Listing.objects.filter(user=request.user)
    return render(request, 'auctions/create_auction.html', {'form': form, 'categories': categories, 'listings': user_listings})



@login_required
def my_listings(request, user_id):
    # Retrieve the user's ID from the request
    user_id = request.user.id
    
    # Filter listings based on user_id
    listings = Listing.objects.filter(user_id=user_id)

    if request.method == "POST":
        # User clicked on the "Close Auction" button
        listing_id = request.POST.get('listing_id')
        if listing_id is not None:
            listing = get_object_or_404(Listing, id=listing_id)

            if listing.user == request.user:
                # Mark the listing as closed (you might want to set 'live' to False)
                listing.live = False
                listing.save()
                messages.success(request, f"Auction {listing_id} has been closed.")
            else:
                messages.error(request, "You don't have permission to close this auction.")
            
            # Redirect to the same page
            return redirect("auctions:my_listings")

    if not listings:
        no_listings_message = "You have no listings to view."
        return render(request, "auctions/my_listings.html", {"no_listings_message": no_listings_message})

    return render(request, "auctions/my_listings.html", {"listings": listings})


@login_required
def your_listing(request):
    user_listings = Listing.objects.filter(user=request.user)

    if request.method == "POST":
        # Handle POST requests for closing auctions
        auction_id_to_close = request.POST.get("auctions:close_auction")
        if auction_id_to_close:
            listing_to_close = get_object_or_404(Listing, pk=auction_id_to_close, user=request.user)
            listing_to_close.live = False
            listing_to_close.save()
            messages.success(request, "Auction closed successfully.")
            return redirect("auctions:your_listing")

    return render(request, 'auctions/your_listing.html', {'user_listings': user_listings})


def edit_listing(request, pk):
    # Get the listing object with the specified ID
    listing = get_object_or_404(Listing, id=pk)

    if request.method == 'POST':
        # create a form instance with the submitted data and the existing listing object
        form = ListingForm(request.POST, instance=listing)
        print(form.errors)
        if form.is_valid():
            # save the form data to the listing object
            form.save()
            # redirect to the listing detail page
            return redirect('auctions:your_listing', pk=listing.pk)
    else:
        # create a form instance with the existing listing object
        form = ListingForm(instance=listing)

    context = {'form': form, 'listing': listing}
    return render(request, 'auctions/edit_listing.html', context)


def delete_auction(request, pk):
    listing = get_object_or_404(Listing, id=pk)
    if request.method == 'POST':
        listing.delete()
        all_listings = Listing.objects.filter(live=True)
        return render(request, "auctions/index.html", {
        "listings": all_listings
    })

    else:
        messages.success(request, f"{listing.id}, {listing.title}")
        return render(request, 'auctions/delete_auction.html', {"listing":listing})



def auction_detail(request, pk):
    # Retrieve the listing
    listing = get_object_or_404(Listing, pk=pk)

    # Retrieve all bids related to this listing
    listing_bids = listing.bids.all().order_by('-created_at')

    # Retrieve all bids made by the current user across all listings
    user_bids = Bid.objects.filter(user=request.user).order_by('-created_at') if request.user.is_authenticated else []

    # Check if the listing is in the user's watchlist
    user_watchlist = set()
    if request.user.is_authenticated:
        watchlist = Watchlist.objects.filter(user=request.user).first()
        if watchlist:
            user_watchlist = set(watchlist.listings.values_list('id', flat=True))

    return render(request, 'auctions/auction_detail.html', {
        'listing': listing,
        'listing_bids': listing_bids,
        'user_bids': user_bids,
        'user_watchlist': user_watchlist,  # Pass the watchlist to the context
    })


@login_required
def place_bid(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.method == 'POST':
        bid_amount = request.POST.get('bid_amount')
        try:
            bid_amount = float(bid_amount)
        except ValueError:
            messages.error(request, "Please enter a valid bid amount.")
            return redirect('auctions:auction_detail', pk=listing.pk)
        
        if bid_amount <= 0:
            messages.error(request, "Bid amount must be greater than zero.")
        elif bid_amount <= listing.price:
            messages.error(request, "Your bid must be greater than the current highest bid.")
        else:
            # Update listing price
            listing.price = bid_amount
            listing.save()

            # Create a new bid instance
            Bid.objects.create(listing=listing, user=request.user, amount=bid_amount)

            messages.success(request, f"Bid placed successfully. Current highest bid: ${listing.price:.2f}")
            return redirect('auctions:auction_detail', pk=listing.pk)
    return redirect('auctions:login')





@login_required
def watchlist(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if request.method == 'POST':
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)
        if created:
            watchlist.save()

        if listing in watchlist.listings.all():
            watchlist.listings.remove(listing)
        else:
            watchlist.listings.add(listing)

        return redirect('auctions:watchlist', pk=pk)

    # Retrieve the user's watchlist
    watchlist = get_object_or_404(Watchlist, user=request.user)

    # Check if the watchlist is empty
    if not watchlist.listings.all():
        no_listings_message = "You have no watchlist items."
        return render(request, "auctions/watchlist.html", {"no_listings_message": no_listings_message})

    return render(request, 'auctions/watchlist.html', {'watchlist': watchlist})

@login_required
def remove_listing(request, id):
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    listing = get_object_or_404(Listing, pk=id)

    if request.method == 'POST':
        if listing in watchlist.listings.all():
            watchlist.listings.remove(listing)

    return render(request, 'auctions/watchlist.html', {'watchlist': watchlist})



@login_required
def watchlist_view(request):
    watchlist = Watchlist.objects.filter(user=request.user).first()

    if watchlist is None:
        no_listings_message = "You have no watchlist items."
        return render(request, 'auctions/watchlist_view.html', {'no_listings_message': no_listings_message})

    watchlist_items = watchlist.listings.all()

    return render(request, 'auctions/watchlist_view.html', {'watchlist': watchlist, 'watchlist_items': watchlist_items})

@login_required

def my_bids(request, pk):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return redirect('auctions:login')

    # Retrieve all bids placed by the user
    user_bids = Bid.objects.filter(user=request.user).select_related('listing').order_by('-created_at')

    # Check if the user has placed any bids
    if not user_bids.exists():
        no_bids_message = "You have not placed any bids yet."
        return render(request, "auctions/my_bids.html", {"no_bids_message": no_bids_message})

    # Render the template with bid history if bids exist
    return render(request, 'auctions/my_bids.html', {'user_bids': user_bids})





























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
from .models import Watchlist
from .models import Comment
from django.shortcuts import render
from .models import Listing
from django.core.paginator import Paginator


def index(request):
    category = request.GET.get('category')
    if category:
        all_listings = Listing.objects.filter(category=category, live=True)
    else:
        all_listings = Listing.objects.filter(live=True)

    # Retrieve unique categories from the Listing model
    categories = Listing.objects.values_list('category', flat=True).distinct()

    # Set the number of items per page
    items_per_page = 6  # Adjust this as needed

    paginator = Paginator(all_listings, items_per_page)
    page_number = request.GET.get('page')

    listings = paginator.get_page(page_number)



    context = {
        'listings': listings,
        'category': category,
        'categories': categories,
        
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

    categories = ListingForm.CATEGORIES # Define your categories here
    if not request.user.is_authenticated:
        messages.success(request, ('You need to be logged in to view this page.'))
        #return redirect('login.html')

    elif request.method == 'POST':
        form = ListingForm(request.POST)
        print(form.errors)
        if form.is_valid():

            listing = form.save(commit=False)
            listing.user = request.user # Set the created_by field to the current user
            listing.save()

            return render(request, 'auctions/your_listing.html', {'listing': listing})
        else:
            messages.error(request, ('Your submission did not go through. Try again.'))
            return render(request, 'auctions/create_auction.html', {'form': form, 'categories': categories})
    else:
        form = ListingForm()
        return render(request, 'auctions/create_auction.html', {'form': form, 'categories': categories})



@login_required
def my_listings(request, pk, user_id):
    listings = Listing.objects.filter(user_id=user_id, pk=pk)
    if request.method == "POST":
        # User clicked on the "Close Auction" button
        listing_id = request.POST.get("listing_id")  # Assuming there is a hidden input field in the form containing the listing ID
        listing = get_object_or_404(Listing, id=listing_id)
        listing.live = False  # Set the 'live' field to False to indicate the auction is closed
        listing.save()
        listing.delete()
        messages.success(request, f"Auction {listing_id} has been deleted from your listings.")
        return redirect("auctions:my_listings", user_id=user_id, pk=pk)
    if not listings:
        no_listings_message = "You have no listings to view."
        return render(request, "auctions/my_listings.html", {"no_listings_message": no_listings_message, "user_id": user_id, "pk": pk})

    return render(request, "auctions/my_listings.html", {"listings": listings, "user_id": user_id, "pk": pk})



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
    listing = get_object_or_404(Listing, id=pk)
    listing.title = listing.title.capitalize()

    # Assuming you have a related_name 'comments' for the ForeignKey relationship in your Comment model
    comments = listing.comments.all()

    if request.method == "POST":
        # Handle comment submission
        comment_text = request.POST.get('comment')
        Comment.objects.create(listing=listing, text=comment_text)

    return render(request, 'auctions/auction_detail.html', {'listing': listing, 'comments': comments})


@login_required
def place_bid(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.method == 'POST':
        bid_amount = request.POST['bid_amount']
        if bid_amount:
            # Convert the string input into an integer value
            bid_amount = float(bid_amount)
            # Check that the new bid is greater than the current highest bid
            if bid_amount > listing.price:
                listing.price = bid_amount
                listing.save()
                messages.success(request, f"Bid placed successfully. Current highest bid: {listing.price}")
                return redirect('auctions:auction_detail', pk=listing.pk)
            else:
                messages.error(request, "Your bid should be greater than the current highest bid.")
                return redirect('auctions:auction_detail', pk=listing.pk)
        else:
            messages.error(request, "Please enter a valid bid amount.")
            return redirect('auctions:auction_detail', pk=listing.pk)
    else:
        if not request.user.is_authenticated:
            # Set a message to be shown in the login page
            messages.error(request, "You must log in to place a bid.")
            request.session['login_required_message'] = True
            request.session.modified = True  # Mark the session as modified

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





























from multiprocessing import context
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from clubmate.models import Club, UserProfile, Rating
from django.contrib.auth import login, authenticate, logout
from clubmate.forms import UserForm, UserProfileForm
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from clubmate.forms import RatingDetailForm

from django.core.paginator import Paginator


def index(request):
    return render(request, 'clubmate/index.html')


def about(request):
    return render(request, 'clubmate/about.html')


def discover(request):
    all_clubs = Club.objects.all()
    clubs_by_rating = sorted(Club.objects.all(), key=lambda c: c.average_rating_, reverse=True)[:3]  # High to low
    safe_clubs = sorted(Club.objects.all(), key=lambda c: c.user_reported_safety_)[:3]
    cheapest_clubs = Club.objects.order_by('entry_fee')[:3]
    context = {'all_clubs': all_clubs, 'clubs_by_rating': clubs_by_rating, 'safe_clubs': safe_clubs,
               'cheapest_clubs': cheapest_clubs}
    return render(request, 'clubmate/discover.html', context=context)


def club_detail(request, club_id):
    try:
        club = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        club = None
    context = {'club': club}
    return render(request, 'clubmate/club_detail.html', context=context)


def ratings(request):
    # maybe used with js
    all_rating_by_time = sorted(Rating.objects.all(), key=lambda c: c.posted_at, reverse=True)
    all_rating_by_upvote = sorted(Rating.objects.all(), key=lambda c: c.number_of_upvotes, reverse=True)

    # use for display directly
    default_rating_by_time = sorted(Rating.objects.all(), key=lambda c: c.posted_at, reverse=True)
    default_rating_by_upvote = sorted(Rating.objects.all(), key=lambda c: c.number_of_upvotes, reverse=True)

    paginator_time = Paginator(all_rating_by_time, 3)
    paginator_upvote = Paginator(all_rating_by_upvote, 3)

    page_number = request.GET.get('page')
    page_object_time = paginator_time.get_page(page_number)
    page_object_upvote = paginator_upvote.get_page(page_number)

    context = {'page_object_time': page_object_time, 'page_object_upvote': page_object_upvote,
               'default_rating_by_time': default_rating_by_time,
               'default_rating_by_upvote': default_rating_by_upvote}
    return render(request, 'clubmate/ratings.html', context)  # TODO – someone flipped ratings and rate


# not sure
@login_required
def rating_detail(request, rating_id):
    return render(request, 'clubmate/profile.html')


@login_required
def rate(request):
    return render(request, 'clubmate/rate_club.html')  # The template that was there before was incorrect


# new because not sure which route i should mathch the content to
def rate_content(request, rating_id):
    try:
        this_rate = Rating.objects.get(id=rating_id)
    except Rating.DoesNotExist:
        this_rate = None
    context = {'this_rate': this_rate}
    return render(request, 'clubmate/rate_content.html', context=context)


@login_required
def rate_detail(request, club_id):
    form = RatingDetailForm()

    if request.method == 'POST':
        form = RatingDetailForm(request.POST)
        user = request.user
        this_club = Club.objects.filter(id=club_id)
        if form.is_valid():
            if this_club:
                this_rate = form.save(commit=False)
                this_rate.author = user.profile
                this_rate.club = this_club
                this_rate.save()
        else:
            print(form.errors)
    context = {'club_id': club_id, 'form': form}

    return render(request, 'clubmate/rate_club_detail.html', context)


@login_required
def upvote_rating(request, rating_id):
    rating = Rating.objects.get(id=rating_id)  # Get the rating to be modified
    rating.number_of_upvotes += 1  # Increment the number of votes
    rating.save()
    club_id = rating.club.id
    return redirect(reverse('clubmate:club_detail', kwargs={'club_id': club_id}))  # Redirect back to club detail


@login_required
def save_club(request, club_id):
    club = Club.objects.get(id=club_id)  # Get the club in question
    user = request.user  # Get the current user
    clubmate_user = UserProfile.objects.get(user=user)  # Map to out user
    clubmate_user.clubs.add(club)  # Add it to the user's profile
    return redirect(reverse('clubmate:profile', kwargs={'username': user.username}))  # Redirect to profile


@staff_member_required
def add_club(request):
    return render(request, 'clubmate/add_club.html')


def profile(request, username):
    user = User.objects.get(username=username)  # Match username from the default user
    clubmate_user = UserProfile.objects.get(user=user)  # Match it with our custom user
    rating_list = Rating.objects.filter(author=clubmate_user)
    context = {'clubmate_user': clubmate_user, 'ratingList': rating_list}
    return render(request, 'clubmate/profile.html', context=context)


@staff_member_required
def edit_club(request, club_id):
    return render(request, 'clubmate/edit_club.html')


@staff_member_required
def delete_club(request, club_id):
    return render(request, 'clubmate/delete_club.html')


@login_required
def edit_rating(request, rating_id):
    rating = Rating.objects.get(id=rating_id)  # Get the rating

    if request.method == 'POST':
        new_rating = request.POST.get('user_commentary')
        rating.user_commentary = new_rating
        rating.save()
        return redirect("rating:rating_detail")
    else:
        context = {'rating': rating}
        return render(request, 'clubmate/edit_rating.html', context)


@login_required
def delete_rating(request, rating_id):
    ratingDelete = Rating.objects.filter(id=rating_id)
    user = request.user
    ratingDelete.delete()
    return redirect(reverse('clubmate:profile', kwargs={'username': user.username}))


def log_in(request):
    if request.method == 'POST':
          username = request.POST['username']
          password = request.POST['password']
          user = authenticate(username=username, password=password)
          if user is not None:
              if user.is_active:
                  login(request, user)
                  # Redirect to index page.
                  return redirect(reverse("clubmate:index"))
              else:
                  # Return a 'disabled account' error message
                  return HttpResponse("Your account is disabled.")
          else:
              # Return an 'invalid login' error message.
              print  ("invalid login details " + username + " " + password)
    else:
        # the login is a  GET request, so just show the user the login form.
        return render(request, 'clubmate/login.html')


@login_required
def log_out(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect(reverse("clubmate:index"))


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user=user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'clubmate/register.html', context = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

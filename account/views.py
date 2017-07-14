from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from account.forms import LoginForm
from .models import Profile
from .forms import UserRegistrationForm, ChangeEmailForm, ChangeNameForm, EditProfileForm
from journal import models as journal_models


def change_personal_details(request):
    if request.method == 'POST':
        name_form = ChangeNameForm(instance=request.user, data=request.POST)
        profile_form = EditProfileForm(instance=request.user.profile, data=request.POST)
        if name_form.is_valid() and profile_form.is_valid():
            name_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
        else:
            messages.warning(request, "Error updating profile!")

    else:
        name_form = ChangeNameForm()
        profile_form = EditProfileForm()
    return render(request, 'account/change_personal_details.html',
                  {'name_form': name_form, 'profile_form': profile_form, 'section': 'account'})


# View for changing the user's email.
@login_required
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Email changed!")
        else:
            messages.error(request, "Error changing email!")
    else:
        form = ChangeEmailForm()
    return render(request, 'account/change_email.html', {'form': form, 'section': 'account'})


@login_required
def dashboard(request):
    # Get all papers submitted by the user.
    papers = journal_models.Paper.objects.filter(user=request.user)
    reviewed_papers = journal_models.Paper.objects.filter(reviewers=request.user)

    # Papers that are under review and need a review
    review_papers = reviewed_papers.filter(status='under_review')

    # Don't list papers that are in Processing or Under Review
    reviewed_papers = reviewed_papers.filter(~Q(status='processing'), ~Q(status='under_review'))

    return render(request, 'account/dashboard.html',
                  {'section': 'account', 'papers': papers, 'review_papers': review_papers,
                   'reviewed_papers': reviewed_papers})


# Login the user.
def user_login(request):
    if request.user.is_authenticated():
        return redirect('account:dashboard')
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            # If the user exists and it is active, login, else error.
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('account:dashboard')
                else:
                    return render(request, 'account/login.html', {'form': form, 'error': 'Disabled account'})
            else:
                return render(request, 'account/login.html', {'form': form, 'error': 'Disabled account'})
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


# Will register a user an create a profile for it.
def register(request):
    if request.user.is_authenticated():
        return redirect('account:dashboard')
    elif request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'form': user_form})


def custom_404(request):
    return render(request, '404.html', {}, status=404)

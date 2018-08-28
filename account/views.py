import json
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from account.forms import LoginForm
from account.mail import send_token_email, send_review_invitation_email
from .models import Profile, Invitation, create_login_token, get_login_token
from .forms import UserRegistrationForm, ChangeEmailForm, ChangeNameForm, EditProfileForm
from journal import models as journal_models
from journal import utilities as journal_utilities


def accept_invite(request, rev_id):
    """
    Accepts the user invite.
    It shows that the user has accepted the invite and gives the token to the user.
    It also assigns the user as a reviewer to the paper.
    """

    ri = get_object_or_404(Invitation, token=rev_id)
    user = User.objects.filter(email=ri.email)

    if user is None:
        return "No user"

    if ri.accepted is None:  # The ReviewInvitation wasn't accepted nor rejected, it was accepted for the first time.
        token = create_login_token(user[0])
        ri.accepted = True
        ri.save()
        # Must add user as a reviewer fml how do I do that? this is getting messy.
        journal_utilities.add_reviewer_from_invitation(ri)
    elif ri.accepted is True:
        token = get_login_token(user[0])
    else:
        return HttpResponseRedirect("/")

    return HttpResponseRedirect("{url}?token={token}".format(url=ri.url, token=token.token))


def reject_invite(request, rev_id):
    """
    Rejects the user invite, deleting it /w the login token.
    """
    ri = get_object_or_404(Invitation, token=rev_id)
    name = ri.name

    # Redirect to home if the Review Invite was already rejected.
    if ri.accepted is False:
        return HttpResponseRedirect("/")

    ri.accepted = False
    ri.save()

    return render(request, 'account/reject_invite.html', {'name': name})


@login_required
@user_passes_test(lambda u: u.is_staff)
def cancel_invitation(request):
    """
        Function that will cancel the user's invitation.
    """
    if not request.is_ajax():
        raise Http404

    data = json.loads(str(request.body, encoding="utf-8"))
    invitation = Invitation.objects.filter(email=data["email"], name=data["name"])
    response = {}
    if invitation:
        invitation[0].delete()
        response["message"] = "Invitation deleted!"
    else:
        response["error"] = "No invitation deleted!"

    return JsonResponse(response)


@login_required
@user_passes_test(lambda u: u.is_staff)
def get_invitations(request):
    """
    This method should return the invitations by name
    """
    if not request.is_ajax():
        raise Http404

    data = json.loads(str(request.body, encoding="utf-8"))
    invitations = Invitation.objects.filter(name=data["name"])
    response = {}

    if invitations:
        response = serializers.serialize('json', invitations)
    else:
        response["error"] = "No invitations!"

    return JsonResponse(response, safe=False)


@login_required
@user_passes_test(lambda u: u.is_staff)
def invite_user(request):
    """
    This method is invoked via JavaScript and it's used by the admins to invite users to the website.
    The method will generate an Invitation and send it to the user.
    """
    if not request.is_ajax():
        raise Http404

    data = json.loads(str(request.body, encoding="utf-8"))
    response = {}

    user = User.objects.filter(email=data["email"])

    if user:
        invitation = Invitation.objects.filter(email=data["email"], name=data["name"])

        # If we don't have an invitation for the user, create on and save it to the database.
        if not invitation:
            invitation = Invitation(email=data["email"], name=data["name"], url=data["url"])
            invitation.save()
            # Notify user that he has been invited.
            # This is the worst piece of shit code that I ever written in my life..........
            a_url = "invite/{id}/accept".format(id=invitation.token)
            d_url = "invite/{id}/reject".format(id=invitation.token)
            send_review_invitation_email(invitation.email, a_url, d_url)
            response["message"] = "{} {} was invited successfully".format(user[0].first_name, user[0].last_name)
        else:
            response["error"] = "User has been invited already!"
    else:
        response["error"] = "User not found!"

    return JsonResponse(response)


@login_required
@user_passes_test(lambda u: u.is_staff)
def generate_user_token(request):
    """
    This function will generate a login token that expires in 10 days and it will assign it to a user.
    It is retrieves the user_id and paper_id from the GET request.
    It also notifies the user via email that a token has been generated.

    This function is used by account.accept_invite view.
    """
    user_id = request.GET.get("user_id", None)
    data = {}

    if user_id is None:
        data["error"] = "No user id provided!"

    try:
        user = User.objects.filter(id=int(user_id))

        if not user:
            data["user_id"] = str(user_id)
            data["error"] = "User not found!"
        else:  # This is where we make the LoginToken.

            token = create_login_token(user[0])

            # Notify the user that a token has been generated
            send_token_email(token.user.email, token.token)

            data['message'] = "Token was generated successfully!"
            data['token'] = token.token
    except ValueError as e:
        data["error"] = str(e)
    except TypeError as e:
        data["error"] = str(e)
    except Exception as e:
        data["error"] = str(e)

    return JsonResponse(data)


def change_personal_details(request):
    """
        Function that will change the user's personal details. The details are retrieved from the request's post data.
        The name is changed using the ChangeNameForm and the profile using the EditProfileForm
    :param request:
    :return:
    """
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

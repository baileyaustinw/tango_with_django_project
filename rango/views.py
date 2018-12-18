from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from tango_with_django_project.settings import MEDIA_URL
from rango.models import Category, Page
from rango.forms import PageForm, CategoryForm, UserForm, UserProfileForm
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rango.functions import visitor_cookie_handler


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list, 'MEDIA_URL': MEDIA_URL}

    # call helper function to handle the cookies
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    # obtain response object early so we can add cookie information
    response = render(request, 'rango/index.html', context=context_dict)
    # return response back to user, updating any cookies that need changed
    return response


def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None

    return render(request, 'rango/category.html', context_dict)


def show_categories(request):
    category_list = Category.objects.all()
    context_dict = {'categories': category_list}

    return render(request, 'rango/categories.html', context=context_dict)


def show_pages(request):
    page_list = Page.objects.all()
    context_dict = {'pages': page_list}

    return render(request, 'rango/pages.html', context=context_dict)


def about(request):
    context_dict = {
        'boldmessage': 'This tutorial has been put together by Austin Bailey',
        'MEDIA_URL': MEDIA_URL
    }

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/about.html', context=context_dict)

    return response


@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            #return index(request)
            return HttpResponseRedirect(reverse('index'))
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug.lower())
    except Category.DoesNotExist:
        category = None

    print(category)
    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                #return show_category(request, category_name_slug)
                return HttpResponseRedirect(reverse('category', args=[category_name_slug.lower()]))
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    # boolean value for telling the template
    # whether the registration was successful
    # set to false initially and code changes
    # value upon successful registration
    registered = False

    # process data if its a POST request
    if request.method == 'POST':
        # grab information from raw post data
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # if both forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # save user's form data
            user = user_form.save()

            # hash the password and update user object
            user.set_password(user.password)
            user.save()

            # set commit to false to delay saving the model
            profile = profile_form.save(commit=False)
            profile.user = user

            # check if user submitted image
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # save userprofile instance
            profile.save()

            # update variable to notify template of successful registration
            registered = True
        else:
            # invalid form - print errors
            print(user_form.errors, profile_form.errors)
    else:
        # didn't receive a POST request so display blank forms
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


def user_login(request):
    # if a POST method try to process data
    if request.method == 'POST':
        # gather username and password provided by user
        # use request.POST.get() because request.POST[] returns a KeyError if value does not exist
        # while request.POST.get() returns None
        username = request.POST.get('username')
        password = request.POST.get('password')

        # use Django's built-in authenticate() function to see if username/password combo is valid
        # returns a User object if it is valid
        user = authenticate(username=username, password=password)

        # if we have a User object the details are correct
        if user:
            # check if account is active
            if user.is_active:
                # if the account is valid and active, log the user in
                login(request, user)
                # redirect user to homepage on login
                return HttpResponseRedirect(reverse('index'))
            else:
                # inactive account, don't log in
                return HttpResponse("Your Rango account is disabled")
        else:
            # incorrect login details provided
            if not username and not password:
                print("No username or password given")
                messages.add_message(request, messages.ERROR, 'Please enter a username and password.')
            elif not username:
                print("No username given")
                messages.add_message(request, messages.ERROR, 'Please enter a username.')
            elif not password:
                print("No password given")
                messages.add_message(request, messages.ERROR, 'Please enter a password.')
            else:
                print("Incorrect login credentials: {0}, {1}".format(username, password))
                messages.add_message(request, messages.ERROR, "The username/password combination entered is incorrect.")
            return render(request, 'rango/login.html', {})

    # the request is not a POST request so display login form
    else:
        # no context variables to pass to template
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

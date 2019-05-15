from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from tango_with_django_project.settings import MEDIA_URL
from rango.models import Category, Page, UserProfile
from rango.forms import PageForm, CategoryForm, UserForm, UserProfileForm
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rango.functions import visitor_cookie_handler, get_category_list
from rango.webhose_search import run_query
from django.contrib.auth.models import User
from django.shortcuts import redirect
import datetime


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
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None

    context_dict['query'] = category.name
    results_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            results_list = run_query(query)
            context_dict['query'] = query
            context_dict['results_list'] = results_list

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
def like_category(request):
    cat_id = None

    if request.method == 'GET':
        cat_id = request.GET['category_id']
        likes = 0

        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()

    return HttpResponse(likes)


def suggest_category(request):
    cat_list = []
    starts_with = ''

    if request.method == 'GET':
        starts_with = request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)

    return render(request, 'rango/categories_sidebar.html', {'categories': cat_list})


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
                page.first_visit = datetime.date.today()
                page.save()
                #return show_category(request, category_name_slug)
                return HttpResponseRedirect(reverse('category', args=[category_name_slug.lower()]))
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}

    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']

        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')
            context_dict['pages'] = pages

    return render(request, 'rango/page_list.html', context_dict)


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


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES)

        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()

            return HttpResponseRedirect(reverse('index'))
        else:
            print(form.errors)

    context_dict = {'form': form}

    return render(request, 'registration/profile_registration_form.html', context_dict)


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


def search(request):
    results_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        cat_id = request.POST['category']
        category = Category.objects.get(id=int(cat_id))
        print('query:' + query)
        print('cat_id:' + cat_id)
        if query:
            results_list = run_query(query)

    context_dict = {'results_list': results_list,
                    'query': query,
                    'category': category}

    return render(request, 'rango/category.html', context_dict)


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))

    context_dict = {}
    profile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm(
        {'website': profile.website, 'picture': profile.picture}
    )

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save(commit=True)

            return HttpResponseRedirect(reverse('profile', args=(user.username,)))
        else:
            print(form.errors)

    context_dict['form'] = form
    context_dict['user_profile'] = profile
    return render(request, 'rango/profile.html', context_dict)


@login_required
def profile_list(request):
    context_dict = {}
    profiles = UserProfile.objects.all()
    context_dict['profiles'] = profiles
    users = []

    if profiles:
        for profile in profiles:
            users.append(User.objects.get(id=profile.user.id))

    context_dict['users'] = users

    return render(request, 'rango/profile_list.html', context_dict)


def track_url(request):
    page_id = None
    url = '/rango/'

    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.last_visit = datetime.date.today()
                page.save()
                url = page.url
            except Page.DoesNotExist:
                pass

    return redirect(url)


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

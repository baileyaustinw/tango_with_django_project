import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'tango_with_django_project.settings')

import django

django.setup()

from rango.models import Category, Page

def populate():
    # Create lists of dictionaries containing the pages we want to add into each category
    # Then create a dictionary of dictionaries for our categories
    python_pages = [
        {'title': 'Official python tutorial',
         'url': 'http://docs.python.org/2/tutorial',
         'views': 0},
        {'title': 'How to think like a computer scientist',
         'url': 'http://www.greenteapress.com/thinkpython',
         'views': 0},
        {'title': 'Learn python in 10 minutes',
         'url': 'http://www.korokithakis.net/tutorials/python',
         'views': 0}
    ]
    django_pages = [
        {'title': 'Official django tutorial',
         'url': 'https://docs.djangoproject.com/en/1.9/intro/tutorial01',
         'views': 0},
        {'title': 'Django rocks',
         'url': 'http://www.djangorocks.com',
         'views': 0},
        {'title': 'How to tango with django',
         'url': 'http://www.tangowithdjango.com',
         'views': 0}
    ]
    other_pages = [
        {'title': 'Bottle',
         'url': 'http://bottlepy.org/docs/dev/',
         'views': 0},
        {'title': 'Flask',
         'url': 'http://flask.pocoo.org',
         'views': 0}
    ]
    cats = {
        'Python': {'pages': python_pages, 'likes': 0, 'views': 0},
        'Django': {'pages': django_pages, 'likes': 0, 'views': 0},
        'Other frameworks': {'pages': other_pages, 'likes': 0, 'views': 0}
    }

    # iterate through the cats dictionary and add each category and each page associated with that category
    for cat, cat_data in cats.items():
        c = add_cat(cat, cat_data['likes'], cat_data['views'])
        for p in cat_data['pages']:
            add_page(c, p['title'], p['url'], p['views'])

    # print each category we have added
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print('- {0} - {1}'.format(str(c), str(p)))


# method for creating a new page
def add_page(cat, title, url, views):
    if cat.name == 'Python':
        views = 108
    if cat.name == 'Django':
        views = 312
    if cat.name == 'Other frameworks':
        views = 76

    p = Page.objects.get_or_create(category=cat, title=title, url=url, views=views)[0]
    p.save()
    return p


# method for creating a new category
def add_cat(name, likes, views):
    if name == 'Python':
        likes = 64
        views = 128
    if name == 'Django':
        likes = 32
        views = 64
    if name == 'Other frameworks':
        likes = 16
        views = 32

    """
    print('inside add_cat')
    print('name:' + name)
    print('likes:' + str(likes))
    print('views:' + str(views))
    print('end add_cat')
    """

    c = Category.objects.get_or_create(name=name, views=views, likes=likes)[0]
    c.save()
    return c


# execute the code
# code within conditional below only executes when run as a standalone script
if __name__ == '__main__':
    print('starting rango population script')
    populate()
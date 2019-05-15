from django.test import TestCase
from rango.models import Category, Page
from django.urls import reverse
import datetime


def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c


# Create your tests here.
class CategoryMethodTests(TestCase):
    def test_ensure_views_are_positive(self):
        """
        ensure_views_are_positive should result True for categories where views
        are zero or positive
        :return:
        """
        cat = Category(name='test', views=-1, likes=0)
        cat.save()
        self.assertEqual((cat.views >= 0), True)

    def test_slug_line_creation(self):
        """
        slug_line_creation checks to make sure that when we add a category
        an appropriate slug line is created
        i.e. "Random Category String" -> "random-category-string"
        :return:
        """
        cat = Category(name='Random Category String')
        cat.save()
        self.assertEqual(cat.slug, 'random-category-string')


class IndexViewTest(TestCase):
    def test_index_view_with_no_categories(self):
        """
        If no categories exist, an appropriate message should be displayed
        :return:
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no categories present.")
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_index_view_with_categories(self):
        """
        Check to make sure that the index has categories displayed
        :return:
        """
        add_cat('test', 1, 1)
        add_cat('temp', 1, 1)
        add_cat('tmp', 1, 1)
        add_cat('tmp test temp', 1, 1)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tmp test temp")

        num_cats = len(response.context['categories'])
        self.assertEqual(num_cats, 4)


class PageMethodTests(TestCase):
    def test_ensure_visits_not_in_future(self):
        category = Category(name='test')
        category.save()
        page = Page(category=category, title='test', url='http://www.google.com', views=1,
                    last_visit=datetime.date.today()+datetime.timedelta(days=1),
                    first_visit=datetime.date.today()+datetime.timedelta(days=1))
        page.save()
        self.assertEqual((page.last_visit <= datetime.date.today()), True)
        self.assertEqual((page.first_visit <= datetime.date.today()), True)

    def test_ensure_last_visit_not_before_first(self):
        category = Category(name='test')
        category.save()
        page = Page(category=category, title='test', url='http://www.google.com', views=1,
                    last_visit=datetime.date.today() + datetime.timedelta(days=1), first_visit=datetime.date.today())
        page.save()
        self.assertEqual((page.last_visit <= page.first_visit), True)

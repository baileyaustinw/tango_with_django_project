from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
import datetime


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self.views < 0:
            self.views = 0

        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Page(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    last_visit = models.DateField(null=True)
    first_visit = models.DateField(null=True)

    def save(self, *args, **kwargs):
        if self.first_visit > datetime.date.today():
            self.first_visit = datetime.date.today()

        if self.last_visit > datetime.date.today():
            self.last_visit = datetime.date.today()

        if self.last_visit <= self.first_visit:
            self.last_visit = self.first_visit

        super(Page, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

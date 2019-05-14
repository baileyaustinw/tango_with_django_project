from registration.backends.simple.views import RegistrationView


class RegistrationView(RegistrationView):
    def get_success_url(self, user):
        return '/rango/'

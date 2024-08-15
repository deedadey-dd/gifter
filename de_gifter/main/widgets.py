from django import forms
from django_countries.widgets import CountrySelectWidget
from country_dialcode.widgets import CountryDialcodeSelectWidget


class CountryDialcodeWidget(CountryDialcodeSelectWidget):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # Optionally format the choices here if needed
        return context
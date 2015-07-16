from django.views.generic import View
from django.shortcuts import render


class TrackerView(View):

    def get_context_data(self, **kwargs):
        self.context = super(TrackerView, self).get_context_data(**kwargs)
        return self.context

    def post(self, request, *args, **kwargs):
        """Allows a POST -- without the class returns a 405 error."""
        return render(
                    request,
                    self.template_name,
                    self.get_context_data(**kwargs)
                )

    def get(self, request, *args, **kwargs):
        """Allows a GET -- without the class returns a 405 error."""
        return render(
                    request,
                    self.template_name,
                    self.get_context_data(**kwargs)
                )

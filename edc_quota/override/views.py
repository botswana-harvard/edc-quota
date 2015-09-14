from django.views.generic import View
from django.shortcuts import render

from .code import Code


class OverrideCodeView(View):

    def __init__(self):
        self.template_name = 'override_code.html'

    def get_context_data(self, request, **kwargs):
        override_request = request.POST.get('override_request', '')
        self.context = {'override_request': override_request}
        if override_request:
            self.context.update({'override_code': Code(override_request).validation_code})
        return self.context

    def post(self, request, *args, **kwargs):
        """Allows a POST -- without the class returns a 405 error."""
        return render(request, self.template_name, self.get_context_data(request, **kwargs))

    def get(self, request, *args, **kwargs):
        """Allows a GET -- without the class returns a 405 error."""
        return render(request, self.template_name, {})

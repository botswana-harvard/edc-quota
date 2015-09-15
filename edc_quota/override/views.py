from .forms import OverrideForm
from django.views.generic.edit import FormView
from django.shortcuts import render_to_response


class OverrideCodeView(FormView):

    template_name = 'override_code.html'
    form_class = OverrideForm
    success_url = '/override_code/'

    def form_valid(self, form):
        return render_to_response(self.template_name, {'override_code': form.clean().get("override_request")})

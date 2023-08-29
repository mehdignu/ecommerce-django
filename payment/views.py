from django.shortcuts import render
from django.views.generic import View


class PaymentView(View):

    def post(self, request, *args, **kwargs):
        return redirect("payment:product_color", slug=slug, color=color)
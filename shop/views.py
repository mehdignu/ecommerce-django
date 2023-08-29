from django.shortcuts import render


def handler404(request, *args, **argv):
    return render(request, 'not_found.html')


def handler500(request, *args, **argv):
    return render(request, 'not_found.html')
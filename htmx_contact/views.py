from django.shortcuts import redirect, render


def home(request):
    return redirect('contact:index')


def page_not_found(request, exception):  # noqa
    return render(request, '404.html', status=404)

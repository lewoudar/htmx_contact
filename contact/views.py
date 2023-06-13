from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django_htmx.middleware import HtmxDetails

from .forms import ContactForm
from .models import Contact


class HttpSeeOtherRedirect(HttpResponseRedirect):
    status_code = 303


# Typing pattern recommended by django-stubs:
# https://github.com/typeddjango/django-stubs#how-can-i-create-a-httprequest-thats-guaranteed-to-have-an-authenticated-user
class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


def index(request: HtmxHttpRequest):
    search = request.GET.get('q')
    template = 'contact/index.html'
    if search is not None:
        predicates = [
            Q(firstname__icontains=search)
            | Q(lastname__icontains=search)
            | Q(email__icontains=search)
            | Q(phone__icontains=search)
        ]
        contacts = Contact.objects.filter(*predicates)
        if request.htmx.trigger == 'search':
            template = 'contact/rows.html'
    else:
        contacts = Contact.objects.all()

    paginator = Paginator(contacts, 10)
    page = int(request.GET.get('page', '1'))
    page_obj = paginator.get_page(page)
    return render(request, template, {'page_obj': page_obj})


def contact_count(request):
    count = Contact.objects.count()
    return HttpResponse(f'({count} total Contacts)')


class ContactCreate(View):
    @staticmethod
    def get(request):
        return render(request, 'contact/new.html', {'form': ContactForm()})

    @staticmethod
    def post(request):
        form = ContactForm(request.POST)
        if form.is_valid():
            Contact.objects.create(
                firstname=form.cleaned_data['firstname'],
                lastname=form.cleaned_data['lastname'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
            )
            messages.success(request, 'Created New Contact!')
            return redirect('contact:index')
        else:
            return render(request, 'contact/new.html', {'form': form})


class ReadDeleteContact(View):
    @staticmethod
    def get(request, contact_id: int):
        contact = get_object_or_404(Contact, id=contact_id)
        return render(request, 'contact/show.html', {'contact': contact})

    @staticmethod
    def delete(request, contact_id: int):
        contact = get_object_or_404(Contact, id=contact_id)
        contact.delete()
        messages.success(request, 'Deleted Contact!')
        return HttpSeeOtherRedirect(reverse('contact:index'))


class ContactEdit(View):
    @staticmethod
    def get(request, contact_id: int):
        contact = get_object_or_404(Contact, id=contact_id)
        context = {'form': ContactForm(initial=contact.to_dict()), 'contact': contact}
        return render(request, 'contact/edit.html', context)

    @staticmethod
    def post(request, contact_id: int):
        contact = get_object_or_404(Contact, id=contact_id)
        form = ContactForm(request.POST)
        if form.is_valid():
            for item in ['firstname', 'lastname', 'email', 'phone']:
                setattr(contact, item, form.cleaned_data[item])
            contact.save()
            messages.success(request, 'Updated Contact!')
            return redirect('contact:index')
        else:
            context = {'form': form, 'contact': contact}
            return render(request, 'contact/edit.html', context)


def check_email(request):
    email = request.GET.get('email', '')
    # we make a partial form validation only to check email
    form = ContactForm({'email': email})
    return render(request, 'contact/email_errors.html', {'errors': form.errors.get('email', [])})

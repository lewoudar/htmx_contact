from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .forms import ContactForm
from .models import Contact


class HttpSeeOtherRedirect(HttpResponseRedirect):
    status_code = 303


def index(request):
    search = request.GET.get('q')
    if search is not None:
        predicates = [
            Q(firstname__icontains=search)
            | Q(lastname__icontains=search)
            | Q(email__icontains=search)
            | Q(phone__icontains=search)
        ]
        contacts = Contact.objects.filter(*predicates)
    else:
        contacts = Contact.objects.all()
    return render(request, 'contact/index.html', {'contacts': contacts})


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


@method_decorator(csrf_exempt, name='dispatch')
class ReadEditDeleteContact(View):

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

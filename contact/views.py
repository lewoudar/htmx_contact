from django.contrib import messages
from django.core.paginator import Paginator, Page
from django.db import transaction
from django.db.models import Q, QuerySet
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse, QueryDict, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django_htmx.middleware import HtmxDetails
from render_block import render_block_to_string

from .forms import ContactForm
from .helpers import get_archiver
from .models import Contact


class HttpSeeOtherRedirect(HttpResponseRedirect):
    status_code = 303


# Typing pattern recommended by django-stubs:
# https://github.com/typeddjango/django-stubs#how-can-i-create-a-httprequest-thats-guaranteed-to-have-an-authenticated-user
class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


def partial_render(
    template_name: str,
    block_name: str,
    context: dict | None = None,
    request: HtmxHttpRequest | None = None,
    status: int = 200,
) -> HttpResponse:
    data = render_block_to_string(template_name, block_name, context, request)
    return HttpResponse(data, status=status)


class ContactHome(View):
    @staticmethod
    def _get_page_obj(contacts: QuerySet, page: str = '1') -> Page:
        paginator = Paginator(contacts, 10)
        return paginator.get_page(page)

    def get(self, request: HtmxHttpRequest):
        search = request.GET.get('q')
        page = request.GET.get('page', '1')
        if search is not None:
            predicates = [
                Q(firstname__icontains=search)
                | Q(lastname__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            ]
            contacts = Contact.objects.filter(*predicates)
            if request.htmx.trigger == 'search':
                page_obj = self._get_page_obj(contacts, page)
                return partial_render('contact/index.html', 'table-rows', {'page_obj': page_obj})
        else:
            contacts = Contact.objects.all()
        page_obj = self._get_page_obj(contacts, page)
        return render(request, 'contact/index.html', {'page_obj': page_obj, 'archiver': get_archiver()})

    @transaction.atomic
    def delete(self, request: HtmxHttpRequest):
        data = QueryDict(request.body)
        for contact_id in data.getlist('selected_contact_ids'):
            contact = Contact.objects.get(id=int(contact_id))
            contact.delete()

        messages.success(request, 'Deleted contacts!')
        page_obj = self._get_page_obj(Contact.objects.all())
        return render(request, 'contact/index.html', {'page_obj': page_obj})


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
    def delete(request: HtmxHttpRequest, contact_id: int):
        contact = get_object_or_404(Contact, id=contact_id)
        contact.delete()
        if request.htmx.trigger == 'delete-btn':
            messages.success(request, 'Deleted Contact!')
            return HttpSeeOtherRedirect(reverse('contact:index'))
        else:
            return HttpResponse()


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
    return partial_render('contact/edit.html', 'email-errors', {'errors': form.errors.get('email', [])})


class ContactArchive(View):
    @staticmethod
    def get(request):
        return render(request, 'contact/archive_ui.html', {'archiver': get_archiver()})

    @staticmethod
    def post(request):
        archiver = get_archiver()
        archiver.run()
        return render(request, 'contact/archive_ui.html', {'archiver': archiver})

    @staticmethod
    def delete(request):
        archiver = get_archiver()
        archiver.reset()
        return render(request, 'contact/archive_ui.html', {'archiver': archiver})


def get_archive_file(request):
    archiver = get_archiver()
    return FileResponse(
        archiver.archive_file.open(mode='rb'),
        filename=archiver.archive_file.name,
        as_attachment=True,
        content_type='text/csv',
    )

from ninja_extra import ControllerBase, api_controller, route
from ninja import Schema, ModelSchema
from ninja_extra.controllers import Detail
from pydantic import EmailStr

from .models import Contact


class ContactSchema(ModelSchema):
    class Config:
        model = Contact
        model_fields = ['id', 'firstname', 'lastname', 'email', 'phone']


class ContactListResponse(Schema):
    contacts: list[ContactSchema]


class ValidationErrorSchema(Schema):
    detail: dict


class BaseErrorSchema(Schema):
    detail: str


class ContactCreateSchema(Schema):
    firstname: str
    lastname: str
    email: EmailStr
    phone: str


@api_controller('/contacts', tags=['Contact'])
class ContactController(ControllerBase):

    @route.get('/', response=ContactListResponse)
    def get_contacts(self):
        return {'contacts': [contact for contact in Contact.objects.all()]}

    @route.post('/', response={201: ContactSchema, 422: ValidationErrorSchema})
    def create_contact(self, payload: ContactCreateSchema):
        contact = Contact.objects.create(
            firstname=payload.firstname, lastname=payload.lastname, email=payload.email, phone=payload.phone
        )
        return 201, contact


@api_controller('/contacts/{contact_id}', tags=['Contact'])
class ContactDetailController(ControllerBase):

    @route.get('/', response={200: ContactSchema, 404: BaseErrorSchema})
    def get_contact(self, contact_id: int):
        return self.get_object_or_exception(Contact, pk=contact_id, error_message='Contact not found')

    @route.put('/', response={200: ContactSchema, 404: BaseErrorSchema, 422: ValidationErrorSchema})
    def update_contact(self, payload: ContactCreateSchema, contact_id: int):
        contact = self.get_object_or_exception(Contact, pk=contact_id, error_message='Contact not found')
        for item in ['firstname', 'lastname', 'email', 'phone']:
            value = getattr(payload, item)
            setattr(contact, item, value)
        contact.save()
        return contact

    @route.delete('/', response=Detail(status_code=204))
    def delete_contact(self, contact_id: int):
        contact = self.get_object_or_exception(Contact, pk=contact_id, error_message='Contact not found')
        contact.delete()
        return self.create_response('', status_code=204)

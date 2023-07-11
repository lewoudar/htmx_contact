from ninja_extra import NinjaExtraAPI

from contact.api import ContactController, ContactDetailController

api = NinjaExtraAPI(title='Contact App API')
api.register_controllers(ContactController, ContactDetailController)

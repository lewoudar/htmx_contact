from django.db import models


class Contact(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=30)

    def __str__(self):
        return f'id={self.pk}, firstname={self.firstname}, lastname={self.lastname}'

    def to_dict(self) -> dict[str, str]:
        return {'firstname': self.firstname, 'lastname': self.lastname, 'email': self.email, 'phone': self.phone}

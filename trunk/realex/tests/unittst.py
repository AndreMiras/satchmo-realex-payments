from django.test import TestCase
from django.test.client import Client

from django.contrib.sites.models import Site
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from livesettings import Setting, config_value
from satchmo_store.contact.models import Contact

class TestRealex(TestCase):
    fixtures = [
      'Config',
      'Setting',
      'Site',
    ]

    def setUp(self):
        Site.objects.clear_cache()
        self.site = Site.objects.get_current()

        setting = Setting.objects.get_or_create(site=self.site,
                                                group='PAYMENT_REALEX',
                                                key='DO_POST',
                                                value=False)
        self.assertEquals(config_value('PAYMENT_REALEX', 'DO_POST'), False)

        self.user = User.objects.create_user(username='realex_test_user', email='test@foo.bar', password='a')
        self.contact = Contact.objects.create(user=self.user)
        self.group = Group.objects.get_or_create(name=self.site.domain)[0]
        self.user.groups.add(self.group)

    def test(self):
        c = Client()
        self.assertTrue(c.login(username='realex_test_user', password='a'))

        url = reverse('REALEX_satchmo_checkout-step3')
        postdata = {
            'credit_type': 'VISA',
            'credit_number': '4' + '1' * 9,
            'month_expires': '01',
            'year_expires': '2222',
            'ccv': '123',
            'bill_street1': 'street1',
            'bill_street2': 'street2',
            'bill_city': 'dublin',
            'bill_postal_code': 'd1',
            'card_holder': 'denis',
            }
        response = c.post(url, postdata)

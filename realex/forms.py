from django import forms
from satchmo.payment.forms import CreditPayShipForm
from django.utils.translation import ugettext as _
from satchmo.payment import signals

from satchmo.contact.models import Contact, AddressBook

class RealexCreditPayShipForm(CreditPayShipForm):
    bill_street1 = forms.CharField(max_length=30, label=_('Street'))
    bill_street2 = forms.CharField(max_length=30, required=False)
    bill_city = forms.CharField(max_length=30, label=_('City'))
    bill_postal_code = forms.CharField(max_length=10, label=_('ZIP code/Postcode'))
    card_holder = forms.CharField(label=_("Card Holder Name"), max_length=60, required=False)

    def __init__(self, request, paymentmodule, *args, **kwargs):
        CreditPayShipForm.__init__(self, request, paymentmodule, *args, **kwargs)

        # some Laser cards don't have a ccv
        self.fields['ccv'].required = False

        # select the first (and only) shipping method by default
        self.fields['shipping'].initial = self.fields['shipping'].choices[0][0]
        try:
            self.fields['card_holder'].initial = request.user.contact_set.get().full_name
        except Contact.DoesNotExist:
            pass

    def clean_ccv(self):
        ccv = self.cleaned_data['ccv']
        if self.cleaned_data['credit_type'] != u'LASER':
            if ccv == '':
                raise forms.ValidationError(_('CCV is mandatory for cards other than Laser.'))
            return CreditPayShipForm.clean_ccv(self)
        return ccv

    def save(self, request, cart, contact, payment_module):
        """Save the order and the credit card information for this orderpayment"""
        CreditPayShipForm.save(self, request, cart, contact, payment_module)

        self.order.bill_street1 = self.cleaned_data['bill_street1']
        self.order.bill_street2 = self.cleaned_data['bill_street2']
        self.order.bill_city = self.cleaned_data['bill_city']
        self.order.bill_postal_code = self.cleaned_data['bill_postal_code']
        self.order.save()
        cc = self.order.credit_card
        cc.card_holder = self.cleaned_data['card_holder']
        cc.save()
        
        signals.form_save.send(RealexCreditPayShipForm, form=self)

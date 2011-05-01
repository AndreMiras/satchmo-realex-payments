from django import forms
from payment.forms import CreditPayShipForm
from django.utils.translation import ugettext as _
from payment import signals
from satchmo_store.contact.models import Contact
from satchmo_store.contact.forms import ContactInfoForm

class RealexCreditPayShipForm(CreditPayShipForm, ContactInfoForm):
    """
    Adds fields required by Realex to the Credit form.
    """

    card_holder = forms.CharField(label=_("Card Holder Name"), max_length=60, required=False)

    def __init__(self, request, paymentmodule, *args, **kwargs):
        super(RealexCreditPayShipForm, self).__init__(request, paymentmodule, *args, **kwargs)

        # some Laser cards don't have a ccv
        self.fields['ccv'].required = False

    def clean_ccv(self):
        ccv = self.cleaned_data['ccv']
        if self.cleaned_data['credit_type'] != u'LASER':
            if ccv == '':
                raise forms.ValidationError(_('CCV is mandatory for cards other than Laser.'))
            return CreditPayShipForm.clean_ccv(self)
        return ccv

    def save(self, request, cart, contact, payment_module, data=None):
        """
        Save the order and the credit card information for this orderpayment
        """
        # ContactInfoForm to save contact info
        # This will update the contact info
        self.save_info(contact)
        super(RealexCreditPayShipForm, self).save(request, cart, contact, payment_module, data=None)

        # this is bill
        self.order.street1 = self.cleaned_data['street1']
        self.order.street2 = self.cleaned_data['street2']
        self.order.city = self.cleaned_data['city']
        self.order.postal_code = self.cleaned_data['postal_code']
        self.order.save()
        cc = self.order.credit_card
        cc.card_holder = self.cleaned_data['card_holder']
        cc.save()
        
        signals.form_save.send(RealexCreditPayShipForm, form=self)


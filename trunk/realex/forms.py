from django import forms
from satchmo.payment.forms import CreditPayShipForm
from django.utils.translation import ugettext as _


class RealexCreditPayShipForm(CreditPayShipForm):

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

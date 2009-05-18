from django.db import models
from satchmo.shop.models import Order
from django.utils.translation import ugettext_lazy as _

class RealexPayments(models.Model):
    order = models.ForeignKey(Order)
    realex_merchant_id = models.CharField(_('Realex merchant id'),
        max_length=20)
    realex_order_id = models.CharField(_('Realex order id'), max_length=20,
        help_text="Realex unique order id of this transaction.")
    realex_pasref = models.CharField(_('Realex reference'), max_length=20,
        blank=True, null=True,
        help_text="Realex payments reference for the transaction.")
    realex_authcode = models.CharField(_('Realex authcode'), max_length=20,
        blank=True, null=True,
        help_text='The authcode of the original transaction.')
    paydate = models.DateField(_('Paid on'), auto_now_add=True)
    realex_response_code = models.CharField(max_length=20,
        help_text="Realex response code.")
    realex_response_message = models.CharField(max_length=50,
        help_text='Realex response message.')

    def __unicode__(self):
        return u'%s, authcode: %s, pasref: %s' % (repr(self.order), self.realex_authcode,
            self.realex_pasref)

    class Meta:
        verbose_name_plural = 'Realex payments'


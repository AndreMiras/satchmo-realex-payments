from django.conf.urls.defaults import *
from livesettings import config_get_group

config = config_get_group('PAYMENT_REALEX')

urlpatterns = patterns('',
     (r'^$', 'realex.views.pay_ship_info', {'SSL':config.SSL.value}, 'REALEX_satchmo_checkout-step2'),
     (r'^confirm/$', 'realex.views.confirm_info', {'SSL':config.SSL.value}, 'REALEX_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {'SSL':config.SSL.value}, 'REALEX_satchmo_checkout-success'),
)

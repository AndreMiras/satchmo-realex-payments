from livesettings import config_get_group
from payment.views import confirm, payship

def pay_ship_info(request, SSL=None):
    if SSL: print 'pay_ship_info SSL=', SSL, " SHOULD ONLY BE IN DEBUG MODE!!"
    return payship.credit_pay_ship_info(request, config_get_group('PAYMENT_REALEX'))

def confirm_info(request, SSL=None):
    if SSL: print 'confirm_ship_info SSL=', SSL, " SHOULD ONLY BE IN DEBUG MODE!!"
    return confirm.credit_confirm_info(request, config_get_group('PAYMENT_REALEX'))

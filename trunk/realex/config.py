from livesettings import *
from django.utils.translation import ugettext_lazy as _


# PAYMENT_MODULES = config_get('PAYMENT', 'MODULES')
# PAYMENT_MODULES.add_choice(('PAYMENT_REALEX', 'Realex'))

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_REALEX',
_('Realex Payment Settings'),
# requires=PAYMENT_MODULES,
ordering=102)


# config_register([
config_register_list(

    StringValue(PAYMENT_GROUP,
        'KEY',
        description=_("Module key"),
        hidden=True,
        default = 'REALEX'),

    ModuleValue(PAYMENT_GROUP,
        'MODULE',
        description=_('Implementation module'),
        hidden=True,
        default = 'realex'),

    BooleanValue(PAYMENT_GROUP,
        'SSL',
        description=_("Use SSL for the checkout pages?"),
        default=False),

    BooleanValue(PAYMENT_GROUP,
        'LIVE', # Should this be merged default LIVE Payment Settings ?
        description=_("Accept real payments"),
        help_text=_("False if you want to be in test mode"),
        default=False),

    BooleanValue(PAYMENT_GROUP,
        'DO_POST',
        description=_("Send requests to Realex when in test mode"),
        help_text=_("False if you do not want to post requests to Realex in test mode"),
        default=True),

    StringValue(PAYMENT_GROUP,
        'LABEL',
        description=_('English name for this group on the checkout screens'),
        default = 'Realex Payments',
        help_text = _('This will be passed to the translation utility')),

    BooleanValue(PAYMENT_GROUP,
        'EXTRA_LOGGING',
        description=_("Verbose logs"),
        help_text=_("Add extensive logs during post."),
        default=False),

    StringValue(PAYMENT_GROUP,
        'URL_BASE',
        description=_('The url base used for constructing urlpatterns which will use this module'),
        default = r'^credit/'),

    MultipleStringValue(PAYMENT_GROUP,
        'CREDITCHOICES',
        description=_('Available credit cards'),
        choices = (
            (('AMEX', 'American Express')),
            (('LASER','Laser')),
            (('VISA','Visa')),
            (('MC','Mastercard')),
            (('SWITCH','Switch'))),
        default = ('AMEX', 'LASER', 'VISA', 'MC', 'SWITCH')),

    # MultiStringValue(PAYMENT_GROUP,
    # Could both be used for auth (Realex guys to ask)?
    StringValue(PAYMENT_GROUP,
        'HASHALGO',
        description=_('Prefered Hash Method'),
        choices = (
            (('sha1', 'SHA1')),
            (('md5','MD5'))),
        default = ('sha1')),

    StringValue(PAYMENT_GROUP,
        'CURRENCY_CODE',
        description=_('Currency Code'),
        help_text=_('Currency code for Realex transactions.'),
        default = 'EUR'),

    StringValue(PAYMENT_GROUP,
        'MERCHANT_ID',
        description=_('Your Realex Merchant ID'),
        default="internettest"),

    StringValue(PAYMENT_GROUP,
        'PASSWORD',
        description=_('Your Realex password'),
        default="secret"),

    StringValue(PAYMENT_GROUP,
        'SUB_ACCOUNT',
        description=_('Your Realex Sub-Account to use'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'POST_URL',
        description=_('This is the address to submit live transactions for Realex'),
        default="https://epage.payandshop.com/epage-remote.cgi")

)
# ])

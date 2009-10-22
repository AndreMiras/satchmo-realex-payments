import random
import urllib2
from realex.models import RealexPayments
from time import strftime
from xml.dom import minidom
from django.template import Context, loader
from django.utils.translation import ugettext_lazy as _
from satchmo.payment.utils import record_payment
from satchmo.payment.modules.base import BasePaymentProcessor
import forms
FORM = forms.RealexCreditPayShipForm

class PaymentProcessor(BasePaymentProcessor):
    """
    Realex payment processing module
    this module uses the remote payment rather using redirect one.
    You must have an account (or a test/trial account) in order to use this module
    See Realex developer's guide for additional info.
    """

    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('realex', settings)
        self.demo = True
        if settings.LIVE.value:
            self.demo = False
        self.do_post = True
        if not settings.DO_POST.value:
            self.do_post = False
        if settings.HASHALGO.value == "md5":
            import md5
            self.hashfunc = md5.new
        else:
            import sha
            self.hashfunc = sha.new
        # self.auth = settings.AUTH_TYPE.value

    def createHash(self, s):
        """
        Creates the hash that is needed
        timestamp + '.'+MerchantID + '.'+satchmo_order_id + '.'+amount +'.'+'EUR'+'.'+card_number
        """
        if self.settings.HASHALGO.value == "md5":
            return md5.new(s).hexdigest()
        return sha.new(s).hexdigest()


    def prepareData(self, data):
        # data will contain an order object
        # use this data to create the unique string that will
        # be sent to the payment processor
        self.data = data
        settings = self.settings
        cc = data.credit_card
        contact = data.contact

        amount = int((data.balance * 100).to_integral()) # 2999 = 29.99
        currency = settings.CURRENCY_CODE.value
        cardnumber = cc.decryptedCC # "4111111111111111"
        cardname = cc.card_holder
        cardtype = cc.credit_type
        expdate = "%02i%02i" % (cc.expire_month, cc.expire_year % 1000) # "mmyy"

        # From Realex Payments
        merchant_id = settings.MERCHANT_ID.value
        secret = settings.PASSWORD.value
        sub_account = settings.SUB_ACCOUNT.value

        # The Timestamp is created here and used in the digital signature
        timestamp = strftime("%Y%m%d%H%M%S")
        realex_order_id = timestamp +'-'+ str(random.randint(1,999))
        tmpdigest = self.hashfunc(timestamp
                    +'.'+ merchant_id
                    +'.'+ realex_order_id
                    +'.'+ str(amount)
                    +'.'+ currency
                    +'.'+ cardnumber
        ).hexdigest() 
        digest = self.hashfunc(tmpdigest +'.'+ secret).hexdigest()

        self.bill_to = {
            'full_name': contact.full_name,
            'country': data.bill_country,
        }

        self.ship_to = {
            'country': data.ship_country,
        }

        self.order = {
            'satchmo_order_id': data.id,
            'realex_order_id': realex_order_id,
            'amount': amount,
            'hash': digest,
            'currency': currency,
            'timestamp': timestamp,
            'contact_id': data.contact_id,
            'product_ids': [itm.product_id for itm in data.orderitem_set.all()],
        }

        self.card = {
            'number': cardnumber,
            'expdate': expdate,
            'type': cardtype,
            'card_holder': cc.card_holder, # will Satchmo team add this to default forms somedays ?
            'issue_num': cc.issue_num,
        }

        self.config = {
            'merchant_id': merchant_id,
            'sub_account': sub_account,
            'hash_method': settings.HASHALGO.value,
        }


    def post_xml_request(self, realex_post_url):
        t = loader.get_template('checkout/realex/request.xml')
        c = Context({
            'bill_to' : self.bill_to,
            'ship_to' : self.ship_to,
            'order' : self.order,
            'config' : self.config,
            'card' : self.card,
        })
        request = t.render(c)
        conn = urllib2.Request(url=realex_post_url, data=request)
        f = urllib2.urlopen(conn)

        results = f.read()
        self.log_extra('Posted xml: %s', request)
        self.log_extra('Realex response: %s', results)
        return results


    def parse_xml_reply(self, xml_string):
        """
        Parse xml_string
        Return Realex response code and message
        """
        realex_authcode = ''
        realex_pasref = ''
        try:
            response = minidom.parseString(xml_string)
            doc = response.documentElement
            realex_response_code = \
                doc.getElementsByTagName('result')[0].firstChild.nodeValue
            realex_message = \
                doc.getElementsByTagName('message')[0].firstChild.nodeValue

            # if an error occure authcode and pasref could be missing or empty
            realex_authcode = doc.getElementsByTagName('authcode')
            if realex_authcode and realex_authcode[0].firstChild:
                realex_authcode = realex_authcode[0].firstChild.nodeValue
            else:
                realex_authcode = ''

            realex_pasref = \
                doc.getElementsByTagName('pasref')
            if realex_pasref and realex_pasref[0].firstChild:
                realex_pasref = realex_pasref[0].firstChild.nodeValue
            else:
                realex_pasref = ''
        except Exception, e:
            self.log.error("%s\nCould not parse response: %s", e, response)
            realex_response_code = "Parse Error"
            realex_message = "Could not parse response"

        reply_dict = {
            'code': realex_response_code,
            'message': realex_message,
            'authcode': realex_authcode,
            'pasref': realex_pasref,
        }

        return reply_dict


    def process(self):
        """
        Process payments
        Return True if successful, False if not plus an error message
        """
        if not self.do_post:
            transaction_id = 'TESTING'
            record_payment(self.data, self.settings, amount=self.data.balance, transaction_id=transaction_id)

            realexObj = RealexPayments(
                order = self.data,
                realex_merchant_id = self.config['merchant_id'],
                realex_order_id = self.order['realex_order_id'],
                realex_response_code = '00',
                realex_response_message = 'Test realex order')
            realexObj.save()
            return True, '00', 'Test realex order'
            
        realex_url = self.settings.POST_URL.value
        try:
            results = self.post_xml_request(realex_url)
        except urllib2.HTTPError, e:
            self.log.error("error opening %s\n%s", realex_url, e)
            return(False, 'ERROR', _('Could not reach Realex gateway'))

        reply_dict = self.parse_xml_reply(results)
        code = reply_dict['code']
        message = reply_dict['message']
        success = (code == "00") or \
            (self.demo and (code in ("104"))) # UNABLE TO AUTH (realex payments test only), this code is not more documentated by Realex
        if success:
            transaction_id = self.demo and 'TESTING' or reply_dict['pasref']
            record_payment(self.data, self.settings, amount=self.data.balance, transaction_id=transaction_id)
#        else:
#            record_payment(self.data, self.settings, amount=self.data.balance, transaction_id='PENDING')

        realexObj = RealexPayments(
            order = self.data,
            realex_merchant_id = self.config['merchant_id'],
            realex_order_id = self.order['realex_order_id'],
            realex_pasref = reply_dict['pasref'],
            realex_authcode = reply_dict['authcode'],
            realex_response_code = code,
            realex_response_message = message)
        try:
            realexObj.save()
        except:
            pass

        return success, code, message

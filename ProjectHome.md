## Introduction ##


This is an implementation of [Realex Payments](http://www.realexpayments.com/) as a [Satchmo](http://www.satchmoproject.com/) [custom payment module](http://www.satchmoproject.com/docs/rel/latest/custom-payment.html).

You can find out more regarding its integration with Satchmo there:
https://bitbucket.org/bkroeze/django-bursar/issue/1/create-realex-payment-module

This version of the module is for Satchmo 0.9.
The realex module for Satchmo 0.8 sits in tags/v0.1/


## Install instructions ##


### 1) Check out the code: ###
```
$ svn checkout http://satchmo-realex-payments.googlecode.com/svn/trunk/ realex
```

### 2) Modify your settings ###
In order to enable realex payment processor, you must add realex to your INSTALLED\_APPS.

### 3) Copy the XML template ###
Move request.xml template into templates/shop/checkout/realex/

### 4) Configure Realex payment through settings interface ###
"Realex Payment" section in http://localhost:8000/settings/
"""
This library allows you to quickly and easily use the Loyalicos Web API v2 via Python.
For more information on this library, see the README on GitHub.

For more information on the Loyalicos API, see:

For the user guide, code examples, and more, visit the main docs page:

This file provides the Loyalicos API Client.
"""

from .simplified_http_client import Response
import os
import requests
from .interface import Interface
from .exceptions import *
import json

class LoyalicosAPIClient(Interface):
    """ Loyaicos basic API client Object
        Extend these to add new objects with API interface.

        Use this object to interact with the Loyalicos API

    """

    def __init__(self, api_key=None, user_token={}, host=None, client_id=None, secret=None):
        self.user_token = user_token
        self.host = host 
        self.api_client = client_id 
        self.api_secret = secret 
        # conf = {'LOYALICOS_API_CLIENT': None, 'LOYALICOS_API_SECRET': None, 'LOYALICOS_API_HOST':None, 'LOYALICOS_API_KEY':None }
        # env = json.loads(os.environ.get('LOYALICOS_CONF'))
        conf = {
            'LOYALICOS_API_CLIENT': os.environ.get('LOYALICOS_CLIENT', None),
            'LOYALICOS_API_SECRET': os.environ.get('LOYALICOS_SECRET', None),
            'LOYALICOS_API_HOST': os.environ.get('LOYALICOS_HOST', None),
            'LOYALICOS_API_KEY': os.environ.get('LOYALICOS_API_KEY', None),
        }
        # conf.update(env)
        if self.api_client == None:
            self.api_client = conf.get('LOYALICOS_API_CLIENT')
        if self.api_secret == None:
            self.api_secret = conf.get('LOYALICOS_API_SECRET')
        if self.host == None:
            self.host = conf.get('LOYALICOS_API_HOST')
        self.api_key = api_key 
        if self.api_key == None:
            self.api_key = conf.get('LOYALICOS_API_KEY')
        if self.api_key != None:
            auth = 'Bearer {}'.format(self.api_key)
        else:
            if self.api_client == None or self.api_secret == None:
                raise NoCredentialsFoundError
            else:
                auth_response = requests.get(f'{self.host}/oauth/authapi', auth=requests.auth.HTTPBasicAuth(self.api_client, self.api_secret))
                if auth_response.status_code != 200:
                    raise NoCredentialsFoundError
                auth_result = auth_response.json()
                self.api_key = auth_result.get('token')
                auth = 'Bearer {}'.format(self.api_key)
        super(LoyalicosAPIClient, self).__init__(self.host, auth)
    
    def set_user_token(self, user_token:dict):
        self.user_token.update(user_token)

    def set_from_dict(self, data:dict):
        self.make_body()
        for key in self.json:
            if key in data and data[key] != None and data[key] != [] and data[key] != {}:
                self.__setattr__(key,data[key])

    def clear(self):
        self.__init__()
        self.make_body()

    def make_body(self, format='json'):
        if format=='json':
            self.json = {
            }


class Member(LoyalicosAPIClient):
    """
        Extends API Client to handle Members
    """
    def __init__(self, id='', api_key=None, user_token={}, host=None):
        self.id = id
        self.attributes = {}
        self.stages = {}
        super(Member, self).__init__(api_key, user_token, host)

    """
        Add a Member
    """
    def create(self, alias=None, data={}):
        self.method = 'POST'
        self.path = ['member']
        self.json = {}
        if data != {}:
            self.set_from_dict(data)
        self.make_body()
        self.json.update({"external_id" : alias})
        self.send_request()
        if self.response.status_code != 200:
            if self.response.status_code == 409:
                raise DuplicateKeyForMemberError
            raise HTTPRequestError
        self.access_token = self.response.body

    def make_body(self, format='json'):
        if format=='json':
            self.json = {
            'firstname':self.firstname,
            'f_lastname':self.f_lastname,
            'm_lastname':self.m_lastname,
            'gender':self.gender,
            'birthdate':self.birthdate,
            'address_country':self.address_country,
            'address_zipcode':self.zipcode,
            'email':self.email,
            'phone':self.phone,
            'username':self.username,
            'privacy':self.privacy,
            'terms':self.terms
        }

    """
        Get a Member profile
    """
    def read(self, id=None, user_token={}):
        self.user_token.update(user_token)
        if id != None:
            self.id = id
        self.method = 'GET'
        self.path = ['member', self.id]
        user_auth = {self.user_token['token_type'] : self.user_token['access_token']}
        self.update_headers(user_auth)
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.profile = self.response.body
        [self.__setattr__(key, self.profile[key]) for key in self.profile]
        

    """
        Get a Member statement
    """
    def get_awards(self, user_token={}, filter_dict={}):
        filter_string = '|'.join([f"{v}={filter_dict[v]}" for v in filter_dict])
        if filter_dict != {}:
            self.params = f'filters={filter_string}'
        self.user_token.update(user_token)
        self.method = 'GET'
        self.path = ['member', 'awards', self.id]
        user_auth = {self.user_token['token_type'] : self.user_token['access_token']}
        self.update_headers(user_auth)
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.awards = self.response.body
        

    """
        Get a Member balance per type and code
    """
    def get_balance(self, type="currency", code="points", user_token={}):
        self.user_token.update(user_token)
        self.method = 'GET'
        self.path = ['member', 'profileValue', self.id, type, code]
        user_auth = {self.user_token['token_type'] : self.user_token['access_token']}
        self.update_headers(user_auth)
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.balance = self.response.body

    """
        Post a Signal for the member
    """
    def post_signal(self, signal_data:dict, user_token={}, wait_for_response=False):
        self.user_token.update(user_token)
        signal = Signal(user_token=self.user_token, api_key=self.api_key, host=self.host)
        signal.set_from_dict(signal_data)
        signal.post(member_id=self.id,wait_for_response=wait_for_response)
        return signal

    """
        See if a member has an event type
    """
    def check_event(self,  id=None, user_token={}, search_params={}):
        self.user_token.update(user_token)
        if id != None:
            self.id = id
        self.method = 'POST'
        self.path = ['3PAMI', 'member', 'has_event', self.id]
        self.json = search_params
        user_auth = {self.user_token['token_type'] : self.user_token['access_token']}
        self.update_headers(user_auth)
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.event_check = self.response.body.get('result')
        

    """
        Refresh a member token
    """
    def renew_token(self, user_token={}):
        self.user_token.update(user_token)
        self.method = 'POST'
        self.path = ['oauth', 'refreshToken']
        self.json = {'grant_type' : 'refresh_token', 'refresh_token' : user_token['refresh_token'] }
        self.send_request()
        if self.response.status_code != 200:
            if self.response.status_code == 404:
                raise MemberNotFoundError
            raise HTTPRequestError
        self.access_token = self.response.body
        

    """
        Get a new member token
    """
    def new_token(self, id = None):
        if id != None:
            self.id = id
        self.method = 'POST'
        self.path = ['3PAMI', 'accessToken', self.id]
        self.json = {'grant_type' : 'code', 'client_secret' : self.api_secret }
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.access_token = self.response.body
        

    """
        Set custom attribute
    """
    def set_custom_attribute(self, att_code, att_value, partner_code, id = None):
        if id != None:
            self.id = id
        self.method = 'POST'
        self.path = ['member', 'customAttribute', self.id]
        self.json = {'code' : att_code, 'value' : att_value, 'partner_code' : partner_code }
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        if self.attributes == None:
            self.attributes = {}
        self.attributes[att_code] = self.response.body
        

    """
        Get member stage
    """
    def get_stage(self, stage_family, id = None):
        if id != None:
            self.id = id
        self.method = 'GET'
        self.path = ['member', 'stage', self.id, stage_family]
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        if self.stages == None:
            self.stages = {}
        self.stages[stage_family] = self.response.body

class Event(LoyalicosAPIClient):
    """
        Extends API Client to handle events
    """
    pass

class Signal(LoyalicosAPIClient):
    """
        Extends API Client to handle Signals
    """
    def __init__(self, partner_code='',activity=None, type=None, channel=None,  member_id='', subactivity=None, subtype=None, subchannel=None, currency=None, date_activity=None, items=[], api_key=None, user_token={}, host=None):
        self.partner_code = partner_code
        self.member_id = member_id
        self.activity = activity
        self.type = type
        self.channel = channel
        self.subactivity = subactivity
        self.subtype = subtype
        self.subchannel = subchannel
        self.currency = currency
        self.date_activity = date_activity
        self.items = items
        self.id =""
        self.awards_ids = []
        super(Signal, self).__init__(api_key, user_token, host)


    def make_body(self, format='json'):
        if format=='json':
            self.json = {
                'partner_code': self.partner_code,
                'member_id' : self.member_id,
                'date_activity' : self.date_activity,
                'channel': self.channel,
                'subchannel': self.subchannel,
                'type': self.type,
                'subtype': self.subtype,
                'activity': self.activity,
                'subactivity': self.subactivity,
                'currency': self.currency,
                'items': self.items
                }

    """
        Get a Signal
    """
    def read(self, id=None):
        if id != None:
            self.id = id
        self.method = 'GET'
        self.path = ['signal', self.id]
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.data = self.response.body
        [self.__setattr__(key, self.data[key]) for key in self.data]


    def process_many(self, filters={}):
        """
            Process batch Signal
        """
        if id != None:
            self.id = id
        self.method = 'POST'
        self.path = ['processSignals', 'batch']
        self.json = filters
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.data = self.response.body
        self.awards_ids = self.response.body['awards_ids']


    def process(self, id=None):
        """
            Process One Signal
        """
        if id != None:
            self.id = id
        self.method = 'POST'
        self.path = ['processSignal', self.id]
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.data = self.response.body
        self.awards_ids = self.response.body['awards_ids']


    def cancel(self, id=None):
        """
            Reverse One Signal
        """
        if id != None:
            self.id = id
        self.method = 'POST'
        self.path = ['cancelSignal', self.id]
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.data = self.response.body
        self.new_state = self.response.body['new_state']


    def post(self, member_id='', date_activity=None, wait_for_response=False, user_token={}):
        """
            Send Signal
        """
        self.set_user_token(user_token)
        if member_id != '':
           self.member_id = member_id
        if date_activity != None:
           self.date_activity = date_activity
        self.method = 'POST'
        self.path = ['signal']
        self.make_body('json')
        if self.user_token != {} and self.user_token != None:
            user_auth = {self.user_token.get('token_type', 'Access-Token') : self.user_token.get('access_token', 'Not Provided')}
            self.update_headers(user_auth)
        proccess_header = {'Process-Sync' : str(wait_for_response)}
        self.update_headers(proccess_header)
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.id = self.response.body['signal_id']
        if wait_for_response:
            self.awards_ids = self.response.body['awards_ids']

    def reward(self, member_id='', user_token={}, date_activity=None):
        """
            Send redemption transaction
        """
        self.post(member_id=member_id, user_token=user_token, date_activity=date_activity, wait_for_response=True)

class Award(LoyalicosAPIClient):
    """
        Extends API Client to handle Awards
    """
    def __init__(self, partner_code='',date_received=None, date_activity=None, date_processed=None,  member_id='', rule=None, validity=None, outstanding=None, state=None, type=None, currency_value=None, code=None, subcode=None, kv_desc=None, api_key=None, user_token={}, host=None):
        self.partner_code = partner_code
        self.member_id = member_id
        self.date_received = date_received
        self.date_activity = date_activity
        self.date_processed = date_processed
        self.rule = rule
        self.validity = validity
        self.outstanding = outstanding
        self.state = state
        self.type = type
        self.currency_value = currency_value
        self.id =""
        self.code = code
        self.subcode = subcode
        self.kv_desc = kv_desc
        super(Signal, self).__init__(api_key, user_token, host)


    def make_body(self, format='json'):
        if format=='json':
            self.json = {
                "_key": self.id,
                "_from": self.partner_code,
                "_to": self.member_id,
                "date_received": self.date_received,
                "date_activity": self.date_activity ,
                "date_processed": self.date_processed,
                "rule": self.rule,
                "validity": self.validity,
                "outstanding": self.outstanding,
                "state": self.state,
                "type": self.type,
                "currency_value": self.currency_value ,
                "code": self.code,
                "subcode": self.subcode,
                "kv_desc": self.kv_desc
                }

    """
        Get a Signal
    """
    def read(self, id=None):
        if id != None:
            self.id = id
        self.method = 'GET'
        self.path = ['signal', self.id]
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.data = self.response.body
        [self.__setattr__(key, self.data[key]) for key in self.data]


    def post(self, member_id='', date_activity=None, wait_for_response=False, user_token={}):
        """
            Send Signal
        """
        self.set_user_token(user_token)
        if member_id != '':
           self.member_id = member_id
        if date_activity != None:
           self.date_activity = date_activity
        self.method = 'POST'
        self.path = ['signal']
        self.make_body('json')
        if self.user_token != {} and self.user_token != None:
            user_auth = {self.user_token.get('token_type', 'Access-Token') : self.user_token.get('access_token', 'Not Provided')}
            self.update_headers(user_auth)
        proccess_header = {'Process-Sync' : str(wait_for_response)}
        self.update_headers(proccess_header)
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.id = self.response.body['signal_id']
        if wait_for_response:
            self.awards_ids = self.response.body['awards_ids']

    def reward(self, member_id='', user_token={}, date_activity=None):
        """
            Send redemption transaction
        """
        self.post(member_id=member_id, user_token=user_token, date_activity=date_activity, wait_for_response=True)


class Partner(LoyalicosAPIClient):
    """
        Extends API Client to handle Partners
    """
    def __init__(self, api_key=None, host=None,
        partner_code='',
        name='',
        desc='',
        logo='',
        email='',
        phone=''):
        self.partner_code=partner_code
        self.name=name
        self.desc=desc
        self.logo=logo
        self.email=email
        self.phone=phone
        super(Partner, self).__init__(api_key, {}, host)

    def create(self, data={}):
        self.method = 'POST'
        self.path = ['partner']
        self.json = {}
        self.make_body()
        self.json.update(data)
        self.send_request()
        if self.response.status_code != 200:
            if self.response.status_code == 409:
                raise DuplicateKeyForPartnerError
            raise HTTPRequestError
        self.partner_code = self.response.body['partner_id']

    def make_body(self, format='json'):
        if format=='json':
            self.json = {
                'partner_code':self.partner_code,
                'name':self.name,
                'desc':self.desc,
                'logo':self.logo,
                'name':self.name,
                'email':self.email,
                'phone':self.phone,
            }

    """
        Get a Partner profile
    """
    def read(self, partner_code=''):
        if partner_code != None:
            self.partner_code = partner_code
        self.method = 'GET'
        self.path = ['partner', self.partner_code]
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.profile = self.response.body
        [self.__setattr__(key, self.profile[key]) for key in self.profile]


class Currency(LoyalicosAPIClient):
    """
        Extends API Client to handle Currencies
    """
    def __init__(self, api_key=None, host=None,
        code='',
        name='',
        desc='',
        family=''):
        self.code=code
        self.name=name
        self.desc=desc
        self.family=family
        super(Currency, self).__init__(api_key, {}, host)

    def create(self, data={}):
        self.method = 'POST'
        self.path = ['currency']
        self.json = {}
        self.make_body()
        self.json.update(data)
        self.send_request()
        if self.response.status_code != 200:
            if self.response.status_code == 409:
                raise DuplicateKeyForPartnerError
            raise HTTPRequestError
        self.id = self.response.body['currency_id']

    def make_body(self, format='json'):
        if format=='json':
            self.json = {
                'code':self.code,
                'name':self.name,
                'desc':self.desc,
                'family':self.family
            }

    """
        Get a Currency profile
    """
    def read(self, code=''):
        if code != None:
            self.code = code
        self.method = 'GET'
        self.path = ['currency', self.code]
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.profile = self.response.body
        [self.__setattr__(key, self.profile[key]) for key in self.profile]




class Achievement(LoyalicosAPIClient):
    """
        Extends API Client to handle Achievements
    """
    def __init__(self, api_key=None, host=None,
        partner_code='',
        code='',
        name='',
        desc='',
        notification_text='',
        family='',
        order_index=''):
        self.partner_code=partner_code
        self.code=code
        self.name=name
        self.desc=desc
        self.notification_text=notification_text
        self.family=family
        self.order_index=order_index
        super(Achievement, self).__init__(api_key, {}, host)

    def create(self, data={}):
        self.method = 'POST'
        self.path = ['achievement']
        self.json = {}
        self.make_body()
        self.json.update(data)
        self.send_request()
        if self.response.status_code != 200:
            if self.response.status_code == 409:
                raise DuplicateKeyForPartnerError
            raise HTTPRequestError
        self.id = self.response.body['achievement_id']

    def make_body(self, format='json'):
        if format=='json':
            self.json = {
                'partner_code':self.partner_code,
                'code':self.code,
                'name':self.name,
                'desc':self.desc,
                'notification_text':self.notification_text,
                'order_index':self.order_index,
                'family':self.family
            }

    """
        Get an Achievement profile
    """
    def read(self, code=''):
        if code != None:
            self.code = code
        self.method = 'GET'
        self.path = ['achievement', self.code]
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.profile = self.response.body
        [self.__setattr__(key, self.profile[key]) for key in self.profile]

class Badge(LoyalicosAPIClient):
    """
        Extends API Client to handle Badges
    """
    def __init__(self, api_key=None, host=None,
        code='',
        name='',
        desc='',
        family='',
        partner_code='',
        order_index=0,
        max_repetitions=-1,
        valid_state_pending=False,
        valid_state_expired=False,
        valid_state_redeemed=False):
        self.valid_state_redeemed=str(valid_state_redeemed)
        self.valid_state_expired=str(valid_state_expired)
        self.valid_state_pending=str(valid_state_pending)
        self.max_repetitions=max_repetitions
        self.order_index=order_index
        self.code=code
        self.partner_code=partner_code
        self.name=name
        self.desc=desc
        self.family=family
        super(Badge, self).__init__(api_key, {}, host)

    def create(self, data={}):
        self.method = 'POST'
        self.path = ['badge']
        self.json = {}
        self.make_body()
        self.json.update(data)
        self.send_request()
        if self.response.status_code != 200:
            if self.response.status_code == 409:
                raise DuplicateKeyForPartnerError
            raise HTTPRequestError
        self.id = self.response.body['badge_id']

    def make_body(self, format='json'):
        if format=='json':
            self.json = {
                'code':self.code,
                'name':self.name,
                'desc':self.desc,
                'family':self.family,
                'partner_code' : self.partner_code,
                'order_index' : self.order_index,
                'max_repetitions' : self.max_repetitions,
                'valid_state_redeemed' : self.valid_state_redeemed,
                'valid_state_expired' : self.valid_state_expired,
                'valid_state_pending' : self.valid_state_pending
            }

    """
        Get a badge profile
    """
    def read(self, code=''):
        if code != None:
            self.code = code
        self.method = 'GET'
        self.path = ['badge', self.code]
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.profile = self.response.body
        [self.__setattr__(key, self.profile[key]) for key in self.profile]

        
class Product(LoyalicosAPIClient):
    """
        Extends API Client to handle Products
    """
    def __init__(self, api_key=None, host=None,
        code='',
        name='',
        desc='',
        family='',
        partner_code='',
        order_index=0,
        max_repetitions=-1,
        valid_state_pending=False,
        valid_state_expired=False,
        valid_state_redeemed=False):
        self.valid_state_redeemed=str(valid_state_redeemed)
        self.valid_state_expired=str(valid_state_expired)
        self.valid_state_pending=str(valid_state_pending)
        self.max_repetitions=max_repetitions
        self.order_index=order_index
        self.code=code
        self.partner_code=partner_code
        self.name=name
        self.desc=desc
        self.family=family
        super(Product, self).__init__(api_key, {}, host)

    def create(self, data={}):
        self.method = 'POST'
        self.path = ['product']
        self.json = {}
        self.make_body()
        self.json.update(data)
        self.send_request()
        if self.response.status_code != 200:
            if self.response.status_code == 409:
                raise DuplicateKeyForPartnerError
            raise HTTPRequestError
        self.id = self.response.body['product_id']

    def make_body(self, format='json'):
        if format=='json':
            self.json = {
                'code':self.code,
                'name':self.name,
                'desc':self.desc,
                'family':self.family,
                'partner_code' : self.partner_code,
                'order_index' : self.order_index,
                'max_repetitions' : self.max_repetitions,
                'valid_state_redeemed' : self.valid_state_redeemed,
                'valid_state_expired' : self.valid_state_expired,
                'valid_state_pending' : self.valid_state_pending
            }

    """
        Get a product profile
    """
    def read(self, code=''):
        if code != None:
            self.code = code
        self.method = 'GET'
        self.path = ['product', self.code]
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.profile = self.response.body
        [self.__setattr__(key, self.profile[key]) for key in self.profile]


class Rule(LoyalicosAPIClient):
    """
        Extends API Client to handle Rules
    """
    def __init__(self, 
            partner_code='',
            activity=None, 
            type=None, 
            channel=None,  
            subactivity=None, 
            subtype=None, 
            subchannel=None, 
            currency=None, 
            name='',
            desc='',
            code='',
            action='',
            give='',
            extend='',
            take='',
            require='',
            give_rule={},
            require_rule={},
            take_rule={},
            validity_rule={},
            valid_from='',
            valid_to='',
            api_key=None, 
            host=None):
        self.name = name
        self.desc = desc
        self.code = code
        self.action = action
        self.give = give
        self.extend = extend
        self.take = take
        self.require = require
        self.give_rule = give_rule
        self.require_rule = require_rule
        self.take_rule = take_rule
        self.validity_rule = validity_rule
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.activity = activity
        self.type = type
        self.channel = channel
        self.subactivity = subactivity
        self.subtype = subtype
        self.subchannel = subchannel
        self.currency = currency
        self.partner_code = partner_code
        self.id =""
        super(Rule, self).__init__(api_key, {}, host)


    def make_body(self, format='json'):
        if format=='json':
            self.json = {
            'name':self.name,
            'desc':self.desc,
            'code':self.code,
            'action':self.action,
            'give':self.give,
            'extend':self.extend,
            'take':self.take,
            'require':self.require,
            'give_rule':self.give_rule,
            'require_rule':self.require_rule,
            'take_rule':self.take_rule,
            'validity_rule':self.validity_rule,
            'valid_from':self.valid_from,
            'valid_to':self.valid_to,
            'activity':self.activity,
            'type':self.type,
            'channel':self.channel,
            'subactivity':self.subactivity,
            'subtype':self.subtype,
            'subchannel':self.subchannel,
            'currency':self.currency,
            'partner_code':self.partner_code
        }

    """
        Get a Rule
    """
    def read(self, code=None):
        if code != None:
            self.code = code
        self.method = 'GET'
        self.path = ['rule', self.code]
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.data = self.response.body
        [self.__setattr__(key, self.data[key]) for key in self.data]


    def create(self):
        """
            Send Rule
        """
        self.method = 'POST'
        self.path = ['rule']
        self.make_body('json')
        self.send_request()
        if self.response.status_code != 200:
            raise HTTPRequestError
        self.id = self.response.body['rule_id']

class GiveRule(Rule):
    """
        Extends API Client to handle GiveRules
    """
    def __init__(self, 
            partner_code='',
            activity=None, 
            type=None, 
            channel=None,  
            subactivity=None, 
            subtype=None, 
            subchannel=None, 
            currency=None, 
            name='',
            desc='',
            code='',
            give='',
            give_rule={},
            valid_from='',
            valid_to='',
            api_key=None, 
            host=None):
        self.name = name
        self.desc = desc
        self.code = code
        self.action = "reward"
        self.give = give
        self.give_rule = give_rule
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.activity = activity
        self.type = type
        self.channel = channel
        self.subactivity = subactivity
        self.subtype = subtype
        self.subchannel = subchannel
        self.currency = currency
        self.partner_code = partner_code
        self.id =""
        self.make_body()
        data = self.json
        super(GiveRule, self).__init__(api_key, {}, host)
        self.set_from_dict(data)


    def make_body(self, format='json'):
        if format=='json':
            self.json = {
            'name':self.name,
            'desc':self.desc,
            'code':self.code,
            'action':self.action,
            'give':self.give,
            'give_rule':self.give_rule,
            'valid_from':self.valid_from,
            'valid_to':self.valid_to,
            'activity':self.activity,
            'type':self.type,
            'channel':self.channel,
            'subactivity':self.subactivity,
            'subtype':self.subtype,
            'subchannel':self.subchannel,
            'currency':self.currency,
            'partner_code':self.partner_code,
        }

class GoalRule(Rule):
    """
        Extends API Client to handle GiveRules
    """
    def __init__(self, 
            partner_code='',
            activity=None, 
            type=None, 
            channel=None,  
            subactivity=None, 
            subtype=None, 
            subchannel=None, 
            currency=None, 
            name='',
            desc='',
            code='',
            give='',
            require='',
            give_rule={},
            require_rule={},
            valid_from='',
            valid_to='',
            api_key=None, 
            host=None):
        self.name = name
        self.desc = desc
        self.code = code
        self.action = 'goal'
        self.give = give
        self.require = require
        self.give_rule = give_rule
        self.require_rule = require_rule
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.activity = activity
        self.type = type
        self.channel = channel
        self.subactivity = subactivity
        self.subtype = subtype
        self.subchannel = subchannel
        self.currency = currency
        self.partner_code = partner_code
        self.id =""
        self.make_body()
        data = self.json
        super(GoalRule, self).__init__(api_key, {}, host)
        self.set_from_dict(data)


    def make_body(self, format='json'):
        if format=='json':
            self.json = {
            'name':self.name,
            'desc':self.desc,
            'code':self.code,
            'action':self.action,
            'give':self.give,
            'require':self.require,
            'give_rule':self.give_rule,
            'require_rule':self.require_rule,
            'valid_from':self.valid_from,
            'valid_to':self.valid_to,
            'activity':self.activity,
            'type':self.type,
            'channel':self.channel,
            'subactivity':self.subactivity,
            'subtype':self.subtype,
            'subchannel':self.subchannel,
            'currency':self.currency,
            'partner_code':self.partner_code,
        }

class ExchangeRule(Rule):
    """
        Extends API Client to handle Rules
    """
    def __init__(self, 
            partner_code='',
            activity=None, 
            type=None, 
            channel=None,  
            subactivity=None, 
            subtype=None, 
            subchannel=None, 
            currency=None, 
            name='',
            desc='',
            code='',
            give='',
            take='',
            give_rule={},
            take_rule={},
            valid_from='',
            valid_to='',
            api_key=None, 
            host=None):
        self.name = name
        self.desc = desc
        self.code = code
        self.action = 'exchange'
        self.give = give
        self.take = take
        self.give_rule = give_rule
        self.take_rule = take_rule
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.activity = activity
        self.type = type
        self.channel = channel
        self.subactivity = subactivity
        self.subtype = subtype
        self.subchannel = subchannel
        self.currency = currency
        self.partner_code = partner_code
        self.id =""
        self.make_body()
        data = self.json
        super(ExchangeRule, self).__init__(api_key, {}, host)
        self.set_from_dict(data)


    def make_body(self, format='json'):
        if format=='json':
            self.json = {
            'name':self.name,
            'desc':self.desc,
            'code':self.code,
            'action':self.action,
            'give':self.give,
            'take':self.take,
            'give_rule':self.give_rule,
            'take_rule':self.take_rule,
            'valid_from':self.valid_from,
            'valid_to':self.valid_to,
            'activity':self.activity,
            'type':self.type,
            'channel':self.channel,
            'subactivity':self.subactivity,
            'subtype':self.subtype,
            'subchannel':self.subchannel,
            'currency':self.currency,
            'partner_code':self.partner_code,
        }

class ValidityRule(Rule):
    """
        Extends API Client to handle Rules
    """
    def __init__(self, 
            partner_code='',
            activity=None, 
            type=None, 
            channel=None,  
            subactivity=None, 
            subtype=None, 
            subchannel=None, 
            currency=None, 
            name='',
            desc='',
            code='',
            extend='',
            validity_rule={},
            value_from=-1,
            value_to=-1,
            max_repetitions=-1,
            max_value=-1,
            valid_from='',
            valid_to='',
            api_key=None, 
            host=None):
        self.name = name
        self.desc = desc
        self.code = code
        self.action = 'validity'
        self.extend = extend
        self.validity_rule = validity_rule
        self.value_from = value_from
        self.value_to = value_to
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.activity = activity
        self.type = type
        self.channel = channel
        self.subactivity = subactivity
        self.subtype = subtype
        self.subchannel = subchannel
        self.currency = currency
        self.partner_code = partner_code
        self.max_repetitions = max_repetitions
        self.max_value = max_value
        self.id =""
        self.make_body()
        data = self.json
        super(ValidityRule, self).__init__(api_key, {}, host)
        self.set_from_dict(data)


    def make_body(self, format='json'):
        if format=='json':
            self.json = {
            'name':self.name,
            'desc':self.desc,
            'code':self.code,
            'action':self.action,
            'extend':self.extend,
            'validity_rule':self.validity_rule,
            'value_from':self.value_from,
            'value_to':self.value_to,
            'valid_from':self.valid_from,
            'valid_to':self.valid_to,
            'activity':self.activity,
            'type':self.type,
            'channel':self.channel,
            'subactivity':self.subactivity,
            'subtype':self.subtype,
            'subchannel':self.subchannel,
            'currency':self.currency,
            'partner_code':self.partner_code,
            'max_repetitions':self.max_repetitions,
            'max_value':self.max_value
        }


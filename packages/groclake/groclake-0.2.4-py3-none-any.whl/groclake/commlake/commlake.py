from ..utillake import Utillake
import requests
from ..config import GUPSHUP_URL



class Commlake:
    def __init__(self):
        self.utillake = Utillake()
        self.commlake_id = None
        self.params = {}

    def send_sms(self, payload):
        sms_params = {
            'message': payload.get('message'),
            'mobile': payload.get('mobile'),
            'userid': payload.get('userid'),
            'dltTemplateId': payload.get('dltTemplateId'),
            'principalEntityId': payload.get('principalEntityId'),
            'password': payload.get('password')
        }
        response = self.send_otp_to_customer(sms_params)
        if response:
            return {"message": "OTP Sent Successfully"}


    def send_otp_to_customer(self, params):
        otp_params = {
            'method': 'SendMessage', 'msg_type': 'TEXT', 'v': '1.1', 'format': 'text', 'auth_scheme': 'plain',
            'userid': params.get('userid'), 'principalEntityId': params.get('principalEntityId'),
            'password': params.get('password'), 'dltTemplateId': params.get('dltTemplateId'),
            'send_to': int(params.get('mobile')), 'msg': params.get('message'), 'mask': 'PLTCAI'
        }

        gupshup_url = GUPSHUP_URL
        response = requests.get(gupshup_url, params=otp_params)

        if 'success' in response.text:
            return True
        else:
            raise Exception('OTP Failure')

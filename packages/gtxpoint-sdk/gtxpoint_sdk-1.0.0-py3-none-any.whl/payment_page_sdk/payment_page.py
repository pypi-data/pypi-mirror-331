
import urllib.parse
from payment_page_sdk.signature_handler import SignatureHandler
from payment_page_sdk.payment import Payment
from payment_page_sdk.cipher import AESCipher

class PaymentPage(object):
    """Class PaymentPage for URL building

    Attributes:
        __baseUrl - Base URL for payment
        __signatureHandler - Signature Handler (check, sign)
    """
    __baseUrl = ''
    __signatureHandler = None

    def __init__(self, signature_handler: SignatureHandler, base_url: str = ''):
        """
        PaymentPage constructor

        :param signature_handler:
        :param base_url:
        """
        self.__signatureHandler = signature_handler

        if base_url:
            self.__baseUrl = base_url

    def get_url(self, payment: Payment, encryption_key: str ='') -> str:
        """
        Get full URL for payment

        :param Payment payment:
        :return:
        """
        payload = '/payment?' + urllib.parse.urlencode(payment.get_params()) \
            + '&signature=' + urllib.parse.quote_plus(self.__signatureHandler.sign(payment.get_params()))
        
        if encryption_key:
            crypt = AESCipher(encryption_key)
            encrypted = crypt.encrypt(payload)
            return self.__baseUrl + '/' + payment.project_id + '/' + encrypted
        

        return self.__baseUrl + payload
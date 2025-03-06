import requests
import aiohttp
import json
from anura.direct.result import DirectResult
from anura.direct.exceptions import AnuraException, AnuraClientException, AnuraServerException
from typing import Awaitable
from urllib.parse import quote, quote_plus, urlencode

class AnuraDirect:
    """
    An Anura Direct API client.
    """

    __instance = ''
    __use_https = True
    __api_url = 'https://direct.anura.io/direct.json'

    def __init__(self, instance: str, use_https: bool = True):
        self.__instance = instance
        self.__use_https = use_https
        
        if (self.__use_https):
            self.__api_url = 'https://direct.anura.io/direct.json'
        else:
            self.__api_url = 'http://direct.anura.io/direct.json'

    def get_result(
        self, 
        ip_address: str,
        user_agent: str = '', 
        app: str = '', 
        device: str = '',
        source: str = '',
        campaign: str = '', 
        additional_data: dict = {}
    ) -> DirectResult:
        """
        Gets a result from Anura Direct, or raises an exception if an error occurred.
        """
        
        params = {
            'instance': self.__instance,
            'ip': ip_address
        }

        if (source):
            params['source'] = quote(source)
        if (campaign):
            params['campaign'] = quote(campaign)
        if (user_agent):
            params['ua'] = quote(user_agent)
        if (app):
            params['app'] = quote(app)
        if (device):
            params['device'] = quote(device)
        if (len(additional_data) > 0):
            params['additional'] = self.__get_additional_data_string(additional_data)

        response = requests.get(self.__api_url, params)

        is_server_error = response.status_code in range(500, 600)
        if is_server_error:
            raise AnuraServerException("Anura Server Error: " + response.status_code)

        try:
            result = response.json()
        except:
            raise AnuraException("Unknown error occurred")

        is_client_error = response.status_code in range(400, 500)
        if is_client_error:
            raise AnuraClientException(result['error'] or 'Client side error occurred')

        direct_result = DirectResult(result['result'], result['mobile'])
        if 'rule_sets' in result:
            direct_result.rule_sets = result['rule_sets']
        if 'invalid_traffic_type' in result:
            direct_result.invalid_traffic_type = result['invalid_traffic_type']

        return direct_result

    async def get_result_async(
        self, 
        session: aiohttp.ClientSession, 
        ip_address: str,
        user_agent: str = '', 
        app: str = '', 
        device: str = '',
        source: str = '',
        campaign: str = '', 
        additional_data: dict = {}
    ) -> Awaitable[DirectResult]:
        """
        Asynchronously gets a result from Anura Direct, or raises an exception if an error occurred.
        """

        params = {
            'instance': self.__instance,
            'ip': ip_address
        }

        if (source):
            params['source'] = quote(source)
        if (campaign):
            params['campaign'] = quote(campaign)
        if (user_agent):
            params['ua'] = quote(user_agent)
        if (app):
            params['app'] = quote(app)
        if (device):
            params['device'] = quote(device)
        if (len(additional_data) > 0):
            params['additional'] = self.__get_additional_data_string(additional_data)

        async with session as client:
            async with client.get(url=self.__api_url, params=params) as response:
                is_server_error = response.status in range(500, 600)
                if is_server_error:
                    raise AnuraServerException("Anura Server Error: " + response.status)
                
                try:
                    result = await response.json()
                except:
                    raise AnuraException("Unknown error occurred")

                is_client_error = response.status in range(400, 500)
                if is_client_error:
                    raise AnuraClientException(result['error'] or 'Client error occurred')
                
                direct_result = DirectResult(result['result'], result['mobile'])
                if 'rule_sets' in result:
                    direct_result.rule_sets = result['rule_sets']
                if 'invalid_traffic_type' in result:
                    direct_result.invalid_traffic_type = result['invalid_traffic_type']
                
                return direct_result

    @property
    def instance(self) -> str:
        return self.__instance

    @instance.setter
    def instance(self, instance: str) -> None:
        self.__instance = instance

    @property
    def use_https(self) -> bool:
        return self.__use_https

    @use_https.setter
    def use_https(self, use_https: bool) -> None:
        self.__use_https = use_https
        if (self.__use_https):
            self.__api_url = 'https://direct.anura.io/direct.json'
        else:
            self.__api_url = 'http://direct.anura.io/direct.json'
        
    def __get_additional_data_string(self, additional_data: dict) -> str:
        if (len(additional_data) <= 0):
            return ''
        
        additional_data_string = json.dumps(additional_data)
        return additional_data_string
"""Manages authentication and error handling"""

from aiohttp import ClientSession
import json
import base64
import logging

from . import endpoints, exceptions


#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36', 'Referer': 'https://connect-web.froeling.com/'}
# Seems like user-agent and referer are not required

class Session:
    user_id: int = None
    token: str = None
    def __init__(self,
                 username: str=None, password: str=None, token: str=None,
                 auto_reauth: bool=False,
                 token_callback=None,
                 lang: str = 'en',
                 logger: logging.Logger=None,
                 clientsession: ClientSession=None
                 ):
        assert token or (username and password), "Set either token or username and password."
        assert not (auto_reauth and not (username and password)), "Set username and password to use auto_reauth."

        self.clientsession = clientsession or ClientSession()
        self._headers = {'Accept-Language': lang }
        self.username = username
        self.password = password
        self.auto_reauth = auto_reauth
        self.token_callback = token_callback


        if token:
            self.set_token(token)

        self._logger = logger or logging.getLogger(__name__)
        self._reauth_previous = False # Did the previous request result in renewing the token?

    async def close(self):
        await self.clientsession.close()

    def set_token(self, token: str):
        """Sets the token used in Authorization and updates/sets user-id
        :param token The bearer token"""
        self._headers['Authorization'] = token
        try:
            self.user_id = json.loads(base64.b64decode(token.split('.')[1] + "==").decode("utf-8"))['userId']
        except:
            raise ValueError("Token is in an invalid format.")
        if self.token_callback and self.token:  # Only run when overwriting existing token
            self.token = token
            self.token_callback(token)
        else:
            self.token = token

    async def login(self) -> dict:
        """Gets a token using username and password
        :return: Json sent by server (includes userdata)"""
        data = {'osType': 'web', 'username': self.username, 'password': self.password}
        async with await self.clientsession.post(endpoints.LOGIN, json=data) as res:
            if res.status != 200:
                raise exceptions.AuthenticationError(f'Server returned {res.status}: "{await res.text()}"')
            self.set_token(res.headers['Authorization'])
            userdata = await res.json()
        self._logger.debug("Logged in with username and password.")
        return userdata

    async def request(self, method, url, headers=None, **kwargs):
        """

        :param method:
        :param url:
        :param headers: Additional headers used in the request
        :param kwargs:
        """
        self._logger.debug(f'Sent %s: %s', method.upper(), url)
        request_headers = self._headers
        if headers:
            request_headers |= headers

        try:
            async with await self.clientsession.request(method, url, headers=request_headers, **kwargs) as res:
                if 299 >= res.status >= 200:
                    r = await res.text()
                    self._logger.debug('Got %s', r)
                    self._reauth_previous = False
                    return await res.json()

                if res.status == 401:
                    if self.auto_reauth:
                        if self._reauth_previous:
                            raise exceptions.AuthenticationError("Reauth did not work.", await res.text())
                        self._logger.info('Error %s, renewing token...', await res.text())
                        await self.login()
                        self._logger.info('Reauthorized.')
                        self._reauth_previous = True
                        return await self.request(method, url, **kwargs)
                    else:
                        self._logger.error("Request unauthorized")
                        raise exceptions.AuthenticationError("Request not authorized: ", await res.text())
                else:
                    error_data = await res.text()
                    raise exceptions.NetworkError("Unexpected return code", status=res.status, url=res.url, res=error_data)

        except json.decoder.JSONDecodeError as e:
            raise exceptions.ParsingError(e.msg, e.doc, e.pos, url)

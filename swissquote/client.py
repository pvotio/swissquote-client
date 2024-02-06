from typing import Union

from swissquote import request


class SwissQuote:

    BASE_URL = "https://bankingapi.swissquote.ch/am-interface-v2/api/v1/"

    def __init__(self, token: str, max_retries: int, backoff_factor: float) -> None:
        self.req = request.init_session(token, max_retries, backoff_factor)
        
    def request(self, url):
        resp = self.req.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_managed_clients(self) -> list:
        url = self.BASE_URL + "clients"
        return self.request(url)

    def get_positions(self, clientid: Union[int, str]):
        url = self.BASE_URL + f"clients/{clientid}/positions"
        return self.request(url)

    def get_transactions(self, clientid: Union[int, str]):
        url = self.BASE_URL + f"clients/{clientid}/transactions"
        return self.request(url)

    def get_buyingpower(self, clientid: Union[int, str], currency: str) -> dict:
        url = self.BASE_URL + f"clients/{clientid}/buyingPower/{currency}"
        return self.request(url)

    def get_lists(self) -> dict:
        url = self.BASE_URL + f"lists/"
        return self.request(url)

from typing import Optional, Union

from swissquote import request


class SwissQuote:

    BASE_URL = "https://bankingapi.swissquote.ch/am-interface-v2/api/v1/"

    def __init__(self, token: str, max_retries: int, backoff_factor: float) -> None:
        self.req = request.init_session(token, max_retries, backoff_factor)

    def request(self, url: str) -> Union[list, dict]:
        resp = self.req.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_managed_clients(self) -> list:
        url = self.BASE_URL + "clients"
        return self.request(url)

    def get_positions(self, clientid: Union[int, str]) -> dict:
        url = self.BASE_URL + f"clients/{clientid}/positions"
        return self.request(url)

    def get_transactions(
        self, clientid: Union[int, str], page: Optional[int] = None
    ) -> dict:
        url = self.BASE_URL + f"clients/{clientid}/transactions"
        if page:
            url = url + f"?page={page}"

        return self.request(url)

    def get_buyingpower(self, clientid: Union[int, str], currency: str) -> dict:
        url = self.BASE_URL + f"clients/{clientid}/buyingPower/{currency}"
        return self.request(url)

    def get_rates(self, date: Optional[str]) -> dict:
        url = self.BASE_URL + "clients/rates"
        if date:
            url = url + f"?date={date}"

        return self.request(url)

    def get_staticlists(self) -> dict:
        url = self.BASE_URL + "lists/"
        return self.request(url)

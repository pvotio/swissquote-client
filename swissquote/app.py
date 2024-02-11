import threading

from swissquote.client import SwissQuote


class App:
    def __init__(self, *args, **kwargs):
        self.data = {}
        self.clients = []
        self.client = SwissQuote(*args, **kwargs)

    def fetch(self) -> dict:
        self.clients = self.client.get_managed_clients()
        self.data["clients"] = self.clients

        threads = []
        for func in [
            self.fetch_clients_buyingpowers,
            self.fetch_clients_positions,
            self.fetch_clients_transactions,
        ]:
            thread = threading.Thread(target=func)
            threads.append(thread)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        return self.data

    def fetch_clients_transactions(self) -> None:
        transactions = {}
        for client in self.clients:
            clientid = client["clientId"]
            transactions[clientid] = self._fetch_client_transactions(clientid)

        self.data["transactions"] = transactions

    def _fetch_client_transactions(self, clientid) -> list:
        page = 1
        transactions = []
        while True:
            resp = self.client.get_transactions(clientid, page)
            if not resp["totalNumberOfPages"]:
                return transactions

            transactions.append(resp)
            if resp["totalNumberOfPages"] == resp["page"]:
                return transactions

            page += 1

    def fetch_clients_positions(self) -> None:
        positions = {}
        for client in self.clients:
            clientid = client["clientId"]
            positions[clientid] = self.client.get_positions(clientid)

        self.data["positions"] = positions

    def fetch_clients_buyingpowers(self) -> None:
        buyingpowers = {}
        for client in self.clients:
            clientid = client["clientId"]
            currency = client["referenceCurrency"]
            buyingpowers[clientid] = self.client.get_buyingpower(clientid, currency)

        self.data["buyingpowers"] = buyingpowers

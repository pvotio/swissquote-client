import datetime

import pandas as pd

from config import logger


class Agent:
    def __init__(self, data: dict) -> None:
        self.dfs = {}
        self.raw_data = data
        self.data = {"securities": []}
        self.clients = data["clients"]

    def transform(self) -> pd.DataFrame:
        logger.info("Starting data transformation.")
        try:
            self.transform_transactions()
            self.transform_positions()
            self.init_dfs()
        except Exception as e:
            logger.error(f"Data transformation failed. Error: {e}")
            raise

        logger.info("Data transformation completed successfully.")
        logger.debug(f"\n{self.dfs}")
        return self.dfs

    def init_dfs(self):
        for name, data in self.data.items():
            self.dfs[name] = pd.DataFrame(data)
            if name == "securities":
                self.dfs[name].drop_duplicates(inplace=True)

            self.add_timestamp(self.dfs[name])

    def transform_transactions(self):
        self.data["transactions"] = []
        for clientid, data in self.raw_data["transactions"].items():
            for txblock in data:
                if not txblock["transactions"]:
                    continue

                txs = self._transform_client_transactions(
                    clientid, txblock["transactions"]
                )
                self.data["transactions"].extend(txs)
                self.data["securities"].extend(txblock["securities"])

    def _transform_client_transactions(self, clientid, transactions):
        txs = [{"clientId": clientid, **tx} for tx in transactions]
        return txs

    def transform_positions(self):
        self.data["positions"] = []
        for clientid, data in self.raw_data["positions"].items():
            if not data["positions"]:
                continue

            positions = self._transform_client_positions(clientid, data["positions"])
            self.data["positions"].extend(positions)
            self.data["securities"].extend(data["securities"])

    def _transform_client_positions(self, clientid, positions):
        psn = []
        for position in positions:
            _position = {"clientId": clientid, **position}
            if "averageBuyCosts" in _position:
                for curr, price in _position["averageBuyCosts"].items():
                    _position[f"averageBuyCosts_{curr}"] = price

                del _position["averageBuyCosts"]
            psn.append(_position)

        return psn

    @staticmethod
    def add_timestamp(dataframe) -> None:
        try:
            dataframe["timestamp_created_utc"] = datetime.datetime.utcnow()
        except Exception as e:
            logger.error(f"Failed to add timestamps. Error: {e}")
            raise

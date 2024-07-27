import datetime

import pandas as pd

from config import logger
from transformer.columns import COLUMNS


class Agent:
    def __init__(self, data: dict) -> None:
        self.dfs = {}
        self.raw_data = data
        self.data = {"securities": []}
        self.clients = data["clients"]

    def transform(self) -> pd.DataFrame:
        logger.info("Starting data transformation.")
        try:
            self.transform_staticlists()
            self.transform_transactions()
            self.transform_positions()
            self.transform_buyingpowers()
            self.init_dfs()
        except Exception as e:
            logger.error(f"Data transformation failed. Error: {e}")
            raise

        logger.info("Data transformation completed successfully.")
        logger.debug(f"\n{self.dfs}")
        return self.dfs

    def init_dfs(self):
        self._init_dfs()
        self._init_client_df()
        self._init_buyingpowers_df()

    def _init_dfs(self):
        for name, data in self.data.items():
            if name == "buyingpowers":
                continue

            if not data:
                continue

            self.dfs[name] = pd.DataFrame(data)
            self.dfs[name] = self.convert_date(self.dfs[name])
            if name == "securities":
                self.dfs[name].drop_duplicates(inplace=True)

            if name in COLUMNS:
                self.dfs[name] = self.dfs[name][COLUMNS[name]]

            self.add_timestamp(self.dfs[name])

    def _init_client_df(self):
        if not self.clients:
            return

        self.dfs["clients"] = pd.DataFrame(self.clients)
        self.dfs["clients"] = self.dfs["clients"].drop(
            columns=["positions", "transactions", "buyingPower"]
        )
        self.dfs["clients"] = self._convert_date(self.dfs["clients"], "contractStart")
        self.dfs["clients"] = self.dfs["clients"][COLUMNS["clients"]]
        self.add_timestamp(self.dfs["clients"])

    def _init_buyingpowers_df(self):
        if "buyingpowers" not in self.data:
            return

        base_df = pd.DataFrame(self.data["buyingpowers"]["parsed_dict"])
        sub_dfs = self._init_buyingpowers_sub_dfs()
        self.dfs["buyingpowers"] = self._merge_buyingpowers_dfs(base_df, sub_dfs)
        self.add_timestamp(self.dfs["buyingpowers"])

    def _init_buyingpowers_sub_dfs(self):
        dfs = {}
        for k, v in self.data["buyingpowers"]["parsed_list"].items():
            if k in ["clientMargins", "prenotes", "fxPnlDetails"]:
                continue

            dfs[k] = pd.DataFrame(v)
            dfs[k] = dfs[k].add_prefix(f"{k}_")
            dfs[k] = dfs[k].rename(columns={f"{k}_client": "client"})

        return dfs

    def _merge_buyingpowers_dfs(self, base_df, sub_dfs):
        merged_df = base_df.copy()
        for sub_df in sub_dfs.values():
            merged_df = pd.merge(merged_df, sub_df, how="inner", on="client")

        return merged_df

    def _rename_statlists_stockexchange(self, v):
        rows = [
            {
                "source": "stockExchanges",
                "code": data["stockExchange"],
                "description": data["description"],
                "country": data.get("country", None),
            }
            for data in v
            if data
        ]

        return rows

    def _rename_statlists_currencies(self, v):
        rows = [
            {
                "source": "currencies",
                "code": data["currency"],
                "description": data.get("currencyName", None),
            }
            for data in v
            if data
        ]

        return rows

    def transform_staticlists(self):
        if "staticlists" not in self.raw_data or not self.raw_data["staticlists"]:
            return

        self.data["staticlists"] = []
        for k, v in self.raw_data["staticlists"].items():
            if k == "stockExchanges":
                rows = self._rename_statlists_stockexchange(v)
            elif k == "currencies":
                rows = self._rename_statlists_currencies(v)
            else:
                rows = [{"source": k, **data} for data in v if data]

            self.data["staticlists"].extend(rows)

    def transform_transactions(self):
        if "transactions" not in self.raw_data or not self.raw_data["transactions"]:
            return

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
        if "positions" not in self.raw_data or not self.raw_data["positions"]:
            return

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

    def transform_buyingpowers(self):
        if "buyingpowers" not in self.raw_data or not self.raw_data["buyingpowers"]:
            return

        self.data["buyingpowers"] = {}
        self.data["buyingpowers"]["parsed_dict"] = self.transform_dict_buyingpowers()
        self.data["buyingpowers"]["parsed_list"] = self.transform_list_buyingpowers()

    def transform_dict_buyingpowers(self):
        bps = []
        for data in self.raw_data["buyingpowers"].values():
            bps.append(self._transform_dict_buyingpower_item(data))

        return bps

    def transform_list_buyingpowers(self):
        bps = {}
        for clientid, data in self.raw_data["buyingpowers"].items():
            parsed_item = self._transform_list_buyingpower_item(clientid, data)
            for k, v in parsed_item.items():
                if k not in bps:
                    bps[k] = []

                bps[k].extend(v)

        return bps

    def _transform_dict_buyingpower_item(self, buyingpowers):
        bps = {}
        for k, v in buyingpowers.items():
            if isinstance(v, list):
                continue

            if not isinstance(v, dict):
                bps[k] = v
                continue
            else:
                for sub_k, sub_v in v.items():
                    bps[f"{k}_{sub_k}"] = sub_v

        return bps

    def _transform_list_buyingpower_item(self, clientid, buyingpowers):
        bps = {}
        for k, v in buyingpowers.items():
            if not isinstance(v, list):
                continue

            bps[k] = [{"client": clientid, **_r} for _r in v]

        return bps

    def convert_date(self, df, col=None):
        for col in df.columns:
            if "date" in col.lower() or "time" in col.lower():
                self._convert_date(df, col)

        return df

    @staticmethod
    def _convert_date(df, col):
        df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
        df[col] = df[col].dt.tz_localize(None)
        return df

    @staticmethod
    def add_timestamp(dataframe) -> None:
        try:
            dataframe["timestamp_created_utc"] = datetime.datetime.utcnow()
        except Exception as e:
            logger.error(f"Failed to add timestamps. Error: {e}")
            raise

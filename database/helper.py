import threading

from config import logger, settings
from database import MSSQLDatabase


def init_db_instance():
    return MSSQLDatabase()


def insert_data(inserter: MSSQLDatabase, df_transformed):
    threads = []
    for name, df in df_transformed.items():
        table_name = getattr(settings, f"{name.upper()}_OUTPUT_TABLE")
        logger.info(f"Inserting Data into {table_name}")
        t = threading.Thread(target=inserter.insert_table, args=(df, table_name))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

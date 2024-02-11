import threading

from config import logger, settings
from database.helper import create_inserter_objects
from swissquote import App
from transformer import Agent


def insert_data(inserter, df_transformed):
    threads = []
    for name, df in df_transformed.items():
        table_name = getattr(settings, f"{name.upper()}_OUTPUT_TABLE")
        logger.info(f"Inserting Data into {table_name}")
        t = threading.Thread(target=inserter.insert, args=(df, table_name))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


def main():
    logger.info("Initializing SwissQuote Client")
    app = App(
        token=settings.TOKEN,
        max_retries=settings.REQUEST_MAX_RETRIES,
        backoff_factor=settings.REQUEST_BACKOFF_FACTOR,
    )

    data = app.fetch()
    logger.info("Transforming data")
    df_transformed = Agent(data).transform()
    logger.info("Inserting data to database")
    inserter = create_inserter_objects(
        server=settings.MSSQL_SERVER,
        database=settings.MSSQL_DATABASE,
        username=settings.MSSQL_USERNAME,
        password=settings.MSSQL_PASSWORD,
    )
    insert_data(inserter, df_transformed)
    logger.info("Application completed successfully")


if __name__ == "__main__":
    main()

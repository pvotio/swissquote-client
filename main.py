from config import logger, settings
from database.helper import insert_data
from swissquote import App
from transformer import Agent


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
    insert_data(df_transformed)
    logger.info("Application completed successfully")


if __name__ == "__main__":
    main()

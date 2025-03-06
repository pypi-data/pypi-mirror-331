from aiohttp import ClientSession
from webbrowser import open_new
from numpy import ndarray
import logging


def launch_browser(base_url: str, view_id: str):
    url = f"{base_url}{view_id}"
    open_new(url)


async def validate_config(validation_url: str, config: dict) -> dict:
    async with ClientSession() as session:
        output = None
        async with session.post(validation_url, json=config) as response:
            if response.status == 200:
                output = await response.json()
            else:
                error = await response.text()
                logging.error(f"Validation failed with {response.status}: {error}")
                raise Exception(f"Validation failed with {response.status}: {error}")
        return output


def get_dataset_column_names(dataset: ndarray, column_names: list[str]) -> list[str]:
    column_count = (
        len(dataset) if dataset.ndim == 1 else len(dataset[0])
    )  # ndim checks the dimensions of numpy array
    # If column names mismatch, log warning
    if len(column_names) != column_count:
        logging.warning(
            f"Mismatch: Dataset has {column_count} columns, but {len(column_names)} column names were provided."
        )

    # Ensure dataset_column_names has enough names, filling missing ones
    output = column_names[:column_count] + [
        f"column-{i+1}" for i in range(len(column_names), column_count)
    ]

    return output


# TODO: Verify if need to handle multi output classifiers.
def get_score_column_names(scores: list[str], column_names: list[str]) -> list[str]:
    column_names_count = len(column_names)
    scores_count = len(scores)

    # Log warning if there's a mismatch
    if column_names_count != scores_count:
        logging.warning(
            f"Mismatch: Scores has {scores_count} possible values, but {column_names_count} column names were provided."
        )

    # Ensure output has enough names, filling missing ones
    output = column_names[:scores_count] + [
        f"score-class-{column_name}" for column_name in scores[column_names_count:]
    ]

    return output

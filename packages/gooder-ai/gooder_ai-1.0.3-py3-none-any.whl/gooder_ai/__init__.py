from datetime import datetime
from uuid import uuid4
from gooder_ai import globals
from gooder_ai.s3 import upload_files
from gooder_ai.view import execute_graphql_query, ExecuteGraphQLParams
from gooder_ai.auth import authenticate
from gooder_ai.utils import (
    validate_config,
    launch_browser,
    get_dataset_column_names,
    get_score_column_names,
)
from gooder_ai.types import (
    ViewMeta,
    ValuateModelOutput,
    ScikitModel,
    Credentials,
    AWSVariables,
    ColumnNames,
)
from numpy import ndarray, column_stack
from pandas import DataFrame
import logging


async def valuate_model(
    model: ScikitModel,
    x_data: ndarray,
    y: ndarray,
    auth_credentials: Credentials,
    config: dict,
    view_meta: ViewMeta,
    column_names: ColumnNames = {},
    aws_variables: AWSVariables = {},
) -> ValuateModelOutput:
    logging.info("Model valuation started.")
    email = auth_credentials["email"]
    password = auth_credentials["password"]
    mode = view_meta.get("mode", "private")
    view_id = view_meta.get("view_id", None)
    dataset_name = view_meta.get("dataset_name", f"{datetime.now().timestamp()}")

    # AWS Global Variables
    api_url = aws_variables.get("api_url", globals.API_URL)
    app_client_id = aws_variables.get("app_client_id", globals.App_Client_ID)
    identity_pool_id = aws_variables.get("identity_pool_id", globals.Identity_Pool_ID)
    user_pool_id = aws_variables.get("user_pool_id", globals.User_Pool_ID)
    bucket_name = aws_variables.get("bucket_name", globals.Bucket_Name)
    base_url = aws_variables.get("base_url", globals.Base_URL)
    validation_api_url = aws_variables.get(
        "validation_api_url", globals.Validation_API_URL
    )

    scorer = getattr(
        model, "predict_proba", None
    )  # We are using predict_proba as scorer.
    if scorer is None:
        logging.error(
            "Failed: Input model instance doesn't have a predict_proba method to score the model performance."
        )
        raise Exception(
            "Failed: Input model instance doesn't have a predict_proba method to score the model performance."
        )

    model_classes = getattr(
        model, "classes_", None
    )  # We are using predict_proba as scorer.
    if model_classes is None:
        logging.error(
            "Failed: Input model instance doesn't have classes to classify the target variable"
        )
        raise Exception(
            "Failed: Input model instance doesn't have classes to classify the target variable."
        )

    # Convert to csv
    scores = scorer(x_data)

    dataset_column_names = get_dataset_column_names(
        x_data, column_names.get("dataset_column_names", [])
    )
    score_column_names = get_score_column_names(
        model_classes, column_names.get("score_column_names", [])
    )
    all_column_names = (
        dataset_column_names
        + [column_names.get("dependent_variable_name", "dependent_variable")]
        + score_column_names
    )

    # TODO: Refactor to avoid using dataframe
    dataset = column_stack((x_data, y, scores))
    data = DataFrame(dataset, columns=all_column_names)

    logging.info("Started: Validating config as per the Gooder AI schema.")
    parsed_config = await validate_config(validation_api_url, config)

    if parsed_config["success"] == False:
        logging.error("Failed: Validating config as per the Gooder AI schema.")
        raise Exception("Invalid configuration", parsed_config["error"])
    else:
        logging.info("Success: Validating config as per the Gooder AI schema.")

    logging.info("Started: Authenticating for the Gooder AI platform.")
    credentials = authenticate(
        {
            "email": email,
            "password": password,
            "app_client_id": app_client_id,
            "identity_pool_id": identity_pool_id,
            "user_pool_id": user_pool_id,
        }
    )
    logging.info("Success: Authenticating for the Gooder AI platform.")

    token = credentials["cognito_client_response"]["AuthenticationResult"][
        "AccessToken"
    ]
    aws_access_key_id = credentials["cognito_credentials"]["Credentials"]["AccessKeyId"]
    aws_secret_access_key = credentials["cognito_credentials"]["Credentials"][
        "SecretKey"
    ]
    aws_session_token = credentials["cognito_credentials"]["Credentials"][
        "SessionToken"
    ]
    identity_id = credentials["cognito_credentials"]["IdentityId"]

    parsed_config["data"][
        "datasetID"
    ] = f"{dataset_name}.csv/Sheet1"  # override datasetID of config to match with dataset.

    logging.info("Started: Uploading config and dataset to the Gooder AI platform.")
    path_dictionary = await upload_files(
        {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
            "identity_id": identity_id,
            "data": data,
            "config": parsed_config["data"],
            "file_name": f"{dataset_name}",
            "mode": mode,
            "bucket_name": bucket_name,
        }
    )
    csv_path = path_dictionary["csv_path"]
    config_path = path_dictionary["config_path"]

    if csv_path is None or config_path is None:
        logging.error("Failed: Uploading config and dataset to the Gooder AI platform.")
        raise Exception("Failed to upload files")
    else:
        logging.info("Started: Uploading config and dataset to the Gooder AI platform.")

    mutation_type = (
        "updateSharedView" if isinstance(view_id, str) else "createSharedView"
    )

    view_params: ExecuteGraphQLParams = {
        "api_url": api_url,
        "token": token,
        "mutation": mutation_type,
        "variables": {
            "input": {
                "configPath": config_path,
                "datasetPath": csv_path,
                "id": view_id if isinstance(view_id, str) else f"{uuid4()}",
            }
        },
    }

    view = await execute_graphql_query(view_params)
    id: str = view["data"][mutation_type]["id"]
    message = (
        f"View with ID {id} has been successfully updated using the provided view ID: {view_id}."
        if mutation_type == "updateSharedView"
        else f"A new view has been created successfully. Your view ID is {id}. Please save it for future reference and reuse."
    )
    logging.info(message)
    logging.info("Model valuation can be continued on the Gooder AI platform now.")
    launch_browser(base_url, id)
    return {"view_id": id, "view_url": f"{base_url}{id}"}

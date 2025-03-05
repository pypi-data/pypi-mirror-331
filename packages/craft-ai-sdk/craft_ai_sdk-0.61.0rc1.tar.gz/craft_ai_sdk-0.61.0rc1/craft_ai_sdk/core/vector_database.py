from craft_ai_sdk.shared.environments import get_environment_id

from ..sdk import BaseCraftAiSdk


def get_vector_database_credentials(sdk: BaseCraftAiSdk):
    """Get the credentials of the vector database.

    Returns:
        :obj:`dict`: The vector database credentials, with the following keys:
            * ``"vector_database_url"`` (:obj:`str`): URL of the vector database.
            * ``"vector_database_token"`` (:obj:`str`): Token to connect to the vector
              database.
    """
    environment_id = get_environment_id(sdk)

    vector_database_url = (
        f"{sdk.base_control_api_url}/environments/{environment_id}/vector-database"
    )

    return sdk._get(vector_database_url)

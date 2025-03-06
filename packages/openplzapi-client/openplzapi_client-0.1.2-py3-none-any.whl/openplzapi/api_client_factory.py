##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.api_base_client import ApiBaseClient

class ApiClientFactory:
    """
    An API client factory for all supported API clients (German, Austrian, Swiss or Liechtenstein)
    """

    @staticmethod
    def create_client(client_class, base_url=None, session=None) -> ApiBaseClient:
        """
        Creates and returns a new instance of an ApiBaseClient derived API client

        Args:
            client_class: The type of the API client
            base_url: The base url of the OpenPLZ API
            session: An optional requests session

        Returns:
            A new API client
        """
        return client_class(base_url=base_url, session=session)

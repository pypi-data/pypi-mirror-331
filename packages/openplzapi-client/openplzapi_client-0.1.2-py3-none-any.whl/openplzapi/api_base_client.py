##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

import requests
from abc import ABC
from typing import Callable, TypeVar
from openplzapi.pagination import ReadOnlyCollection, ReadOnlyPagedCollection
from openplzapi.problem_details import ProblemDetailsException

T = TypeVar('T')

class ApiBaseClient(ABC):
    """
    An abstract base class for API client implementations
    """
    OPLZ_API_BASE_URL = "https://openplzapi.org"

    def __init__(self, base_url=None, session=None):
        """
        Initializes a new instance of the ApiBaseClient class.

        Args:
            base_url: The base url of the OpenPLZ API
            session: An optional requests session
        """
        self._base_url = base_url or self.OPLZ_API_BASE_URL
        self._session = session or requests.Session()

    def _create_url(self, relative_url="") -> str:
        """
        Returns an url by combining _base_url and relative_url.

        Args:
            relative_url: The relative url

        Returns:
            The newly created url
        """
        return f"{self._base_url}/{relative_url}"
      
    def _get_list(self, url, model_class) -> ReadOnlyCollection[T]:
        """
        Requests an API endpoint and return back a list of elements

        Args:
            url: The requests url
            model_class: The type of the element to be returned

        Returns:
            The list of elements
        """
        headers = {"Accept": "application/json"}
        response = self._session.get(url, headers=headers)
        if response.status_code != 200:
            self.__handle_problem_details(response)
        else:    
            return ReadOnlyCollection[model_class].from_json(response, model_class)

    def _get_page(self, url, params, model_class, next_page: Callable[[], 'ReadOnlyPagedCollection[T]']) -> ReadOnlyPagedCollection[T]:
        """
        Request an API endpoint and return back a page of elements

        Args:
            url: The requests url
            params: Additional request params
            model_class: The type of the element to be returned
            next_page: A callable for the getting the next page.

        Returns:
            The page of elements
        """
        headers = {"Accept": "application/json"}
        response = self._session.get(url, params=params, headers=headers)
        if response.status_code != 200:
            self.__handle_problem_details(response)
        else:    
            return ReadOnlyPagedCollection[model_class].from_json(response, model_class, next_page)

    def __handle_problem_details(self, response):
        """
        Handles the HTTP response and raises a ProblemDetailsException if applicable.
        """
        if response.status_code != 200:
            content_type = response.headers.get("Content-Type", "")
            if "application/problem+json" in content_type:
                problem_details = response.json()
                raise ProblemDetailsException(
                    type=problem_details.get("type"),
                    title=problem_details.get("title"),
                    status=problem_details.get("status"),
                    detail=problem_details.get("detail"),
                    instance=problem_details.get("instance"),
                    errors=problem_details.get("errors"),
                    trace_id=problem_details.get("traceId")
                )
            else:
                response.raise_for_status()



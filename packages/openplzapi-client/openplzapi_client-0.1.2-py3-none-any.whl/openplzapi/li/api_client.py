##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.li.commune import Commune
from openplzapi.li.locality import Locality
from openplzapi.li.street import Street
from openplzapi.api_base_client import ApiBaseClient
from openplzapi.pagination import ReadOnlyCollection, ReadOnlyPagedCollection

class ApiClientForLiechtenstein(ApiBaseClient):
    """
    Client for the Liechtenstein API endpoint of the OpenPLZ API
    """

    def get_communes(self) -> ReadOnlyCollection[Commune]:
        """
        Returns all communes (Gemeinden)

        Returns:
            A list of Commune instances
        """

        url = self._create_url("li/Communes")
        return self._get_list(url, Commune)

    def get_localities(self, postal_code, name, page_index=1, page_size=50) -> ReadOnlyPagedCollection[Locality]:
        """
        Returns localities whose postal code and/or name matches the given patterns.

        Args:
            postal_code: Postal code pattern
            name: Name pattern
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of Locality instances
        """

        url = self._create_url("li/Localities")
        params = {"postalCode": postal_code, "name": name, "page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_localities(postal_code, name, page_index + 1, page_size)
        return self._get_page(url, params, Locality, next_page)

    def get_streets(self, name, postal_code, locality, page_index=1, page_size=50) -> ReadOnlyPagedCollection[Street]:
        """
        Returns streets whose name, postal code and/or name matches the given patterns.

        Args:
            name: Name pattern
            postal_code: Postal code pattern
            locality: Locality pattern
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of Street instances
        """

        url = self._create_url(f"li/Streets")
        params = {"name": name, "postalCode": postal_code, "locality": locality, "page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_streets(name, postal_code, locality, page_index + 1, page_size)
        return self._get_page(url, params, Street, next_page)

    def perform_full_text_search(self, search_term, page_index=1, page_size=50) -> ReadOnlyPagedCollection[Street]:
        """
        Performs a full-text search using the street name, postal code and city.

        Args:
            searchTerm: Search term for full text search
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of Street instances
        """

        url = self._create_url("li/FullTextSearch")
        params = {"searchTerm": search_term, "page": page_index, "pageSize": page_size}
        next_page = lambda : self.perform_full_text_search(search_term, page_index + 1, page_size)
        return self._get_page(url, params, Street, next_page)

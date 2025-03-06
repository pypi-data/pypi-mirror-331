##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.ch.district import District
from openplzapi.ch.canton import Canton
from openplzapi.ch.commune import Commune
from openplzapi.ch.locality import Locality
from openplzapi.ch.street import Street
from openplzapi.api_base_client import ApiBaseClient
from openplzapi.pagination import ReadOnlyCollection, ReadOnlyPagedCollection

class ApiClientForSwitzerland(ApiBaseClient):
    """
    Client for the Swiss API endpoint of the OpenPLZ API
    """

    def get_cantons(self) -> ReadOnlyCollection[Canton]:
        """
        Returns all cantons (Kantone).

        Returns:
            A list of Canton instances
        """

        url = self._create_url("ch/Cantons")
        return self._get_list(url, Canton)

    def get_districts_by_canton(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[District]:
        """
        Returns districts (Bezirke) within a canton (Kanton).

        Args:
            key: Key of the canton
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of District instances
        """

        url = self._create_url(f"ch/Cantons/{key}/Districts")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_districts_by_canton(key, page_index + 1, page_size)
        return self._get_page(url, params, District, next_page)

    def get_communes_by_canton(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[Commune]:
        """
        Returns communes (Gemeinden) within a canton (Kanton).

        Args:
            key: Key of the canton
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of Commune instances
        """

        url = self._create_url(f"ch/Cantons/{key}/Communes")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_communes_by_canton(key, page_index + 1, page_size)
        return self._get_page(url, params, Commune, next_page)

    def get_communes_by_district(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[Commune]:
        """
        Returns communes (Gemeinden) within a district (Bezirk).

        Args:
            key: Key of the district
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of Commune instances
        """

        url = self._create_url(f"ch/Districts/{key}/Communes")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_communes_by_district(key, page_index + 1, page_size)
        return self._get_page(url, params, Commune, next_page)

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

        url = self._create_url("ch/Localities")
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

        url = self._create_url(f"ch/Streets")
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

        url = self._create_url("ch/FullTextSearch")
        params = {"searchTerm": search_term, "page": page_index, "pageSize": page_size}
        next_page = lambda : self.perform_full_text_search(search_term, page_index + 1, page_size)
        return self._get_page(url, params, Street, next_page)

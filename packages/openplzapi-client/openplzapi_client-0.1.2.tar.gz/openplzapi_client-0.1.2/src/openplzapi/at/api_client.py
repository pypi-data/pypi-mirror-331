##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.at.district import District
from openplzapi.at.federal_province import FederalProvince
from openplzapi.at.locality import Locality
from openplzapi.at.municipality import Municipality
from openplzapi.at.street import Street
from openplzapi.api_base_client import ApiBaseClient
from openplzapi.pagination import ReadOnlyCollection, ReadOnlyPagedCollection

class ApiClientForAustria(ApiBaseClient):
    """
    Client for the Autrian API endpoint of the OpenPLZ API
    """

    def get_federal_provinces(self) -> ReadOnlyCollection[FederalProvince]:
        """
        Returns federal provinces (Bundesländer).

        Returns:
            A list of FederalProvince instances
        """

        url = self._create_url("at/FederalProvinces")
        return self._get_list(url, FederalProvince)

    def get_districts_by_federal_province(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[District]:
        """
        Returns districts (Bezirke) within a federal province (Bundesland).

        Args:
            key: Key of the federal province
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of District instances
        """

        url = self._create_url(f"at/FederalProvinces/{key}/Districts")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_districts_by_federal_province(key, page_index + 1, page_size)
        return self._get_page(url, params, District, next_page)

    def get_municipalities_by_federal_province(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[Municipality]:
        """
        Returns municipalities (Gemeinden) within a federal province (Bundesland).

        Args:
            key: Key of the federal province
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of Municipality instances
        """

        url = self._create_url(f"at/FederalProvinces/{key}/Municipalities")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_municipalities_by_federal_province(key, page_index + 1, page_size)
        return self._get_page(url, params, Municipality, next_page)

    def get_municipalities_by_district(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[Municipality]:
        """
        Returns municipalities (Gemeinden) within a district (Bezirk).

        Args:
            key: Key of the district
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of Municipality instances
        """

        url = self._create_url(f"at/Districts/{key}/Municipalities")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_municipalities_by_district(key, page_index + 1, page_size)
        return self._get_page(url, params, Municipality, next_page)

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

        url = self._create_url("at/Localities")
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

        url = self._create_url(f"at/Streets")
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

        url = self._create_url("at/FullTextSearch")
        params = {"searchTerm": search_term, "page": page_index, "pageSize": page_size}
        next_page = lambda : self.perform_full_text_search(search_term, page_index + 1, page_size)
        return self._get_page(url, params, Street, next_page)

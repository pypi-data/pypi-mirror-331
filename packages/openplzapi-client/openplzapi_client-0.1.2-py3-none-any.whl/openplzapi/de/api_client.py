##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.de.street import Street
from openplzapi.de.district import District
from openplzapi.de.federal_state import FederalState
from openplzapi.de.locality import Locality
from openplzapi.de.government_region import GovernmentRegion
from openplzapi.de.municipal_association import MunicipalAssociation
from openplzapi.de.municipality import Municipality
from openplzapi.api_base_client import ApiBaseClient
from openplzapi.pagination import ReadOnlyCollection, ReadOnlyPagedCollection

class ApiClientForGermany(ApiBaseClient):
    """
    Client for the German API endpoint of the OpenPLZ API
    """

    def get_federal_states(self) -> ReadOnlyCollection[FederalState]:
        """
        Returns all federal states (Bundesländer).

        Returns:
            A list of FederalState instances
        """

        url = self._create_url("de/FederalStates")
        return self._get_list(url, FederalState)

    def get_government_regions_by_federal_state(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[GovernmentRegion]:
        """
        Returns government regions (Regierungsbezirke) within a federal state (Bundesaland).

        Args:
            key: Key of the federal state
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of GovernmentRegion instances
        """

        url = self._create_url(f"de/FederalStates/{key}/GovernmentRegions")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_government_regions_by_federal_state(key, page_index + 1, page_size)
        return self._get_page(url, params, GovernmentRegion, next_page)

    def get_districts_by_federal_state(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[District]:
        """
        Returns districts (Kreise) within a federal state (Bundesland).

        Args:
            key: Key of the federal state
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of District instances
        """

        url = self._create_url(f"de/FederalStates/{key}/Districts")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_districts_by_federal_state(key, page_index + 1, page_size)
        return self._get_page(url, params, District, next_page)

    def get_districts_by_government_region(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[District]:
        """
        Returns districts (Kreise) within a government region (Regierungsbezirk).

        Args:
            key: Key of the government region
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of District instances
        """

        url = self._create_url(f"de/GovernmentRegions/{key}/Districts")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_districts_by_government_region(key, page_index + 1, page_size)
        return self._get_page(url, params, District, next_page)

    def get_municipal_associations_by_federal_state(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[MunicipalAssociation]:
        """
        Returns municipal associations (Gemeindeverbände) within a federal state (Bundesland).

        Args:
            key: Key of the federal state
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of MunicipalAssociations instances
        """

        url = self._create_url(f"de/FederalStates/{key}/MunicipalAssociations")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_municipal_associations_by_federal_state(key, page_index + 1, page_size)
        return self._get_page(url, params, MunicipalAssociation, next_page)

    def get_municipal_associations_by_government_region(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[MunicipalAssociation]:
        """
        Returns municipal associations (Gemeindeverbünde) within a government region (Regierungsbezirk).

        Args:
            key: Key of the government region
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of MunicipalAssociations instances
        """

        url = self._create_url(f"de/GovernmentRegions/{key}/MunicipalAssociations")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_municipal_associations_by_government_region(key, page_index + 1, page_size)
        return self._get_page(url, params, MunicipalAssociation, next_page)

    def get_municipal_associations_by_district(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[MunicipalAssociation]:
        """
        Returns municipal associations (Gemeindeverbände) within a district (Kreis).

        Args:
            key: Key of the district
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of MunicipalAssociations instances
        """

        url = self._create_url(f"de/Districts/{key}/MunicipalAssociations")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_municipal_associations_by_district(key, page_index + 1, page_size)
        return self._get_page(url, params, MunicipalAssociation, next_page)

    def get_municipalities_by_federal_state(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[Municipality]:
        """
        Returns municipalities (Gemeinden) within a federal state (Bundesland).

        Args:
            key: Key of the federal state
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of Municipality instances
        """

        url = self._create_url(f"de/FederalStates/{key}/Municipalities")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_municipalities_by_federal_state(key, page_index + 1, page_size)
        return self._get_page(url, params, Municipality, next_page)

    def get_municipalities_by_government_region(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[Municipality]:
        """
        Returns municipalities (Gemeinden) within a government region (Regierungsbezirk).

        Args:
            key: Key of the government region
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of Municipality instances
        """

        url = self._create_url(f"de/GovernmentRegions/{key}/Municipalities")
        params = {"page": page_index, "pageSize": page_size}
        next_page = lambda : self.get_municipalities_by_government_region(key, page_index + 1, page_size)
        return self._get_page(url, params, Municipality, next_page)

    def get_municipalities_by_district(self, key, page_index=1, page_size=50) -> ReadOnlyPagedCollection[Municipality]:
        """
        Returns municipalities (Gemeinden) within a district (Kreis).

        Args:
            key: Key of the district
            page_index: Page index for paging
            page_size: Page size for paging

        Returns:
            A paged list of Municipality instances
        """

        url = self._create_url(f"de/Districts/{key}/Municipalities")
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

        url = self._create_url("de/Localities")
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

        url = self._create_url(f"de/Streets")
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

        url = self._create_url("de/FullTextSearch")
        params = {"searchTerm": search_term, "page": page_index, "pageSize": page_size}
        next_page = lambda : self.perform_full_text_search(search_term, page_index + 1, page_size)
        return self._get_page(url, params, Street, next_page)

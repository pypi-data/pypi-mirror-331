##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.de.federal_state_summary import FederalStateSummary
from openplzapi.de.government_region_summary import GovernmentRegionSummary
from openplzapi.de.district_summary import DistrictSummary
from openplzapi.de.municipal_association_summary import MunicipalAssociationSummary

class Municipality:
    """
    Representation of a German municipality (Gemeinde)
    """

    def __init__(self, key, name, type, postal_code, multiple_postal_codes, association, district, government_region, federal_state):
        self.key = key
        self.name = name
        self.type = type
        self.multiple_postal_codes = multiple_postal_codes
        self.postal_code = postal_code
        self.district = district
        self.association = association
        self.government_region = government_region
        self.federal_state = federal_state

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"),
            name=data.get("name"),
            type=data.get("type"), 
            postal_code=data.get("postalCode"),
            multiple_postal_codes=data.get("multiplePostalCodes"),
            association=MunicipalAssociationSummary.from_json(data.get("association")),
            district=DistrictSummary.from_json(data.get("district")),
            government_region=GovernmentRegionSummary.from_json(data.get("governmentRegion")),
            federal_state=FederalStateSummary.from_json(data.get("federalState")))

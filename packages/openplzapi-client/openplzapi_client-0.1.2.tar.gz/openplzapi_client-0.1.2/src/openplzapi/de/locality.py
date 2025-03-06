##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.de.federal_state_summary import FederalStateSummary
from openplzapi.de.district_summary import DistrictSummary
from openplzapi.de.municipality_summary import MunicipalitySummary

class Locality:
    """
    Representation of a German locality (Ort oder Stadt)
    """

    def __init__(self, name, postal_code, municipality, district, federal_state):
        self.name = name
        self.postal_code = postal_code
        self.municipality = municipality
        self.district = district
        self.federal_state = federal_state

    @classmethod
    def from_json(cls, data):
        return cls(
            name=data.get("name"),
            postal_code=data.get("postalCode"),
            municipality=MunicipalitySummary.from_json(data.get("municipality")),
            district=DistrictSummary.from_json(data.get("district")),
            federal_state=FederalStateSummary.from_json(data.get("federalState")))

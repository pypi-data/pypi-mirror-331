##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.de.federal_state_summary import FederalStateSummary
from openplzapi.de.district_summary import DistrictSummary
from openplzapi.de.municipality_summary import MunicipalitySummary

class Street:
    """
    Representation of a German street (Straße)
    """

    def __init__(self, name, postal_code, locality, borough, suburb, municipality, district, federal_state):
        self.name = name
        self.postal_code = postal_code
        self.locality = locality
        self.borough = borough
        self.suburb = suburb
        self.municipality = municipality
        self.district = district
        self.federal_state = federal_state

    @classmethod
    def from_json(cls, data):
        return cls(
            name=data.get("name"),
            postal_code=data.get("postalCode"),
            locality=data.get("locality"),
            borough=data.get("borough"),
            suburb=data.get("suburb"),
            municipality=MunicipalitySummary.from_json(data.get("municipality")),
            district=DistrictSummary.from_json(data.get("district")),
            federal_state=FederalStateSummary.from_json(data.get("federalState")))

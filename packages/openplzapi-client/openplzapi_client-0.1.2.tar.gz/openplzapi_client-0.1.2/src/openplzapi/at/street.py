##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.at.district_summary import DistrictSummary
from openplzapi.at.federal_province_summary import FederalProvinceSummary
from openplzapi.at.municipality_summary import MunicipalitySummary

class Street:
    """
    Representation of an Austrian street (Straße)
    """

    def __init__(self, key, name, postal_code, locality, municipality, district, federal_province):
        self.key = key
        self.name = name
        self.postal_code = postal_code
        self.locality = locality
        self.municipality = municipality
        self.district = district
        self.federal_province = federal_province

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"), 
            name=data.get("name"), 
            postal_code=data.get("postalCode"), 
            locality=data.get("locality"),
            municipality=MunicipalitySummary.from_json(data.get("municipality")),
            district=DistrictSummary.from_json(data.get("district")),
            federal_province=FederalProvinceSummary.from_json(data.get("federalProvince")))

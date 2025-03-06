##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.at.district_summary import DistrictSummary
from openplzapi.at.federal_province_summary import FederalProvinceSummary

class Municipality:
    """
    Representation of an Austrian municipality (Gemeinde)
    """

    def __init__(self, key, name, code, postal_code, multiple_postal_codes, status, district, federal_province):
        self.key = key
        self.name = name
        self.code = code
        self.postal_code = postal_code
        self.multiple_postal_codes = multiple_postal_codes
        self.status = status
        self.district = district
        self.federal_province = federal_province

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"),
            name=data.get("name"), 
            code=data.get("code"), 
            postal_code=data.get("postalCode"),
            multiple_postal_codes=data.get("multiplePostalCodes"),
            status=data.get("status"),
            district=DistrictSummary.from_json(data.get("district")),
            federal_province=FederalProvinceSummary.from_json(data.get("federalProvince")))

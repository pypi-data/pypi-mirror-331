##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.at.federal_province_summary import FederalProvinceSummary

class District:
    """
    Representation of an Austrian district (Bezirk)
    """

    def __init__(self, key, name, code, federal_province):
        self.key = key
        self.name = name
        self.code = code
        self.federal_province = federal_province

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"),
            name=data.get("name"),
            code=data.get("code"), 
            federal_province=FederalProvinceSummary.from_json(data.get("federalProvince")))


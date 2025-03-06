##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.de.federal_state_summary import FederalStateSummary
from openplzapi.de.district_summary import DistrictSummary

class MunicipalAssociation:
    """
    Representation of a German municipal association (Gemeindeverband)
    """

    def __init__(self, key, name, type, administrative_headquarters, district, federal_state):
        self.key = key
        self.name = name
        self.type = type
        self.administrative_headquarters = administrative_headquarters
        self.district = district
        self.federal_state = federal_state

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"),
            name=data.get("name"),
            type=data.get("type"), 
            administrative_headquarters=data.get("administrativeHeadquarters"),
            district=DistrictSummary.from_json(data.get("district")),
            federal_state=FederalStateSummary.from_json(data.get("federalState")))

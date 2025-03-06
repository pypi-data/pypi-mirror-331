##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.de.federal_state_summary import FederalStateSummary
from openplzapi.de.government_region_summary import GovernmentRegionSummary

class District:
    """
    Representation of a German district (Kreis)
    """

    def __init__(self, key, name, type, administrative_headquarters, government_region, federal_state):
        self.key = key
        self.name = name
        self.type = type
        self.administrative_headquarters = administrative_headquarters
        self.government_region = government_region
        self.federal_state = federal_state

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"),
            name=data.get("name"),
            type=data.get("type"), 
            administrative_headquarters=data.get("administrativeHeadquarters"),
            government_region=GovernmentRegionSummary.from_json(data.get("governmentRegion")),
            federal_state=FederalStateSummary.from_json(data.get("federalState")))

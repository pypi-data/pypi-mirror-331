##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.de.federal_state_summary import FederalStateSummary

class GovernmentRegion:
    """
    Representation of a German government region (Regierungsbezirk)
    """

    def __init__(self, key, name, administrative_headquarters, federal_state):
        self.key = key
        self.name = name
        self.administrative_headquarters = administrative_headquarters
        self.federal_state = federal_state

    @classmethod
    def from_json(cls, data):
        return cls(
            name=data.get("name"), 
            key=data.get("key"),
            administrative_headquarters=data.get("administrativeHeadquarters"),
            federal_state=FederalStateSummary.from_json(data.get("federalState")))

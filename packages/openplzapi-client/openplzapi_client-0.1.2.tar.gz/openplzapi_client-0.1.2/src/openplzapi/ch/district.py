##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.ch.canton_summary import CantonSummary

class District:
    """
    Representation of a Swiss district (Bezirk)
    """

    def __init__(self, key, historical_code, name, short_name, canton):
        self.key = key
        self.historical_code = historical_code
        self.name = name
        self.short_name = short_name
        self.canton = canton

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"),
            historical_code=data.get("historicalCode"),
            name=data.get("name"),
            short_name=data.get("shortName"),
            canton=CantonSummary.from_json(data.get("canton")))

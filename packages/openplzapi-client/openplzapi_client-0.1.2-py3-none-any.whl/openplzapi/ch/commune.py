##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.ch.canton_summary import CantonSummary
from openplzapi.ch.district_summary import DistrictSummary

class Commune:
    """
    Reduced representation of a Swiss commune (Gemeinde)
    """

    def __init__(self, key, historical_code, name, short_name, district, canton):
        self.key = key
        self.historical_code = historical_code
        self.name = name
        self.short_name = short_name
        self.district = district
        self.canton = canton

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"),
            historical_code=data.get("historicalCode"),
            name=data.get("name"),
            short_name=data.get("shortName"),
            district=DistrictSummary.from_json(data.get("district")),
            canton=CantonSummary.from_json(data.get("canton")))

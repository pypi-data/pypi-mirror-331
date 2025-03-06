##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.ch.canton_summary import CantonSummary
from openplzapi.ch.commune_summary import CommuneSummary
from openplzapi.ch.district_summary import DistrictSummary

class Locality:
    """
    Representation of a Swiss locality (Ort oder Stadt)
    """

    def __init__(self, name, postal_code, commune, district, canton):
        self.name = name
        self.postal_code = postal_code
        self.commune = commune
        self.district = district
        self.canton = canton

    @classmethod
    def from_json(cls, data):
        return cls(
            name=data.get("name"), 
            postal_code=data.get("postalCode"),
            commune=CommuneSummary.from_json(data.get("commune")),
            district=DistrictSummary.from_json(data.get("district")),
            canton=CantonSummary.from_json(data.get("canton")))

##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.ch.canton_summary import CantonSummary
from openplzapi.ch.commune_summary import CommuneSummary
from openplzapi.ch.district_summary import DistrictSummary

class Street:
    """
    Representation of a Swiss street (Straße)
    """

    def __init__(self, key, name, postal_code, locality, status, commune, district, canton):
        self.key = key
        self.name = name
        self.postal_code = postal_code
        self.locality = locality
        self.status = status
        self.commune = commune
        self.district = district
        self.canton = canton

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"), 
            name=data.get("name"), 
            postal_code=data.get("postalCode"), 
            locality=data.get("locality"),
            status=data.get("status"), 
            commune=CommuneSummary.from_json(data.get("commune")),
            district=DistrictSummary.from_json(data.get("district")),
            canton=CantonSummary.from_json(data.get("canton")))

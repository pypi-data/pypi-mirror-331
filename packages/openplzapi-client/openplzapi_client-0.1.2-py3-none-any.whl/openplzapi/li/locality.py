##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.li.commune_summary import CommuneSummary

class Locality:
    """
    Representation of a Liechtenstein locality (Ort oder Stadt)
    """

    def __init__(self, name, postal_code, commune):
        self.name = name
        self.postal_code = postal_code
        self.commune = commune

    @classmethod
    def from_json(cls, data):
        return cls(
            name=data.get("name"),
            postal_code=data.get("postalCode"),
            commune=CommuneSummary.from_json(data.get("commune")))

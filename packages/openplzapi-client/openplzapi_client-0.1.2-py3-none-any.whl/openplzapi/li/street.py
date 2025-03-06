##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.li.commune_summary import CommuneSummary

class Street:
    """
    Representation of a Liechtenstein street (Straße)
    """

    def __init__(self, key, name, postal_code, locality, status, commune):
        self.key = key
        self.name = name
        self.postal_code = postal_code
        self.locality = locality
        self.status = status
        self.commune = commune

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"), 
            name=data.get("name"), 
            postal_code=data.get("postalCode"), 
            locality=data.get("locality"),
            status=data.get("status"),
            commune=CommuneSummary.from_json(data.get("commune")))


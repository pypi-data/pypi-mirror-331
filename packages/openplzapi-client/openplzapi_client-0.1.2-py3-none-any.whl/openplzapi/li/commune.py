##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

class Commune:
    """
    Representation of a Liechtenstein commune (Gemeinde)
    """

    def __init__(self, key, name, electoral_district):
        self.key = key
        self.name = name
        self.electoral_district = electoral_district

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"),
            name=data.get("name"),
            electoral_district=data.get("electoralDistrict"))

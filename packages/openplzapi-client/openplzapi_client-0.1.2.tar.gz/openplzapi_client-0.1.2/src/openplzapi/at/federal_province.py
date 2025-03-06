##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

class FederalProvince:
    """
    Representation of an Austrian federal province (Bundesland)
    """

    def __init__(self, key, name):
        self.key = key
        self.name = name

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"),
            name=data.get("name"))

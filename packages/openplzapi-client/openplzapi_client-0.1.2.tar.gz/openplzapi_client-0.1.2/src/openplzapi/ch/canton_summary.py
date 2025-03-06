##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

class CantonSummary:
    """
    Reduced representation of a Swiss canton (Kanton)
    """

    def __init__(self, key, name, short_name):
        self.key = key
        self.name = name
        self.short_name = short_name

    @classmethod
    def from_json(cls, data):
        return None if not data else cls(
            key=data.get("key"),
            name=data.get("name"),
            short_name=data.get("shortName")
        ) 

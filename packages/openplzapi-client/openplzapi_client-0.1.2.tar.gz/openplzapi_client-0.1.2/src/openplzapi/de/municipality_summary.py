##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

class MunicipalitySummary:
    """
    Reduced representation of a German municipality (Gemeinde)
    """

    def __init__(self, key, name, type):
        self.key = key
        self.name = name
        self.type = type

    @classmethod
    def from_json(cls, data):
        return None if not data else cls(
            key=data.get("key"),
            name=data.get("name"),
            type=data.get("type")
        )

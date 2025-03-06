##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

class FederalStateSummary:
    """
    Reduced representation of a German federal state (Bundesland)
    """

    def __init__(self, key, name):
        self.key = key
        self.name = name

    @classmethod
    def from_json(cls, data):
        return None if not data else cls(
            key=data.get("key"),
            name=data.get("name")
        ) 

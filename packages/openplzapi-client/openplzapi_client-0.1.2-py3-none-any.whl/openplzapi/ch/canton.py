##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

class Canton:
    """
    Representation of a Swiss canton (Kanton)
    """

    def __init__(self, key, historical_code, name, short_name):
        self.key = key
        self.historical_code = historical_code
        self.name = name
        self.short_name = short_name

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"),
            historical_code=data.get("historicalCode"),
            name=data.get("name"),
            short_name=data.get("shortName")) 

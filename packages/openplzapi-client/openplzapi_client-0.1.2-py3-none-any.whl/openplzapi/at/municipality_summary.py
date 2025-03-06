##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

class MunicipalitySummary:
    """
    Reduced representation of an Austrian municipality (Gemeinde)
    """

    def __init__(self, key, name, code, status):
        self.key = key
        self.name = name
        self.code = code
        self.status = status

    @classmethod
    def from_json(cls, data):
        return None if not data else cls(
            key=data.get("key"), 
            name=data.get("name"), 
            code=data.get("code"), 
            status=data.get("status")
        )

##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

class FederalState:
    """
     Representation of a German federal state (Bundesland)
    """

    def __init__(self, key, name, seat_of_government):
        self.key = key
        self.name = name
        self.seat_of_government = seat_of_government

    @classmethod
    def from_json(cls, data):
        return cls(
            key=data.get("key"),
            name=data.get("name"),
            seat_of_government=data.get("seatOfGovernment")) 

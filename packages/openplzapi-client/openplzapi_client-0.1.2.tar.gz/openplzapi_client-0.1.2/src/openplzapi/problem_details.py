##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

class ProblemDetailsException(Exception):
    """
    Exception to handle Problem Details as per RFC 7807.
    """

    def __init__(self, type, title, status, detail, instance, errors, trace_id):
        """
        Initializes a new instance of the ProblemDetailsException class.

        Args:
            type: An URI reference identifying the error type
            title: A short, human-readable summary of the problem
            status: The HTTP status code for the error
            detail: A detailed, human-readable explanation of the error
            instance: An URI pointing to the specific instance of the error
            errors: A grouped list of specific validation errors
            trace_id: Used for correlation and troubleshooting in distributed systems
        """
        self.type = type
        self.title = title
        self.status = status
        self.detail = detail
        self.instance = instance
        self.errors = errors or {}
        self.trace_id = trace_id
        super().__init__(self.__str__())

    def __str__(self) -> str:
        """
        Informal string representation of the exception.

        Returns:
            The informal string representation of the exception
        """
        details = [
            f"Type: {self.type}",
            f"Title: {self.title}",
            f"Status: {self.status}",
            f"Detail: {self.detail}",
            f"Instance: {self.instance}",
            f"Errors: {self.errors}",
            f"TraceId: {self.trace_id}"
        ]
        return "\n".join(filter(None, details))

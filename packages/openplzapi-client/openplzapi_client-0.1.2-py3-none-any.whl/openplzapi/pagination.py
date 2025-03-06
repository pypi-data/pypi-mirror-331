##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from typing import Callable, Generic, Optional, Sequence, TypeVar

T = TypeVar('T')

class ReadOnlyCollection(Sequence, Generic[T]):
    """
    A list with additional pagination information.
    """

    def __init__(self, items):
        """
        Initializes a new instance of the ReadOnlyCollection class.

        Args:
            items: The list of items
        """
        self._list = items

    def __len__(self) -> int:
        """
        Returns the number of elements.

        Returns:
            The number of elements
        """
        return len(self._list)

    def __getitem__(self, index) -> T:
        """
        Returns an element specified by its index.

        Args:
            index: The index

        Returns:
            The element
        """
        return self._list[index]

    def __repr__(self) -> str:
        """
        Returns the string representation of the object.

        Returns:
            The string representation of the object
        """
        return repr(self._list)

    @classmethod
    def from_json(cls, response, model_class) -> Optional["ReadOnlyCollection[T]"]:
        """
        Creates and returns a new instance of the ReadOnlyCollection class.

        Args:
            response: The response object from an HTTP Get request
            model_class: The class type of items in the list

        Returns:
            A new ReadOnlyCollection object
        """
        return cls(
            items = [model_class.from_json(item) for item in response.json()]
        )

class ReadOnlyPagedCollection(ReadOnlyCollection, Generic[T]):
    """
    A list with additional pagination information.
    """

    def __init__(self, items, page_index, page_size, total_pages, total_count, next_page):
        """
        Initializes a new instance of the ReadOnlyPagedCollection class.

        Args:
            items: The list of items
            page_index: The page index
            page_size: The page size
            total_pages: The total number of pages
            total_count: The total number of items
            next_page: A callable for the getting the next page
        """
        super().__init__(items)
        self.page_index = page_index
        self.page_size = page_size
        self.total_pages = total_pages
        self.total_count = total_count
        self.next_page = next_page

    def __repr__(self) -> str:
        """
        Returns the string representation of the object.

        Returns:
            The string representation of the object
        """
        return super().__repr__

    def is_last_page(self) -> bool:
        """
        Returns whether this is the last page within a paged collection.

        Returns:
            True, if this is the last page
        """
        return (self.page_index * self.page_size) >= self.total_count

    def get_next_page(self) -> Optional["ReadOnlyPagedCollection[T]"]:
        """
        Requests and returns the next page with elements.

        Returns:
            A new ReadOnlyPagedCollection object or None
        """
        return self.next_page() if not self.is_last_page() else None

    @classmethod
    def from_json(cls, response, model_class, next_page: Callable[[], 'ReadOnlyPagedCollection[T]']) -> Optional["ReadOnlyPagedCollection[T]"]:
        """
        Creates and returns a new instance of the Page class.

        Args:
            response: The response object from an HTTP Get request
            model_class: The class type of items in the list
            next_page: A callable for the getting the next page

        Returns:
            A new ReadOnlyPagedCollection object
        """
        return cls(
            items = [model_class.from_json(item) for item in response.json()],
            page_index = int(response.headers.get("x-page")),
            page_size = int(response.headers.get("x-page-size")),
            total_pages = int(response.headers.get("x-total-pages")),
            total_count = int(response.headers.get("x-total-count")),
            next_page = next_page
        )

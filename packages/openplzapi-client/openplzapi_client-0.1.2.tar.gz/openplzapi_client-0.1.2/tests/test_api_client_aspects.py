##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

import pytest;
from openplzapi.de.api_client import ApiClientForGermany
from openplzapi.problem_details import ProblemDetailsException

client = ApiClientForGermany()

def test_pagination():
    exists_key = False
    page_index = 1

    streetsPage = client.perform_full_text_search("Berlin Platz", page_size = 10)

    while streetsPage != None:

        assert len(streetsPage) > 0
        assert streetsPage.page_index == page_index
        assert streetsPage.page_size == 10
        assert streetsPage.total_pages >= 2
        assert streetsPage.total_count >= 10

        for street in streetsPage:
            if street.name == "Pariser Platz" and street.postal_code == "10117":
                assert street.locality == "Berlin"
                assert street.municipality.key == "11000000"
                assert street.municipality.name == "Berlin, Stadt"
                assert street.municipality.type == "Kreisfreie Stadt"
                assert street.federal_state.key == "11"
                assert street.federal_state.name == "Berlin"
                exists_key = True
                break
        
        streetsPage = streetsPage.get_next_page()
        page_index += 1

    assert exists_key

def test_problem_details():

    with pytest.raises(ProblemDetailsException) as exception_info:
        client.perform_full_text_search("Berlin Platz", page_size = 99)

    assert str(exception_info.value.title) == 'One or more validation errors occurred.'
    assert str(exception_info.value.status) == '400'

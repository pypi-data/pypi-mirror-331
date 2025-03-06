##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.li.api_client import ApiClientForLiechtenstein

client = ApiClientForLiechtenstein()

def test_communes():
    communes = client.get_communes()

    assert len(communes) == 11

    assert any(commune.name == "Triesen" for commune in communes)
    assert any(commune.name == "Planken" for commune in communes)

def test_full_text_search():
    streets = client.perform_full_text_search("9490 Alte Landstrasse", 1, 10)

    assert len(streets) > 0
    assert streets.page_index == 1
    assert streets.page_size == 10
    assert streets.total_pages >= 1
    assert streets.total_count >= 1

    exists_key = False

    for street in streets:
        if street.key == "89440155":
            assert street.name == "Alte Landstrasse"
            assert street.postal_code == "9490"
            assert street.locality == "Vaduz"
            assert street.status == "Real"  
            assert street.commune.key == "7001"
            assert street.commune.name == "Vaduz"
            exists_key = True
            break

    assert exists_key

def test_localities():
    localities = client.get_localities(None, "Vaduz", 1, 10)

    assert len(localities) > 0
    assert localities.page_index == 1
    assert localities.page_size == 10
    assert localities.total_pages >= 1
    assert localities.total_count >= 1

    exists_name = False
    exists_postal_code = False

    for locality in localities:
        if locality.postal_code == "9490" and locality.name == "Vaduz":
            exists_name = True
            exists_postal_code = True
            assert locality.commune.key == "7001"
            assert locality.commune.name == "Vaduz"
            break

    assert exists_name
    assert exists_postal_code

def test_streets():
    streets = client.get_streets("Alte Landstrasse", "9490", None, 1, 10)

    assert len(streets) > 0
    assert streets.page_index == 1
    assert streets.page_size == 10
    assert streets.total_pages >= 1
    assert streets.total_count >= 1

    exists_key = False

    for street in streets:
        if street.key == "89440155":
            assert street.name == "Alte Landstrasse"
            assert street.postal_code == "9490"
            assert street.locality == "Vaduz"
            assert street.status == "Real"  # Update to match actual enum or status format
            assert street.commune.key == "7001"
            assert street.commune.name == "Vaduz"
            exists_key = True
            break

    assert exists_key

##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.ch.api_client import ApiClientForSwitzerland

client = ApiClientForSwitzerland()

def test_cantons():
    cantons = client.get_cantons()

    assert len(cantons) == 26
    assert any(canton.name == "Zürich" for canton in cantons)
    assert any(canton.name == "Aargau" for canton in cantons)

def test_communes_by_canton():
    communes = client.get_communes_by_canton("10", 1, 10)

    assert communes.page_index == 1
    assert communes.page_size == 10
    assert communes.total_pages >= 1
    assert communes.total_count >= 1

    exists_key = False

    for commune in communes:
        if commune.key == "2008":
            assert commune.name == "Châtillon (FR)"
            assert commune.short_name == "Châtillon (FR)"
            assert commune.district.key == "1001"
            assert commune.district.name == "District de la Broye"
            assert commune.canton.key == "10"
            assert commune.canton.name == "Fribourg / Freiburg"
            assert commune.canton.short_name == "FR"
            exists_key = True
            break

    assert exists_key

def test_communes_by_district():
    communes = client.get_communes_by_district("1002", 1, 10)

    assert communes.page_index == 1
    assert communes.page_size == 10
    assert communes.total_pages >= 1
    assert communes.total_count >= 1

    exists_key = False

    for commune in communes:
        if commune.key == "2063":
            assert commune.name == "Billens-Hennens"
            assert commune.historical_code == "14103"
            assert commune.short_name == "Billens-Hennens"
            assert commune.district.key == "1002"
            assert commune.district.name == "District de la Glâne"
            assert commune.canton.key == "10"
            assert commune.canton.name == "Fribourg / Freiburg"
            assert commune.canton.short_name == "FR"
            exists_key = True
            break

    assert exists_key

def test_districts_by_canton():
    districts = client.get_districts_by_canton("10", 1, 10)

    assert districts.page_index == 1
    assert districts.page_size == 10
    assert districts.total_pages >= 1
    assert districts.total_count >= 1

    exists_key = False

    for district in districts:
        if district.key == "1001":
            assert district.name == "District de la Broye"
            assert district.canton.key == "10"
            assert district.canton.name == "Fribourg / Freiburg"
            assert district.canton.short_name == "FR"
            exists_key = True
            break

    assert exists_key

def test_full_text_search():
    streets = client.perform_full_text_search("8002 Bederstrasse", 1, 10)

    assert streets.page_index == 1
    assert streets.page_size == 10
    assert streets.total_pages >= 1
    assert streets.total_count >= 1

    exists_key = False

    for street in streets:
        if street.key == "10098541":
            assert street.name == "Bederstrasse"
            assert street.postal_code == "8002"
            assert street.locality == "Zürich"
            assert street.status == "Real"
            assert street.commune.key == "261"
            assert street.commune.name == "Zürich"
            assert street.commune.short_name == "Zürich"
            assert street.district.key == "112"
            assert street.district.name == "Bezirk Zürich"
            assert street.canton.key == "1"
            assert street.canton.short_name == "ZH"
            assert street.canton.name == "Zürich"
            exists_key = True
            break

    assert exists_key

def test_localities():
    localities = client.get_localities(None, "Zürich", 1, 10)

    assert localities.page_index == 1
    assert localities.page_size == 10
    assert localities.total_pages >= 1
    assert localities.total_count >= 1

    exists_key = False

    for locality in localities:
        if locality.postal_code == "8001":
            assert locality.name == "Zürich"
            assert locality.postal_code == "8001"
            assert locality.canton.short_name == "ZH"
            assert locality.canton.name == "Zürich"
            exists_key = True
            break

    assert exists_key

def test_streets():
    streets = client.get_streets("Bederstrasse", "8002", None, 1, 10)

    assert streets.page_index == 1
    assert streets.page_size == 10
    assert streets.total_pages >= 1
    assert streets.total_count >= 1

    exists_key = False

    for street in streets:
        if street.key == "10098541":
            assert street.name == "Bederstrasse"
            assert street.postal_code == "8002"
            assert street.locality == "Zürich"
            assert street.status == "Real"  # Update as needed to match your StreetStatus enum
            assert street.commune.key == "261"
            assert street.commune.name == "Zürich"
            assert street.commune.short_name == "Zürich"
            assert street.district.key == "112"
            assert street.district.name == "Bezirk Zürich"
            assert street.canton.key == "1"
            assert street.canton.short_name == "ZH"
            assert street.canton.name == "Zürich"
            exists_key = True
            break

    assert exists_key

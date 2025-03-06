##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.at.api_client import ApiClientForAustria

client = ApiClientForAustria()

def test_districts_by_federal_province():
    districts = client.get_districts_by_federal_province("7", 1, 10)

    assert districts.page_index == 1
    assert districts.page_size == 10
    assert districts.total_pages >= 1
    assert districts.total_count >= 1

    exists_key = False

    for district in districts:
        if district.key == "701":
            assert district.code == "701"
            assert district.name == "Innsbruck-Stadt"
            assert district.federal_province.key == "7"
            assert district.federal_province.name == "Tirol"
            exists_key = True
            break

    assert exists_key

def test_federal_provinces():
    federal_provinces = client.get_federal_provinces()

    assert len(federal_provinces) == 9

    exists_wien = any(fp.name == "Wien" for fp in federal_provinces)
    exists_burgenland = any(fp.name == "Burgenland" for fp in federal_provinces)

    assert exists_wien
    assert exists_burgenland

def test_full_text_search():
    streets = client.perform_full_text_search("1020 Adambergergasse", 1, 10)

    assert len(streets) > 0
    assert streets.page_index == 1
    assert streets.page_size == 10
    assert streets.total_pages >= 1
    assert streets.total_count >= 1

    exists_key = False

    for street in streets:
        if street.key == "900017":
            assert street.name == "Adambergergasse"
            assert street.postal_code == "1020"
            assert street.locality == "Wien, Leopoldstadt"
            assert street.municipality.key == "90001"
            assert street.municipality.code == "90201"
            assert street.municipality.name == "Wien"
            assert street.municipality.status == "Statutarstadt"
            assert street.district.key == "900"
            assert street.district.code == "902"
            assert street.district.name == "Wien  2., Leopoldstadt"
            assert street.federal_province.key == "9"
            assert street.federal_province.name == "Wien"
            exists_key = True
            break

    assert exists_key

def test_localities():
    localities = client.get_localities(None, "Wien", 1, 10)

    assert len(localities) > 0
    assert localities.page_index == 1
    assert localities.page_size == 10
    assert localities.total_pages >= 1
    assert localities.total_count >= 1

    exists_key = False

    for locality in localities:
        if locality.key == "17223":
            assert locality.name == "Wien, Innere Stadt"
            assert locality.postal_code == "1010"
            assert locality.municipality.key == "90001"
            assert locality.municipality.code == "90401"
            assert locality.municipality.name == "Wien"
            assert locality.municipality.status == "Statutarstadt"
            assert locality.district.key == "900"
            assert locality.district.code == "904"
            assert locality.district.name == "Wien  4., Wieden"
            assert locality.federal_province.key == "9"
            assert locality.federal_province.name == "Wien"
            exists_key = True
            break

    assert exists_key

def test_municipalities_by_district():
    municipalities = client.get_municipalities_by_district("701", 1, 10)

    assert len(municipalities) > 0
    assert municipalities.page_index == 1
    assert municipalities.page_size == 10
    assert municipalities.total_pages >= 1
    assert municipalities.total_count >= 1

    exists_key = False
    for municipality in municipalities:

        if municipality.key == "70101":
            assert municipality.code == "70101"
            assert municipality.name == "Innsbruck"
            assert municipality.postal_code == "6020"
            assert municipality.multiple_postal_codes
            assert municipality.status == "Statutarstadt"
            assert municipality.district.key == "701"
            assert municipality.district.code == "701"
            assert municipality.district.name == "Innsbruck-Stadt"
            assert municipality.federal_province.key == "7"
            assert municipality.federal_province.name == "Tirol"
            exists_key = True
            break

    assert exists_key

def test_municipalities_by_federal_province():
    municipalities = client.get_municipalities_by_federal_province("7", 1, 10)

    assert len(municipalities) > 0
    assert municipalities.page_index == 1
    assert municipalities.page_size == 10
    assert municipalities.total_pages >= 1
    assert municipalities.total_count >= 1

    exists_key = False
    
    for municipality in municipalities:
        if municipality.key == "70101":
            assert municipality.code == "70101"
            assert municipality.name == "Innsbruck"
            assert municipality.postal_code == "6020"
            assert municipality.multiple_postal_codes
            assert municipality.status == "Statutarstadt"
            assert municipality.district.key == "701"
            assert municipality.district.code == "701"
            assert municipality.district.name == "Innsbruck-Stadt"
            assert municipality.federal_province.key == "7"
            assert municipality.federal_province.name == "Tirol"
            exists_key = True
            break

    assert exists_key

def test_streets():
    streets = client.get_streets(None, "1020", None, 1, 10)

    assert len(streets) > 0
    assert streets.page_index == 1
    assert streets.page_size == 10
    assert streets.total_pages >= 1
    assert streets.total_count >= 1

    exists_key = False

    for street in streets:
        if street.key == "900017":
            assert street.name == "Adambergergasse"
            assert street.postal_code == "1020"
            assert street.locality == "Wien, Leopoldstadt"
            assert street.municipality.key == "90001"
            assert street.municipality.code == "90201"
            assert street.municipality.name == "Wien"
            assert street.municipality.status == "Statutarstadt"
            assert street.district.key == "900"
            assert street.district.code == "902"
            assert street.district.name == "Wien  2., Leopoldstadt"
            assert street.federal_province.key == "9"
            assert street.federal_province.name == "Wien"
            exists_key = True
            break

    assert exists_key

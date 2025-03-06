##
# Copyright (c) STÜBER SYSTEMS GmbH
# Licensed under the MIT License, Version 2.0. 
##

from openplzapi.de.api_client import ApiClientForGermany

client = ApiClientForGermany()

def test_districts_by_federal_state():
    districts = client.get_districts_by_federal_state("09", 1, 10)

    assert len(districts) > 0
    assert districts.page_index == 1
    assert districts.page_size == 10
    assert districts.total_pages >= 1
    assert districts.total_count >= 1

    exists_key = False

    for district in districts:
        if district.key == "09161":
            assert district.name == "Ingolstadt"
            assert district.type == "Kreisfreie Stadt"
            assert district.administrative_headquarters == "Ingolstadt"
            assert district.government_region.key == "091"
            assert district.government_region.name == "Oberbayern"
            assert district.federal_state.key == "09"
            assert district.federal_state.name == "Bayern"
            exists_key = True
            break

    assert exists_key

def test_districts_by_government_region():
    districts = client.get_districts_by_government_region("091", 1, 10)

    assert len(districts) > 0
    assert districts.page_index == 1
    assert districts.page_size == 10
    assert districts.total_pages >= 1
    assert districts.total_count >= 1

    exists_key = False

    for district in districts:
        if district.key == "09161":
            assert district.name == "Ingolstadt"
            assert district.type == "Kreisfreie Stadt"
            assert district.administrative_headquarters == "Ingolstadt"
            assert district.government_region.key == "091"
            assert district.government_region.name == "Oberbayern"
            assert district.federal_state.key == "09"
            assert district.federal_state.name == "Bayern"
            exists_key = True
            break

    assert exists_key

def test_federal_states():
    federal_states = client.get_federal_states()

    assert len(federal_states) == 16

    exists_berlin = any(state.name == "Berlin" for state in federal_states)
    exists_rheinlandpfalz = any(state.name == "Rheinland-Pfalz" for state in federal_states)

    assert exists_berlin
    assert exists_rheinlandpfalz

def test_full_text_search():
    streetsPage = client.perform_full_text_search("Berlin Pariser Platz", 1, 10)

    assert len(streetsPage) > 0
    assert streetsPage.page_index == 1
    assert streetsPage.page_size == 10
    assert streetsPage.total_pages >= 1
    assert streetsPage.total_count >= 1

    exists_key = False

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

    assert exists_key

def test_government_regions_by_federal_state():
    government_regions = client.get_government_regions_by_federal_state("09", 1, 10)

    assert len(government_regions) > 0
    assert government_regions.page_index == 1
    assert government_regions.page_size == 10
    assert government_regions.total_pages >= 1
    assert government_regions.total_count >= 1

    exists_key = False

    for region in government_regions:
        if region.key == "091":
            assert region.name == "Oberbayern"
            assert region.federal_state.key == "09"
            assert region.federal_state.name == "Bayern"
            exists_key = True
            break

    assert exists_key

def test_localities():
    localities = client.get_localities("56566", None, 1, 10)

    assert len(localities) > 0
    assert localities.page_index == 1
    assert localities.page_size == 10
    assert localities.total_pages >= 1
    assert localities.total_count >= 1

    exists_key = False

    for locality in localities:
        if locality.name == "Neuwied" and locality.postal_code == "56566":
            assert locality.municipality.key == "07138045"
            assert locality.municipality.name == "Neuwied, Stadt"
            assert locality.municipality.type == "Stadt"
            assert locality.district.key == "07138"
            assert locality.district.name == "Neuwied"
            assert locality.federal_state.key == "07"
            assert locality.federal_state.name == "Rheinland-Pfalz"
            exists_key = True
            break

    assert exists_key

def test_municipal_associations_by_district():
    municipal_associations = client.get_municipal_associations_by_district("09180", 1, 10)

    assert len(municipal_associations) > 0
    assert municipal_associations.page_index == 1
    assert municipal_associations.page_size == 10
    assert municipal_associations.total_pages >= 1
    assert municipal_associations.total_count >= 1

    exists_key = False

    for association in municipal_associations:
        if association.key == "091805133":
            assert association.name == "Saulgrub (VGem)"
            assert association.type == "Verwaltungsgemeinschaft"
            assert association.administrative_headquarters == "Saulgrub"
            assert association.district.key == "09180"
            assert association.district.name == "Garmisch-Partenkirchen"
            assert association.district.type == "Landkreis"
            assert association.federal_state.key == "09"
            assert association.federal_state.name == "Bayern"
            exists_key = True
            break

    assert exists_key

def test_municipal_associations_by_federal_state():
    municipal_associations = client.get_municipal_associations_by_federal_state("09", 1, 10)

    assert len(municipal_associations) > 0
    assert municipal_associations.page_index == 1
    assert municipal_associations.page_size == 10
    assert municipal_associations.total_pages >= 1
    assert municipal_associations.total_count >= 1

    exists_key = False

    for association in municipal_associations:
        if association.key == "091715101":
            assert association.name == "Emmerting (VGem)"
            assert association.type == "Verwaltungsgemeinschaft"
            assert association.administrative_headquarters == "Emmerting"
            assert association.district.key == "09171"
            assert association.district.name == "Altötting"
            assert association.federal_state.key == "09"
            assert association.federal_state.name == "Bayern"
            exists_key = True
            break

    assert exists_key

def test_municipalities_by_district():
    municipalities = client.get_municipalities_by_district("09180", 1, 10)

    assert len(municipalities) > 0
    assert municipalities.page_index == 1
    assert municipalities.page_size == 10
    assert municipalities.total_pages >= 1
    assert municipalities.total_count >= 1

    exists_key = False

    for municipality in municipalities:
        if municipality.key == "09180112":
            assert municipality.name == "Bad Kohlgrub"
            assert municipality.type == "Kreisangehörige Gemeinde"
            assert municipality.postal_code == "82433"
            assert not municipality.multiple_postal_codes
            assert municipality.district.key == "09180"
            assert municipality.district.name == "Garmisch-Partenkirchen"
            assert municipality.district.type == "Landkreis"
            assert municipality.government_region.key == "091"
            assert municipality.government_region.name == "Oberbayern"
            assert municipality.federal_state.key == "09"
            assert municipality.federal_state.name == "Bayern"
            exists_key = True
            break

    assert exists_key

def test_municipalities_by_federal_state():
    municipalities = client.get_municipalities_by_federal_state("09", 1, 10)

    assert len(municipalities) > 0
    assert municipalities.page_index == 1
    assert municipalities.page_size == 10
    assert municipalities.total_pages >= 1
    assert municipalities.total_count >= 1

    exists_key = False

    for municipality in municipalities:
        if municipality.key == "09161000":
            assert municipality.name == "Ingolstadt"
            assert municipality.type == "Kreisfreie Stadt"
            assert municipality.postal_code == "85047"
            assert municipality.multiple_postal_codes
            assert municipality.district.key == "09161"
            assert municipality.district.name == "Ingolstadt"
            assert municipality.district.type == "Kreisfreie Stadt"
            assert municipality.government_region.key == "091"
            assert municipality.government_region.name == "Oberbayern"
            assert municipality.federal_state.key == "09"
            assert municipality.federal_state.name == "Bayern"
            exists_key = True
            break

    assert exists_key

def test_streets():
    streets = client.get_streets("Pariser Platz", None, None, 1, 10)

    assert len(streets) > 0
    assert streets.page_index == 1
    assert streets.page_size == 10
    assert streets.total_pages >= 1
    assert streets.total_count >= 1

    exists_key = False

    for street in streets:
        if street.name == "Pariser Platz" and street.postal_code == "10117":
            assert street.locality == "Berlin"
            assert street.municipality.key == "11000000"
            assert street.municipality.name == "Berlin, Stadt"
            assert street.municipality.type == "Kreisfreie Stadt"
            assert street.federal_state.key == "11"
            assert street.federal_state.name == "Berlin"
            exists_key = True
            break

    assert exists_key

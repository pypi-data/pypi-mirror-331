"""
Tests for writing surface containers
"""

import os
import tempfile
import zipfile

import pytest
import topobank
import yaml
from django.conf import settings
from django.test import override_settings
from topobank.manager.containers import write_surface_container
from topobank.manager.models import Topography
from topobank.testing.factories import (SurfaceFactory, TagFactory,
                                        Topography1DFactory,
                                        Topography2DFactory, UserFactory)

from ..models import Publication


@override_settings(DELETE_EXISTING_FILES=True)
@pytest.mark.django_db
def test_surface_container(example_authors, django_capture_on_commit_callbacks):
    instrument_name = "My nice profilometer"
    instrument_type = "contact-based"
    instrument_params = {
        "tip_radius": {
            "value": 10,
            "unit": "µm",
        }
    }
    has_undefined_data = False
    fill_undefined_data_mode = Topography.FILL_UNDEFINED_DATA_MODE_NOFILLING

    user = UserFactory()
    tag1 = TagFactory(name="apple")
    tag2 = TagFactory(name="banana")
    surface1 = SurfaceFactory(creator=user, tags=[tag1])
    surface2 = SurfaceFactory(creator=user)
    surface3 = SurfaceFactory(creator=user, description="Nice results")

    Topography1DFactory(surface=surface1)
    topo1b = Topography2DFactory(
        surface=surface1,
        filename="example4.txt",
        height_scale_editable=False,
    )
    # for topo1b we use a datafile which has an height_scale_factor defined - this is needed in order
    # to test that this factor is NOT exported to meta.yaml -
    # for the initialisation syntax (datafile__from_path) here see:
    # https://factoryboy.readthedocs.io/en/stable/orms.html

    topo2a = Topography2DFactory(
        surface=surface2,
        tags=[tag1, tag2],
        description="Nice measurement",
        size_x=10,
        size_y=5,
        instrument_name=instrument_name,
        instrument_type=instrument_type,
        instrument_parameters=instrument_params,
        has_undefined_data=has_undefined_data,
        fill_undefined_data_mode=fill_undefined_data_mode,
    )
    # surface 3 is empty

    # surface 2 is published
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        publication = Publication.publish(surface2, "cc0-1.0", surface2.creator, example_authors)
    assert len(callbacks) == 1
    surface4 = publication.surface
    surfaces = [surface1, surface2, surface3, surface4]
    assert publication.surface.topography_set.first().squeezed_datafile

    #
    # Create container file
    #
    outfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    write_surface_container(outfile, surfaces)
    outfile.close()

    # reopen and check contents
    with zipfile.ZipFile(outfile.name, mode="r") as zf:
        meta_file = zf.open("meta.yml")
        meta = yaml.safe_load(meta_file)

        meta_surfaces = meta["surfaces"]

        # check number of surfaces and topographies
        for surf_idx, surf in enumerate(surfaces):
            assert meta_surfaces[surf_idx]["name"] == surf.name
            assert meta_surfaces[surf_idx]["category"] == surf.category
            assert meta_surfaces[surf_idx]["description"] == surf.description
            assert meta_surfaces[surf_idx]["creator"]["name"] == surf.creator.name
            assert meta_surfaces[surf_idx]["creator"]["orcid"] == surf.creator.orcid_id
            assert (
                len(meta_surfaces[surf_idx]["topographies"])
                == surf.topography_set.count()
            )

        # check some tags
        assert meta_surfaces[0]["tags"] == ["apple"]
        assert meta_surfaces[1]["topographies"][0]["tags"] == ["apple", "banana"]

        # all data files should be included
        for surf_descr in meta_surfaces:
            for topo_descr in surf_descr["topographies"]:
                datafile_name = topo_descr["datafile"]["original"]
                assert datafile_name
                assert datafile_name in zf.namelist()
                squeezed_datafile_name = topo_descr["datafile"]["squeezed-netcdf"]
                assert squeezed_datafile_name
                assert squeezed_datafile_name in zf.namelist()

        # check version information
        assert meta["versions"]["topobank"] == topobank.__version__
        assert "creation_time" in meta

        # check publication fields
        assert not meta_surfaces[0]["is_published"]
        assert not meta_surfaces[1]["is_published"]
        assert not meta_surfaces[2]["is_published"]
        assert meta_surfaces[3]["is_published"]
        meta_surface4 = meta_surfaces[3]
        meta_surface_4_pub = meta_surface4["publication"]
        assert meta_surface_4_pub["authors"] == "Hermione Granger, Harry Potter"
        assert (
            meta_surface_4_pub["license"]
            == settings.CC_LICENSE_INFOS["cc0-1.0"]["option_name"]
        )
        assert meta_surface_4_pub["version"] == 1

        # check some topography fields
        topo_meta = meta_surface4["topographies"][0]
        assert topo_meta["tags"] == ["apple", "banana"]
        for field in [
            "is_periodic",
            "description",
            "detrend_mode",
            "data_source",
            "measurement_date",
            "name",
            "unit",
        ]:
            assert topo_meta[field] == getattr(topo2a, field)
        assert topo_meta["size"] == [topo2a.size_x, topo2a.size_y]

        assert topo_meta["instrument"] == {
            "name": instrument_name,
            "type": instrument_type,
            "parameters": instrument_params,
        }

        # topo1a should have an height_scale_factor in meta data because
        # this information is not included in the data file
        topo1a_meta = meta_surfaces[0]["topographies"][0]
        assert "height_scale" in topo1a_meta

        #
        # topo1b should have no height_scale_factor included
        # because it's already applied on import, see GH 718
        #
        topo1b_meta = meta_surfaces[0]["topographies"][1]
        assert topo1b_meta["name"] == topo1b.name
        assert "height_scale" not in topo1b_meta

        assert "fill_undefined_data_mode" in topo1a_meta
        assert "fill_undefined_data_mode" in topo1b_meta
        assert "has_undefined_data" in topo1a_meta
        assert "has_undefined_data" in topo1b_meta

    os.remove(outfile.name)

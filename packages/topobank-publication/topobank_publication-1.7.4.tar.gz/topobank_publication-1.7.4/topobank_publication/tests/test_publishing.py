import datetime
import zipfile

import django.db.models.deletion
import pytest
from django.conf import settings
from django.shortcuts import reverse
from topobank.manager.models import Surface
from topobank.testing.factories import (SurfaceFactory, TagFactory,
                                        Topography2DFactory, UserFactory)
from topobank.testing.utils import assert_in_content, assert_not_in_content

from topobank_publication.forms import SurfacePublishForm
from topobank_publication.models import Publication
from topobank_publication.utils import (NewPublicationTooFastException,
                                        PublicationException,
                                        PublicationsDisabledException,
                                        set_publication_permissions)

# Example user
bob = dict(
    first_name="Bob",
    last_name="Doe",
    orcid_id="123",
    affiliations=[dict(name="UofA", ror_id="123")],
)


@pytest.mark.django_db
def test_publication_version(settings):
    settings.MIN_SECONDS_BETWEEN_SAME_SURFACE_PUBLICATIONS = None  # disable

    surface = SurfaceFactory()
    publication_v1 = Publication.publish(surface, "cc0-1.0", surface.creator, "Bob")

    assert publication_v1.version == 1

    surface.name = "new name"
    publication_v2 = Publication.publish(surface, "cc0-1.0", surface.creator, "Bob")
    assert publication_v2.version == 2

    assert publication_v1.original_surface == publication_v2.original_surface
    assert publication_v1.surface != publication_v2.surface


@pytest.mark.django_db
def test_publication_disabled(settings):
    settings.PUBLICATION_ENABLED = False
    surface = SurfaceFactory()
    with pytest.raises(PublicationsDisabledException):
        Publication.publish(surface, "cc0-1.0", surface.creator, "Bob")


@pytest.mark.django_db
def test_publication_superuser(settings):
    surface = SurfaceFactory()
    surface.creator.is_superuser = True
    surface.creator.save()
    nb_surfaces = len(Surface.objects.all())
    with pytest.raises(PublicationException):
        Publication.publish(surface, "cc0-1.0", surface.creator, "Bob")
    # Make sure that the copy, and not the original surface, is deleted again
    assert len(Surface.objects.all()) == nb_surfaces


@pytest.mark.django_db
def test_failing_publication(settings):
    settings.DATACITE_API_URL = "https://nonexistent.api.url/"  # lets publication fail
    settings.PUBLICATION_DOI_MANDATORY = True  # make sure to contact DataCite
    settings.PUBLICATION_DOI_PREFIX = "10.12345"
    surface = SurfaceFactory()
    nb_surfaces = len(Surface.objects.all())
    with pytest.raises(PublicationException):
        Publication.publish(surface, "cc0-1.0", surface.creator, [bob])
    # Check that the copy of the surface was properly deleted again
    assert len(Surface.objects.all()) == nb_surfaces


@pytest.mark.django_db
def test_publication_fields(example_authors):
    user = UserFactory(name="Tom")
    surface = SurfaceFactory(creator=user)
    publication = Publication.publish(surface, "cc0-1.0", surface.creator, example_authors)

    assert publication.license == "cc0-1.0"
    assert publication.original_surface == surface
    assert publication.surface != publication.original_surface
    assert publication.publisher == surface.creator
    assert publication.version == 1
    assert publication.get_authors_string() == "Hermione Granger, Harry Potter"


@pytest.mark.django_db
def test_published_field():
    surface = SurfaceFactory()
    assert not surface.is_published
    publication = Publication.publish(surface, "cc0-1.0", surface.creator, "Alice")
    assert not publication.original_surface.is_published
    assert publication.surface.is_published


@pytest.mark.django_db
def test_set_publication_permissions():
    user1 = UserFactory()
    user2 = UserFactory()
    surface = SurfaceFactory(creator=user1)

    # before publishing, user1 is allowed everything,
    # user2 nothing
    assert surface.has_permission(user1, "full")
    assert not surface.has_permission(user2, "view")

    set_publication_permissions(surface)

    # now, both users are only allowed viewing
    user1_perms = surface.get_permission(user1)
    user2_perms = surface.get_permission(user2)

    assert user1_perms == "view"
    assert user2_perms == "view"

    assert not surface.has_permission(user1, "edit")


@pytest.mark.django_db
def test_permissions_for_published():
    user1 = UserFactory()
    user2 = UserFactory()
    surface = SurfaceFactory(creator=user1)

    # before publishing, user1 is allowed everything,
    # user2 nothing
    assert surface.has_permission(user1, "full")
    assert not surface.has_permission(user2, "view")

    # for the published surface, both users are only allowed viewing
    publication = Publication.publish(surface, "cc0-1.0", surface.creator, "Alice")

    assert publication.surface.get_permission(user1) == "view"
    assert publication.surface.get_permission(user2) == "view"

    # the permissions for the original surface has not been changed
    assert surface.has_permission(user1, "full")
    assert not surface.has_permission(user2, "view")


@pytest.mark.django_db
def test_surface_deepcopy():
    tag1 = TagFactory()
    tag2 = TagFactory()

    datea = datetime.date(2020, 7, 1)
    dateb = datetime.date(2020, 7, 2)

    surface1 = SurfaceFactory(description="test", tags=[tag1])
    topo1a = Topography2DFactory(
        surface=surface1,
        name="a",
        measurement_date=datea,
        tags=[tag2],
        description="This is a)",
        instrument_name="Instrument A",
        instrument_type="undefined",
    )
    topo1b = Topography2DFactory(
        surface=surface1,
        name="b",
        measurement_date=dateb,
        tags=[tag1, tag2],
        description="This is b)",
        instrument_name="Instrument B",
        instrument_type="microscope-based",
        instrument_parameters={"resolution": {"value": 10, "unit": "mm"}},
    )

    surface2 = surface1.deepcopy()

    assert surface1.id != surface2.id  # really different objects

    assert surface1.name == surface2.name
    assert surface1.category == surface2.category
    assert surface1.creator == surface2.creator
    assert surface1.description == surface2.description
    assert surface1.tags == surface2.tags

    topo2a = surface2.topography_set.get(name="a")
    topo2b = surface2.topography_set.get(name="b")

    for t1, t2 in ((topo1a, topo2a), (topo1b, topo2b)):
        assert t1.id != t2.id  # really different objects
        assert t1.measurement_date == t2.measurement_date
        assert t1.datafile != t2.datafile

        assert t1.tags == t2.tags

        assert t1.size_x == t2.size_x
        assert t1.size_y == t2.size_y
        assert t1.description == t2.description

        assert t1.datafile.filename == t2.datafile.filename  # must be unique
        assert t1.datafile.file.name != t2.datafile.file.name  # must be unique

        # file contents should be the same
        assert t1.datafile.open(mode="rb").read() == t2.datafile.open(mode="rb").read()
        assert t1.data_source == t2.data_source
        assert t1.datafile_format == t2.datafile_format

        assert t1.instrument_name == t2.instrument_name
        assert t1.instrument_type == t2.instrument_type
        assert t1.instrument_parameters == t2.instrument_parameters


@pytest.mark.parametrize("license", settings.CC_LICENSE_INFOS.keys())
@pytest.mark.django_db
def test_license_in_surface_download(
    client, license, handle_usage_statistics, example_authors
):
    import io

    user1 = UserFactory()
    user2 = UserFactory()
    surface = SurfaceFactory(creator=user1)
    Topography2DFactory(surface=surface)
    publication = Publication.publish(surface, license, surface.creator, example_authors)
    client.force_login(user2)

    response = client.get(
        reverse(
            "manager:surface-download", kwargs=dict(surface_id=publication.surface.id)
        )
    )

    assert response.status_code == 200
    # for published surfaces, the downloaded file should have the name "ce-<short_url>.zip"
    assert (
        response["Content-Disposition"]
        == f'attachment; filename="ce-{publication.short_url}.zip"'
    )

    downloaded_file = io.BytesIO(response.content)
    with zipfile.ZipFile(downloaded_file) as z:
        with z.open("README.txt") as readme_file:
            readme_bytes = readme_file.read()
            readme_txt = readme_bytes.decode("utf-8")
            # assert publication.get_license_display() in readme_txt
            assert settings.CC_LICENSE_INFOS[license]["title"] in readme_txt

        # There should be also a file "LICENSE-....txt"
        expected_license_filename = f"LICENSE-{license}.txt"
        with z.open(expected_license_filename) as license_file:
            license_bytes = license_file.read()
            license_txt = license_bytes.decode("utf-8")
            # title of license should be in the text
            assert settings.CC_LICENSE_INFOS[license]["title"] in license_txt


@pytest.mark.django_db
def test_dont_show_published_surfaces_when_shared_filter_used(
    client, handle_usage_statistics, example_authors
):
    alice = UserFactory()
    bob = UserFactory()
    surface1 = SurfaceFactory(creator=alice, name="Shared Surface")
    surface1.grant_permission(bob)
    surface2 = SurfaceFactory(creator=alice, name="Published Surface")
    Publication.publish(surface2, "cc0-1.0", surface2.creator, example_authors)

    client.force_login(bob)

    response = client.get(
        reverse("ce_ui:search") + "?sharing_status=others"
    )  # means "created by someone else"
    assert_in_content(response, "Shared Surface")
    assert_not_in_content(response, "Published Surface")

    response = client.get(
        reverse("ce_ui:search") + "?sharing_status=published"
    )  # means "published by anyone"
    assert_not_in_content(response, "Shared Surface")
    assert_in_content(response, "Published Surface")


@pytest.mark.django_db
def test_limit_publication_frequency(settings):
    """
    If the publication link is clicked several
    times in a fast sequence, there should be only
    one publication.
    """
    settings.MIN_SECONDS_BETWEEN_SAME_SURFACE_PUBLICATIONS = (
        10000  # to be sure this must fail here
    )

    alice = UserFactory()
    surface = SurfaceFactory(creator=alice)

    Publication.publish(surface, "cc0-1.0", surface.creator, "Alice")
    with pytest.raises(NewPublicationTooFastException):
        Publication.publish(surface, "cc0-1.0", surface.creator, "Alice, Bob")


def test_publishing_no_authors_given():
    form_data = {
        "license": "cc0-1.0",
        "agreed": True,
        "copyright_hold": True,
    }
    form = SurfacePublishForm(data=form_data)
    assert not form.is_valid()
    assert form.errors["__all__"] == ["At least one author must be given."]


def test_publishing_unique_author_names():
    form_data = {
        "authors_json": [
            {
                "first_name": "Alice",
                "last_name": "Wonderland",
                "orcid_id": "",
                "affiliations": [],
            },
            {
                "first_name": "Bob",
                "last_name": "Wonderland",
                "orcid_id": "",
                "affiliations": [],
            },
            {
                "first_name": "Alice",
                "last_name": "Wonderland",
                "orcid_id": "",
                "affiliations": [],
            },
        ],
        "license": "cc0-1.0",
        "agreed": True,
        "copyright_hold": True,
    }
    form = SurfacePublishForm(data=form_data)
    assert not form.is_valid()
    assert form.errors["__all__"] == [
        "Duplicate author given! Make sure authors differ in at least one field."
    ]


def test_publishing_invalid_orcid():
    form_data = {
        "authors_json": [
            {
                "first_name": "Alice",
                "last_name": "Wonderland",
                "orcid_id": "1234-1234-1234-abcd",
                "affiliations": [],
            },
        ],
        "license": "cc0-1.0",
        "agreed": True,
        "copyright_hold": True,
    }
    form = SurfacePublishForm(data=form_data)
    assert not form.is_valid()
    assert form.errors["__all__"] == [
        "ORCID ID must match pattern xxxx-xxxx-xxxx-xxxy, where x is a digit "
        "and y a digit or the capital letter X."
    ]


def test_publishing_invalid_ror_id():
    form_data = {
        "authors_json": [
            {
                "first_name": "Alice",
                "last_name": "Wonderland",
                "orcid_id": "",
                "affiliations": [
                    {
                        "name": "Wonderland University",
                        "ror_id": "0123456789downtherabbithole",
                    }
                ],
            },
        ],
        "license": "cc0-1.0",
        "agreed": True,
        "copyright_hold": True,
    }
    form = SurfacePublishForm(data=form_data)
    assert not form.is_valid()
    assert form.errors["__all__"] == [
        "Incorrect format for ROR ID '0123456789downtherabbithole', "
        "should start with 0 (zero), followed by 6 characters and "
        "should end with 2 digits."
    ]


def test_publishing_wrong_license(example_authors):
    form_data = {
        "authors_json": example_authors,
        "agreed": True,
        "copyright_hold": True,
        "license": "fantasy",
    }
    form = SurfacePublishForm(data=form_data)
    assert not form.is_valid()

    assert form.errors["license"] == [
        "Select a valid choice. fantasy is not one of the available choices."
    ]


@pytest.mark.django_db
def test_publication_original_cannot_be_deleted(example_authors):
    user = UserFactory(name="Tom")
    surface = SurfaceFactory(creator=user)
    Publication.publish(surface, "cc0-1.0", surface.creator, example_authors)

    assert Surface.objects.filter(id=surface.id).count() == 1
    assert Publication.objects.filter(original_surface=surface.id).count() == 1

    with pytest.raises(django.db.models.deletion.ProtectedError):
        surface.delete()

    assert Surface.objects.filter(id=surface.id).count() == 1
    assert Publication.objects.filter(original_surface=surface.id).count() == 1

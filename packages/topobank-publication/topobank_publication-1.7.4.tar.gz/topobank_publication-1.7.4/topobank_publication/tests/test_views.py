"""Tests related to views."""

import zipfile
from io import BytesIO

import pytest
import yaml
from django.shortcuts import reverse
from topobank.testing.factories import UserFactory
from topobank.testing.utils import assert_in_content


@pytest.mark.django_db
def test_go_link_html(client, example_pub):
    # The normal client send not header
    user = UserFactory()
    client.force_login(user)
    url = reverse('publication:go', kwargs=dict(short_url=example_pub.short_url))
    assert url == f'/go/{example_pub.short_url}/'
    response = client.get(url, follow=False)
    assert response.status_code == 302
    assert response.url.endswith(f'?surface={example_pub.surface.id}')


@pytest.mark.django_db
def test_go_link_api(api_client, example_pub, handle_usage_statistics):
    # We send a header with HTTP_ACCEPT application/json to get the API response
    user = UserFactory()
    api_client.force_login(user)
    url = reverse('publication:go', kwargs=dict(short_url=example_pub.short_url))
    assert url == f'/go/{example_pub.short_url}/'
    response = api_client.get(url, follow=False, HTTP_ACCEPT='application/json')
    assert response.status_code == 302
    assert response.url.endswith(f'api/publication/{example_pub.id}/')

    response = api_client.get(url, follow=True, HTTP_ACCEPT='application/json')
    assert response.status_code == 200
    assert response.data['url'].endswith(f'api/publication/{example_pub.id}/')
    assert response.data['surface'].endswith(f'api/surface/{example_pub.surface.id}/')
    assert response.data['short_url'] == example_pub.short_url


@pytest.mark.django_db
def test_go_download(api_client, example_pub, handle_usage_statistics):
    user = UserFactory()
    api_client.force_login(user)
    url = reverse('publication:go', kwargs=dict(short_url=example_pub.short_url))
    assert url == f'/go/{example_pub.short_url}/'
    response = api_client.get(url, follow=True, HTTP_ACCEPT='application/json')
    assert response.status_code == 200

    response = api_client.get(response.data['download_url'], follow=True)
    assert response.status_code == 200

    surface = example_pub.surface

    # open zip file and look into meta file, there should be two surfaces and three topographies
    with zipfile.ZipFile(BytesIO(response.content)) as zf:
        meta_file = zf.open('meta.yml')
        meta = yaml.safe_load(meta_file)
        assert len(meta['surfaces']) == 1
        assert len(meta['surfaces'][0]['topographies']) == surface.num_topographies()
        assert meta['surfaces'][0]['name'] == surface.name

    assert_in_content(response, example_pub.surface.name)


@pytest.mark.django_db
def test_redirection_invalid_publication_link(client, orcid_socialapp, handle_usage_statistics):
    response = client.get(reverse('publication:go', kwargs=dict(short_url='THISISNONSENSE')))
    assert response.status_code == 404

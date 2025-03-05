import io
from unittest.mock import Mock

import pytest

from entitysdk.client import Client
from entitysdk.models.core import Entity


def test_client_project_context__raises():
    client = Client(api_url="foo", project_context=None)

    with pytest.raises(ValueError, match="A project context must be specified."):
        client._project_context(override_context=None)


def test_client_search(client):
    client._http_client.request.return_value = Mock(json=lambda: {"data": [{"id": 1}, {"id": 2}]})

    res = list(
        client.search(
            entity_type=Entity,
            query={"name": "foo"},
            token="mock-token",
            limit=2,
        )
    )
    assert len(res) == 2
    assert res[0].id == 1
    assert res[1].id == 2


def test_client_update(client):
    client._http_client.request.return_value = Mock(json=lambda: {"id": 1})

    res = client.update(
        entity_id=1,
        entity_type=Entity,
        attrs_or_entity=Entity(id="1"),
        token="mock-token",
    )

    assert res.id == 1


@pytest.fixture
def mock_asset_response():
    return {
        "id": 1,
        "path": "path/to/asset",
        "fullpath": "full/path/to/asset",
        "bucket_name": "bucket_name",
        "is_directory": False,
        "content_type": "text/plain",
        "size": 100,
        "status": "completed",
        "meta": {},
    }


def test_client_upload_file(tmp_path, client, mock_asset_response, api_url, project_context):
    client._http_client.request.return_value = Mock(json=lambda: mock_asset_response)

    path = tmp_path / "foo.h5"
    path.write_bytes(b"foo")

    res = client.upload_file(
        entity_id=1,
        entity_type=Entity,
        file_name="foo",
        file_path=path,
        file_content_type="text/plain",
        file_metadata={"key": "value"},
        token="mock-token",
    )

    call_args = client._http_client.request.call_args

    assert call_args.kwargs["method"] == "POST"
    assert call_args.kwargs["url"] == f"{api_url}/entity/1/assets"
    assert call_args.kwargs["headers"]["project-id"] == project_context.project_id
    assert call_args.kwargs["headers"]["virtual-lab-id"] == project_context.virtual_lab_id
    assert call_args.kwargs["headers"]["Authorization"] == "Bearer mock-token"

    assert res.id == 1


def test_client_upload_content(client, mock_asset_response, api_url, project_context):
    client._http_client.request.return_value = Mock(json=lambda: mock_asset_response)

    buffer = io.BytesIO(b"foo")

    res = client.upload_content(
        entity_id=1,
        entity_type=Entity,
        file_name="foo.txt",
        file_content=buffer,
        file_content_type="text/plain",
        file_metadata={"key": "value"},
        token="mock-token",
    )

    client._http_client.request.assert_called_once_with(
        method="POST",
        url=f"{api_url}/entity/1/assets",
        headers={
            "project-id": project_context.project_id,
            "virtual-lab-id": project_context.virtual_lab_id,
            "Authorization": "Bearer mock-token",
        },
        json=None,
        files={
            "file": (
                "foo.txt",
                buffer,
                "text/plain",
            )
        },
        params=None,
        follow_redirects=True,
    )

    assert res.id == 1


def test_client_download_content(client, mock_asset_response, api_url, project_context):
    client._http_client.request.return_value = Mock(content=b"foo")

    res = client.download_content(
        entity_id=1,
        entity_type=Entity,
        asset_id=2,
        token="mock-token",
    )
    assert res == b"foo"

    client._http_client.request.assert_called_once_with(
        method="GET",
        url=f"{api_url}/entity/1/assets/2",
        headers={
            "project-id": project_context.project_id,
            "virtual-lab-id": project_context.virtual_lab_id,
            "Authorization": "Bearer mock-token",
        },
        json=None,
        params=None,
        files=None,
        follow_redirects=True,
    )


def test_client_download_file(tmp_path, client, mock_asset_response, api_url, project_context):
    client._http_client.request.return_value = Mock(content=b"foo")

    output_path = tmp_path / "foo.h5"

    client.download_file(
        entity_id=1,
        entity_type=Entity,
        asset_id=2,
        output_path=output_path,
        token="mock-token",
    )
    assert output_path.read_bytes() == b"foo"


def test_client_get(client, mock_asset_response, api_url, project_context):
    def mock_request(*args, **kwargs):
        if "assets" in kwargs["url"]:
            return Mock(
                json=lambda: {"data": [mock_asset_response, mock_asset_response]},
            )
        return Mock(json=lambda: {"id": 1})

    client._http_client.request = mock_request

    res = client.get(
        entity_id=1,
        entity_type=Entity,
        token="mock-token",
        with_assets=True,
    )
    assert res.id == 1
    assert len(res.assets) == 2

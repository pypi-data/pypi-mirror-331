import pytest
import os
from typing import Optional
from pydantic import BaseModel
from pytest_mock.plugin import MockerFixture
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from ssb_altinn3_util.security.role_authorization import authorize

app = FastAPI()


class AccessTestModel(BaseModel):
    ra_nummer: Optional[str] = None
    skjema_id: Optional[int] = None
    app_id: Optional[str] = None
    periode_id: Optional[int] = None
    periode_aar: Optional[int] = None
    periode_type: Optional[str] = None
    periode_nr: Optional[int] = None
    pulje_id: Optional[int] = None
    utsending_id: Optional[int] = None
    message: str


@app.get("/hello")
@authorize(require_role="admin")
def hello(request: Request) -> str:
    return "hello"


@app.post("/enforce")
@authorize(require_role="admin", enable_form_access=True)
def post_call_with_form_access_enforcement(request: Request, model: AccessTestModel):
    return f"Received: '{model.message}'"


@app.put("/enforce")
@authorize(require_role="admin", enable_form_access=True)
def post_call_with_form_access_enforcement(request: Request, model: AccessTestModel):
    return f"Received: '{model.message}'"


@app.delete("/ra_nummer/{ra_nummer}")
@authorize(require_role="admin", enable_form_access=True)
def delete_ra_nummer(ra_nummer: str, request: Request):
    return f"ra_nummer: {ra_nummer}"


@app.delete("/skjema/{skjema_id}")
@authorize(require_role="admin", enable_form_access=True)
def delete_skjema(skjema_id: int, request: Request):
    return f"skjema_id: {skjema_id}"


@app.delete("/app/{app_id}")
@authorize(require_role="admin", enable_form_access=True)
def delete_app_id(app_id: str, request: Request):
    return f"app_id: {app_id}"


@app.delete("/periode/{periode_id}")
@authorize(require_role="admin", enable_form_access=True)
def delete_periode0(periode_id: int, request: Request):
    return f"periode_id: {periode_id}"


@app.delete("/pulje/{pulje_id}")
@authorize(require_role="admin", enable_form_access=True)
def delete_pulje(pulje_id: int, request: Request):
    return f"pulje_id: {pulje_id}"


@app.delete("/utsending/{utsending_id}")
@authorize(require_role="admin", enable_form_access=True)
def delete_utsending(utsending_id: int, request: Request):
    return f"utsending_id: {utsending_id}"


client = TestClient(app)


def test_testclient_working(
    mocker: MockerFixture, fake_auth_result_ok, fake_auth_header
):
    result = fake_auth_result_ok()
    mocker.patch.dict(os.environ, {"AUTH_SERVICE_URL": "https://auth.mock"}, clear=True)

    auth_call = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    headers = {"Authorization": fake_auth_header('{"email":"user@email.com"}')}
    response = client.get("/hello", headers=headers)

    assert response.json() == "hello"
    auth_call.assert_called_once()
    auth_call.assert_called_with(
        user_email="user@email.com",
        requested_role="admin",
        form_access_key=None,
        is_root_element=False,
    )


@pytest.mark.parametrize(
    "method,field,val,expected",
    {
        ("post", "ra_nummer", "RA-1234A3", "RA_NUMMER:RA-1234A3"),
        ("post", "skjema_id", "42", "SKJEMA_ID:42"),
        ("post", "app_id", "ra1234-01", "APP_ID:ra1234-01"),
        ("post", "periode_id", "42", "PERIODE_ID:42"),
        ("post", "pulje_id", "42", "PULJE_ID:42"),
        ("post", "utsending_id", "42", "UTSENDING_ID:42"),
        ("post", None, None, None),
        ("put", "ra_nummer", "RA-1234A3", "RA_NUMMER:RA-1234A3"),
        ("put", "skjema_id", "42", "SKJEMA_ID:42"),
        ("put", "app_id", "ra1234-01", "APP_ID:ra1234-01"),
        ("put", "periode_id", "42", "PERIODE_ID:42"),
        ("put", "pulje_id", "42", "PULJE_ID:42"),
        ("put", "utsending_id", "42", "UTSENDING_ID:42"),
        ("put", None, None, None),
    },
)
def test_form_access_post_key_ok(
    mocker: MockerFixture,
    fake_auth_result_ok,
    fake_auth_header,
    method: str,
    field: Optional[str],
    val: Optional[str or int],
    expected: Optional[str],
):
    result = fake_auth_result_ok()
    mocker.patch.dict(os.environ, {"AUTH_SERVICE_URL": "https://auth.mock"}, clear=True)

    auth_call = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    headers = {"Authorization": fake_auth_header('{"email":"user@email.com"}')}
    model = AccessTestModel(message="hello, test")

    if field is not None:
        setattr(model, field, val)
        if field == "periode_aar":
            setattr(model, "periode_type", "KVRT")
            setattr(model, "periode_nr", 1)

    if method == "post":
        response = client.post(
            "/enforce", headers=headers, data=model.model_dump_json(exclude_none=True)
        )
    elif method == "put":
        response = client.put(
            "/enforce", headers=headers, data=model.model_dump_json(exclude_none=True)
        )
    else:
        assert False

    if expected is None:
        assert response.status_code == 403
        auth_call.assert_not_called()
    else:
        assert response.json() == f"Received: '{model.message}'"
        auth_call.assert_called_once()
        auth_call.assert_called_with(
            user_email="user@email.com",
            requested_role="admin",
            form_access_key=expected,
            is_root_element=False,
        )


@pytest.mark.parametrize(
    "path,field,val,expected",
    {
        ("ra_nummer", "ra_nummer", "RA-1234A3", "RA_NUMMER:RA-1234A3"),
        ("skjema", "skjema_id", "42", "SKJEMA_ID:42"),
        ("app", "app_id", "ra1234-01", "APP_ID:ra1234-01"),
        ("periode", "periode_id", "42", "PERIODE_ID:42"),
        ("pulje", "pulje_id", "42", "PULJE_ID:42"),
        ("utsending", "utsending_id", "42", "UTSENDING_ID:42"),
    },
)
def test_form_access_delete_key_ok(
    mocker: MockerFixture,
    fake_auth_result_ok,
    fake_auth_header,
    path: str,
    field: Optional[str],
    val: Optional[str or int],
    expected: Optional[str],
):
    result = fake_auth_result_ok()
    mocker.patch.dict(os.environ, {"AUTH_SERVICE_URL": "https://auth.mock"}, clear=True)

    auth_call = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    headers = {"Authorization": fake_auth_header('{"email":"user@email.com"}')}

    response = client.delete(f"/{path}/{val}", headers=headers)

    if expected is None:
        assert response.status_code == 403
        auth_call.assert_not_called()
    else:
        assert response.json() == f"{field}: {val}"
        auth_call.assert_called_once()
        auth_call.assert_called_with(
            user_email="user@email.com",
            requested_role="admin",
            form_access_key=expected,
            is_root_element=False,
        )

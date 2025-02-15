import json
import os
from base64 import b64decode

import pytest
from fastapi.testclient import TestClient
from prepline_test_project.api.app import app
from requests_toolbelt.multipart import decoder

from functions_and_variables import (
    FILENAME_LENGTHS,
    FILENAME_FORMATS,
    JSON,
    MIXED,
    FILE_DOCX,
    FILE_IMAGE,
    FILE_JSON,
    FILE_MSG,
    RESPONSE_SCHEMA_ISD,
    RESPONSE_SCHEMA_LABELSTUDIO,
    P_INPUT_1_SINGLE,
    P_INPUT_2_EMPTY,
    P_INPUT_2_MULTI,
    P_INPUT_1_AND_2_MULTI,
    P_INPUT_1_EMPTY,
    P_INPUT_1_MULTI,
    P_INPUT_2_SINGLE,
    TEXT_CSV,
    convert_files_for_api,
    generate_header_kwargs,
    GZIP_FILE_IMAGE,
    GZIP_FILE_DOCX,
    FILE_MARKDOWN,
)

# accepts: files, input2
PROCESS_FILE_1_ROUTE = ["/test-project/v1.2.3/process-file-1", "/test-project/v1/process-file-1"]

# Pull this over here for test_supported_mimetypes
PROCESS_FILE_TEXT_1_ROUTE = [
    "/test-project/v1.2.3/process-text-file-1",
    "/test-project/v1/process-text-file-1",
]

# accepts: files
PROCESS_FILE_2_ROUTE = ["/test-project/v1.2.3/process-file-2", "/test-project/v1/process-file-2"]

# accepts: files, response_type, response_schema
PROCESS_FILE_3_ROUTE = ["/test-project/v1.2.3/process-file-3", "/test-project/v1/process-file-3"]

# accepts: files, response_type, response_schema, input1
PROCESS_FILE_4_ROUTE = ["/test-project/v1.2.3/process-file-4", "/test-project/v1/process-file-4"]

# accepts: files, response_type, response_schema, input1, input2
PROCESS_FILE_5_ROUTE = ["/test-project/v1.2.3/process-file-5", "/test-project/v1/process-file-5"]

client = TestClient(app)


def _assert_response_for_process_file_1(
    test_files, test_params, test_type_header, response, gz_content_type
):
    """assert json response payload matches expected response."""
    api_param_value = []
    if test_params is not None and "input2" in test_params:
        api_param_value = test_params["input2"]

    def _json_for_one_file(test_file):
        if test_file.endswith(".gz"):
            test_file = test_file[:-3]
        return {
            "silly_result": " : ".join(
                [
                    str(FILENAME_LENGTHS[test_file]),
                    test_file,
                    gz_content_type or FILENAME_FORMATS[test_file],
                    str(api_param_value),
                ]
            )
        }

    if test_type_header == JSON:
        if len(test_files) == 1:
            assert response.json() == _json_for_one_file(test_files[0])
        else:
            assert response.json() == [_json_for_one_file(test_file) for test_file in test_files]

    elif test_type_header == MIXED:
        data = decoder.MultipartDecoder.from_response(response)
        for i, part in enumerate(data.parts):
            json_part = json.loads(b64decode(part.content))
            assert json_part == _json_for_one_file(test_files[i])


def _assert_response_for_process_file_2(test_files, response, response_type):
    def _json_for_one_file(test_file):
        if test_file.endswith(".gz"):
            test_file = test_file[:-3]
        return {"silly_result": " : ".join([str(FILENAME_LENGTHS[test_file])])}

    if response_type in [JSON, TEXT_CSV]:
        if len(test_files) == 1:
            assert response.json() == _json_for_one_file(test_files[0])
        else:
            assert response.json() == [_json_for_one_file(test_file) for test_file in test_files]
    elif response_type == MIXED:
        data = decoder.MultipartDecoder.from_response(response)
        for i, part in enumerate(data.parts):
            json_part = json.loads(b64decode(part.content))
            assert json_part == _json_for_one_file(test_files[i])


def _asert_response_for_process_file_3(
    test_files, response, response_schema, response_type=TEXT_CSV, gz_content_type=None
):
    def _json_for_one_file(test_file):
        if test_file.endswith(".gz"):
            test_file = test_file[:-3]
        return {
            "silly_result": " : ".join(
                [
                    str(FILENAME_LENGTHS[test_file]),
                    str(response_type),
                    str(response_schema["output_schema"]),
                ]
            )
        }

    if response_type in [JSON, TEXT_CSV]:
        if len(test_files) == 1:
            assert response.json() == _json_for_one_file(test_files[0])
        else:
            assert response.json() == [_json_for_one_file(test_file) for test_file in test_files]
    elif response_schema == MIXED:
        data = decoder.MultipartDecoder.from_response(response)
        for i, part in enumerate(data.parts):
            json_part = json.loads(b64decode(part.content))
            assert json_part == _json_for_one_file(test_files[i])


def _assert_response_for_process_file_4(
    test_files, response, response_schema, response_type, m_input1, gz_content_type
):
    def _json_for_one_file(test_file):
        if test_file.endswith(".gz"):
            test_file = test_file[:-3]
        return {
            "silly_result": " : ".join(
                [
                    str(FILENAME_LENGTHS[test_file]),
                    str(gz_content_type or FILENAME_FORMATS[test_file]),
                    str(response_type),
                    str(response_schema["output_schema"]),
                    str(m_input1["input1"]),
                ]
            )
        }

    if response_type in [JSON, TEXT_CSV]:
        if len(test_files) == 1:
            assert response.json() == _json_for_one_file(test_files[0])
        else:
            assert response.json() == [_json_for_one_file(test_file) for test_file in test_files]
    elif response_schema == MIXED:
        data = decoder.MultipartDecoder.from_response(response)
        for i, part in enumerate(data.parts):
            json_part = json.loads(b64decode(part.content))
            assert json_part == _json_for_one_file(test_files[i])


def _assert_response_for_process_file_5(
    test_files, response, response_schema, response_type, m_input1, m_input2, gz_content_type
):
    def _json_for_one_file(test_file):
        if test_file.endswith(".gz"):
            test_file = test_file[:-3]
        return {
            "silly_result": " : ".join(
                [
                    str(FILENAME_LENGTHS[test_file]),
                    str(gz_content_type or FILENAME_FORMATS[test_file]),
                    str(response_type),
                    str(response_schema["output_schema"]),
                    str(m_input1["input1"]),
                    str(m_input2["input2"]),
                ]
            )
        }

    if response_type in [JSON, TEXT_CSV]:
        if len(test_files) == 1:
            assert response.json() == _json_for_one_file(test_files[0])
        else:
            assert response.json() == [_json_for_one_file(test_file) for test_file in test_files]
    elif response_schema == MIXED:
        data = decoder.MultipartDecoder.from_response(response)
        for i, part in enumerate(data.parts):
            json_part = json.loads(b64decode(part.content))
            assert json_part == _json_for_one_file(test_files[i])


@pytest.mark.parametrize(
    "test_files,test_params,test_type_header,expected_status,gz_content_type",
    [
        ([FILE_DOCX], P_INPUT_2_SINGLE, JSON, 200, None),
        ([FILE_DOCX], P_INPUT_2_MULTI, JSON, 200, None),
        ([FILE_DOCX], None, JSON, 200, None),
        ([FILE_DOCX], P_INPUT_1_SINGLE, JSON, 200, None),
        ([FILE_DOCX], P_INPUT_1_MULTI, JSON, 200, None),
        ([FILE_DOCX], P_INPUT_1_AND_2_MULTI, JSON, 200, None),
        ([FILE_IMAGE], P_INPUT_1_AND_2_MULTI, JSON, 200, None),
        ([FILE_DOCX, FILE_IMAGE], P_INPUT_1_AND_2_MULTI, JSON, 200, None),
        ([FILE_DOCX, FILE_IMAGE], P_INPUT_1_AND_2_MULTI, MIXED, 200, None),
        ([FILE_DOCX], P_INPUT_1_MULTI, MIXED, 200, None),
        # json returned though csv requested
        pytest.param(
            [FILE_IMAGE], P_INPUT_1_AND_2_MULTI, TEXT_CSV, 200, None, marks=pytest.mark.xfail
        ),
        ([FILE_MSG], None, JSON, 200, None),
        ([FILE_JSON], None, JSON, 200, None),
        ([GZIP_FILE_IMAGE], P_INPUT_1_EMPTY, JSON, 200, None),
        ([GZIP_FILE_DOCX], P_INPUT_1_EMPTY, JSON, 200, None),
        ([GZIP_FILE_DOCX, FILE_IMAGE], P_INPUT_1_EMPTY, TEXT_CSV, 406, None),
        ([], P_INPUT_1_EMPTY, JSON, 400, None),
        ([GZIP_FILE_DOCX], P_INPUT_1_EMPTY, JSON, 200, FILENAME_FORMATS[FILE_DOCX]),
        ([GZIP_FILE_DOCX], P_INPUT_1_EMPTY, JSON, 200, FILENAME_FORMATS[FILE_IMAGE]),
    ],
)
def test_process_file_1(
    test_files, test_params, test_type_header, expected_status, gz_content_type
):
    for endpoint in PROCESS_FILE_1_ROUTE:
        data = {}
        if test_params:
            data = test_params
        if gz_content_type:
            data["gz_uncompressed_content_type"] = gz_content_type

        response = client.post(
            endpoint,
            files=convert_files_for_api(test_files),
            data=data,
            **generate_header_kwargs(test_type_header),
        )
        assert response.status_code == expected_status
        if response.status_code == 200:
            if test_type_header == MIXED:
                assert response.headers["content-type"].startswith("multipart/mixed; boundary=")
            else:
                assert response.headers["content-type"] == test_type_header
            _assert_response_for_process_file_1(
                test_files, test_params, test_type_header, response, gz_content_type
            )


@pytest.mark.parametrize(
    "test_files,"
    "response_type,"
    "expected_status,"
    "allowed_mimetypes_str,"
    "use_octet_stream_type,"
    "gz_content_type",
    [
        ([FILE_DOCX], JSON, 200, FILENAME_FORMATS[FILE_DOCX], False, None),
        ([FILE_DOCX], JSON, 400, FILENAME_FORMATS[FILE_MARKDOWN], False, None),
        ([FILE_DOCX, FILE_IMAGE], JSON, 200, None, False, None),
        ([], JSON, 400, None, False, None),
        ([FILE_DOCX, FILE_IMAGE], MIXED, 200, None, False, None),
        ([GZIP_FILE_DOCX, FILE_IMAGE], MIXED, 200, None, False, None),
        ([FILE_DOCX, GZIP_FILE_IMAGE], MIXED, 200, None, False, None),
        ([GZIP_FILE_DOCX, GZIP_FILE_IMAGE], MIXED, 200, None, False, None),
        ([GZIP_FILE_DOCX, GZIP_FILE_IMAGE], TEXT_CSV, 406, None, False, None),
        ([FILE_MARKDOWN, GZIP_FILE_IMAGE], JSON, 200, None, False, None),
        ([FILE_MARKDOWN], JSON, 200, None, False, None),
        ([FILE_MARKDOWN], JSON, 200, None, True, None),
        ([FILE_MSG], JSON, 200, None, True, None),
        ([FILE_JSON], JSON, 200, None, True, None),
        ([GZIP_FILE_DOCX], JSON, 200, None, False, FILENAME_FORMATS[FILE_DOCX]),
        ([GZIP_FILE_DOCX], JSON, 200, None, False, FILENAME_FORMATS[FILE_IMAGE]),
    ],
)
def test_process_file_2(
    test_files,
    response_type,
    expected_status,
    allowed_mimetypes_str,
    use_octet_stream_type,
    gz_content_type,
    monkeypatch,
):
    if allowed_mimetypes_str:
        monkeypatch.setenv("UNSTRUCTURED_ALLOWED_MIMETYPES", allowed_mimetypes_str)
    else:
        monkeypatch.delenv("UNSTRUCTURED_ALLOWED_MIMETYPES", False)
    for endpoint in PROCESS_FILE_2_ROUTE:
        response = client.post(
            endpoint,
            files=convert_files_for_api(test_files, use_octet_stream_type),
            data={"output_format": response_type, "gz_uncompressed_content_type": gz_content_type},
            **generate_header_kwargs(response_type),
        )
        assert response.status_code == expected_status
        if response.status_code == 200:
            _assert_response_for_process_file_2(test_files, response, response_type)


@pytest.mark.parametrize(
    "test_files,"
    "response_type,"
    "response_schema,"
    "expected_status,"
    "use_octet_stream_type,"
    "allowed_mimetypes_str,"
    "gz_content_type",
    [
        ([FILE_DOCX], JSON, RESPONSE_SCHEMA_ISD, 200, False, None, None),
        ([FILE_DOCX], MIXED, RESPONSE_SCHEMA_ISD, 200, False, None, None),
        # endpoint fails because media type text/csv should have response type str
        pytest.param(
            [FILE_DOCX],
            TEXT_CSV,
            RESPONSE_SCHEMA_ISD,
            200,
            False,
            None,
            None,
            marks=pytest.mark.xfail,
        ),
        # endpoint fails because media type text/csv should have response type str
        # because None response type has default text/csv value
        pytest.param(
            [FILE_DOCX], None, RESPONSE_SCHEMA_ISD, 200, False, None, None, marks=pytest.mark.xfail
        ),
        ([FILE_DOCX], JSON, RESPONSE_SCHEMA_LABELSTUDIO, 200, False, None, None),
        pytest.param(
            [FILE_DOCX],
            MIXED,
            RESPONSE_SCHEMA_LABELSTUDIO,
            200,
            False,
            None,
            None,
        ),
        # endpoint fails because media type text/csv should have response type str
        pytest.param(
            [FILE_DOCX],
            TEXT_CSV,
            RESPONSE_SCHEMA_LABELSTUDIO,
            200,
            False,
            None,
            None,
            marks=pytest.mark.xfail,
        ),
        # endpoint fails because media type text/csv should have response type str
        # because None response type has default text/csv value
        pytest.param(
            [FILE_DOCX],
            None,
            RESPONSE_SCHEMA_LABELSTUDIO,
            200,
            False,
            None,
            None,
            marks=pytest.mark.xfail,
        ),
        ([FILE_DOCX, FILE_IMAGE], JSON, RESPONSE_SCHEMA_ISD, 200, False, None, None),
        ([FILE_MSG], JSON, RESPONSE_SCHEMA_ISD, 200, True, None, None),
        ([FILE_JSON], JSON, RESPONSE_SCHEMA_ISD, 200, False, None, None),
        ([FILE_DOCX, FILE_IMAGE], MIXED, RESPONSE_SCHEMA_ISD, 200, False, None, None),
        # endpoint fails because text/csv is not acceptable for multiple files
        pytest.param(
            [FILE_DOCX, FILE_IMAGE],
            TEXT_CSV,
            RESPONSE_SCHEMA_ISD,
            200,
            False,
            None,
            None,
            marks=pytest.mark.xfail,
        ),
        ([FILE_DOCX, FILE_IMAGE], None, RESPONSE_SCHEMA_ISD, 406, False, None, None),
        ([FILE_DOCX, FILE_IMAGE], JSON, RESPONSE_SCHEMA_LABELSTUDIO, 200, False, None, None),
        ([FILE_DOCX, FILE_IMAGE], MIXED, RESPONSE_SCHEMA_LABELSTUDIO, 200, False, None, None),
        # endpoint fails because text/csv is not acceptable for multiple files
        pytest.param(
            [FILE_DOCX, FILE_IMAGE],
            TEXT_CSV,
            RESPONSE_SCHEMA_LABELSTUDIO,
            200,
            False,
            None,
            None,
            marks=pytest.mark.xfail,
        ),
        ([FILE_DOCX, FILE_IMAGE], None, RESPONSE_SCHEMA_LABELSTUDIO, 406, False, None, None),
        (
            [FILE_DOCX, FILE_IMAGE, GZIP_FILE_IMAGE],
            None,
            RESPONSE_SCHEMA_LABELSTUDIO,
            406,
            False,
            None,
            None,
        ),
        (
            [FILE_DOCX, FILE_IMAGE, GZIP_FILE_DOCX],
            None,
            RESPONSE_SCHEMA_LABELSTUDIO,
            406,
            False,
            None,
            None,
        ),
        (
            [FILE_DOCX, FILE_IMAGE, GZIP_FILE_IMAGE, GZIP_FILE_DOCX],
            None,
            RESPONSE_SCHEMA_LABELSTUDIO,
            406,
            False,
            None,
            None,
        ),
        ([FILE_MARKDOWN], JSON, RESPONSE_SCHEMA_LABELSTUDIO, 200, True, None, None),
        (
            [FILE_MARKDOWN],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            200,
            False,
            FILENAME_FORMATS[FILE_MARKDOWN],
            None,
        ),
        (
            [FILE_MARKDOWN],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            400,
            False,
            FILENAME_FORMATS[FILE_DOCX],
            None,
        ),
        ([], JSON, RESPONSE_SCHEMA_LABELSTUDIO, 400, False, FILENAME_FORMATS[FILE_DOCX], None),
        (
            [GZIP_FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            200,
            False,
            None,
            FILENAME_FORMATS[FILE_DOCX],
        ),
        (
            [GZIP_FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            200,
            False,
            None,
            FILENAME_FORMATS[FILE_IMAGE],
        ),
    ],
)
def test_process_file_3(
    test_files,
    response_type,
    response_schema,
    expected_status,
    use_octet_stream_type,
    allowed_mimetypes_str,
    gz_content_type,
    monkeypatch,
):
    if allowed_mimetypes_str:
        monkeypatch.setenv("UNSTRUCTURED_ALLOWED_MIMETYPES", allowed_mimetypes_str)
    else:
        monkeypatch.delenv("UNSTRUCTURED_ALLOWED_MIMETYPES", False)
    for endpoint in PROCESS_FILE_3_ROUTE:
        response = client.post(
            endpoint,
            files=convert_files_for_api(test_files, use_octet_stream_type),
            data={
                **response_schema,
                "output_format": response_type,
                "gz_uncompressed_content_type": gz_content_type,
            },
            **generate_header_kwargs(response_type),
        )
        assert response.status_code == expected_status
        if response.status_code == 200:
            _asert_response_for_process_file_3(
                test_files, response, response_schema, response_type, gz_content_type
            )


@pytest.mark.parametrize(
    "test_files,"
    "response_type,"
    "response_schema,"
    "m_input1,"
    "expected_status,"
    "allowed_mimetypes_str,"
    "use_octet_stream_type,"
    "gz_content_type",
    [
        ([FILE_DOCX], JSON, RESPONSE_SCHEMA_ISD, P_INPUT_1_EMPTY, 200, None, False, None),
        ([FILE_DOCX], JSON, RESPONSE_SCHEMA_ISD, P_INPUT_1_MULTI, 200, None, False, None),
        ([FILE_DOCX], JSON, RESPONSE_SCHEMA_LABELSTUDIO, P_INPUT_1_SINGLE, 200, None, False, None),
        (
            [FILE_DOCX, FILE_IMAGE],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_EMPTY,
            200,
            None,
            False,
            None,
        ),
        (
            [FILE_DOCX, FILE_IMAGE],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_MULTI,
            200,
            None,
            False,
            None,
        ),
        (
            [FILE_DOCX, FILE_IMAGE],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_SINGLE,
            200,
            None,
            False,
            None,
        ),
        ([GZIP_FILE_DOCX], JSON, RESPONSE_SCHEMA_ISD, P_INPUT_1_EMPTY, 200, None, False, None),
        ([GZIP_FILE_DOCX], JSON, RESPONSE_SCHEMA_ISD, P_INPUT_1_MULTI, 200, None, False, None),
        (
            [GZIP_FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_SINGLE,
            200,
            None,
            False,
            None,
        ),
        (
            [GZIP_FILE_DOCX, FILE_IMAGE],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_EMPTY,
            200,
            None,
            False,
            None,
        ),
        (
            [FILE_DOCX, GZIP_FILE_IMAGE],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_MULTI,
            200,
            None,
            False,
            None,
        ),
        (
            [GZIP_FILE_DOCX, GZIP_FILE_IMAGE],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_SINGLE,
            200,
            None,
            False,
            None,
        ),
        pytest.param(
            [GZIP_FILE_DOCX, GZIP_FILE_IMAGE],
            TEXT_CSV,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_SINGLE,
            200,
            None,
            False,
            None,
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            [GZIP_FILE_DOCX],
            TEXT_CSV,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_SINGLE,
            200,
            None,
            False,
            None,
            marks=pytest.mark.xfail,
        ),
        (
            [FILE_MSG],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_SINGLE,
            200,
            FILENAME_FORMATS[FILE_MSG],
            True,
            None,
        ),
        (
            [FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_SINGLE,
            200,
            FILENAME_FORMATS[FILE_DOCX],
            False,
            None,
        ),
        (
            [FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_SINGLE,
            400,
            FILENAME_FORMATS[FILE_IMAGE],
            False,
            None,
        ),
        ([FILE_MARKDOWN], JSON, RESPONSE_SCHEMA_ISD, P_INPUT_1_SINGLE, 200, None, True, None),
        (
            [GZIP_FILE_DOCX, GZIP_FILE_IMAGE],
            MIXED,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_SINGLE,
            200,
            None,
            False,
            None,
        ),
        ([FILE_DOCX], MIXED, RESPONSE_SCHEMA_ISD, P_INPUT_1_SINGLE, 200, None, False, None),
        ([], MIXED, RESPONSE_SCHEMA_ISD, P_INPUT_1_SINGLE, 400, None, False, None),
        (
            [GZIP_FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_SINGLE,
            200,
            None,
            False,
            FILENAME_FORMATS[FILE_DOCX],
        ),
        (
            [GZIP_FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_SINGLE,
            200,
            None,
            False,
            FILENAME_FORMATS[FILE_IMAGE],
        ),
    ],
)
def test_process_file_4(
    test_files,
    response_type,
    response_schema,
    m_input1,
    expected_status,
    allowed_mimetypes_str,
    use_octet_stream_type,
    gz_content_type,
    monkeypatch,
):
    if allowed_mimetypes_str:
        monkeypatch.setenv("UNSTRUCTURED_ALLOWED_MIMETYPES", allowed_mimetypes_str)
    else:
        monkeypatch.delenv("UNSTRUCTURED_ALLOWED_MIMETYPES", False)
    for endpoint in PROCESS_FILE_4_ROUTE:
        response = client.post(
            endpoint,
            files=convert_files_for_api(test_files, use_octet_stream_type),
            data={
                **response_schema,
                **m_input1,
                "output_format": response_type,
                "gz_uncompressed_content_type": gz_content_type,
            },
            **generate_header_kwargs(response_type),
        )
        assert response.status_code == expected_status
        if response.status_code == 200:
            _assert_response_for_process_file_4(
                test_files, response, response_schema, response_type, m_input1, gz_content_type
            )


@pytest.mark.parametrize(
    "test_files,"
    "response_type,"
    "response_schema,"
    "m_input1,"
    "m_input2,"
    "expected_status,"
    "use_octet_stream_type,"
    "allowed_mimetypes_str,"
    "gz_content_type",
    [
        (
            [FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_MULTI,
            P_INPUT_2_MULTI,
            200,
            False,
            None,
            None,
        ),
        (
            [FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_EMPTY,
            P_INPUT_2_MULTI,
            200,
            False,
            None,
            None,
        ),
        (
            [FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_SINGLE,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            None,
        ),
        (
            [FILE_DOCX, FILE_IMAGE],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_SINGLE,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            None,
        ),
        (
            [FILE_DOCX, FILE_IMAGE],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_EMPTY,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            None,
        ),
        (
            [FILE_DOCX, FILE_IMAGE],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_MULTI,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            None,
        ),
        (
            [GZIP_FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_MULTI,
            P_INPUT_2_MULTI,
            200,
            False,
            None,
            None,
        ),
        (
            [GZIP_FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_EMPTY,
            P_INPUT_2_MULTI,
            200,
            False,
            None,
            None,
        ),
        (
            [GZIP_FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_SINGLE,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            None,
        ),
        (
            [GZIP_FILE_DOCX, FILE_IMAGE],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_SINGLE,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            None,
        ),
        (
            [FILE_DOCX, GZIP_FILE_IMAGE],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_EMPTY,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            None,
        ),
        (
            [GZIP_FILE_DOCX, GZIP_FILE_IMAGE],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_MULTI,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            None,
        ),
        pytest.param(
            [GZIP_FILE_IMAGE],
            TEXT_CSV,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_MULTI,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            None,
            marks=pytest.mark.xfail,
        ),
        (
            [FILE_MSG],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_MULTI,
            P_INPUT_2_EMPTY,
            200,
            True,
            None,
            None,
        ),
        (
            [FILE_MARKDOWN],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_MULTI,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            None,
        ),
        (
            [FILE_MARKDOWN],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_MULTI,
            P_INPUT_2_EMPTY,
            200,
            True,
            None,
            None,
        ),
        (
            [FILE_MARKDOWN],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_MULTI,
            P_INPUT_2_EMPTY,
            200,
            False,
            FILENAME_FORMATS[FILE_MARKDOWN],
            None,
        ),
        (
            [FILE_MARKDOWN],
            JSON,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_MULTI,
            P_INPUT_2_EMPTY,
            400,
            False,
            FILENAME_FORMATS[FILE_IMAGE],
            None,
        ),
        (
            [FILE_DOCX, GZIP_FILE_IMAGE],
            MIXED,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_EMPTY,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            None,
        ),
        (
            [FILE_DOCX, GZIP_FILE_IMAGE],
            TEXT_CSV,
            RESPONSE_SCHEMA_LABELSTUDIO,
            P_INPUT_1_EMPTY,
            P_INPUT_2_EMPTY,
            406,
            False,
            None,
            None,
        ),
        (
            [FILE_IMAGE],
            MIXED,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_MULTI,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            None,
        ),
        (
            [],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_MULTI,
            P_INPUT_2_EMPTY,
            400,
            False,
            None,
            None,
        ),
        (
            [GZIP_FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_MULTI,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            FILENAME_FORMATS[FILE_DOCX],
        ),
        (
            [GZIP_FILE_DOCX],
            JSON,
            RESPONSE_SCHEMA_ISD,
            P_INPUT_1_MULTI,
            P_INPUT_2_EMPTY,
            200,
            False,
            None,
            FILENAME_FORMATS[FILE_IMAGE],
        ),
    ],
)
def test_process_file_5(
    test_files,
    response_type,
    response_schema,
    m_input1,
    m_input2,
    expected_status,
    use_octet_stream_type,
    allowed_mimetypes_str,
    gz_content_type,
    monkeypatch,
):
    if allowed_mimetypes_str:
        monkeypatch.setenv("UNSTRUCTURED_ALLOWED_MIMETYPES", allowed_mimetypes_str)
    else:
        monkeypatch.delenv("UNSTRUCTURED_ALLOWED_MIMETYPES", False)
    for endpoint in PROCESS_FILE_5_ROUTE:
        response = client.post(
            endpoint,
            files=convert_files_for_api(test_files, use_octet_stream_type),
            data={
                **response_schema,
                **m_input1,
                **m_input2,
                "output_format": response_type,
                "gz_uncompressed_content_type": gz_content_type,
            },
            **generate_header_kwargs(response_type),
        )
        assert response.status_code == expected_status
        if response.status_code == 200:
            _assert_response_for_process_file_5(
                test_files,
                response,
                response_schema,
                response_type,
                m_input1,
                m_input2,
                gz_content_type,
            )


def test_supported_mimetypes():
    """
    Verify that we return 400 if a filetype is not supported
    (configured via UNSTRUCTURED_ALLOWED_MIMETYPES)
    """
    client = TestClient(app)

    # get_validated_mimetype is inserted at 4 different points
    # Let's disallow docx and make sure we get the right error in each case
    os.environ["UNSTRUCTURED_ALLOWED_MIMETYPES"] = "image/jpeg"

    docx_content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    docx_unsupported_error_message = (
        f"Unable to process {FILE_DOCX}: " f"File type {docx_content_type} is not supported."
    )

    for process_file_endpoint in PROCESS_FILE_1_ROUTE:
        # Sending one file
        response = client.post(
            process_file_endpoint,
            files=convert_files_for_api([FILE_DOCX]),
        )
        assert (
            response.status_code == 400
            and response.json()["detail"] == docx_unsupported_error_message
        )

        # Sending multiple files
        response = client.post(
            process_file_endpoint,
            files=convert_files_for_api([FILE_DOCX, FILE_IMAGE]),
        )
        assert (
            response.status_code == 400
            and response.json()["detail"] == docx_unsupported_error_message
        )

        # for process_file_text_endpoint in PROCESS_FILE_TEXT_1_ROUTE:

        for process_file_text_endpoint in PROCESS_FILE_TEXT_1_ROUTE:
            # Sending one file (in an api that supports text files)
            response = client.post(
                process_file_text_endpoint,
                files=convert_files_for_api([FILE_DOCX]),
            )
            assert (
                response.status_code == 400
                and response.json()["detail"] == docx_unsupported_error_message
            )

            # Multiple files (in an api that supports text files)
            response = client.post(
                process_file_text_endpoint,
                files=convert_files_for_api([FILE_DOCX, FILE_IMAGE]),
            )
            assert (
                response.status_code == 400
                and response.json()["detail"] == docx_unsupported_error_message
            )

    # If the client doesn't set a mimetype, we may just see application/octet-stream
    # Here we get the mimetype from the file extension
    response = client.post(
        process_file_endpoint,
        files=[("files", (FILE_DOCX, open(FILE_DOCX, "rb"), "application/octet-stream"))],
    )
    assert (
        response.status_code == 400 and response.json()["detail"] == docx_unsupported_error_message
    )

    # Finally, allow all file types again
    # Note that a failure before this line will cause cascading test errors
    del os.environ["UNSTRUCTURED_ALLOWED_MIMETYPES"]

    response = client.post(
        process_file_endpoint,
        files=convert_files_for_api([FILE_DOCX]),
    )
    assert response.status_code == 200

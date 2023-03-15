#####################################################################
# THIS FILE IS AUTOMATICALLY GENERATED BY UNSTRUCTURED API TOOLS.
# DO NOT MODIFY DIRECTLY
#####################################################################

import os
from typing import List, Union
from fastapi import status, FastAPI, File, Form, Request, UploadFile, APIRouter
from fastapi.responses import PlainTextResponse
import json
from fastapi.responses import StreamingResponse
from starlette.types import Send
from base64 import b64encode
from typing import Optional, Mapping, Iterator, Tuple
import secrets


app = FastAPI()
router = APIRouter()


def is_expected_response_type(media_type, response_type):
    if media_type == "application/json" and response_type not in [dict, list]:
        return True
    elif media_type == "text/csv" and response_type != str:
        return True
    else:
        return False


# pipeline-api
def pipeline_api(
    file,
    file_content_type=None,
    response_type="application/json",
    response_schema="labelstudio",
    m_input1=[],
    m_input2=[],
):
    return {
        "silly_result": " : ".join(
            [
                str(len(file.read())),
                str(file_content_type),
                str(response_type),
                str(response_schema),
                str(m_input1),
                str(m_input2),
            ]
        )
    }


class MultipartMixedResponse(StreamingResponse):
    CRLF = b"\r\n"

    def __init__(self, *args, content_type: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_type = content_type

    def init_headers(self, headers: Optional[Mapping[str, str]] = None) -> None:
        super().init_headers(headers)
        self.boundary_value = secrets.token_hex(16)
        content_type = f'multipart/mixed; boundary="{self.boundary_value}"'
        self.raw_headers.append((b"content-type", content_type.encode("latin-1")))

    @property
    def boundary(self):
        return b"--" + self.boundary_value.encode()

    def _build_part_headers(self, headers: dict) -> bytes:
        header_bytes = b""
        for header, value in headers.items():
            header_bytes += f"{header}: {value}".encode() + self.CRLF
        return header_bytes

    def build_part(self, chunk: bytes) -> bytes:
        part = self.boundary + self.CRLF
        part_headers = {
            "Content-Length": len(chunk),
            "Content-Transfer-Encoding": "base64",
        }
        if self.content_type is not None:
            part_headers["Content-Type"] = self.content_type
        part += self._build_part_headers(part_headers)
        part += self.CRLF + chunk + self.CRLF
        return part

    async def stream_response(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        async for chunk in self.body_iterator:
            if not isinstance(chunk, bytes):
                chunk = chunk.encode(self.charset)
                chunk = b64encode(chunk)
            await send(
                {
                    "type": "http.response.body",
                    "body": self.build_part(chunk),
                    "more_body": True,
                }
            )

        await send({"type": "http.response.body", "body": b"", "more_body": False})


@router.post("/test-project/v1.2.3/process-file-5")
async def pipeline_1(
    request: Request,
    files: Union[List[UploadFile], None] = File(default=None),
    output_format: Union[str, None] = Form(default=None),
    output_schema: str = Form(default=None),
    input1: List[str] = Form(default=[]),
    input2: List[str] = Form(default=[]),
):
    content_type = request.headers.get("Accept")

    default_response_type = output_format or "application/json"
    if not content_type or content_type == "*/*" or content_type == "multipart/mixed":
        media_type = default_response_type
    else:
        media_type = content_type

    default_response_schema = output_schema or "labelstudio"

    if isinstance(files, list) and len(files):
        if len(files) > 1:
            if content_type and content_type not in [
                "*/*",
                "multipart/mixed",
                "application/json",
            ]:
                return PlainTextResponse(
                    content=(
                        f"Conflict in media type {content_type}"
                        ' with response type "multipart/mixed".\n'
                    ),
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                )

            def response_generator(is_multipart):
                for file in files:
                    _file = file.file

                    response = pipeline_api(
                        _file,
                        m_input1=input1,
                        m_input2=input2,
                        response_type=media_type,
                        response_schema=default_response_schema,
                        file_content_type=file.content_type,
                    )
                    if is_multipart:
                        if type(response) not in [str, bytes]:
                            response = json.dumps(response)
                    yield response

            if content_type == "multipart/mixed":
                return MultipartMixedResponse(
                    response_generator(is_multipart=True), content_type=media_type
                )
            else:
                return response_generator(is_multipart=False)
        else:
            file = files[0]
            _file = file.file

            response = pipeline_api(
                _file,
                m_input1=input1,
                m_input2=input2,
                response_type=media_type,
                response_schema=default_response_schema,
                file_content_type=file.content_type,
            )

            if is_expected_response_type(media_type, type(response)):
                return PlainTextResponse(
                    content=(
                        f"Conflict in media type {media_type}"
                        f" with response type {type(response)}.\n"
                    ),
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                )
            valid_response_types = ["application/json", "text/csv", "*/*"]
            if media_type in valid_response_types:
                return response
            else:
                return PlainTextResponse(
                    content=f"Unsupported media type {media_type}.\n",
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                )

    else:
        return PlainTextResponse(
            content='Request parameter "files" is required.\n',
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@app.get("/healthcheck", status_code=status.HTTP_200_OK)
async def healthcheck(request: Request):
    return {"healthcheck": "HEALTHCHECK STATUS: EVERYTHING OK!"}


app.include_router(router)

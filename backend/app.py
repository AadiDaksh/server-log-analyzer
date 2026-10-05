from pathlib import Path

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)

from fastapi.responses import (
    FileResponse,
)

from fastapi.staticfiles import (
    StaticFiles,
)

from backend.analyzer import (
    build_dashboard_data,
)

from backend.parsers.detector import (
    parse_log_content,
)

from backend.live_monitor import (
    watch_log_file,
)

from backend.parsers.detector import (
    parse_log_content,
    parse_log_line,
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

FRONTEND_DIR = (
    BASE_DIR / "frontend"
)


app = FastAPI(
    title="Server Log Dashboard",
    description=(
        "Multi-format HTTP server "
        "log analysis dashboard."
    ),
    version="2.0.0",
)


app.mount(
    "/static",
    StaticFiles(
        directory=FRONTEND_DIR
    ),
    name="static",
)


@app.get("/")
def home():
    return FileResponse(
        FRONTEND_DIR
        / "index.html"
    )


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "version": "2.0.0",
    }


@app.get("/api/formats")
def formats():
    return {
        "supported_formats": [
            "JSON application logs",
            "Nginx access logs",
            "Apache access logs",
            "Custom application logs",
        ]
    }


@app.post("/api/analyze")
async def analyze_log(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided."
        )

    content = await file.read()

    max_size = (
        10 * 1024 * 1024
    )

    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=(
                "File is larger than "
                "the 10 MB limit."
            )
        )

    try:
        text = content.decode(
            "utf-8"
        )

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail=(
                "File must contain "
                "UTF-8 text."
            )
        )

    parsed = parse_log_content(
        text
    )

    requests = parsed[
        "requests"
    ]

    if not requests:
        raise HTTPException(
            status_code=400,
            detail=(
                "No supported log entries "
                "could be detected."
            )
        )

    dashboard = (
        build_dashboard_data(
            requests
        )
    )

    return {
        "filename":
            file.filename,

        "parsed_requests":
            len(requests),

        "total_lines":
            parsed["total_lines"],

        "ignored_lines":
            parsed["ignored_lines"],

        "formats":
            parsed["formats"],

        "dashboard":
            dashboard,
    }

@app.websocket("/ws/live")
async def live_monitor(
    websocket: WebSocket
):
    await websocket.accept()

    live_log = (
        BASE_DIR
        / "logs"
        / "live.log"
    )

    requests = []

    try:
        async for line in watch_log_file(
            live_log
        ):
            request = parse_log_line(
                line
            )

            if request is None:
                continue

            requests.append(
                request
            )

            dashboard = (
                build_dashboard_data(
                    requests
                )
            )

            await websocket.send_json(
                {
                    "type":
                        "dashboard_update",

                    "parsed_requests":
                        len(requests),

                    "format":
                        request["format"],

                    "latest_request": {
                        "method":
                            request[
                                "method"
                            ],

                        "endpoint":
                            request[
                                "endpoint"
                            ],

                        "status":
                            request[
                                "status"
                            ],

                        "response_time":
                            request[
                                "response_time"
                            ],
                    },

                    "dashboard":
                        dashboard,
                }
            )

    except WebSocketDisconnect:
        pass
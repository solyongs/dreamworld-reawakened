import re
import atexit
import mimetypes
from pathlib import Path
from urllib.parse import parse_qs
from flask import Flask, request, redirect, Response

from utils import language
from utils.patch_swf import get_cached, SWF_PATHS
from game_sync_server.entralinked.utility.db_manager import db
from api.routes import GET_RESPONSES, POST_RESPONSES

# ---------------
# Config
# ---------------

atexit.register(db.close)

PATCHED_SWFS = set(SWF_PATHS.keys())
LANG = language.player_language

ROOT_DIR   = Path(__file__).resolve().parent.parent
SITE_DIR   = ROOT_DIR / "dreamworld_assets" / f"{LANG}.pokemon-gl.com"
SHARED_DIR = ROOT_DIR / "dreamworld_assets" / "shared.pokemon-gl.com"

# file extensions that should be patched before serving
# binary assets (images, fonts, etc.) are served as-is
PATCHABLE_EXTENSIONS = {".js", ".html", ".css"}

# incoming paths that need to be redirected to an equivalent local path
# rules are mutually exclusive, only the first match is applied
PATH_REWRITES = [
    (re.compile(rf"^/gus\.pokemon\.com/{LANG}/"), f"/pgl-363/{LANG}/"),
    (re.compile(r"^/cdn2\.pokemon-gl\.com"),       ""),
    (re.compile(rf"^/{LANG}\.pokemon-gl\.com"),    ""),
    (re.compile(r"^/www\.pokemon-gl\.com"),        ""),
]

NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}

# ---------------
# App
# ---------------

app = Flask(__name__)

# ---------------
# Helpers
# ---------------

def rewrite_path(path: str) -> str:
    """Apply the first matching rewrite rule and return the result."""
    for pattern, replacement in PATH_REWRITES:
        rewritten = pattern.sub(replacement, path, count=1)
        if rewritten != path:
            return rewritten
    return path


def apply_replacements(data: bytes, filename: str) -> bytes:
    """Patch text assets: fix language detection, remove interaction blockers."""
    subs = [
        (
            b"(location.href.match(/\\W(ja|en|fr|it|de|es|ko)\\./) || [null, 'ja'])[1];",
            f"'{LANG}';".encode(),
        ),
        (b'http://cdn2.pokemon-gl.com',   b''),
        (b'/cdn2.pokemon-gl.com',         b''),
        (b'oncontextmenu="return false"', b""),
        (b'ondragstart="return false"',   b""),
        (b'onselectstart="return false"', b""),
        (b"en.pokemon-gl.com", f"{LANG}.pokemon-gl.com".encode())
    ]

    if filename == "swfembed2.js":
        # point the SWF embed at the local language host instead of window.location.
        lang_url = f"lang:'http://{LANG}.pokemon-gl.com/'"
        subs.append( (b"lang:window.location", lang_url.encode()) )

    for old, new in subs:
        data = data.replace(old, new)

    return data


def read_and_patch(file_path: Path) -> bytes:
    data = file_path.read_bytes()
    if file_path.suffix.lower() in PATCHABLE_EXTENSIONS:
        data = apply_replacements(data, file_path.name)
    return data


def send_file(file_path: Path) -> Response:
    data = read_and_patch(file_path)
    content_type, _ = mimetypes.guess_type(file_path)
    return Response(data, content_type=content_type or "application/octet-stream")

def send_bytes(data: bytes, content_type: str) -> Response:
    """Serve raw bytes for patched SWF assets."""
    return Response(data, content_type=content_type)

def resolve_static(path: str) -> Path | None:
    """Return the filesystem path for a static asset, checking site dir, then shared dir as a fallback."""
    relative = path.lstrip("/")

    # site-specific first
    site_path = SITE_DIR / relative
    if site_path.is_file():
        return site_path

    # shared fallback, strip language prefix (e.g. /en/ → /).
    shared_relative = re.sub(r"/(ja|en|fr|it|de|es|ko)/", "/", relative)
    shared_path = SHARED_DIR / shared_relative
    if shared_path.is_file():
        return shared_path

    return None


def not_found(path: str) -> Response:
    app.logger.info("404 %s", path)
    return Response("Error: Not found", status=404, content_type="text/html")

# ---------------
# Routes
# ---------------

@app.before_request
def rewrite_incoming_path():
    """Apply path rewrites and enforce trailing slash on directory paths."""
    path = request.path
    rewritten = rewrite_path(path)

    if rewritten != path:
        qs = f"?{request.query_string.decode()}" if request.query_string else ""
        return redirect(rewritten + qs, 302)

    # enforce trailing slash for paths that map to a site directory
    if not path.endswith("/") and (SITE_DIR / path.lstrip("/")).is_dir():
        return redirect(f"{path}/", 301)


@app.route("/api/", methods=["GET"])
def api_get():
    query    = {k: v[0] for k, v in parse_qs(request.query_string.decode(), strict_parsing=True).items()}
    api_name = query.get("p")
    app.logger.info("API GET: %s", api_name)

    if api_name not in GET_RESPONSES:
        app.logger.warning("Unknown API: %s", api_name)
        return Response("{}", status=501, content_type="application/json")

    return Response(GET_RESPONSES[api_name](query), content_type="application/json", headers=NO_CACHE_HEADERS)


@app.route("/api/", methods=["POST"])
def api_post():
    qs_params   = {k: v[0] for k, v in parse_qs(request.query_string.decode(), strict_parsing=True).items()}
    body_params = {k: v[0] for k, v in parse_qs(request.get_data(as_text=True), strict_parsing=True).items()}
    query       = {**qs_params, **body_params}
    api_name    = query.get("p")
    app.logger.info("API POST: %s", api_name)

    if api_name not in POST_RESPONSES:
        app.logger.warning("Unknown API: %s", api_name)
        return Response("{}", status=501, content_type="application/json")

    return Response(POST_RESPONSES[api_name](query), content_type="application/json", headers=NO_CACHE_HEADERS)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path: str):
    full_path = f"/{path}"
    filename  = Path(path).name

    # return patched SWFs from our cache
    if filename in PATCHED_SWFS:
        return send_bytes(get_cached(filename), "application/x-shockwave-flash")

    # find first HTML file inside given directory
    dir_path = SITE_DIR / path
    if dir_path.is_dir():
        index = next(iter(sorted(dir_path.glob("*.html"))), None)
        if index is None:
            return not_found(full_path)
        return send_file(index)

    # static asset
    file_path = resolve_static(full_path)
    if file_path is None:
        return not_found(full_path)

    return send_file(file_path)

# ---------------
# Entry point
# ---------------

def run(port: int = 8080, debug: bool = False):
    app.logger.info("Server started!%s\n", " (debug mode)" if debug else "")
    app.run(host="127.0.0.1", port=port, debug=debug, use_reloader=False)
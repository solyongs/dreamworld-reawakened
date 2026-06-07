import shutil
import subprocess
from pathlib import Path
from textwrap import dedent
from zipfile import ZipFile
from dataclasses import dataclass
from urllib.request import urlretrieve

from utils import language

LANG = language.player_language

# ---------------
# Dataclasses
# ---------------

@dataclass
class Substitution:
    """A simple find-and-replace patch for text assets"""
    old: bytes
    new: bytes

@dataclass
class Insertion:
    """A line-range replacement patch for ActionScript inside a SWF"""
    class_path: str
    line_number: tuple[int, int]
    replacement: str

# ---------------
# Paths
# ---------------

ROOT_DIR    = Path(__file__).resolve().parent.parent
PATCHES_DIR = ROOT_DIR / "patches"

FFDEC_JAR = str(PATCHES_DIR / "ffdec.jar")
JAVA      = "java"

# ---------------
# JS / text patches
# ---------------

JS_PATCHES: dict[str, tuple[Substitution]] = {
    "pgl.js": (
        Substitution(
            b"(location.href.match(/\\W(ja|en|fr|it|de|es|ko)\\./) || [null, 'ja'])[1];",
            f"'{LANG}';".encode(),
        ),
        Substitution(b"http://cdn2.pokemon-gl.com", b""),
        Substitution(b"/cdn2.pokemon-gl.com",       b""),
        Substitution(b"en.pokemon-gl.com", f"{LANG}.pokemon-gl.com".encode()),
    ),
    "swfembed2.js": (
        # point the SWF embed at the local language host instead of window.location
        Substitution(
            b"lang:window.location",
            f"lang:'http://{LANG}.pokemon-gl.com/'".encode(),
        ),
    ),
    "top.js": (
        # use Intl.DateTimeFormat so the time respects DST
        Substitution(
            b"d.setTime(d.getTime() + area.tz.offset * 60 * 60 * 1000);\r\n"
            b"        $('#report-records .area .tzname').text(area.tz.name);\r\n"
            b"        $('#report-records .area .time').text(PGL.Utils.zerofill(d.getUTCHours(), 2) + ':' + PGL.Utils.zerofill(d.getUTCMinutes(), 2));",

            b"var _tz_adj = new Intl.DateTimeFormat('en-GB', { timeZone: area.tz.name, hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());\r\n"
            b"        $('#report-records .area .tzname').text(area.tz.name);\r\n"
            b"        $('#report-records .area .time').text(_tz_adj.find(function(p){return p.type==='hour';}).value + ':' + _tz_adj.find(function(p){return p.type==='minute';}).value);",
        ),
    ),
}

# substitutions applied to every patchable file
_GLOBAL_SUBS: tuple[Substitution] = (
    Substitution(b'oncontextmenu="return false"', b""),
    Substitution(b'ondragstart="return false"',   b""),
    Substitution(b'onselectstart="return false"', b""),
)

def apply_substitutions(data: bytes, filename: str) -> bytes:
    """Apply global substitutions, then file-specific ones."""
    for sub in _GLOBAL_SUBS:
        data = data.replace(sub.old, sub.new)
    for sub in JS_PATCHES.get(filename, ()):
        data = data.replace(sub.old, sub.new)
    return data

# ---------------
# SWF patch content
# ---------------

# this patch is only needed to support the Standalone
# Flash Player, as it cannot execute JavaScript
_SoundController_patch = dedent("""\
    try
    {
        ExternalInterface.addCallback("sendVolume", this.receivedFromJavaScript);
    }
    catch(e:Error)
    {
    }
""")

_PokemonBridge_patch = dedent("""\
    PDW_API = "http://127.0.0.1:8080/api/";
    PDW_API_SSL = "http://127.0.0.1:8080/api/";

    Logger.log("PATH : " + PokemonBridge.PATH);
    Logger.log("API : " + PDW_API);
""")

# this patch is only used for debugging and makes empty
# strings display their string ID instead of nothing
_textFieldManager_patch = "_loc2_ = param1;"

# this patch sets the player's tutorial completion to
# full, as we don't have the tutorial assets yet
_Home_patch = dedent("""\
    var data:Object = PDWSharedObject.load();
    if(!data["member" + PokemonBridge.member_id]["tutorial0"])
    {
        i = 0;
        while(i <= 11)
        {
            data["member" + PokemonBridge.member_id]["tutorial" + i] = true;
            trace(data["member" + PokemonBridge.member_id]["tutorial" + i]);
            i++;
        }
        PDWSharedObject.save(data);
    }
""")

# ---------------
# SWF paths / insertions
# ---------------

SWF_PATHS = {
    "main.swf":     ROOT_DIR / "dreamworld_assets" / "shared.pokemon-gl.com" / "src" / "swf" / "theme" / "assets" / "common" / "main.swf",
    "pdw_home.swf": ROOT_DIR / "dreamworld_assets" / "shared.pokemon-gl.com" / "src" / "swf" / "pdw" / "assets" / "pdw_home.swf",
}

INSERTIONS = {
    "main.swf": (
        Insertion("bfp.main.SoundController",    (21,  22),  _SoundController_patch),
        Insertion("bfp.common.PokemonBridge",    (460, 462), _PokemonBridge_patch),
        Insertion("bfp.common.textFieldManager", (349, 350), _textFieldManager_patch),
    ),
    "pdw_home.swf": (
        Insertion("bfp.tpc.pdw.home.Home", (628, 629), _Home_patch),
    ),
}

# ---------------
# SWF patching
# ---------------

_PATCHED_CACHE: dict[str, bytes] = {}

def _patched_path(swf_name: str) -> Path:
    return PATCHES_DIR / f"{swf_name[:-4]}.patched.swf"

def _prewarm():
    PATCHES_DIR.mkdir(exist_ok=True)

    all_cached = all(_patched_path(swf_name).exists() for swf_name in SWF_PATHS)
    if all_cached:
        print("Loading patched SWFs from disk")
        for swf_name in SWF_PATHS:
            _PATCHED_CACHE[swf_name] = _patched_path(swf_name).read_bytes()
        return

    download_ffdec()

    for swf_name in SWF_PATHS:
        print(f"Patching {swf_name}")
        get_cached(swf_name)

    # remove all non-.swf files and directories left behind by ffdec
    for item in PATCHES_DIR.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        elif item.suffix != ".swf":
            item.unlink()

def download_ffdec():
    print("Need to download ffdec for swf patching")
    urlretrieve(
        "https://github.com/jindrapetrik/jpexs-decompiler/releases/download/version26.2.1/ffdec_26.2.1.zip",
        PATCHES_DIR / "ffdec.zip",
    )
    with ZipFile(PATCHES_DIR / "ffdec.zip") as z:
        z.extractall(PATCHES_DIR)

def get_cached(swf_name: str) -> bytes:
    if swf_name not in _PATCHED_CACHE:
        _PATCHED_CACHE[swf_name] = _get_patched_bytes(swf_name)
    return _PATCHED_CACHE[swf_name]

def _to_path(class_path: str) -> Path:
    *module_parts, class_name = class_path.split(".")
    return PATCHES_DIR / "scripts" / Path(*module_parts) / f"{class_name}.as"

def _get_patched_bytes(swf_name: str) -> bytes:
    src_path = SWF_PATHS[swf_name]
    out_path = _patched_path(swf_name)

    shutil.copy(src_path, out_path)

    # export only the scripts which have a patch
    export_list = ",".join(i.class_path for i in INSERTIONS[swf_name])
    subprocess.run(
        [JAVA, "-jar", FFDEC_JAR, "-selectclass", export_list, "-export", "script", PATCHES_DIR, out_path],
        stdout=subprocess.DEVNULL,
    )

    # apply patches to exported .as files
    for insertion in INSERTIONS[swf_name]:
        file_path = _to_path(insertion.class_path)
        start, end = insertion.line_number

        lines = file_path.read_text(encoding="UTF-8").splitlines(keepends=True)
        padding = len(lines[start]) - len(lines[start].lstrip(" "))
        lines[start:end] = "\n".join(" " * padding + line for line in insertion.replacement.splitlines()) + "\n"
        file_path.write_text("".join(lines))

    # reimport .as files into .swf
    subprocess.run(
        [JAVA, "-jar", FFDEC_JAR, "-importScript", out_path, out_path, PATCHES_DIR / "scripts"],
        stdout=subprocess.DEVNULL,
    )

    out_bytes = out_path.read_bytes()
    shutil.rmtree(PATCHES_DIR / "scripts")
    return out_bytes

_prewarm()
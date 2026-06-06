import os
import shutil
import subprocess
from pathlib import Path
from textwrap import dedent
from zipfile import ZipFile
from dataclasses import dataclass
from urllib.request import urlretrieve

@dataclass
class Insertion:
    class_path: str
    line_number: tuple[int, int]
    replacement: str

ROOT_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT_DIR / "tools"

FFDEC_JAR = str(Path(TOOLS_DIR / "ffdec-cli.jar"))
JAVA = "java"

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

SWF_PATHS = {
    "main.swf": ROOT_DIR / "dreamworld_assets" / "shared.pokemon-gl.com" / "src" / "swf" / "theme" / "assets" / "common" / "main.swf",
    "pdw_home.swf": ROOT_DIR / "dreamworld_assets" / "shared.pokemon-gl.com" / "src" / "swf" / "pdw" / "assets" / "pdw_home.swf"
}

INSERTIONS = {
    "main.swf": (
        Insertion(
            "bfp.main.SoundController",
            (21, 22),
            _SoundController_patch
        ),
        Insertion(
            "bfp.common.PokemonBridge",
            (460, 462),
            _PokemonBridge_patch
        ),
        Insertion(
            "bfp.common.textFieldManager",
            (349, 350),
            _textFieldManager_patch
        ),
    ),
    "pdw_home.swf": (
        Insertion(
            "bfp.tpc.pdw.home.Home",
            (628, 629),
            _Home_patch
        ),
    )
}

_PATCHED_CACHE: dict[str, bytes] = {}

def _prewarm():
    for swf_name in SWF_PATHS:
        print(f"Patching {swf_name}")
        get_cached(swf_name)

def get_cached(swf_name: str) -> bytes:
    if swf_name not in _PATCHED_CACHE:
        _PATCHED_CACHE[swf_name] = get_patched_bytes(swf_name)
    return _PATCHED_CACHE[swf_name]

def to_path(class_path: str) -> Path:
    *module_parts, class_name = class_path.split(".")
    return TOOLS_DIR / "scripts" / Path(*module_parts) / f"{class_name}.as"

def get_patched_bytes(swf_name: str):
    src_path = SWF_PATHS[swf_name]
    out_path = TOOLS_DIR / f"{swf_name[:-4]}.patched.swf"

    # copy target .swf to working directory
    shutil.copy(src_path, out_path)

    # export only the scripts which have a patch
    export_list = ",".join([i.class_path for i in INSERTIONS[swf_name]])
    command = [JAVA, "-jar", FFDEC_JAR, "-selectclass", export_list, "-export", "script", TOOLS_DIR, out_path]
    subprocess.run(command, stdout=subprocess.DEVNULL)

    # apply patches to exported .as files
    for insertion in INSERTIONS[swf_name]:
        file_path = to_path(insertion.class_path)
        start, end = insertion.line_number

        lines = file_path.read_text(encoding="UTF-8").splitlines(keepends=True)

        padding = len(lines[start]) - len(lines[start].lstrip(" "))

        lines[start:end] = "\n".join(" "*padding + line for line in insertion.replacement.splitlines()) + "\n"

        file_path.write_text("".join(lines))

    # reimport .as files into .swf
    command = [JAVA, "-jar", FFDEC_JAR, "-importScript", out_path, out_path, TOOLS_DIR / "scripts"]
    subprocess.run(command, stdout=subprocess.DEVNULL)

    out_bytes = out_path.read_bytes()

    os.remove(out_path)
    shutil.rmtree(TOOLS_DIR / "scripts")

    return out_bytes

if not TOOLS_DIR.exists():
    TOOLS_DIR.mkdir(exist_ok=True)
    print("First run - need to download ffdec for swf patching")
    urlretrieve("https://github.com/jindrapetrik/jpexs-decompiler/releases/download/version26.2.1/ffdec_26.2.1.zip", ROOT_DIR / "tools" / "ffdec.zip")

    with ZipFile(TOOLS_DIR/ "ffdec.zip") as z:
        z.extractall(TOOLS_DIR)

    os.remove(TOOLS_DIR / "ffdec.zip")

_prewarm()
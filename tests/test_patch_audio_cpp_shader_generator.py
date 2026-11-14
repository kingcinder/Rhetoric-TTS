"""The vendored patches, exercised against a synthetic tree.

`scripts/patch_audio_cpp_ggml.sh` edits the cloned audio.cpp tree in place. The
shader-generator patch it now carries is what keeps the Vulkan build from going
red on an upstream race: the generator forks glslc processes, and a fork that
fails with EAGAIN used to drop that shader silently, leaving an undefined
`matmul_id_subgroup_*` symbol for the linker to find minutes later. These tests
run the real script against a fixture tree so the anchors, the markers and the
fail-loud behaviour stay pinned without cloning audio.cpp.

The committed `scripts/patches/*.patch` artifacts are the reviewable copy of
exactly those edits, and they drift silently when the script's text changes
without a regeneration (that happened once already, from a stale local tree).
The last tests here compare each artifact's added/removed lines with what the
script produces on the fixture, so a changed edit cannot land with a stale
artifact.
"""

from __future__ import annotations

import difflib
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "patch_audio_cpp_ggml.sh"

# The patch script is bash, and the audio.cpp build it feeds is Linux-only:
# Windows runners resolve `bash` to the WSL shim, which has no distribution.
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="bash script; WSL has no distributions on CI",
)

GGML_MINIMAL = """\
#include <vulkan/vulkan.hpp>
#include <spirv/unified1/spirv.hpp>

void ggml_vk_buffer_memset_stub(uint8_t * dst, int offset, int c, size_t size) {
    if (dst->device->architecture == vk_device_architecture::AMD_RDNA1_DISABLED) {
        memset((uint8_t*)dst->ptr + offset, c, size);
        return;
    }

    std::lock_guard<std::recursive_mutex> guard(dst->device->mutex);
    vk_context subctx = ggml_vk_create_temporary_context(dst->device->transfer_queue.cmd_pool);
}
"""

SENTENCEPIECE_CMAKE = """\
add_library(sentencepiece-static STATIC ${SPM_SRCS})
  string(APPEND CMAKE_CXX_FLAGS " -fmacro-prefix-map=${CMAKE_SOURCE_DIR}/=''")
"""

GENERATOR_MINIMAL = """\
#include <iostream>
#include <thread>
#include <mutex>
#include <future>

std::mutex lock;

void execute_command(std::vector<std::string>& command, std::string& stdout_str, std::string& stderr_str) {
    pid_t pid = fork();
    if (pid < 0) {
        std::cerr << strerror(errno) << "\\n";
        throw std::runtime_error("Failed to fork process");
    }
}

static bool generate_dep_file = true;

void string_to_spv_func(std::string name, std::string in_path, std::string out_path) {
    std::string stdout_str, stderr_str;
    std::vector<std::string> cmd;
    try {
        execute_command(cmd, stdout_str, stderr_str);
        if (!stderr_str.empty()) {
            std::cerr << "cannot compile " << name << "\\n\\n";
            for (const auto& part : cmd) {
                std::cerr << part << " ";
            }
            std::cerr << "\\n\\n" << stderr_str << std::endl;
            return;
        }
        std::lock_guard<std::mutex> guard(lock);
        shader_fnames.push_back(std::make_pair(name, out_path));
    } catch (const std::exception& e) {
        std::cerr << "Error executing command for " << name << ": " << e.what() << std::endl;
    }
}

void write_output_files() {
    for (const auto& pair : shader_fnames) {
        const std::string& name = pair.first;
        {
            std::string data = read_binary_file(path);
            if (data.empty()) {
                continue;
            }
            src << name;
        }
    }

    if (input_filepath == "") {
        write_file_if_changed(target_hpp, hdr.str());
    }
    if (target_cpp != "") {
        write_binary_file(target_cpp, src.str());
    }
}

int main(int argc, char** argv) {
    write_output_files();
    return 0;
}
"""


def _tree(tmp_path: Path) -> Path:
    """A synthetic audio.cpp tree the real patch script can be pointed at."""
    root = tmp_path / "repo"
    (root / "scripts").mkdir(parents=True)
    (root / "scripts" / "patch_audio_cpp_ggml.sh").write_text(
        SCRIPT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    gpu = root / "audio.cpp" / "external" / "ggml" / "src" / "ggml-vulkan"
    (gpu / "vulkan-shaders").mkdir(parents=True)
    # The pinned tree uses CRLF; a fixture in LF would hide a line-ending mistake
    # in a committed artifact, so keep the endings the real files have.
    for path, text in (
        (gpu / "ggml-vulkan.cpp", GGML_MINIMAL),
        (gpu / "vulkan-shaders" / "vulkan-shaders-gen.cpp", GENERATOR_MINIMAL),
    ):
        path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    sp = root / "audio.cpp" / "external" / "sentencepiece"
    sp.mkdir(parents=True)
    (sp / "CMakeLists.txt").write_bytes(SENTENCEPIECE_CMAKE.replace("\n", "\r\n").encode("utf-8"))
    return root


def _run(root: Path, **overrides: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["AUDIOCPP_DIR"] = str(root / "audio.cpp")
    env["PYTHON_BIN"] = sys.executable
    env.update(overrides)
    return subprocess.run(
        ["bash", str(root / "scripts" / "patch_audio_cpp_ggml.sh")],
        cwd=str(root),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_generator_patch_is_applied_and_idempotent(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    generator = root / "audio.cpp" / "external" / "ggml" / "src" / "ggml-vulkan" / "vulkan-shaders" / "vulkan-shaders-gen.cpp"

    first = _run(root)
    assert first.returncode == 0, first.stderr + first.stdout
    patched = generator.read_text(encoding="utf-8")

    # The retry waits out a transient fork failure instead of losing the shader.
    assert "RHETORIC VENDORED PATCH (shader fork retry)" in patched
    assert "std::this_thread::sleep_for(std::chrono::milliseconds(250));" in patched
    assert "#include <chrono>" in patched
    # The wait is bounded per generator, not per shader: 40 x 250ms, and the
    # compile latch it then sets stops every other waiter immediately.
    assert "rhetoric_fork_attempt < 40" in patched
    assert "FORK_FAIL_RETRY_COUNT" not in patched, (
        "the retry window is a patch-time constant and must be emitted as a number; "
        "the identifier does not exist in the generated C++"
    )
    assert "rhetoric_fork_stalled" not in patched, "one flag is enough; the latch already covers this"
    # A shader that still fails cannot become a silent hole in the archive.
    assert "rhetoric_shader_compile_failed = true;" in patched
    assert "refusing to write" in patched
    # glslc warns on stderr as well, and upstream dropped the shader on any
    # output there. The patch keeps the text for diagnosis but removes the early
    # return; a failed compile is caught by the empty embed below.
    assert "shader compile: stderr is not fatal" in patched
    assert "cannot compile " not in patched
    assert (
        '            std::cerr << "\\n\\n" << stderr_str << std::endl;\n            return;'
        not in patched
    )
    for marker in (
        "shader compile latch: declaration",
        "shader compile latch: catch",
        "shader compile latch: embed",
        "shader compile latch: exit",
    ):
        assert marker in patched
    # "refusing to write" has to come before the writes, or a failed run still
    # leaves a partial shader pair behind; main turns the latch into exit code 1.
    assert patched.index("refusing to write") < patched.index("write_file_if_changed(target_hpp")
    assert patched.index("refusing to write") < patched.index("write_binary_file(target_cpp")
    assert "shader compile latch: exit code" in patched
    assert "    write_output_files();\n\n    // ===== BEGIN RHETORIC VENDORED PATCH (shader compile latch: exit code)" in patched

    second = _run(root)
    assert second.returncode == 0, second.stderr + second.stdout
    assert generator.read_text(encoding="utf-8") == patched, "a second run must not re-patch"


def test_the_retry_window_override_reaches_the_generated_cpp(tmp_path: Path) -> None:
    """FORK_FAIL_RETRY_COUNT is a patch-time constant, so the number must be
    written into the C++. Emitting the identifier instead produced a generator
    that could not compile: the symbol does not exist in that translation unit.
    """
    root = _tree(tmp_path)
    generator = (
        root / "audio.cpp" / "external" / "ggml" / "src" / "ggml-vulkan"
        / "vulkan-shaders" / "vulkan-shaders-gen.cpp"
    )

    completed = _run(root, FORK_FAIL_RETRY_COUNT="7")
    assert completed.returncode == 0, completed.stderr + completed.stdout
    patched = generator.read_text(encoding="utf-8")
    assert "rhetoric_fork_attempt < 7" in patched
    assert "FORK_FAIL_RETRY_COUNT" not in patched


def test_a_non_numeric_retry_window_is_refused(tmp_path: Path) -> None:
    root = _tree(tmp_path)

    completed = _run(root, FORK_FAIL_RETRY_COUNT="many")
    assert completed.returncode != 0
    assert "FORK_FAIL_RETRY_COUNT must be a positive integer" in completed.stderr + completed.stdout


def test_a_missing_generator_file_is_refused(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    (root / "audio.cpp" / "external" / "ggml" / "src" / "ggml-vulkan" / "vulkan-shaders" / "vulkan-shaders-gen.cpp").unlink()

    completed = _run(root)
    assert completed.returncode != 0
    assert "vulkan-shaders-gen.cpp not found" in completed.stderr + completed.stdout


def test_a_moved_anchor_fails_loudly(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    generator = root / "audio.cpp" / "external" / "ggml" / "src" / "ggml-vulkan" / "vulkan-shaders" / "vulkan-shaders-gen.cpp"
    generator.write_text(
        GENERATOR_MINIMAL.replace("    pid_t pid = fork();\n", "    pid_t pid = some_other_spawn();\n"),
        encoding="utf-8",
    )

    completed = _run(root)
    assert completed.returncode != 0
    assert "ANCHOR NOT FOUND" in completed.stderr + completed.stdout
    assert "shader fork retry patch application failed" in completed.stderr + completed.stdout


# Each patched file, and the artifact that is supposed to be its reviewable diff.
ARTIFACTS = {
    "external/ggml/src/ggml-vulkan/ggml-vulkan.cpp": "scripts/patches/ggml_rdna1_buffer_memset.patch",
    "external/sentencepiece/CMakeLists.txt": "scripts/patches/audio_cpp_space_safe_build.patch",
    "external/ggml/src/ggml-vulkan/vulkan-shaders/vulkan-shaders-gen.cpp": "scripts/patches/ggml_shader_compile_robustness.patch",
}

_DIFF_HEADER = (
    "+++",
    "---",
    "@@",
    "diff --git",
    "index ",
    "new file mode",
    "deleted file mode",
    "old mode",
    "new mode",
    "similarity index",
    "rename from",
    "rename to",
)

# The RDNA1 block records the ggml commit it was vendored against. The fixture
# tree is not a git checkout, so the script writes "unknown" there; compare the
# shape, not the sha. Everything else on the line, including its CR, is compared
# exactly -- a stale artifact can differ only in line endings.
_VENDOR_NOTE = re.compile(r"(\s*// Vendored against ggml) \S+\.")


def _normalise(line: str) -> str:
    return _VENDOR_NOTE.sub(r"\1 <pinned>", line)


def _read_exact(path: Path) -> str:
    """Read text without newline translation, so CRLF stays visible."""
    return path.read_bytes().decode("utf-8")


def _artifact_changes(text: str) -> tuple[list[str], list[str]]:
    added: list[str] = []
    removed: list[str] = []
    # Split on "\n" (not splitlines()) so a trailing CR stays on the line.
    for line in text.split("\n"):
        if line.startswith(_DIFF_HEADER):
            continue
        if line.startswith("+"):
            added.append(_normalise(line[1:]))
        elif line.startswith("-"):
            removed.append(_normalise(line[1:]))
    return added, removed


def _applied_changes(before: str, after: str) -> tuple[list[str], list[str]]:
    before_lines, after_lines = before.split("\n"), after.split("\n")
    added: list[str] = []
    removed: list[str] = []
    matcher = difflib.SequenceMatcher(None, before_lines, after_lines)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ("replace", "delete"):
            removed.extend(_normalise(line) for line in before_lines[i1:i2])
        if tag in ("replace", "insert"):
            added.extend(_normalise(line) for line in after_lines[j1:j2])
    return added, removed


def test_the_committed_artifacts_match_a_fresh_application(tmp_path: Path) -> None:
    """A changed edit must not land with a stale patch artifact: regenerate with
    `scripts/patch_audio_cpp_ggml.sh` and commit the artifact it rewrites."""
    root = _tree(tmp_path)
    # read_text() translates CRLF to LF, which would hide an artifact written with
    # the wrong line endings; read the bytes instead.
    before = {rel: _read_exact(root / "audio.cpp" / rel) for rel in ARTIFACTS}

    completed = _run(root)
    assert completed.returncode == 0, completed.stderr + completed.stdout

    drifted = []
    for rel, artifact in ARTIFACTS.items():
        after = _read_exact(root / "audio.cpp" / rel)
        applied_added, applied_removed = _applied_changes(before[rel], after)
        artifact_added, artifact_removed = _artifact_changes(_read_exact(REPO_ROOT / artifact))
        if sorted(applied_added) != sorted(artifact_added):
            missing = sorted(set(applied_added) - set(artifact_added))
            stale = sorted(set(artifact_added) - set(applied_added))
            drifted.append(f"{artifact}: added lines differ; script adds {missing!r}, artifact has {stale!r}")
        if sorted(applied_removed) != sorted(artifact_removed):
            missing = sorted(set(applied_removed) - set(artifact_removed))
            stale = sorted(set(artifact_removed) - set(applied_removed))
            drifted.append(
                f"{artifact}: removed lines differ; script removes {missing!r}, artifact has {stale!r}"
            )
    assert not drifted, "regenerate the artifacts with scripts/patch_audio_cpp_ggml.sh:\n" + "\n".join(drifted)


def test_every_committed_artifact_is_covered() -> None:
    committed = {path.name for path in (REPO_ROOT / "scripts" / "patches").glob("*.patch")}
    assert committed == {Path(artifact).name for artifact in ARTIFACTS.values()}, (
        "a patch artifact was added or removed without being wired into ARTIFACTS"
    )

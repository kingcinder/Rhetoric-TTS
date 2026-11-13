"""The vendored shader-generator patch, exercised against a synthetic tree.

`scripts/patch_audio_cpp_ggml.sh` edits the cloned audio.cpp tree in place. The
shader-generator patch it now carries is what keeps the Vulkan build from going
red on an upstream race: the generator forks glslc processes, and a fork that
fails with EAGAIN used to drop that shader silently, leaving an undefined
`matmul_id_subgroup_*` symbol for the linker to find minutes later. These tests
run the real script against a fixture tree so the anchors, the markers and the
fail-loud behaviour stay pinned without cloning audio.cpp.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "patch_audio_cpp_ggml.sh"
ENGINE = "python3" if sys.platform != "win32" else "python"

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
    try {
        execute_command(cmd, stdout_str, stderr_str);
        if (!stderr_str.empty()) {
            std::cerr << "cannot compile " << name << "\\n\\n";
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
    (gpu / "ggml-vulkan.cpp").write_text(GGML_MINIMAL, encoding="utf-8")
    (gpu / "vulkan-shaders" / "vulkan-shaders-gen.cpp").write_text(GENERATOR_MINIMAL, encoding="utf-8")
    sp = root / "audio.cpp" / "external" / "sentencepiece"
    sp.mkdir(parents=True)
    (sp / "CMakeLists.txt").write_text(SENTENCEPIECE_CMAKE, encoding="utf-8")
    return root


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["AUDIOCPP_DIR"] = str(root / "audio.cpp")
    env["PYTHON_BIN"] = sys.executable
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
    # And a shader that still fails cannot become a silent hole in the archive.
    assert "rhetoric_shader_compile_failed = true;" in patched
    assert "refusing to write" in patched
    for marker in (
        "shader compile latch: declaration",
        "shader compile latch: stderr",
        "shader compile latch: catch",
        "shader compile latch: embed",
        "shader compile latch: exit",
    ):
        assert marker in patched

    second = _run(root)
    assert second.returncode == 0, second.stderr + second.stdout
    assert generator.read_text(encoding="utf-8") == patched, "a second run must not re-patch"


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

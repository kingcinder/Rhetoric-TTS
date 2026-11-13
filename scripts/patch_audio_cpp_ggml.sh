#!/usr/bin/env bash
# Apply Rhetoric's vendored patches to the cloned audio.cpp tree (ggml is
# vendored in-tree at external/ggml, so these are local, clearly-marked edits).
#
# Patch 1 - RDNA1 buffer memset (ggml): AMD RDNA1 (gfx1010/gfx1012) SDMA
#   transfer queues reject vkCmdFillBuffer (EINVAL), surfacing as
#   VK_ERROR_DEVICE_LOST during buffer init (ggml-org/whisper.cpp#3611).
#   ggml_vk_buffer_memset() runs its memset through the transfer queue's
#   command pool; this patch switches it to the compute queue on RDNA1.
#   vk_command_pool binds its queue, so ggml_vk_submit follows the same queue.
# Patch 2 - space-safe build (sentencepiece): audio.cpp fails to build from
#   checkout paths containing spaces because sentencepiece's
#   -fmacro-prefix-map=... flag is emitted unquoted and split on the space.
#   The value is quoted so builds work from any path.
# Patch 3 - Vulkan shader-compile robustness (vulkan-shaders-gen): the shader
#   generator forks up to min(16, cores) glslc processes at once. On a loaded
#   runner fork() fails with EAGAIN; the generator printed the error, dropped
#   that shader from the generated .cpp, and carried on, so the gap surfaced
#   much later as `undefined reference to matmul_id_subgroup_*` at link time.
#   Retry the fork with a bounded wait, and fail the generator instead of
#   emitting a header/cpp pair with missing definitions. The wait is bounded
#   per generator, not per shader: once one shader uses up its window the
#   shortage is not a burst, so the rest fail at once instead of each waiting
#   another minute (882 shaders would otherwise stall for an hour).
#
# All patches are idempotent (no-op when their RHETORIC_VENDORED marker is
# present) and FAIL LOUDLY if the source changes shape on an audio.cpp/ggml
# update, so the fixes can never be silently lost on a version bump.
set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIOCPP_DIR="${AUDIOCPP_DIR:-$REPO_ROOT/audio.cpp}"
GGML_FILE="$AUDIOCPP_DIR/external/ggml/src/ggml-vulkan/ggml-vulkan.cpp"
SP_FILE="$AUDIOCPP_DIR/external/sentencepiece/CMakeLists.txt"
GGML_MARKER="===== BEGIN RHETORIC VENDORED PATCH (RDNA1 buffer memset) ====="
SP_MARKER="===== BEGIN RHETORIC VENDORED PATCH (space-safe macro-prefix-map) ====="
SPIRV_MARKER="===== BEGIN RHETORIC VENDORED PATCH (portable SPIR-V headers) ====="
SHADERS_GEN_FILE="$AUDIOCPP_DIR/external/ggml/src/ggml-vulkan/vulkan-shaders/vulkan-shaders-gen.cpp"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ ! -f "$GGML_FILE" ]]; then
  echo "ERROR: ggml-vulkan.cpp not found at $GGML_FILE (run scripts/build_audio_cpp.sh first)." >&2
  exit 1
fi

# The shader generator carries the fork-retry and fail-loud patch; refuse to run
# without it rather than shipping a build whose race is silently unpatched.
if [[ ! -f "$SHADERS_GEN_FILE" ]]; then
  echo "ERROR: vulkan-shaders-gen.cpp not found at $SHADERS_GEN_FILE (run scripts/build_audio_cpp.sh first)." >&2
  exit 1
fi

# ggml uses `spv::` opcode constants but does not include the Khronos SPIR-V
# header on a clean Linux checkout. Add a portable SDK-layout include before
# the RDNA1 patch; this is intentionally source-local and platform neutral.
if grep -Fq "$SPIRV_MARKER" "$GGML_FILE"; then
  echo "[patch] portable SPIR-V headers: already applied (no-op)."
elif grep -Fq 'include <spirv/unified1/spirv.hpp>' "$GGML_FILE"; then
  echo "[patch] portable SPIR-V headers: source already includes a Khronos header (no-op)."
else
  "$PYTHON_BIN" - "$GGML_FILE" <<'PYEOF'
import sys
path = sys.argv[1]
raw = open(path, "rb").read()
anchor = b"#include <vulkan/vulkan.hpp>"
block = b"""#include <vulkan/vulkan.hpp>

// ===== BEGIN RHETORIC VENDORED PATCH (portable SPIR-V headers) =====
// ggml uses the `spv::` opcode constants below; include the Khronos header
// explicitly because Vulkan-Hpp does not provide it transitively on Linux.
#if __has_include(<spirv/unified1/spirv.hpp>)
#    include <spirv/unified1/spirv.hpp>
#elif __has_include(<spirv-headers/spirv.hpp>)
#    include <spirv-headers/spirv.hpp>
#elif __has_include(<spirv.hpp>)
#    include <spirv.hpp>
#else
#    include <spirv/unified1/spirv.hpp>
#endif
// ===== END RHETORIC VENDORED PATCH (portable SPIR-V headers) ====="""
if raw.count(anchor) != 1:
    raise SystemExit(f"ANCHOR NOT FOUND or duplicated in {path}")
open(path, "wb").write(raw.replace(anchor, block, 1))
PYEOF
  grep -Fq "$SPIRV_MARKER" "$GGML_FILE"
  echo "[patch] Applied portable SPIR-V headers"
fi

apply_patch() {
  local name="$1" marker="$2" file="$3" original_text="$4" patched_text="$5"

  if grep -q "$marker" "$file"; then
    echo "[patch] $name: already applied to $file (no-op)."
    return 0
  fi

  if ! "$PYTHON_BIN" - "$file" "$original_text" "$patched_text" <<'PYEOF'
import sys

path, original, patched = sys.argv[1], sys.argv[2], sys.argv[3]
o_lines = original.split("\n")
p_lines = patched.split("\n")
with open(path, "rb") as handle:
    raw = handle.read()
# Split on "\n" only: each element keeps its trailing "\r" when the file uses
# CRLF. Only the matched anchor region is replaced, so every other byte (and
# line ending) in the file is preserved byte-for-byte -- no diff churn.
file_lines = raw.split(b"\n")
norm = [line.rstrip(b"\r") for line in file_lines]
target = [line.encode() for line in o_lines]
for i in range(len(norm) - len(target) + 1):
    if norm[i : i + len(target)] == target:
        anchor_crlf = file_lines[i].endswith(b"\r")
        new_lines = [line.encode() + (b"\r" if anchor_crlf else b"") for line in p_lines]
        result = file_lines[:i] + new_lines + file_lines[i + len(target) :]
        open(path, "wb").write(b"\n".join(result))
        sys.exit(0)
sys.exit(
    f"ANCHOR NOT FOUND in {path} -- source changed shape; a vendored fix "
    f"must be re-applied by hand."
)
PYEOF
  then
    echo "ERROR: $name patch application failed (see message above). The vendored fix is NOT in place." >&2
    exit 1
  fi

  if ! grep -q "$marker" "$file"; then
    echo "ERROR: post-apply verification failed for $name; marker missing. Do not proceed until fixed." >&2
    exit 1
  fi
  echo "[patch] Applied $name to $file"
}

# --- Patch 1: RDNA1 buffer memset in ggml-vulkan.cpp -------------------------
GGML_ORIGINAL="$(printf '%s\n' \
  '        memset((uint8_t*)dst->ptr + offset, c, size);' \
  '        return;' \
  '    }' \
  '' \
  '    std::lock_guard<std::recursive_mutex> guard(dst->device->mutex);' \
  '    vk_context subctx = ggml_vk_create_temporary_context(dst->device->transfer_queue.cmd_pool);')"
GGML_PATCHED="$(printf '%s\n' \
  '        memset((uint8_t*)dst->ptr + offset, c, size);' \
  '        return;' \
  '    }' \
  '' \
  '    std::lock_guard<std::recursive_mutex> guard(dst->device->mutex);' \
  "    // $GGML_MARKER" \
  '    // AMD RDNA1 (gfx1010/gfx1012) SDMA transfer queues reject vkCmdFillBuffer' \
  '    // (EINVAL), surfacing as VK_ERROR_DEVICE_LOST during buffer init' \
  '    // (ggml-org/whisper.cpp#3611). Run the memset on the compute queue for' \
  '    // RDNA1; vk_command_pool binds its queue so ggml_vk_submit follows it.' \
  "    // Vendored against ggml $(git -C "$AUDIOCPP_DIR/external/ggml" rev-parse --short HEAD 2>/dev/null || echo unknown)." \
  '    // Re-check this block after any audio.cpp/ggml update.' \
  '    // ===== END RHETORIC VENDORED PATCH (RDNA1 buffer memset) =====' \
  '    vk_context subctx = ggml_vk_create_temporary_context(' \
  '        dst->device->architecture == vk_device_architecture::AMD_RDNA1' \
  '            ? dst->device->compute_queue.cmd_pool' \
  '            : dst->device->transfer_queue.cmd_pool);')"
apply_patch "RDNA1 buffer-memset fix" "$GGML_MARKER" "$GGML_FILE" "$GGML_ORIGINAL" "$GGML_PATCHED"

# --- Patch 2: space-safe macro-prefix-map in sentencepiece -------------------
SP_ORIGINAL="  string(APPEND CMAKE_CXX_FLAGS \" -fmacro-prefix-map=\${CMAKE_SOURCE_DIR}/=''\")"
# CMake comments use '#' (not '//'). The CMake line must contain literal
# backslash-quote escapes so the path stays inside the quotes:
#   string(APPEND CMAKE_CXX_FLAGS " -fmacro-prefix-map=\"...\").
SP_PATCHED="  # $SP_MARKER
  # audio.cpp fails to build from checkout paths containing spaces: the
  # unquoted -fmacro-prefix-map=... flag is split on the space. Quote the
  # value so builds work from any path.
  # ===== END RHETORIC VENDORED PATCH (space-safe macro-prefix-map) =====
  string(APPEND CMAKE_CXX_FLAGS \" -fmacro-prefix-map=\\\"\${CMAKE_SOURCE_DIR}/=\\\"\")"
apply_patch "space-safe sentencepiece build fix" "$SP_MARKER" "$SP_FILE" "$SP_ORIGINAL" "$SP_PATCHED"

# --- Patch 3: Vulkan shader-compile robustness in vulkan-shaders-gen ---------
SH_MARKER_CHRONO="===== BEGIN RHETORIC VENDORED PATCH (shader chrono include) ====="
SH_MARKER_FORK="===== BEGIN RHETORIC VENDORED PATCH (shader fork retry) ====="
SH_MARKER_DECL="===== BEGIN RHETORIC VENDORED PATCH (shader compile latch: declaration) ====="
SH_MARKER_STDERR="===== BEGIN RHETORIC VENDORED PATCH (shader compile: stderr is not fatal) ====="
SH_MARKER_CATCH="===== BEGIN RHETORIC VENDORED PATCH (shader compile latch: catch) ====="
SH_MARKER_EMBED="===== BEGIN RHETORIC VENDORED PATCH (shader compile latch: embed) ====="
SH_MARKER_EXIT="===== BEGIN RHETORIC VENDORED PATCH (shader compile latch: exit) ====="
SH_MARKER_STATUS="===== BEGIN RHETORIC VENDORED PATCH (shader compile latch: exit code) ====="

SH_INCLUDES_ORIGINAL="$(printf '%s\n' \
  '#include <thread>' \
  '#include <mutex>')"
SH_INCLUDES_PATCHED="$(printf '%s\n' \
  '#include <thread>' \
  "// $SH_MARKER_CHRONO" \
  '#include <chrono>' \
  '// ===== END RHETORIC VENDORED PATCH (shader chrono include) =====' \
  '#include <mutex>')"
apply_patch "shader chrono include" "$SH_MARKER_CHRONO" "$SHADERS_GEN_FILE" \
  "$SH_INCLUDES_ORIGINAL" "$SH_INCLUDES_PATCHED"

SH_FORK_ORIGINAL="$(printf '%s\n' \
  '    pid_t pid = fork();' \
  '    if (pid < 0) {' \
  '        std::cerr << strerror(errno) << "\n";' \
  '        throw std::runtime_error("Failed to fork process");' \
  '    }')"
SH_FORK_PATCHED="$(printf '%s\n' \
  '    pid_t pid = fork();' \
  "    // $SH_MARKER_FORK" \
  '    // This process runs up to min(16, cores) glslc forks at once. On a loaded' \
  '    // CI runner the pids cgroup limit makes fork() fail with EAGAIN; the old' \
  '    // code threw, the caller logged and dropped that shader, and the gap only' \
  '    // surfaced much later as undefined matmul_id_subgroup_* at link time.' \
  '    // Wait up to 10s (40 x 250ms) for a slot instead of losing the shader. A' \
  '    // shader that uses the whole window means the shortage is not a burst, and' \
  '    // the compile latch it then sets stops every other wait immediately.' \
  '    for (int rhetoric_fork_attempt = 0; pid < 0 && rhetoric_fork_attempt < 40; ++rhetoric_fork_attempt) {' \
  '        if (errno != EAGAIN && errno != ENOMEM) {' \
  '            break;' \
  '        }' \
  '        {' \
  '            std::lock_guard<std::mutex> rhetoric_guard(lock);' \
  '            if (rhetoric_shader_compile_failed) {' \
  '                break;' \
  '            }' \
  '        }' \
  '        std::this_thread::sleep_for(std::chrono::milliseconds(250));' \
  '        pid = fork();' \
  '    }' \
  '    // ===== END RHETORIC VENDORED PATCH (shader fork retry) =====' \
  '    if (pid < 0) {' \
  '        std::cerr << strerror(errno) << "\n";' \
  '        throw std::runtime_error("Failed to fork process");' \
  '    }')"
apply_patch "shader fork retry" "$SH_MARKER_FORK" "$SHADERS_GEN_FILE" \
  "$SH_FORK_ORIGINAL" "$SH_FORK_PATCHED"

# Declared next to the mutex that guards it, which is above execute_command: the
# retry loop reads the flag, so the declaration has to precede it.
SH_DECL_ORIGINAL="$(printf '%s\n' 'std::mutex lock;')"
SH_DECL_PATCHED="$(printf '%s\n' \
  'std::mutex lock;' \
  '' \
  "// $SH_MARKER_DECL" \
  '// A shader that failed to compile used to be dropped silently: the generated' \
  '// .cpp lacked its definitions while the header still declared them, so the' \
  '// build failed far away at link time. Latch it and fail the generator.' \
  '// glslc writes no .spv when it fails, so an empty embed is the failure test;' \
  '// its exit status is not consulted and warnings on stderr are not fatal.' \
  'static bool rhetoric_shader_compile_failed = false;' \
  '// ===== END RHETORIC VENDORED PATCH (shader compile latch: declaration) =====')"
apply_patch "shader compile latch declaration" "$SH_MARKER_DECL" "$SHADERS_GEN_FILE" \
  "$SH_DECL_ORIGINAL" "$SH_DECL_PATCHED"

# Upstream treats any stderr output as a compile failure and drops the shader.
# glslc reports warnings there too, so keep the text for diagnosis but let the
# .spv decide: a warning must not lose a shader, and a failed compile writes no
# binary, which the embed latch below turns into a hard failure.
SH_STDERR_ORIGINAL="$(printf '%s\n' \
  '        if (!stderr_str.empty()) {' \
  '            std::cerr << "cannot compile " << name << "\n\n";' \
  '            for (const auto& part : cmd) {' \
  '                std::cerr << part << " ";' \
  '            }' \
  '            std::cerr << "\n\n" << stderr_str << std::endl;' \
  '            return;' \
  '        }')"
SH_STDERR_PATCHED="$(printf '%s\n' \
  '        if (!stderr_str.empty()) {' \
  "            // $SH_MARKER_STDERR" \
  '            // glslc writes warnings to stderr as well, so text here does not' \
  '            // mean the shader failed. Print it and carry on; the embed step' \
  '            // rejects a missing .spv, which glslc writes only on success.' \
  '            std::cerr << "glslc wrote to stderr for " << name << "\n\n";' \
  '            for (const auto& part : cmd) {' \
  '                std::cerr << part << " ";' \
  '            }' \
  '            std::cerr << "\n\n" << stderr_str << std::endl;' \
  '            // ===== END RHETORIC VENDORED PATCH (shader compile: stderr is not fatal) =====' \
  '        }')"
apply_patch "shader compile: stderr is not fatal" "$SH_MARKER_STDERR" "$SHADERS_GEN_FILE" \
  "$SH_STDERR_ORIGINAL" "$SH_STDERR_PATCHED"

SH_CATCH_ORIGINAL="$(printf '%s\n' \
  '    } catch (const std::exception& e) {' \
  '        std::cerr << "Error executing command for " << name << ": " << e.what() << std::endl;' \
  '    }')"
SH_CATCH_PATCHED="$(printf '%s\n' \
  '    } catch (const std::exception& e) {' \
  "        // $SH_MARKER_CATCH" \
  '        {' \
  '            std::lock_guard<std::mutex> rhetoric_guard(lock);' \
  '            rhetoric_shader_compile_failed = true;' \
  '        }' \
  '        // ===== END RHETORIC VENDORED PATCH (shader compile latch: catch) =====' \
  '        std::cerr << "Error executing command for " << name << ": " << e.what() << std::endl;' \
  '    }')"
apply_patch "shader compile latch on exception" "$SH_MARKER_CATCH" "$SHADERS_GEN_FILE" \
  "$SH_CATCH_ORIGINAL" "$SH_CATCH_PATCHED"

SH_EMBED_ORIGINAL="$(printf '%s\n' \
  '            std::string data = read_binary_file(path);' \
  '            if (data.empty()) {' \
  '                continue;' \
  '            }')"
SH_EMBED_PATCHED="$(printf '%s\n' \
  '            std::string data = read_binary_file(path);' \
  '            if (data.empty()) {' \
  "                // $SH_MARKER_EMBED" \
  '                {' \
  '                    std::lock_guard<std::mutex> rhetoric_guard(lock);' \
  '                    rhetoric_shader_compile_failed = true;' \
  '                }' \
  '                // ===== END RHETORIC VENDORED PATCH (shader compile latch: embed) =====' \
  '                continue;' \
  '            }')"
apply_patch "shader compile latch on empty embed" "$SH_MARKER_EMBED" "$SHADERS_GEN_FILE" \
  "$SH_EMBED_ORIGINAL" "$SH_EMBED_PATCHED"

# The check sits inside write_output_files, just before it writes: a failed shader
# leaves no partial pair behind, and main still turns the latch into exit code 1.
SH_EXIT_ORIGINAL="$(printf '%s\n' \
  '    if (input_filepath == "") {' \
  '        write_file_if_changed(target_hpp, hdr.str());' \
  '    }' \
  '    if (target_cpp != "") {' \
  '        write_binary_file(target_cpp, src.str());' \
  '    }' \
  '}')"
SH_EXIT_PATCHED="$(printf '%s\n' \
  "    // $SH_MARKER_EXIT" \
  '    // Refuse to emit a header/cpp pair with shader definitions missing: the' \
  '    // linker would report an undefined matmul_id_subgroup_* symbol much later,' \
  '    // far from the shader that actually failed.' \
  '    if (rhetoric_shader_compile_failed) {' \
  '        std::cerr << "a Vulkan shader failed to compile or embed; refusing to write "' \
  '                     "a shader pair with missing definitions" << std::endl;' \
  '        return;' \
  '    }' \
  '    // ===== END RHETORIC VENDORED PATCH (shader compile latch: exit) =====' \
  '    if (input_filepath == "") {' \
  '        write_file_if_changed(target_hpp, hdr.str());' \
  '    }' \
  '    if (target_cpp != "") {' \
  '        write_binary_file(target_cpp, src.str());' \
  '    }' \
  '}')"
apply_patch "shader compile latch exit" "$SH_MARKER_EXIT" "$SHADERS_GEN_FILE" \
  "$SH_EXIT_ORIGINAL" "$SH_EXIT_PATCHED"

SH_STATUS_ORIGINAL="$(printf '%s\n' '    write_output_files();')"
SH_STATUS_PATCHED="$(printf '%s\n' \
  '    write_output_files();' \
  '' \
  "    // $SH_MARKER_STATUS" \
  '    // write_output_files() reports the failure above and writes nothing; the' \
  '    // build has to stop here rather than compile an incomplete translation unit.' \
  '    if (rhetoric_shader_compile_failed) {' \
  '        return 1;' \
  '    }' \
  '    // ===== END RHETORIC VENDORED PATCH (shader compile latch: exit code) =====')"
apply_patch "shader compile latch exit code" "$SH_MARKER_STATUS" "$SHADERS_GEN_FILE" \
  "$SH_STATUS_ORIGINAL" "$SH_STATUS_PATCHED"

# Regenerate the reviewable patch artifacts so they always match what is applied.
mkdir -p "$REPO_ROOT/scripts/patches"
git -C "$AUDIOCPP_DIR/external/ggml" diff -- src/ggml-vulkan/ggml-vulkan.cpp > "$REPO_ROOT/scripts/patches/ggml_rdna1_buffer_memset.patch" || true
git -C "$AUDIOCPP_DIR" diff -- external/sentencepiece/CMakeLists.txt > "$REPO_ROOT/scripts/patches/audio_cpp_space_safe_build.patch" || true
git -C "$AUDIOCPP_DIR/external/ggml" diff -- src/ggml-vulkan/vulkan-shaders/vulkan-shaders-gen.cpp > "$REPO_ROOT/scripts/patches/ggml_shader_compile_robustness.patch" || true
echo "[patch] ggml commit: $(git -C "$AUDIOCPP_DIR/external/ggml" rev-parse HEAD 2>/dev/null || echo '?')"
echo "[patch] Patch artifacts: $REPO_ROOT/scripts/patches/"

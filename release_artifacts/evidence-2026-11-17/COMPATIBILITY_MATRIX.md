# Compatibility matrix — RC1

| Target | Install / CLI | GUI | CPU render | RX 5700 XT Vulkan | Status |
|---|---|---|---|---|---|
| Ubuntu 24.04 amd64, fresh network-isolated container | Kit hashes/install, version/help and uninstall smoke passed in `airgap-install-uninstall-32ac9df.log` | Not verified; session display is unreachable | Not run; no authorized test serial | Not run; no authorized test serial | Partial engineering smoke only; not release qualified |

Host observed: Ubuntu 24.04.5 LTS amd64; AMD RX 5700 XT and NVIDIA Quadro K600 on PCI. Direct session had no accessible X display and no `/dev/dri`. Docker can pass `/dev/dri/renderD128`, but GPU acceptance was not attempted without licensed render authorization. No other Ubuntu version or GPU is certified by this RC work.

set -euo pipefail
cmd() { printf '\033[1;32mlpala@wsl\033[0m:\033[1;34m~/Speedup\033[0m$ %s\n' "$*"; eval "$*"; }
cd "$(dirname "${BASH_SOURCE[0]}")/../.."

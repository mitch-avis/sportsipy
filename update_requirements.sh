#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob

# Runs from the repo root regardless of where it's invoked from.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
VENV_PATH="$REPO_ROOT/.venv"
PYTHON_REQUEST=""
cd "$REPO_ROOT"

# uv is treated as an external tool on PATH rather than as a project dependency inside .venv.

usage() {
	cat <<'EOF'
Usage: ./update_requirements.sh [--python <version-request>]

Updates the project's uv lockfile and syncs the active .venv.

If compatibility requirements files are present, they are refreshed from uv.lock:
- requirements.txt -> runtime dependencies only
- requirements-<group>.txt -> only that dependency group

Examples:
	./update_requirements.sh
	./update_requirements.sh --python 3.13

When no --python argument is provided, uv chooses the newest compatible Python
according to the project's configuration and local uv installation.
EOF
}

info() {
	echo "==> $*"
}

die() {
	echo "Error: $*" >&2
	exit 1
}

canonical_path() {
	cd "$1" >/dev/null 2>&1 && pwd -P
}

confirm() {
	local prompt="$1"
	local reply
	read -r -p "$prompt [y/N] " reply
	[[ "$reply" =~ ^[Yy]([Ee][Ss])?$ ]]
}

parse_args() {
	while [[ $# -gt 0 ]]; do
		case "$1" in
		-p | --python)
			[[ $# -ge 2 ]] || die "Missing value for $1."
			PYTHON_REQUEST="$2"
			shift 2
			;;
		-h | --help)
			usage
			exit 0
			;;
		--)
			shift
			break
			;;
		*)
			die "Unknown option: $1"
			;;
		esac
	done

	[[ $# -eq 0 ]] || die "Unexpected positional arguments: $*"
}

ensure_uv() {
	if ! command -v uv >/dev/null 2>&1; then
		die "'uv' is not installed or not on PATH. Install it from https://astral.sh/uv/."
	fi
}

ensure_pyproject_exists() {
	[[ -f "$REPO_ROOT/pyproject.toml" ]] || die "A pyproject.toml file is required at the repo root."
}

create_venv() {
	local -a command=(uv venv .venv)

	if [[ -n "$PYTHON_REQUEST" ]]; then
		command+=(--python "$PYTHON_REQUEST")
	fi

	"${command[@]}"
}

ensure_venv_exists() {
	local create_command="uv venv .venv"

	if [[ -n "$PYTHON_REQUEST" ]]; then
		create_command+=" --python $PYTHON_REQUEST"
	fi

	if [[ -d "$VENV_PATH" ]]; then
		return
	fi

	info "No .venv directory was found."
	if ! confirm "Create one now with '$create_command'?"; then
		die "A project virtual environment is required to continue."
	fi

	create_venv
	info "Created .venv. Activate it with: source .venv/bin/activate"
	info "Then rerun ./update_requirements.sh"
	exit 0
}

ensure_venv_is_active() {
	local active_venv=""

	if [[ -n "${VIRTUAL_ENV:-}" ]] && [[ -d "${VIRTUAL_ENV}" ]]; then
		active_venv="$(canonical_path "$VIRTUAL_ENV")"
	fi

	if [[ "$active_venv" == "$VENV_PATH" ]]; then
		return
	fi

	info "The project virtual environment exists but is not active."
	echo "Activate it in your current shell with:" >&2
	echo "  source .venv/bin/activate" >&2
	echo "Then rerun this script:" >&2
	echo "  ./update_requirements.sh" >&2
	exit 1
}

export_runtime_requirements() {
	info "Refreshing requirements.txt from uv.lock"
	uv export \
		--format requirements.txt \
		--no-default-groups \
		--no-emit-project \
		--no-hashes \
		--output-file requirements.txt
}

export_group_requirements() {
	local group_name="$1"
	local output_file="requirements-${group_name}.txt"

	info "Refreshing ${output_file} from dependency group '${group_name}'"
	uv export \
		--format requirements.txt \
		--only-group "$group_name" \
		--no-emit-project \
		--no-hashes \
		--output-file "$output_file"
}

refresh_compatibility_requirements() {
	local file group_name
	declare -A seen_groups=()

	if [[ -f "$REPO_ROOT/requirements.in" || -f "$REPO_ROOT/requirements.txt" ]]; then
		export_runtime_requirements
	fi

	for file in requirements-*.in requirements-*.txt; do
		[[ -e "$file" ]] || continue
		group_name="${file#requirements-}"
		group_name="${group_name%.in}"
		group_name="${group_name%.txt}"

		if [[ -z "$group_name" || -n "${seen_groups[$group_name]:-}" ]]; then
			continue
		fi

		seen_groups["$group_name"]=1
		export_group_requirements "$group_name"
	done
}

main() {
	parse_args "$@"
	ensure_uv
	ensure_pyproject_exists
	ensure_venv_exists
	ensure_venv_is_active

	# If supported, keep uv itself up to date (no-op on older uv builds).
	uv self update >/dev/null 2>&1 || true

	info "Locking project dependencies (upgrade all)"
	uv lock --upgrade

	info "Syncing the active virtual environment from uv.lock"
	uv sync --active

	refresh_compatibility_requirements

	info "Done."
}

main "$@"

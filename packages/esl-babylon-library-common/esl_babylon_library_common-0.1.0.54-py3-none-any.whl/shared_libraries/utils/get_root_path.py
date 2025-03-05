from pathlib import Path


def get_root_path(
        marker_folder="DATA"
) -> Path:
    current_path = Path.cwd().resolve()

    for current_path in [current_path] + list(current_path.parents):
        if not (current_path / marker_folder).exists():
            continue

        return current_path

    raise RuntimeError(
        f"Could not determine the project root. Ensure a '{marker_folder}' exists or provide"
    )

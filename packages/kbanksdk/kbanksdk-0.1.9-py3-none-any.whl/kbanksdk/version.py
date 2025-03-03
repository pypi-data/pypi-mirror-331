import subprocess
import re


def validate_version(version: str) -> str:
    """Validate version matches semantic versioning format"""
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        raise ValueError(
            f"Invalid version format: {version}. "
            "Must follow semantic versioning (e.g. 1.0.0)"
        )
    return version


def get_version() -> str:
    try:
        raw_version = (
            subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
        version = raw_version.lstrip("v")
        return validate_version(version)
    except subprocess.CalledProcessError:
        return "0.0.0"
    except ValueError as e:
        raise SystemExit(
            f"Version validation failed: {str(e)}\n"
            "Please create a valid tag using:\n"
            "git tag -a vX.Y.Z -m 'Version X.Y.Z'"
        ) from e

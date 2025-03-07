import json
import logging
from pathlib import Path
from typing import Any, Optional

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

logger = logging.getLogger(__name__)

def load_resource(
    resource_package: str,
    resource_name: str,
    explicit_path: Optional[str] = None,
    parse_json: bool = False
) -> Optional[Any]:
    """
    Load a resource file either from an explicit file path or from a packaged resource.

    Parameters:
        resource_package (str): The package name where the resource is located (e.g., "llmfusion.resources").
        resource_name (str): The name of the resource file (e.g., "cost_map.json").
        explicit_path (Optional[str]): If provided, load the file from this path instead.
        parse_json (bool): If True, parse the content as JSON and return the resulting object.

    Returns:
        The loaded resource content. If parse_json is True, returns a Python object (dict, list, etc.),
        otherwise returns the content as a string. Returns None if the resource cannot be loaded.
    """
    # Load from an explicit file path if provided.
    if explicit_path:
        path = Path(explicit_path)
        if not path.is_absolute():
            # Resolve relative to the current file's directory.
            path = (Path(__file__).parent / explicit_path).resolve()
        if not path.exists():
            logger.warning(f"Resource file '{path}' not found.")
            return None
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Error reading resource file '{path}': {e}")
            return None
    else:
        # Load from packaged resource.
        try:
            with pkg_resources.open_text(resource_package, resource_name) as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error loading resource '{resource_name}' from package '{resource_package}': {e}")
            return None

    if parse_json:
        try:
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error parsing JSON content from resource '{resource_name}': {e}")
            return None

    return content

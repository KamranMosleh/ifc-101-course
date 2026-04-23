from pathlib import Path
from typing import Optional

import streamlit.components.v1 as components

# Keep the component declaration in an importable module to avoid
# Streamlit multipage module resolution issues.
frontend_dir = (Path(__file__).parent.parent / "pages" / "frontend-viewer").absolute()
_component_func = components.declare_component(
    "ifc_js_viewer", path=str(frontend_dir)
)


def ifc_js_viewer(url: Optional[bytes] = None):
    return _component_func(url=url)

from pathlib import Path
from magicgui import widgets


def show_io_win(dtype="APS_tomo"):
    vals = widgets.request_values(
        name={
            "annotation": Path,
            "label": "pick a tomo file",
            "options": {"mode": "r", "filter": "tomo data file (*.h5)"},
        },
        title="pick a tomo file from 3D XANES data series",
    )
    return vals




import numpy as np

import napari
import skimage.data
import skimage.filters

from .guis.tomo_gui import tomo_gui
from .guis.xanes_reg_gui import xanes_reg_gui
from .guis.xanes_fit_gui import xanes_fit_gui
from .guis.xanes_vis_gui import xanes_vis_gui
from .guis.convert_data_gui import convt_dat_gui
from .guis.appl_mask_gui import appl_mask_gui


def txm_gui():
    viewer = napari.Viewer(title="txm_sandbox")
    _tomo_gui = tomo_gui(viewer)
    _xanes_reg_gui = xanes_reg_gui(viewer)
    _xanes_fit_gui = xanes_fit_gui(viewer)
    _xanes_vis_gui = xanes_vis_gui(viewer)
    _convt_dat_gui = convt_dat_gui(viewer)
    _appl_mask_gui = appl_mask_gui(viewer)

    viewer.add_image(
        skimage.data.astronaut().mean(-1).astype(np.float32), name="tomo_viewer"
    )

    viewer.window.add_dock_widget(
        _tomo_gui.gui_layout, name="Tomo Recon", area="right", tabify=True
    )
    viewer.window.add_dock_widget(
        _xanes_reg_gui.gui_layout, name="XANES Reg", area="right", tabify=True
    )
    viewer.window.add_dock_widget(
        _xanes_fit_gui.gui_layout, name="XANES Fit", area="right", tabify=True
    )
    viewer.window.add_dock_widget(
        _xanes_vis_gui.gui_layout, name="XANES Vis", area="right", tabify=True
    )
    viewer.window.add_dock_widget(
        _convt_dat_gui.gui_layout, name="Convert Data", area="right", tabify=True
    )
    viewer.window.add_dock_widget(
        _appl_mask_gui.gui_layout, name="Apply Mask", area="right", tabify=True
    )

    napari.run()


if __name__ == "__main__":
    txm_gui()

import numpy as np
import os

import dask.array as da
import h5py
import json
from pathlib import Path
import matplotlib.pyplot as plt
from magicgui import widgets

from ...utils.io import (
    tif_writer,
    tif_seq_writer,
    raw_writer,
    raw_seq_writer,
    asc_writer,
)
from ..utils.misc import (
    check_avail_items,
    get_slcd_ds_path,
    update_layer_in_viewer,
    show_layers_in_viewer,
    rm_gui_viewers,
    disp_progress_info,
)


cfg_fn = Path(__file__).parents[1] / "configs/txm_simple_gui_script_cfg.json"
xanes3d_fit_script_fn = Path(__file__).parents[1] / "scripts/xanes3D_fit_cmd.py"

with open(Path(__file__).parents[1] / "configs/xanes_proc_data_struct_cfg.json") as f:
    xanes_proc_data_struct = json.load(f)


_CONVT_DATA_ITEM_CHOICES = []


def get_xanes_convt_items_choices(ComboBox):
    global _CONVT_DATA_ITEM_CHOICES
    return _CONVT_DATA_ITEM_CHOICES


################################################################################
#                             XANES Analysis GUI                               #
################################################################################
class convt_dat_gui:
    def __init__(self, viewer):
        self.viewer = viewer
        self._convt_in_data_file = None
        self._convt_data_ready = False
        self._convt_in_dat_type = "3D XANES"
        self._convt_data = None
        self._convt_fn_p = None
        self._viewers = ["convt_data", "tomo_viewer"]

        self.label1 = widgets.Label(
            value="-------------------    Convert Data    -------------------",
        )
        self.convt_in_data_type = widgets.ComboBox(
            name="data type",
            choices=["TOMO Raw", "2D XANES", "3D XANES"],
            value="3D XANES",
            enabled=True,
        )
        self.convt_in_data_file = widgets.FileEdit(
            name="data file", mode="r", filter="*.h5"
        )
        self.convt_avail_items = widgets.ComboBox(
            name="available items", choices=get_xanes_convt_items_choices
        )
        self.convt_out_file_type = widgets.RadioButtons(
            name="save as",
            choices=["tif", "tif seq", "raw", "raw seq"],
            value="tif",
            orientation="horizontal",
            enabled=False,
        )
        self.convt_out_dir = widgets.FileEdit(name="save to", mode="d", enabled=False)
        self.convt = widgets.PushButton(text="convert", enabled=False)
        self.convt_info_board = widgets.TextEdit(
            label="data info", value="", enabled=False
        )
        self.close = widgets.PushButton(text="close", enabled=False)
        self.op_status = widgets.LineEdit(name="operation status", enabled=False)

        self.convt_in_data_type.changed.connect(self._sel_in_data_type)
        self.convt_in_data_file.changed.connect(self._sel_in_data_file)
        self.convt_avail_items.changed.connect(self._sel_convt_in_avail_items)
        self.convt.changed.connect(self._convt)
        self.close.changed.connect(self._close)

        self.gui_layout = widgets.VBox(
            widgets=[
                self.label1,
                self.convt_in_data_type,
                self.convt_in_data_file,
                self.convt_avail_items,
                self.convt_out_file_type,
                self.convt_out_dir,
                self.convt,
                self.convt_info_board,
                self.close,
                self.op_status,
            ]
        )
        self.key_widgets = [
            self.convt_avail_items,
            self.convt_out_file_type,
            self.convt_out_dir,
            self.convt,
            self.convt_info_board,
            self.close,
            self.op_status,
        ]

    def __convt_gui_widgets_logic(self):
        if self._convt_data_ready:
            self.convt_avail_items.enabled = True
            self.convt_out_dir.enabled = True
            self.convt_out_file_type.enabled = True
            self.convt.enabled = True
            self.close.enabled = True
        else:
            self.convt_avail_items.enabled = False
            self.convt_out_dir.enabled = False
            self.convt_out_file_type.enabled = False
            self.convt.enabled = False
            self.close.enabled = False

    def __avail_item_slcd(self):
        if self._convt_data_ready:
            (self._in_dat_path_in_h5, _in_dat_desc, _in_dat_dtype) = get_slcd_ds_path(
                self.convt_in_data_file.value,
                self.convt_in_data_type.value,
                self.convt_avail_items.value,
            )

            self.__close_file()
            with h5py.File(self.convt_in_data_file.value, "r") as f:
                self._in_dat_item_sz = f[self._in_dat_path_in_h5].shape
                self.convt_info_board.value = (
                    _in_dat_desc
                    + f"\nshape: {self._in_dat_item_sz}"
                    + f"\ndtype: {_in_dat_dtype}"
                )

            try:
                self._convt_fn_p = h5py.File(self.convt_in_data_file.value, "a")
                self._convt_data = da.from_array(
                    self._convt_fn_p[self._in_dat_path_in_h5]
                )
                if len(self._convt_data.shape) > 1:
                    update_layer_in_viewer(self.viewer, self._convt_data, "convt_data")
                    show_layers_in_viewer(self.viewer, ["convt_data"])
                    self._convt_data_ready = True
                elif len(self._convt_data.shape) == 1:
                    rm_gui_viewers(self.viewer, self._viewers)
                    self._convt_data_ready = True
                else:
                    rm_gui_viewers(self.viewer, self._viewers)
                    self._convt_data_ready = False
            except:
                self.__close_file()
                self._convt_data_ready = False

    def __dflt_out_file_type(self):
        if (self._convt_data is None) or (len(self._convt_data.shape) <= 2):
            self.convt_out_file_type.enabled = False
        else:
            self.convt_out_file_type.enabled = True
        self.convt_out_file_type.value = "tif"

    def __init_widgets(self):
        global _CONVT_DATA_ITEM_CHOICES
        _CONVT_DATA_ITEM_CHOICES = []
        self.convt_avail_items.reset_choices()
        self.convt_out_file_type.value = "tif"
        self.convt_out_dir.value = ""
        self.convt_info_board.value = ""
        self.op_status.value = ""
        for widget in self.key_widgets:
            widget.enabled = False
        self.convt_in_data_file.enabled = True
        self.convt_in_data_type.enabled = True

    def __reset_data_states(self):
        self._convt_data_ready = False

    def _sel_in_data_type(self):
        self.convt_in_data_file.value = ""

    @disp_progress_info("data loading")
    def _sel_in_data_file(self):
        self.__init_widgets()
        self.__close_file()
        self.__reset_data_states()
        choices = check_avail_items(
            self.convt_in_data_file.value, self.convt_in_data_type.value
        )
        global _CONVT_DATA_ITEM_CHOICES
        _CONVT_DATA_ITEM_CHOICES = choices
        self.convt_avail_items.reset_choices()
        if _CONVT_DATA_ITEM_CHOICES:
            self._convt_data_ready = True
            fn = Path.resolve(self.convt_in_data_file.value)
            self.convt_out_dir.value = str(
                fn.parent / (fn.stem + "_export") / self.convt_avail_items.value
            )
        else:
            self._convt_data_ready = False
            self.convt_out_dir.value = ""
        self.__avail_item_slcd()
        self.__convt_gui_widgets_logic()

    def _sel_convt_in_avail_items(self):
        self.__avail_item_slcd()
        self.__convt_gui_widgets_logic()
        self.__dflt_out_file_type()
        fn = Path.resolve(self.convt_in_data_file.value)
        self.convt_out_dir.value = str(
            fn.parent / (fn.stem + "_export") / self.convt_avail_items.value
        )

    @disp_progress_info("data converting")
    def _convt(self):
        if not Path(self.convt_out_dir.value).exists():
            Path(self.convt_out_dir.value).mkdir(parents=True)

        if len(self._convt_data.shape) == 1:
            out_fn_fnt = self.convt_avail_items.value + ".ascii"
            fn = str(Path(self.convt_out_dir.value).joinpath(out_fn_fnt))
            asc_writer(fn, self._convt_data.compute())
        elif "seq" in self.convt_out_file_type.value:
            if "tif" in self.convt_out_file_type.value:
                out_fn_fnt = self.convt_avail_items.value + "_{}.tiff"
                fn = str(Path(self.convt_out_dir.value).joinpath(out_fn_fnt))
                tif_seq_writer(
                    fn,
                    self._convt_data.compute(),
                    ids=0,
                    digit=5,
                )
            else:
                out_fn_fnt = self.convt_avail_items.value + "_{}.raw"
                fn = str(Path(self.convt_out_dir.value).joinpath(out_fn_fnt))
                raw_seq_writer(
                    fn,
                    self._convt_data.compute(),
                    ids=0,
                    digit=5,
                )
        else:
            if "tif" in self.convt_out_file_type.value:
                out_fn_fnt = self.convt_avail_items.value + ".tiff"
                fn = str(Path(self.convt_out_dir.value).joinpath(out_fn_fnt))
                tif_writer(fn, self._convt_data.compute())
            elif "raw" in self.convt_out_file_type.value:
                out_fn_fnt = self.convt_avail_items.value + ".raw"
                fn = str(Path(self.convt_out_dir.value).joinpath(out_fn_fnt))
                raw_writer(fn, self._convt_data.compute())
        self.viewer.status = "Convertion is done!"

    def __close_file(self):
        if self._convt_fn_p is not None:
            self._convt_fn_p.close()
            self._convt_fn_p = None
            self._convt_data = None
            rm_gui_viewers(self.viewer, self._viewers)

    def _close(self):
        self.convt_in_data_file.value = ""
        self.__close_file()

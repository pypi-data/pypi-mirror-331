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


_APPL_DATA_ITEM_CHOICES = []
_APPL_MASK_ITEM_CHOICES = []


def get_xanes_appl_data_items_choices(ComboBox):
    global _APPL_DATA_ITEM_CHOICES
    return _APPL_DATA_ITEM_CHOICES


def get_xanes_appl_mask_items_choices(ComboBox):
    global _APPL_MASK_ITEM_CHOICES
    return _APPL_MASK_ITEM_CHOICES


################################################################################
#                             XANES Analysis GUI                               #
################################################################################
class appl_mask_gui:
    def __init__(self, viewer):
        self.viewer = viewer
        self._appl_mk_in_data_file = None
        self._appl_mk_data_ready = False
        self._appl_mk_in_dat_type = "3D XANES"
        self._appl_mk_data = None
        self._appl_mk_fn_p = None
        self._viewers = ["appl_mk_data", "appl_mk_mask", "tomo_viewer"]

        self.label1 = widgets.Label(
            value="--------------------    Apply Mask    --------------------",
        )
        self.appl_mk_in_data_type = widgets.ComboBox(
            name="data type",
            choices=["TOMO Raw", "2D XANES", "3D XANES"],
            value="3D XANES",
            enabled=True,
        )
        self.appl_mk_in_data_file = widgets.FileEdit(
            name="data file", mode="r", filter="*.h5"
        )
        self.appl_mk_data_avail_items = widgets.ComboBox(
            name="available items", choices=get_xanes_appl_data_items_choices
        )
        self.appl_mk_mask_avail_items = widgets.ComboBox(
            name="available masks", choices=get_xanes_appl_mask_items_choices
        )
        self.appl_mk_out_file_type = widgets.RadioButtons(
            name="save as",
            choices=["tif", "tif seq", "raw", "raw seq"],
            value="tif",
            orientation="horizontal",
            enabled=False,
        )
        self.appl_mk_out_dir = widgets.FileEdit(name="save to", mode="d", enabled=False)
        self.apply = widgets.PushButton(text="apply", enabled=False)
        self.appl_mk_info_board = widgets.TextEdit(
            label="data info", value="", enabled=False
        )
        self.close = widgets.PushButton(text="close", enabled=False)
        self.op_status = widgets.LineEdit(name="operation status", enabled=False)

        self.appl_mk_in_data_type.changed.connect(self._sel_in_data_type)
        self.appl_mk_in_data_file.changed.connect(self._sel_in_data_file)
        self.appl_mk_data_avail_items.changed.connect(self._sel_data_avail_items)
        self.appl_mk_mask_avail_items.changed.connect(self._sel_mask_avail_items)
        self.apply.changed.connect(self._apply)
        self.close.changed.connect(self._close_file)

        self.gui_layout = widgets.VBox(
            widgets=[
                self.label1,
                self.appl_mk_in_data_type,
                self.appl_mk_in_data_file,
                self.appl_mk_data_avail_items,
                self.appl_mk_mask_avail_items,
                self.appl_mk_out_file_type,
                self.appl_mk_out_dir,
                self.apply,
                self.appl_mk_info_board,
                self.close,
                self.op_status,
            ]
        )
        self.key_widgets = [
            self.appl_mk_data_avail_items,
            self.appl_mk_mask_avail_items,
            self.appl_mk_out_file_type,
            self.appl_mk_out_dir,
            self.apply,
            self.appl_mk_info_board,
            self.close,
            self.op_status,
        ]

    def __lock_appl_mk_gui_widgets(self):
        if self._appl_mk_data_ready:
            self.appl_mk_data_avail_items.enabled = True
            self.appl_mk_mask_avail_items.enabled = True
            self.appl_mk_out_dir.enabled = True
            self.appl_mk_out_file_type.enabled = True
            self.apply.enabled = True
            self.close.enabled = True
        else:
            self.appl_mk_data_avail_items.enabled = False
            self.appl_mk_mask_avail_items.enabled = False
            self.appl_mk_out_dir.enabled = False
            self.appl_mk_out_file_type.enabled = False
            self.apply.enabled = False
            self.close.enabled = False

    def __avail_item_slcd(self, mode="data"):
        if self._appl_mk_data_ready:
            if mode == "data":
                (self._in_data_path_in_h5, _in_dat_desc, _in_dat_dtype) = (
                    get_slcd_ds_path(
                        self.appl_mk_in_data_file.value,
                        self.appl_mk_in_data_type.value,
                        self.appl_mk_data_avail_items.value,
                    )
                )
                self.__close_file(mode="data", kill=False)
                with h5py.File(self.appl_mk_in_data_file.value, "r") as f:
                    self._in_data_sz = f[self._in_data_path_in_h5].shape
                    self.appl_mk_info_board.value = (
                        _in_dat_desc
                        + f"\nshape: {self._in_data_sz}"
                        + f"\ndtype: {_in_dat_dtype}"
                    )
                try:
                    if self._appl_mk_fn_p is None:
                        self._appl_mk_fn_p = h5py.File(
                            self.appl_mk_in_data_file.value, "a"
                        )
                    self._appl_mk_data = da.from_array(
                        self._appl_mk_fn_p[self._in_data_path_in_h5]
                    )
                    if len(self._appl_mk_data.shape) > 1:
                        update_layer_in_viewer(
                            self.viewer, self._appl_mk_data, "appl_mk_data"
                        )
                        show_layers_in_viewer(self.viewer, ["appl_mk_data"])
                        self._appl_mk_data_ready = True
                    else:
                        rm_gui_viewers(self.viewer, ["appl_mk_data"])
                        self._appl_mk_data_ready = False
                except Exception as e:
                    self.op_status.value = (
                        "Invalid file. Check terminal for error message ..."
                    )
                    print(e)
                    self.__close_file(mode="data", kill=True)
                    self.__close_file(mode="mask", kill=False)
                    self._appl_mk_data_ready = False
            else:
                (self._in_mask_path_in_h5, _in_dat_desc, _in_dat_dtype) = (
                    get_slcd_ds_path(
                        self.appl_mk_in_data_file.value,
                        self.appl_mk_in_data_type.value,
                        self.appl_mk_mask_avail_items.value,
                    )
                )
                self.__close_file(mode="mask", kill=False)
                with h5py.File(self.appl_mk_in_data_file.value, "r") as f:
                    self._in_mask_sz = f[self._in_mask_path_in_h5].shape
                    self.appl_mk_info_board.value = (
                        _in_dat_desc
                        + f"\nshape: {self._in_mask_sz}"
                        + f"\ndtype: {_in_dat_dtype}"
                    )
                try:
                    if self._appl_mk_fn_p is None:
                        self._appl_mk_fn_p = h5py.File(
                            self.appl_mk_in_data_file.value, "a"
                        )
                    self._appl_mk_mask = da.from_array(
                        self._appl_mk_fn_p[self._in_mask_path_in_h5]
                    )
                    if len(self._appl_mk_mask.shape) > 1:
                        update_layer_in_viewer(
                            self.viewer, self._appl_mk_mask, "appl_mk_mask"
                        )
                        show_layers_in_viewer(self.viewer, ["appl_mk_mask"])
                        self._appl_mk_data_ready = True
                    else:
                        rm_gui_viewers(self.viewer, ["appl_mk_mask"])
                        self._appl_mk_data_ready = False
                except Exception as e:
                    self.op_status.value = (
                        "Invalid file. Check terminal for error message ..."
                    )
                    print(e)
                    self.__close_file(mode="mask", kill=True)
                    self.__close_file(mode="data", kill=False)
                    self._appl_mk_data_ready = False
        else:
            if _APPL_DATA_ITEM_CHOICES:
                pass
            else:
                self.op_status.value = "No valid data items in the input file ..."
            if _APPL_MASK_ITEM_CHOICES:
                pass
            else:
                self.op_status.value = "No valid mask items in the input file ..."

    def __dflt_out_file_type(self):
        if (self._appl_mk_data is None) or (len(self._appl_mk_data.shape) <= 2):
            self.appl_mk_out_file_type.enabled = False
        else:
            self.appl_mk_out_file_type.enabled = True
        self.appl_mk_out_file_type.value = "tif"

    def __dflt_out_path(self, dflt=True):
        if dflt:
            self.appl_mk_out_dir.value = ""
        else:
            fn = Path.resolve(self.appl_mk_in_data_file.value)
            self.appl_mk_out_dir.value = str(
                fn.parent / (fn.stem + "_export") / self.appl_mk_data_avail_items.value
            )

    def __close_file(self, mode="data", kill=False):
        if mode == "data":
            rm_gui_viewers(self.viewer, ["appl_mk_data"])
        elif mode == "mask":
            rm_gui_viewers(self.viewer, ["appl_mk_mask"])
        if kill:
            if self._appl_mk_fn_p is not None:
                self._appl_mk_fn_p.close()
                self._appl_mk_fn_p = None
            self._appl_mk_data = None
            self._appl_mk_mask = None

    def __set_layers_order(self):
        if ("appl_mk_data" in self.viewer.layers) and (
            "appl_mk_mask" in self.viewer.layers
        ):
            self.viewer.layers.move_multiple(
                [
                    self.viewer.layers.index(self.viewer.layers["appl_mk_data"]),
                    self.viewer.layers.index(self.viewer.layers["appl_mk_mask"]),
                ],
                0,
            )
            self.viewer.layers["appl_mk_mask"].opacity = 0.2
            self.viewer.layers["appl_mk_mask"].colormap = "yellow"
            self.viewer.layers["appl_mk_data"].visible = True
            self.viewer.layers["appl_mk_mask"].visible = True

    def __init_widgets(self):
        global _APPL_MASK_ITEM_CHOICES
        _APPL_MASK_ITEM_CHOICES = []
        self.appl_mk_mask_avail_items.reset_choices()
        global _APPL_DATA_ITEM_CHOICES
        _APPL_DATA_ITEM_CHOICES = []
        self.appl_mk_data_avail_items.reset_choices()
        self.appl_mk_out_file_type.value = "tif"
        self.appl_mk_out_dir.value = ""
        self.appl_mk_info_board.value = ""
        self.op_status.value = ""
        for widget in self.key_widgets:
            widget.enabled = False
        self.appl_mk_in_data_file.enabled = True
        self.appl_mk_in_data_type.enabled = True

    def __reset_data_states(self):
        self._appl_mk_data_ready

    def _sel_in_data_type(self):
        self.appl_mk_in_data_file.value = "''"

    @disp_progress_info("data loading")
    def _sel_in_data_file(self):
        self.__init_widgets()
        self.__close_file(mode="data", kill=True)
        self.__close_file(mode="mask", kill=False)
        self.__reset_data_states()

        choices = check_avail_items(
            self.appl_mk_in_data_file.value, self.appl_mk_in_data_type.value
        )
        masks = [mask for mask in choices if "mk" in mask]
        datas = list(set(choices) - set(masks))
        if "eng_list" in datas:
            datas.remove("eng_list")
        global _APPL_MASK_ITEM_CHOICES
        _APPL_MASK_ITEM_CHOICES = masks
        self.appl_mk_mask_avail_items.reset_choices()
        global _APPL_DATA_ITEM_CHOICES
        _APPL_DATA_ITEM_CHOICES = datas
        self.appl_mk_data_avail_items.reset_choices()
        if _APPL_DATA_ITEM_CHOICES and _APPL_MASK_ITEM_CHOICES:
            self._appl_mk_data_ready = True
            self.__dflt_out_path(dflt=False)
        else:
            self._appl_mk_data_ready = False
            self.__dflt_out_path(dflt=True)
        self.__avail_item_slcd(mode="data")
        self.__avail_item_slcd(mode="mask")
        self.__set_layers_order()
        self.__lock_appl_mk_gui_widgets()

    def _sel_data_avail_items(self):
        self.__avail_item_slcd(mode="data")
        self.__set_layers_order()
        self.__lock_appl_mk_gui_widgets()
        self.__dflt_out_file_type()
        try:
            self.__dflt_out_path(dflt=False)
        except:
            self.__dflt_out_path(dflt=True)

    def _sel_mask_avail_items(self):
        self.__avail_item_slcd(mode="mask")
        self.__set_layers_order()
        self.__lock_appl_mk_gui_widgets()
        self.__dflt_out_file_type()
        try:
            self.__dflt_out_path(dflt=False)
        except:
            self.__dflt_out_path(dflt=True)

    @disp_progress_info("applying mask")
    def _apply(self):
        if not Path(self.appl_mk_out_dir.value).exists():
            Path(self.appl_mk_out_dir.value).mkdir(parents=True)

        if set(self._appl_mk_mask.shape).issubset(set(self._appl_mk_data.shape)):
            if "seq" in self.appl_mk_out_file_type.value:
                if "tif" in self.appl_mk_out_file_type.value:
                    out_fn_fnt = (
                        self.appl_mk_mask_avail_items.value
                        + "_masked_"
                        + self.appl_mk_data_avail_items.value
                        + "_{}.tiff"
                    )
                    fn = str(Path(self.appl_mk_out_dir.value).joinpath(out_fn_fnt))
                    tif_seq_writer(
                        fn,
                        (self._appl_mk_data * self._appl_mk_mask).compute(),
                        ids=0,
                        digit=5,
                    )
                else:
                    out_fn_fnt = (
                        self.appl_mk_mask_avail_items.value
                        + "_masked_"
                        + self.appl_mk_data_avail_items.value
                        + "_{}.raw"
                    )
                    fn = str(Path(self.appl_mk_out_dir.value).joinpath(out_fn_fnt))
                    raw_seq_writer(
                        fn,
                        (self._appl_mk_data * self._appl_mk_mask).compute(),
                        ids=0,
                        digit=5,
                    )
            else:
                if "tif" in self.appl_mk_out_file_type.value:
                    out_fn_fnt = (
                        self.appl_mk_mask_avail_items.value
                        + "_masked_"
                        + self.appl_mk_data_avail_items.value
                        + ".tiff"
                    )
                    fn = str(Path(self.appl_mk_out_dir.value).joinpath(out_fn_fnt))
                    tif_writer(fn, (self._appl_mk_data * self._appl_mk_mask).compute())
                elif "raw" in self.appl_mk_out_file_type.value:
                    out_fn_fnt = (
                        self.appl_mk_mask_avail_items.value
                        + "_masked_"
                        + self.appl_mk_data_avail_items.value
                        + ".raw"
                    )
                    fn = str(Path(self.appl_mk_out_dir.value).joinpath(out_fn_fnt))
                    raw_writer(fn, (self._appl_mk_data * self._appl_mk_mask).compute())
            self.viewer.status = "The selected mask is applited to the selected data!"
        else:
            self.viewer.status = "The selected data and mask have unmached sizes."

    def _close_file(self):
        self.__close_file(mode="data", kill=True)
        self.__close_file(mode="mask", kill=False)
        self.appl_mk_in_data_file.value = ""

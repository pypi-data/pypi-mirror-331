import numpy as np
import os

import dask.array as da
import h5py
import json
from pathlib import Path
from magicgui import widgets

from ..utils.misc import (
    check_avail_items,
    get_slcd_ds_path,
    update_layer_in_viewer,
    show_layers_in_viewer,
    rm_gui_viewers,
    disp_progress_info,
)
from silx.io.dictdump import dicttoh5

_AVAIL_DATA_ITEM_CHOICES = []


def get_xanes_avail_items_choices(ComboBox):
    global _AVAIL_DATA_ITEM_CHOICES
    return _AVAIL_DATA_ITEM_CHOICES


################################################################################
#                             XANES Analysis GUI                               #
################################################################################
class xanes_vis_gui:
    def __init__(self, viewer):
        self.viewer = viewer
        self._vis_data_ready = False
        self._vis_in_dat_type = "3D XANES"
        self._vis_data = None
        self._vis_fn_p = None
        self._mask_thsh_confirmed = False
        self._thsh_for_mask = None
        self._viewers = ["vis_data", "mask_viewer", "tomo_viewer"]

        self.label1 = widgets.Label(
            value="---------------    Visualize XANES Data    ---------------",
        )
        self.vis_in_data_type = widgets.ComboBox(
            name="data type",
            choices=["TOMO Raw", "TOMO Recon", "2D XANES", "3D XANES"],
            value="3D XANES",
            enabled=True,
        )
        self.vis_data_file = widgets.FileEdit(name="data file", mode="r", filter="*.h5")
        self.vis_avail_items = widgets.ComboBox(
            name="available items", choices=get_xanes_avail_items_choices
        )
        self.vis_rd_contr_lims = widgets.PushButton(
            text="read contrast limits", enabled=False
        )
        self.vis_data_cntrst_lowlim = widgets.LineEdit(
            name="contr low lim", value=0, enabled=False
        )
        self.vis_data_cntrst_highlim = widgets.LineEdit(
            name="contr high lim", value=0, enabled=False
        )
        self.vis_test_mask_thsh = widgets.PushButton(text="test thres", enabled=False)
        self.confirm_mask_thsh = widgets.RadioButtons(
            name="confirm thres",
            choices=["Yes", "No"],
            orientation="horizontal",
            value="No",
            tooltip="confirm if the threshold is good for making image mask",
            enabled=False,
        )
        self.excl_fit_bd = widgets.CheckBox(
            value=True, text="exclude fitting boundary", enabled=False
        )

        self.vis_mk_mask = widgets.PushButton(text="make mask", enabled=False)
        self.vis_info_board = widgets.TextEdit(
            label="data info", value="", enabled=False
        )
        self.close = widgets.PushButton(text="close", enabled=False)
        self.op_status = widgets.LineEdit(name="operation status", enabled=False)

        self.vis_in_data_type.changed.connect(self._sel_in_data_type)
        self.vis_data_file.changed.connect(self._sel_in_data_file)
        self.vis_avail_items.changed.connect(self._sel_in_avail_items)
        self.vis_rd_contr_lims.changed.connect(self._read_contr_lims)
        self.vis_test_mask_thsh.changed.connect(self._test_mask_thsh)
        self.confirm_mask_thsh.changed.connect(self._confirm_thsh)
        self.vis_mk_mask.changed.connect(self._mk_mask)
        self.close.changed.connect(self._close)

        self.gui_layout = widgets.VBox(
            widgets=[
                self.label1,
                self.vis_in_data_type,
                self.vis_data_file,
                self.vis_avail_items,
                self.vis_data_cntrst_lowlim,
                self.vis_data_cntrst_highlim,
                self.vis_rd_contr_lims,
                self.vis_test_mask_thsh,
                self.confirm_mask_thsh,
                self.excl_fit_bd,
                self.vis_mk_mask,
                self.vis_info_board,
                self.close,
                self.op_status,
            ]
        )
        self.key_widgets = [
            self.vis_avail_items,
            self.vis_data_cntrst_lowlim,
            self.vis_data_cntrst_highlim,
            self.vis_rd_contr_lims,
            self.vis_test_mask_thsh,
            self.confirm_mask_thsh,
            self.vis_mk_mask,
            self.vis_info_board,
            self.close,
            self.op_status,
        ]

    def __lock_vis_gui_widgets(self):
        if self._vis_data_ready:
            self.vis_avail_items.enabled = True
            self.vis_rd_contr_lims.enabled = True
            self.vis_data_cntrst_lowlim.enabled = False
            self.vis_data_cntrst_highlim.enabled = False
            self.vis_test_mask_thsh.enabled = True
            self.confirm_mask_thsh.enabled = True
            if self._mask_thsh_confirmed:
                self.vis_mk_mask.enabled = True
            else:
                self.vis_mk_mask.enabled = False
            self.excl_fit_bd.enabled = True
            self.close.enabled = True
            if self.vis_in_data_type.value in ["TOMO Raw", "TOMO Recon"]:
                self.vis_rd_contr_lims.enabled = False
                self.vis_test_mask_thsh.enabled = False
                self.confirm_mask_thsh.enabled = False
                self.vis_mk_mask.enabled = False
        else:
            self.vis_avail_items.enabled = False
            self.vis_rd_contr_lims.enabled = False
            self.vis_data_cntrst_lowlim.enabled = False
            self.vis_data_cntrst_highlim.enabled = False
            self.vis_test_mask_thsh.enabled = False
            self.confirm_mask_thsh.enabled = False
            self.excl_fit_bd.enabled = False
            self.vis_mk_mask.enabled = False
            self.close.enabled = False

    def __set_layers_order(self):
        if ("vis_data" in self.viewer.layers) and ("mask_viewer" in self.viewer.layers):
            self.viewer.layers.move_multiple(
                [
                    self.viewer.layers.index(self.viewer.layers["vis_data"]),
                    self.viewer.layers.index(self.viewer.layers["mask_viewer"]),
                ],
                0,
            )
            self.viewer.layers["mask_viewer"].opacity = 0.2
            self.viewer.layers["mask_viewer"].colormap = "yellow"

    def __avail_item_slcd(self):
        if self._vis_data_ready:
            self.__close_file()
            if self.vis_in_data_type.value == "TOMO Recon":
                try:
                    update_layer_in_viewer(self.viewer, self.vis_data_file.value, 
                                        "vis_data", data_type="folder")
                    if self.viewer.layers["vis_data"].ndim == 3:
                        show_layers_in_viewer(self.viewer, ["vis_data"])
                        self._vis_data_ready = True
                    else:
                        rm_gui_viewers(self.viewer, self._viewers)
                        self._vis_data_ready = False
                        self.viewer.status = "No reconstructed tiff files in the selected folder"
                        print("No reconstructed tiff files in the selected folder")
                except Exception as e:
                    self.viewer.status = "Something wrong happened during openning data file. Please check the terminal for more information."
                    print(str(e))
                    self.__close_file()
                    self._vis_data_ready = False
            else:
                (self._in_dat_path_in_h5, _in_dat_desc, _in_dat_dtype) = get_slcd_ds_path(
                    self.vis_data_file.value,
                    self.vis_in_data_type.value,
                    self.vis_avail_items.value,
                )
                try:
                    self._vis_fn_p = h5py.File(self.vis_data_file.value, "a")
                    
                    self._in_dat_item_sz = self._vis_fn_p[self._in_dat_path_in_h5].shape
                    self.vis_info_board.value = (
                        _in_dat_desc
                        + f"\nshape: {self._in_dat_item_sz}"
                        + f"\ndtype: {_in_dat_dtype}"
                    )
                    
                    self._vis_data = da.from_array(self._vis_fn_p[self._in_dat_path_in_h5])
                    if len(self._vis_data.shape) > 1:
                        update_layer_in_viewer(self.viewer, self._vis_data, "vis_data", data_type="image")
                        show_layers_in_viewer(self.viewer, ["vis_data"])
                        self._vis_data_ready = True
                    elif len(self._vis_data.shape) == 1:
                        rm_gui_viewers(self.viewer, self._viewers)
                        self._vis_data_ready = True
                    else:
                        rm_gui_viewers(self.viewer, self._viewers)
                        self._vis_data_ready = False
                except Exception as e:
                    self.viewer.status = "Something wrong happened during openning data file. Please check the terminal for more information."
                    print(str(e))
                    self.__close_file()
                    self._vis_data_ready = False

    def __init_widgets(self):
        global _AVAIL_DATA_ITEM_CHOICES
        _AVAIL_DATA_ITEM_CHOICES = []
        self.vis_avail_items.reset_choices()
        self.vis_data_cntrst_lowlim.value = ""
        self.vis_data_cntrst_highlim.value = ""
        self.confirm_mask_thsh.value = "No"
        self.vis_info_board.value = ""
        self.op_status.value = ""
        for widget in self.key_widgets:
            widget.enabled = False
        self.vis_in_data_type.enabled = True
        self.vis_data_file.enabled = True

    def __reset_data_states(self):
        self._vis_data_ready = False
        self._vis_data = None
        self._thsh_for_mask = None

    def __reset_run_states(self):
        self._mask_thsh_confirmed = False

    def __close_file(self):
        if self._vis_fn_p is not None:
            self._vis_fn_p.close()
            self._vis_fn_p = None
            rm_gui_viewers(self.viewer, self._viewers)

    def _sel_in_data_type(self):
        self.vis_data_file.value = "''"
        if self.vis_in_data_type.value == "TOMO Recon":
            self.vis_data_file.mode = "d"
        else:
            self.vis_data_file.mode = "r"
            self.vis_data_file.filter="*.h5"

    @disp_progress_info("data loading")
    def _sel_in_data_file(self):
        self.__reset_run_states()
        self.__reset_data_states()
        self.__close_file()
        self.__init_widgets()
        choices = check_avail_items(
            self.vis_data_file.value, self.vis_in_data_type.value
        )
        global _AVAIL_DATA_ITEM_CHOICES
        _AVAIL_DATA_ITEM_CHOICES = choices
        self.vis_avail_items.reset_choices()
        if _AVAIL_DATA_ITEM_CHOICES:
            self._vis_data_ready = True
        else:
            self._vis_data_ready = False
        self.__avail_item_slcd()
        self.__lock_vis_gui_widgets()

    def _sel_in_avail_items(self):
        self.__avail_item_slcd()
        self.__lock_vis_gui_widgets()

    def _read_contr_lims(self):
        self.vis_data_cntrst_lowlim.value = self.viewer.layers[
            "vis_data"
        ].contrast_limits[0]
        self.vis_data_cntrst_highlim.value = 1e30

    @disp_progress_info("mask making")
    def _mk_mask(self):
        if self._thsh_for_mask is None:
            self.viewer.status = "No threshold for making mask is confirmed yet."
            print("No threshold for making mask is confirmed yet.")
        else:
            if self.vis_in_data_type.value in ["TOMO Raw", "TOMO Recon"]:
                self.viewer.status = (
                    "Making mask operation is not applicable to Tomo Raw and Tomo Recon data."
                )
                print("Making mask operation is not applicable to Tomo Raw and Tomo Recon data.")
            elif self.vis_in_data_type.value == "2D XANES":
                if "processed_XANES2D" in self._vis_fn_p:
                    if "gen_masks" in self._vis_fn_p["processed_XANES2D"].keys():
                        del self._vis_fn_p["processed_XANES2D/gen_masks"]
                    gm0 = self._vis_fn_p["processed_XANES2D"].create_group("gen_masks")
                    _out_path_in_h5 = "processed_XANES2D/gen_masks"
                else:
                    if "gen_masks" in self._vis_fn_p["processed_XANES"].keys():
                        del self._vis_fn_p["processed_XANES/gen_masks"]
                    gm0 = self._vis_fn_p["processed_XANES"].create_group("gen_masks")
                    _out_path_in_h5 = "processed_XANES/gen_masks"
                mask_name = f"mk00_{self.vis_avail_items.value}"
                gm1 = gm0.create_group(mask_name)
                if self.excl_fit_bd.value:
                    (_wl_fit_path_in_h5, _, _) = get_slcd_ds_path(
                        self.vis_data_file.value,
                        self.vis_in_data_type.value,
                        "wl_pos_fit",
                    )
                    wl_fit = da.from_array(self._vis_fn_p[_wl_fit_path_in_h5])
                    wl_hb = self._vis_fn_p[
                        "/processed_XANES/proc_parameters/wl_fit_eng_e"
                    ][()]
                    wl_lb = self._vis_fn_p[
                        "/processed_XANES/proc_parameters/wl_fit_eng_s"
                    ][()]
                    gm1.create_dataset(
                        mask_name,
                        data=(
                            (self._vis_data > self._thsh_for_mask[0])
                            & (self._vis_data < self._thsh_for_mask[1])
                            & (wl_fit > (wl_lb + 1e-6))
                            & (wl_fit < (wl_hb - 1e-6))
                        )
                        .compute()
                        .astype(np.int8),
                        dtype=np.int8,
                    )
                else:
                    gm1.create_dataset(
                        mask_name,
                        data=(
                            (self._vis_data > self._thsh_for_mask[0])
                            & (self._vis_data < self._thsh_for_mask[1])
                        )
                        .compute()
                        .astype(np.int8),
                        dtype=np.int8,
                    )
                dicttoh5(
                    {
                        "op": {
                            "var_name": self.vis_avail_items.value,
                            "0": {
                                "flt_name": "Threshold",
                                "pars": {
                                    "lower": self._thsh_for_mask[0],
                                    "upper": self._thsh_for_mask[1],
                                },
                            },
                        }
                    },
                    self._vis_fn_p,
                    update_mode="replace",
                    h5path=f"{_out_path_in_h5}/{mask_name}/source",
                )
            elif self.vis_in_data_type.value == "3D XANES":
                if "processed_XANES3D" in self._vis_fn_p:
                    if "gen_masks" in self._vis_fn_p["processed_XANES3D"].keys():
                        del self._vis_fn_p["processed_XANES3D/gen_masks"]
                    gm0 = self._vis_fn_p["processed_XANES3D"].create_group("gen_masks")
                    _out_path_in_h5 = "processed_XANES3D/gen_masks"
                else:
                    if "gen_masks" in self._vis_fn_p["processed_XANES"].keys():
                        del self._vis_fn_p["processed_XANES/gen_masks"]
                    gm0 = self._vis_fn_p["processed_XANES"].create_group("gen_masks")
                    _out_path_in_h5 = "processed_XANES/gen_masks"
                mask_name = f"mk00_{self.vis_avail_items.value}"
                gm1 = gm0.create_group(mask_name)
                if self.excl_fit_bd.value:
                    (_wl_fit_path_in_h5, _, _) = get_slcd_ds_path(
                        self.vis_data_file.value,
                        self.vis_in_data_type.value,
                        "wl_pos_fit",
                    )
                    wl_fit = da.from_array(self._vis_fn_p[_wl_fit_path_in_h5])
                    wl_hb = self._vis_fn_p[
                        "/processed_XANES/proc_parameters/wl_fit_eng_e"
                    ][()]
                    wl_lb = self._vis_fn_p[
                        "/processed_XANES/proc_parameters/wl_fit_eng_s"
                    ][()]
                    gm1.create_dataset(
                        mask_name,
                        data=(
                            (self._vis_data > self._thsh_for_mask[0])
                            & (self._vis_data < self._thsh_for_mask[1])
                            & (wl_fit > (wl_lb + 1e-6))
                            & (wl_fit < (wl_hb - 1e-6))
                        )
                        .compute()
                        .astype(np.int8),
                        dtype=np.int8,
                    )
                else:
                    gm1.create_dataset(
                        mask_name,
                        data=(
                            (self._vis_data > self._thsh_for_mask[0])
                            & (self._vis_data < self._thsh_for_mask[1])
                        )
                        .compute()
                        .astype(np.int8),
                        dtype=np.int8,
                    )
                dicttoh5(
                    {
                        "op": {
                            "var_name": self.vis_avail_items.value,
                            "0": {
                                "flt_name": "Threshold",
                                "pars": {
                                    "lower": self._thsh_for_mask[0],
                                    "upper": self._thsh_for_mask[1],
                                },
                            },
                        }
                    },
                    self._vis_fn_p,
                    update_mode="replace",
                    h5path=f"{_out_path_in_h5}/{mask_name}/source",
                )
            rm_gui_viewers(self.viewer, ["mask_viewer"])
            self._vis_data_mask = da.from_array(
                self._vis_fn_p[f"{_out_path_in_h5}/{mask_name}/{mask_name}"]
            )
            update_layer_in_viewer(self.viewer, self._vis_data_mask, "mask_viewer", data_type="image")
            show_layers_in_viewer(self.viewer, ["vis_data", "mask_viewer"])
            self.__set_layers_order()

    def _test_mask_thsh(self):
        self._read_contr_lims()

        if self.vis_in_data_type.value in ["TOMO Raw", "TOMO Recon"]:
            self.viewer.status = (
                "Making mask operation is not applicable to Tomo Raw and Tomo Recondata."
            )
            print("Making mask operation is not applicable to Tomo Raw and Tomo Recon data.")
        elif self.vis_in_data_type.value == "2D XANES":
            thshed_img = (
                (
                    (self._vis_data > float(self.vis_data_cntrst_lowlim.value))
                    & (self._vis_data < float(self.vis_data_cntrst_highlim.value))
                )
                .compute()
                .astype(np.int8)
            )

        elif self.vis_in_data_type.value == "3D XANES":
            thshed_img = (
                (
                    (
                        self._vis_data[*self.viewer.dims.current_step[:-2], ...]
                        > float(self.vis_data_cntrst_lowlim.value)
                    )
                    & (
                        self._vis_data[*self.viewer.dims.current_step[:-2], ...]
                        < float(self.vis_data_cntrst_highlim.value)
                    )
                )
                .compute()
                .astype(np.int8)
            )

        rm_gui_viewers(self.viewer, ["mask_viewer"])
        update_layer_in_viewer(self.viewer, thshed_img, "mask_viewer", data_type="image")
        show_layers_in_viewer(self.viewer, ["vis_data", "mask_viewer"])
        self.__set_layers_order()

    def _confirm_thsh(self):
        self._mask_thsh_confirmed = (
            True if self.confirm_mask_thsh.value == "Yes" else False
        )
        if self._mask_thsh_confirmed:
            self.vis_mk_mask.enabled = True
            self._thsh_for_mask = [
                float(self.vis_data_cntrst_lowlim.value),
                float(self.vis_data_cntrst_highlim.value),
            ]
        else:
            self.vis_mk_mask.enabled = False
            self._thsh_for_mask = None

    def _close(self):
        self.vis_data_file.value = "''"

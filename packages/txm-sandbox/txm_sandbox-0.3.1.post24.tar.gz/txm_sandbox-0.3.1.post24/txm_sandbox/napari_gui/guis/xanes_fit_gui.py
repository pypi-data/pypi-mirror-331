import numpy as np
import os

import dask.array as da
import h5py
import json
from pathlib import Path
import matplotlib.pyplot as plt
from magicgui import widgets
from copy import deepcopy

from ...gui.gui_components import (
    determine_element,
    determine_fitting_energy_range,
    scale_eng_list,
    def_dflt_eng_rgn,
)
from ...utils.misc import sort_xanes_ref_by_name
from ...utils.io import create_hdf5_from_json
from ..utils.misc import (
    set_data_widget,
    overlap_roi,
    update_layer_in_viewer,
    show_layers_in_viewer,
    rm_gui_viewers,
    disp_progress_info,
)

from ..utils.ext_io_lib import lcf_cfg_gui


cfg_fn = Path(__file__).parents[1] / "configs/txm_simple_gui_script_cfg.json"
xanes3d_fit_script_fn = Path(__file__).parents[1] / "scripts/xanes3D_fit_cmd.py"
xanes2d_fit_script_fn = Path(__file__).parents[1] / "scripts/xanes2D_fit_cmd.py"
diff_imaging_script_fn = Path(__file__).parents[1] / "scripts/diff_imaging_cmd.py"

with open(Path(__file__).parents[1] / "configs/xanes_proc_data_struct_cfg.json") as f:
    xanes_proc_data_struct = json.load(f)

with open(Path(__file__).parents[1] / "configs/diff_imaging_proc_data_struct_cfg.json") as f:
    diff_imaging_proc_data_struct = json.load(f)


_XANES_FIT_SAVE_ITEMS_CHOICES = []


def get_xanes_fit_save_items_choices(ComboBox):
    global _XANES_FIT_SAVE_ITEMS_CHOICES
    return _XANES_FIT_SAVE_ITEMS_CHOICES


################################################################################
#                             XANES Analysis GUI                               #
################################################################################
class xanes_fit_gui:
    def __init__(self, viewer):
        self.viewer = viewer
        self._reg_done = False
        self._spec_in_roi_fig = None
        self._elem = None
        self._xanes_data = None
        self._xanes_data_fn_p = None
        self._xanes_type = None
        self._lcf_ref_dict = {}
        self._lcf_ref_spec_set = False
        self._diff_img_idx = []
        self._viewers = ["xanes_data", "xanes_spec_roi", "tomo_viewer"]

        self._anal_type_dict = {"2D XANES": "xanes2D", "3D XANES": "xanes3D"}

        self.label0 = widgets.Label(
            value="------------------     XANES Fitting    ------------------",
        )
        self.label1 = widgets.Label(
            name="Step 1",
            value="-----------------     XANES Data Type    -----------------",
        )
        self.data_type = widgets.ComboBox(
            choices=["2D XANES", "3D XANES"],
            value="3D XANES",
            enabled=True,
            name="data type",
        )
        self.ana_type = widgets.ComboBox(
            name="data ana Type",
            choices=["XANES", "Differential-Imaging"],
            value="XANES",
            tooltip="XANES: 2D/3D XANES fitting; Differential-Imaging: 2D/3D Differential Imaging; requires two and only two images",
            enabled=True,
        )
        self.label2 = widgets.Label(
            name="Step 2",
            value="---------------     Visualize XANES Reg    ---------------",
        )
        self.xanes_file = widgets.FileEdit(mode="r", filter="*.h5", name="xanes file")
        self.reload = widgets.PushButton(
            text="reload registered data", enabled=False,
            tooltip="reload the registered xanes data for fitting in a different ROI"
        )
        self.eng_eV = widgets.LineEdit(value="", enabled=False, label="eng (eV)")
        self.sli = widgets.Slider(enabled=False, name="sli")
        self.E = widgets.Slider(enabled=False, name="E")
        self.spec_in_roi = widgets.CheckBox(
            value=False, text="spec in roi", enabled=False
        )
        self.roi_cen_x = widgets.Slider(enabled=False, tracking=False, name="roi cen x")
        self.roi_cen_y = widgets.Slider(enabled=False, tracking=False, name="roi cen y")
        self.def_fit_range = widgets.PushButton(
            text="def fit energy range", enabled=False
        )
        self.label3 = widgets.Label(
            name="Step 3",
            value="------------------     XANES Fitting    ------------------",
        )
        self.element = widgets.Label(value="")
        self.xanes_fit_type = widgets.ComboBox(
            choices=["normalized spectra - wl", "raw spectra - wl", "normalized spectra - lcf"], value="raw spectra - wl", enabled=False, name="fit type"
        )
        self.edge_eng = widgets.LineEdit(enabled=False, label="edge eng")
        self.wl_s = widgets.LineEdit(enabled=False, label="wl s eng")
        self.wl_e = widgets.LineEdit(enabled=False, label="wl e eng")
        self.edge_s = widgets.LineEdit(enabled=False, label="edge eng s")
        self.edge_e = widgets.LineEdit(enabled=False, label="edge eng e")
        self.downsample_factor = widgets.SpinBox(
            min=1, max=10, value=1, enabled=False, name="ds fac"
        )
        self.save_items = widgets.Select(
            choices=get_xanes_fit_save_items_choices, name="save items"
        )
        self.fit = widgets.PushButton(text="fit", enabled=False)
        self.close = widgets.PushButton(text="close", enabled=False)
        self.op_status = widgets.LineEdit(name="operation status", enabled=False)

        self.data_type.changed.connect(self._sel_in_data_type)
        self.xanes_file.changed.connect(self._sel_xanes_file)
        self.reload.changed.connect(self._reload_xanes_data)
        self.ana_type.changed.connect(self._sel_anal_type)
        self.sli.changed.connect(self._vis_sli_chgd)
        self.E.changed.connect(self._vis_E_chgd)
        self.spec_in_roi.changed.connect(self._spec_in_roi_chkd)
        self.roi_cen_x.changed.connect(self._spec_roi_cen_x_chgd)
        self.roi_cen_y.changed.connect(self._spec_roi_cen_y_chgd)
        self.def_fit_range.changed.connect(self._def_fit_eng_rgn)
        self.xanes_fit_type.changed.connect(self._xanes_fit_type_chgd)
        self.save_items.changed.connect(self._save_items_chgd)
        self.fit.changed.connect(self._xanes_fit)
        self.close.changed.connect(self._close)

        self.gui_layout = widgets.VBox(
            widgets=[
                self.label0,
                self.label1,
                self.data_type,
                self.ana_type,
                self.label2,
                self.xanes_file,
                self.reload,
                self.eng_eV,
                self.sli,
                self.E,
                self.spec_in_roi,
                self.roi_cen_x,
                self.roi_cen_y,
                self.def_fit_range,
                self.label3,
                self.element,
                self.xanes_fit_type,
                self.edge_eng,
                self.wl_s,
                self.wl_e,
                self.edge_s,
                self.edge_e,
                self.downsample_factor,
                self.save_items,
                self.fit,
                self.close,
                self.op_status,
            ]
        )
        self.key_widgets = [
            self.reload,
            self.eng_eV,
            self.sli,
            self.E,
            self.spec_in_roi,
            self.roi_cen_x,
            self.roi_cen_y,
            self.def_fit_range,
            self.element,
            self.xanes_fit_type,
            self.edge_eng,
            self.wl_s,
            self.wl_e,
            self.edge_s,
            self.edge_e,
            self.downsample_factor,
            self.save_items,
            self.fit,
            self.close,
            self.op_status,
        ]

    def __xanes_gui_widgets_logic(self):
        if self._reg_done:
            self.E.enabled = True
            self.reload.enabled = True

            if self.ana_type.value == "XANES":
                if self._elem is not None:
                    self.spec_in_roi.enabled = True
                    if self.spec_in_roi.value:
                        self.roi_cen_x.enabled = True
                        self.roi_cen_y.enabled = True
                    else:
                        self.roi_cen_x.enabled = False
                        self.roi_cen_y.enabled = False
                    self.def_fit_range.enabled = True

                    if self._xanes_type == "2D XANES":
                        self.sli.enabled = False
                    else:
                        self.sli.enabled = True

                    if self.xanes_fit_type.value == "raw spectra - wl":
                        self.edge_eng.enabled = False
                        self.edge_s.enabled = False
                        self.edge_e.enabled = False
                    else:
                        self.edge_eng.enabled = True
                        self.edge_s.enabled = True
                        self.edge_e.enabled = True
                    self.xanes_fit_type.enabled = True
                    self.wl_s.enabled = True
                    self.wl_e.enabled = True
                    self.downsample_factor.enabled = True
                    self.fit.enabled = True
                    self.enabled = True
                else:
                    self.enabled = False
            elif self.ana_type.value == "Differential-Imaging":
                if len(self._diff_img_idx) < 2:
                    self.fit.enabled = False  
                elif len(self._diff_img_idx) == 2:
                    self.fit.enabled = True
            
                self.def_fit_range.enabled = True
                self.spec_in_roi.enabled = True
                if self.spec_in_roi.value:
                    self.roi_cen_x.enabled = True
                    self.roi_cen_y.enabled = True
                else:
                    self.roi_cen_x.enabled = False
                    self.roi_cen_y.enabled = False
                    
                if self._xanes_type == "2D XANES":
                    self.sli.enabled = False
                else:
                    self.sli.enabled = True
                self.downsample_factor.enabled = True
            self.close.enabled = True                
        else:
            self.enabled = False
        self.data_type.enabled = True
        self.xanes_file.enabled = True
        self.ana_type.enabled = True

    def __set_xanes_gui_widgets(self):
        if self._reg_done:
            if self._xanes_type == "2D XANES":
                set_data_widget(self.E, 0, 0, self._xanes_data_dim[0] - 1)
                set_data_widget(self.sli, 0, 0, 0)
                set_data_widget(
                    self.roi_cen_x,
                    10,
                    int(self._xanes_data_dim[2] / 2),
                    self._xanes_data_dim[2] - 10,
                )
                set_data_widget(
                    self.roi_cen_y,
                    10,
                    int(self._xanes_data_dim[1] / 2),
                    self._xanes_data_dim[1] - 10,
                )
            elif self._xanes_type == "3D XANES":
                set_data_widget(self.E, 0, 0, self._xanes_data_dim[0] - 1)
                set_data_widget(self.sli, 0, 0, self._xanes_data_dim[1] - 1)
                set_data_widget(
                    self.roi_cen_x,
                    10,
                    int(self._xanes_data_dim[3] / 2),
                    self._xanes_data_dim[3] - 10,
                )
                set_data_widget(
                    self.roi_cen_y,
                    10,
                    int(self._xanes_data_dim[2] / 2),
                    self._xanes_data_dim[2] - 10,
                )

            if self.ana_type.value == "XANES":
                self._elem = determine_element(self._eng_lst)
                if self._elem is not None:
                    self.element.value = self._elem
                    (
                        edge_eng,
                        wl_fit_eng_s,
                        wl_fit_eng_e,
                        _,
                        _,
                        edge_0p5_fit_s,
                        edge_0p5_fit_e,
                    ) = determine_fitting_energy_range(self.element.value)
                    self.edge_eng.value = edge_eng
                    self.wl_s.value = wl_fit_eng_s
                    self.wl_e.value = wl_fit_eng_e
                    self.edge_s.value = edge_0p5_fit_s
                    self.edge_e.value = edge_0p5_fit_e
                    self.xanes_fit_type.value = "normalized spectra - wl"
                    self.xanes_fit_type.value = "raw spectra - wl"
                else:
                    self.edge_eng.value = ''
                    self.wl_s.value = ''
                    self.wl_e.value = ''
                    self.edge_s.value = ''
                    self.edge_e.value = ''

    def __vis_xanes_data(self):
        if self._reg_done:
            if self.data_type.value == "2D XANES":
                self.viewer.dims.set_point(
                    axis=[
                        0,
                    ],
                    value=[
                        self.E.value,
                    ],
                )
            else:
                self.viewer.dims.set_point(
                    axis=[0, 1], value=[self.E.value, self.sli.value]
                )

    def __plot_spec_in_roi(self):
        if self.data_type.value == "2D XANES":
            self._spec_in_roi = self._xanes_data[
                :,
                self.roi_cen_y.value - 5 : self.roi_cen_y.value + 5,
                self.roi_cen_x.value - 5 : self.roi_cen_x.value + 5,
            ].squeeze().mean(axis=(1, 2))
        else:
            self._spec_in_roi = self._xanes_data[
                :,
                self.sli.value,
                self.roi_cen_y.value - 5 : self.roi_cen_y.value + 5,
                self.roi_cen_x.value - 5 : self.roi_cen_x.value + 5,
            ].squeeze().mean(axis=(1, 2))
        if self._spec_in_roi_fig is not None:
            plt.close(self._spec_in_roi_fig)
        self._spec_in_roi_fig, ax = plt.subplots()
        ax.plot(self._eng_lst, self._spec_in_roi)
        ax.set_title("spec in roi")
        plt.show()

    def __set_xanes_ana_type(self):
        if (self._eng_lst.min() > (float(self.edge_eng.value) - 50)) and (
            self._eng_lst.max() < (float(self.edge_eng.value) + 50)
        ):
            self.xanes_fit_type.value = "raw spectra - wl"

    def __init_widgets(self):
        self.eng_eV.value = ""
        self.sli.value = 0
        self.E.value = 0
        self.spec_in_roi.value = False
        self.roi_cen_x.value = self.roi_cen_x.min
        self.roi_cen_y.value = self.roi_cen_y.min
        self.element.value = ""
        self.xanes_fit_type.value = "raw spectra - wl"
        self.edge_eng.value = ""
        self.wl_s.value = ""
        self.wl_e.value = ""
        self.edge_s.value = ""
        self.edge_e.value = ""
        self.downsample_factor.value = 1
        global _XANES_FIT_SAVE_ITEMS_CHOICES
        _XANES_FIT_SAVE_ITEMS_CHOICES = []
        self.save_items.reset_choices()
        self.op_status.value = ""
        for widget in self.key_widgets:
            widget.enabled = False
        self.data_type.enabled = True
        self.xanes_file.enabled = True

    def __reset_run_states(self):
        self._reg_done = False
        self._lcf_ref_spec_set = False

    def __reset_data_states(self):
        self._elem = None
        self._xanes_data = None
        self._diff_img_idx = []
        self._lcf_ref_dict = {}

    def __close_file(self):
        if self._spec_in_roi_fig is not None:
            plt.close(self._spec_in_roi_fig)
            self._spec_in_roi_fig = None
        if self._xanes_data_fn_p is not None:
            self._xanes_data_fn_p.close()
            self._xanes_data_fn_p = None

    def __reset_gui(self):
        rm_gui_viewers(self.viewer, self._viewers)
        self.__reset_run_states()
        self.__init_widgets()
        self.__close_file()
        self.__reset_data_states()

    def _sel_in_data_type(self):
        self.xanes_file.value = "''"

    @disp_progress_info("registered image data loading")
    def _sel_xanes_file(self):
        self.__reset_gui()

        if not Path(self.xanes_file.value).is_file():
            self._reg_done = False
        else:
            self.op_status.value = "doing data loading ..."
            try:
                with h5py.File(self.xanes_file.value, "r") as f:
                    if (
                        f"/registration_results/reg_results/registered_{self._anal_type_dict[self.data_type.value]}"
                        in f
                    ):
                        self._reg_done = True
                        self._xanes_type = self.data_type.value
                        self._xanes_data_fn = self.xanes_file.value
                        self._xanes_data_dim = f[
                            f"/registration_results/reg_results/registered_{self._anal_type_dict[self.data_type.value]}"
                        ].shape
                        self._eng_lst = scale_eng_list(
                            f["/registration_results/reg_results/eng_list"][:]
                        )
                    else:
                        self._reg_done = False
                        self._xanes_type = None
                        self._xanes_data_fn = None
                        self._xanes_data = None
                        self._xanes_data_dim = None
                        self._eng_lst = None
            except Exception as e:
                self.op_status.value = "Invalid file!"
                self._reg_done = False
                self._xanes_type = None
                self._xanes_data_fn = None
                self._xanes_data = None
                self._xanes_data_dim = None
                self._eng_lst = None
                print(e)
            if self._reg_done:
                rm_gui_viewers(self.viewer, ["xanes_data"])
                try:
                    self._xanes_data_fn_p = h5py.File(self._xanes_data_fn, "r")
                    self._xanes_data = da.from_array(
                        self._xanes_data_fn_p[
                            f"/registration_results/reg_results/registered_{self._anal_type_dict[self.data_type.value]}"
                        ]
                    )
                    update_layer_in_viewer(self.viewer, self._xanes_data, "xanes_data")
                    show_layers_in_viewer(self.viewer, ["xanes_data"])
                    self.op_status.value = "data loading finished ..."
                except Exception as e:
                    self.op_status.value = (
                        "Something is wrong. Please check terminal for more information."
                    )
                    print(str(e))
                    self._xanes_data_fn_p = None
                    self._xanes_data = None

            self._spec_in_roi = None
            self.__set_xanes_gui_widgets()
            self.__vis_xanes_data()
        self.__xanes_gui_widgets_logic()

    def _sel_anal_type(self):
        self.__reset_gui()
        if self.ana_type.value == "Differential-Imaging":
            self.def_fit_range.text = "pick differential images"
            self.xanes_fit_type.name = ""
            self.edge_eng.label = ""
            self.wl_s.label = "diff1 eng"
            self.wl_e.label = "diff2 eng"
            self.edge_s.label = ""
            self.edge_e.label = ""
            self.save_items.name = ""
            self.fit.text = "calc diff image"
        elif self.ana_type.value == "XANES":
            self.def_fit_range.text = "def fit energy range"
            self.xanes_fit_type.name = "fit type"
            self.edge_eng.label = "edge eng"
            self.wl_s.label = "wl s eng"
            self.wl_e.label = "wl e eng"
            self.edge_s.label = "edge s eng"
            self.edge_e.label = "edge e eng"
            self.save_items.name = "save items"
            self.fit.text = "fit"

    @disp_progress_info("registered image data reloading")
    def _reload_xanes_data(self):
        if self._xanes_data_fn_p is None:
            self._sel_xanes_file()

    def _vis_sli_chgd(self):
        if self._reg_done:
            self.__vis_xanes_data()

    def _vis_E_chgd(self):
        if self._reg_done:
            self.eng_eV.value = str(self._eng_lst[self.E.value])
            self.__vis_xanes_data()

    def _spec_in_roi_chkd(self):
        if self.spec_in_roi.value:
            self.roi_cen_x.enabled = True
            self.roi_cen_y.enabled = True
            self.def_fit_range.enabled = True
        else:
            self.roi_cen_x.enabled = False
            self.roi_cen_y.enabled = False
            self.def_fit_range.enabled = False
            if self._spec_in_roi_fig is not None:
                plt.close(self._spec_in_roi_fig)

    def _spec_roi_cen_x_chgd(self):
        if not self._reg_done:
            return
        if self._xanes_data_fn_p is None:
            self._xanes_data_fn_p = h5py.File(self._xanes_data_fn, "r")
            self._xanes_data = da.from_array(
                        self._xanes_data_fn_p[
                            f"/registration_results/reg_results/registered_{self._anal_type_dict[self.data_type.value]}"
                        ]
                    )
        overlap_roi(self.viewer, self, mode="xanes_spec_roi")
        self.__plot_spec_in_roi()

    def _spec_roi_cen_y_chgd(self):
        if not self._reg_done:
            return
        if self._xanes_data_fn_p is None:
            self._xanes_data_fn_p = h5py.File(self._xanes_data_fn, "r")
            self._xanes_data = da.from_array(
                        self._xanes_data_fn_p[
                            f"/registration_results/reg_results/registered_{self._anal_type_dict[self.data_type.value]}"
                        ]
                    )
        overlap_roi(self.viewer, self, mode="xanes_spec_roi")
        self.__plot_spec_in_roi()

    def _def_fit_eng_rgn(self):
        if self.ana_type.value == "Differential-Imaging":
            if len(self._diff_img_idx) == 0:
                self._diff_img_idx.append(self.E.value)
                self.wl_s.value = self._eng_lst[self._diff_img_idx[0]]
            elif len(self._diff_img_idx) == 1:
                if self.E.value in self._diff_img_idx:
                    self.op_status.value = "please select a different image for differential imaging."
                else:
                    self._diff_img_idx.append(self.E.value)
                    self.wl_s.value = self._eng_lst[self._diff_img_idx[0]]
                    self.wl_e.value = self._eng_lst[self._diff_img_idx[1]]
            elif len(self._diff_img_idx) == 2:
                if self.E.value in self._diff_img_idx:
                    self.op_status.value = f"image at {self._eng_lst[self.E.value]}keV has already been selected."
                else:
                    self._diff_img_idx.pop(0)
                    self._diff_img_idx.append(self.E.value)
                    self.wl_s.value = self._eng_lst[self._diff_img_idx[0]]
                    self.wl_e.value = self._eng_lst[self._diff_img_idx[1]]
            if len(self._diff_img_idx) == 2:
                self.fit.enabled = True
        elif self.ana_type.value == "XANES":
            (wl_eng, wl_fit_s, wl_fit_e, edge_fit_s, edge_fit_e, edge_eng, fit_type) = (
                def_dflt_eng_rgn(self._spec_in_roi, self._eng_lst)
            )
            if fit_type == "wl":
                self.xanes_fit_type.value = "raw spectra - wl"
            elif fit_type == "full":
                self.xanes_fit_type.value = "normalized spectra - wl"

            self.edge_eng.value = edge_eng
            self.wl_s.value = wl_fit_s
            self.wl_e.value = wl_fit_e
            self.edge_s.value = edge_fit_s
            self.edge_e.value = edge_fit_e

    def _xanes_fit_type_chgd(self):
        self.__set_xanes_ana_type()
        self.wl_s.enabled = True
        self.wl_e.enabled = True
        global _XANES_FIT_SAVE_ITEMS_CHOICES
        if self.xanes_fit_type.value == "raw spectra - wl":
            self.edge_eng.enabled = False
            self.edge_s.enabled = False
            self.edge_e.enabled = False
            _XANES_FIT_SAVE_ITEMS_CHOICES = [
                "wl_pos_fit",
                "weighted_attenuation",
                "wl_fit_err",
            ]
            self.save_items.reset_choices()
            self.save_items.value = [
                "wl_pos_fit",
                "weighted_attenuation",
            ]
        elif self.xanes_fit_type.value == "normalized spectra - wl":
            self.edge_eng.enabled = True
            self.edge_s.enabled = True
            self.edge_e.enabled = True
            _XANES_FIT_SAVE_ITEMS_CHOICES = [
                "wl_pos_fit",
                "edge_pos_fit",
                "edge50_pos_fit",
                "weighted_attenuation",
                "wl_fit_err",
                "edge_fit_err",
            ]
            self.save_items.reset_choices()
            self.save_items.value = [
                "wl_pos_fit",
                "edge_pos_fit",
                "edge50_pos_fit",
                "weighted_attenuation",
            ]
        elif self.xanes_fit_type.value == "normalized spectra - lcf":
            ans = lcf_cfg_gui(self)
            if ans.rtn and len(list(ans._ref_spectra.keys())) != 0:
                ready = 1            
                for key in ans._ref_spectra.keys():
                    plt.close(ans._ref_spectra[key]["mu_plot"])
                    plt.close(ans._ref_spectra[key]["chi_plot"])
                    if "chi_ref" in ans._ref_spectra[key]["data"].columns:
                        ready *= 1
                    else:
                        ready *= 0
                if ready == 1:
                    self._lcf_ref_dict = ans._ref_spectra
                    for key in self._lcf_ref_dict.keys():
                        self._lcf_ref_dict[key]["mu_plot"] = None
                        self._lcf_ref_dict[key]["chi_plot"] = None
                        self._lcf_ref_dict[key]["chi_plot_ax"] = None
                        self._lcf_ref_dict[key]["file_path"] = str(
                            self._lcf_ref_dict[key]["file_path"]
                        )
                    self._lcf_ref_spec_set = True
                    self.edge_eng.enabled = True
                    self.edge_s.enabled = True
                    self.edge_e.enabled = True
                    _XANES_FIT_SAVE_ITEMS_CHOICES = [
                        "lcf_fit",
                        "lcf_fit_err",
                        "wl_pos_fit",
                        "edge_pos_fit",
                        "edge50_pos_fit",
                        "weighted_attenuation",
                        "wl_fit_err",
                        "edge_fit_err",
                    ]
                    self.save_items.reset_choices()
                    self.save_items.value = [
                        "wl_pos_fit",
                        "lcf_fit",
                        "weighted_attenuation",
                    ]
                else:
                    self._lcf_ref_dict = {}
                    self._lcf_ref_spec_set = False

    def _save_items_chgd(self):
        if (self.xanes_fit_type.value == "normalized spectra - lcf"):
            if "lcf_fit" not in self.save_items.value:
                self.save_items.value = list(self.save_items.value).append("lcf_fit")
                        
    @disp_progress_info("data fitting")
    def _xanes_fit(self):
        self.__close_file()

        with open(cfg_fn, "r") as f:
            tem = json.load(f)
            if self.ana_type.value == "XANES":
                if self.data_type.value == "3D XANES":
                    tem["xanes3d_fit"]["cfg_file"] = str(self._xanes_data_fn)
                elif self.data_type.value == "2D XANES":
                    tem["xanes2d_fit"]["cfg_file"] = str(self._xanes_data_fn)
            elif self.ana_type.value == "Differential-Imaging":
                tem["diff_imaging"]["cfg_file"] = str(self._xanes_data_fn)
        with open(cfg_fn, "w") as f:
            json.dump(tem, f, indent=4, separators=(",", ": "))

        if self.ana_type.value == "XANES":
            xanes_proc_cfg = deepcopy(xanes_proc_data_struct)
                    
            xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                "analysis_type"] = self.xanes_fit_type.value
            xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                "bin_fact"] = int(self.downsample_factor.value)
            xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                "element"] = self.element.value
            xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                "eng_list"] = np.float32(self._eng_lst)
            xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                "data_shape"] = self._xanes_data_dim
            xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                "wl_fit_eng_s"] = float(self.wl_s.value)
            xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                "wl_fit_eng_e"] = float(self.wl_e.value)
            xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                "edge_eng"] = float(self.edge_eng.value)
            
            if self.xanes_fit_type.value == "normalized spectra - wl":
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "edge50_fit_s"] = float(self.edge_s.value)
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "edge50_fit_e"] = float(self.edge_e.value)
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "edge_fit method"]["params"]["spec"] = "norm"
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "edge_fit method"]["params"][
                        "eng_offset"] = float(self.edge_eng.value)
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "wl_fit method"]["params"]["spec"] = "norm"
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "wl_fit method"]["params"][
                        "eng_offset"] = (float(self.wl_s.value) + float(self.wl_e.value)) / 2.0
            elif self.xanes_fit_type.value == "raw spectra - wl":
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "edge50_fit_s"] = "None"
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "edge50_fit_e"] = "None"
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "wl_fit method"]["params"]["spec"] = "raw"
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "wl_fit method"]["params"][
                        "eng_offset"] = (float(self.wl_s.value) + float(self.wl_e.value)) / 2.0
            elif (self.xanes_fit_type.value == "normalized spectra - lcf") and self._lcf_ref_spec_set:
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "LCF"]["ref"] = self._lcf_ref_dict
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "LCF"]["ref_alias"] = sort_xanes_ref_by_name(list(self._lcf_ref_dict.keys()))
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "LCF"]["use_constr"] = True
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "LCF"]["use_lcf"] = True
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "edge50_fit_s"] = float(self.edge_s.value)
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "edge50_fit_e"] = float(self.edge_e.value)
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "edge_fit method"]["params"]["spec"] = "norm"
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "edge_fit method"]["params"][
                        "eng_offset"] = float(self.edge_eng.value)
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "wl_fit method"]["params"]["spec"] = "norm"
                xanes_proc_cfg["processed_XANES"]["proc_parameters"][
                    "wl_fit method"]["params"][
                        "eng_offset"] = (float(self.wl_s.value) + float(self.wl_e.value)) / 2.0
            elif (self.xanes_fit_type.value == "normalized spectra - lcf") and not self._lcf_ref_spec_set:
                print("LCF reference spectra have not been set correctly.")
                self.op_status.value = "LCF reference spectra have not been set correctly."
                return
            for item in self.save_items.value:
                xanes_proc_cfg["processed_XANES"]["proc_spectrum"][item] = False
            
            create_hdf5_from_json(xanes_proc_cfg, self._xanes_data_fn)
            if self.data_type.value == "3D XANES":
                sig = os.system(f"python {xanes3d_fit_script_fn}")
            elif self.data_type.value == "2D XANES":
                sig = os.system(f"python {xanes2d_fit_script_fn}")
        elif self.ana_type.value == "Differential-Imaging":
            diff_imaging_proc_cfg = deepcopy(diff_imaging_proc_data_struct)
            diff_imaging_proc_cfg["processed_diff_imaging"]["proc_parameters"][
                "reg_img_path"] = f"/registration_results/reg_results/registered_{self._anal_type_dict[self.data_type.value]}"
            diff_imaging_proc_cfg["processed_diff_imaging"]["proc_parameters"][
                "img_shape"] = self._xanes_data_dim[1:]
            diff_imaging_proc_cfg["processed_diff_imaging"]["proc_parameters"][
                "eng_list"] = np.float32(self._eng_lst)
            diff_imaging_proc_cfg["processed_diff_imaging"]["proc_parameters"][
                "diff_img_idx"] = self._diff_img_idx
            diff_imaging_proc_cfg["processed_diff_imaging"]["proc_parameters"][
                "diff_img_eng"] = self._eng_lst[self._diff_img_idx]
            diff_imaging_proc_cfg["processed_diff_imaging"]["proc_parameters"][
                "bin_fact"] = int(self.downsample_factor.value)
            for item in self.save_items.value:
                diff_imaging_proc_cfg["processed_diff_imaging"]["proc_rlt"]["diff_img"] = False
            
            create_hdf5_from_json(diff_imaging_proc_cfg, self._xanes_data_fn)
            sig = os.system(f"python {diff_imaging_script_fn}")

    def _close(self):
        self.xanes_file.value = ""
        self.__reset_gui()

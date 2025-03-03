import numpy as np
import os
import glob
from copy import deepcopy

import tifffile
import h5py
import json
import dask.array as da
import datetime
from pathlib import Path
from magicgui import widgets

from ...gui.gui_components import (
    check_file_availability,
)

from ..utils.misc import (
    set_data_widget,
    overlap_roi,
    update_layer_in_viewer,
    show_layers_in_viewer,
    rm_gui_viewers,
    disp_progress_info,
)
from ...dicts.data_struct_dict import ZFLY_CFG, FLY_CFG, APS_TXM_CFG
from ..utils.ext_io_lib import mk_aps_cfg, opt_reg_roi_gui, ext_reg_params_gui, scan_info_gui, get_scan_info


cfg_fn = Path(__file__).parents[1] / "configs/txm_simple_gui_script_cfg.json"
xanes3d_auto_cen_reg_script_fn = (
    Path(__file__).parents[1] / "scripts/xanes3d_tomo_autocent_cmd.py"
)
xanes2d_img_auto_reg_script_fn = (
    Path(__file__).parents[1] / "scripts/xanes2d_image_autoreg_cmd.py"
)

aps_xanes2d_img_auto_reg_script_fn = (
    Path(__file__).parents[1] / "scripts/aps_xanes2d_image_autoreg_cmd.py"
)

with open(
    Path(__file__).parents[1] / "configs/xanes3d_tomo_autocent_cfg.json", "r"
) as f:
    xanes3d_tomo_autocent_cfg = json.load(f)

with open(
    Path(__file__).parents[1] / "configs/xanes2d_image_autoreg_cfg.json", "r"
) as f:
    xanes2d_image_autocent_cfg = json.load(f)

_TOMO_XANES3D_REC_ID_S_CHOICES = []
_TOMO_XANES3D_REC_ID_E_CHOICES = []


def get_tomo_xanes3d_rec_id_s_choices(ComboBox):
    global _TOMO_XANES3D_REC_ID_S_CHOICES
    return _TOMO_XANES3D_REC_ID_S_CHOICES


def get_tomo_xanes3d_rec_id_e_choices(ComboBox):
    global _TOMO_XANES3D_REC_ID_E_CHOICES
    return _TOMO_XANES3D_REC_ID_E_CHOICES


def check_cfg_type(json_cfg):
    with open(json_cfg, "r") as f:
        tem = json.load(f)

    if "run_type" in tem.keys():
        return "xanes3d_autocen&reg"
    elif len(tem.keys()) == 1:
        key = tem[list(tem.keys())[0]]
        if np.all(
            item in tem[key].keys
            for item in [
                "file_params",
                "recon_config",
                "flt_params",
                "data_params",
                "alg_params",
            ]
        ):
            return "xanes3d_tomo_tplt"
    elif len(tem.keys()) > 1:
        key = tem[list(tem.keys())[0]]
        if np.all(
            item in tem[key].keys
            for item in [
                "file_params",
                "recon_config",
                "flt_params",
                "data_params",
                "alg_params",
            ]
        ) and any([Path(tem[ii]["file_params"]["recon_top_dir"]
                       ).joinpath(Path(tem[ii]["file_params"
                       ]["io_confg"]["tomo_raw_fn_template"]
                       ).stem.format(ii)).iterdir() for ii in tem.keys()]) :
            return "xanes3d_reg"
    else:
        return None


################################################################################
#             auto reconstruction and alignment for XANES3D                    #
################################################################################
class xanes_reg_gui:
    def __init__(self, viewer):
        self.viewer = viewer
        self._tomo_cfg = None
        self.scn_fntpl = None
        self.rec_fntpl = None
        self._ref_rec_tplt = {"file_params": {"raw_data_top_dir": Path("")}}
        self._tomo_recon_tplt = None
        self._test_run_done = False
        self._continue_run_confirmed = False
        self._tomo_tplt_fn_old_val = ""
        self._3dxanes_new_rec_info = ""
        self._3dxanes_rec_roix_old_val = [0, 1]
        self._3dxanes_rec_roiy_old_val = [0, 1]
        self._3dxanes_rec_roiz_old_val = [0, 1]
        self._3dxanes_opt_reg_roi = None
        self._3dxanes_opt_reg_roi_old_val = None
        self._scn_id_s_old_val = ""
        self._scn_id_e_old_val = ""
        self._2dxanes_if_new_reg = True
        self._2dxanes_data = None
        self._2dxanes_eng_lst = None
        self._2dxanes_reg_fn = None
        self._2dxanes_reg_fn_p = None
        self._2dxanes_fn = None
        self._2dxanes_fn_p = None
        self._2dxanes_data_ready = False
        self._2dxanes_new_reg_info = ""
        self._2dxanes_reg_roix_old_val = [0, 1]
        self._2dxanes_reg_roiy_old_val = [0, 1]
        self._2dxanes_reg_roiz_old_val = [0, 1]
        self._2dxanes_reg_ref_im_old_val = 0
        self._2dxanes_if_new_align = False
        self._2dxanes_align_roix_old_val = [0, 1]
        self._2dxanes_align_roiy_old_val = [0, 1]
        self._2dxanes_align_roiz_old_val = [0, 1]
        self._reg_smth_krnl = 1
        self._reg_chnk_sz = 5
        self._viewers = [
            "autocent_check",
            "autoreg_check",
            "xanes_raw_viewer",
            "auto_cen_roi",
            "recon_roi",
            "ext_reg_roi",
            "tomo_viewer",
        ]

        self.label1 = widgets.Label(
            value="-------------------- Auto Cen & Align --------------------",
        )
        self.data_type = widgets.ComboBox(
            name="data type",
            choices=["3D XANES", "APS 3D XANES", "2D XANES", "APS 2D XANES"],
            value="3D XANES",
            enabled=True,
        )
        self.tomo_tplt_fn = widgets.FileEdit(
            mode="r",
            filter="*.json",
            name="tplt file",
            tooltip="xanes tomo recon template json file",
        )
        self.ref_scan_id = widgets.LineEdit(name="ref scan id", enabled=False)
        self._scan_id_s_box = widgets.HBox()
        self.scan_id_s = widgets.ComboBox(
            choices=get_tomo_xanes3d_rec_id_s_choices, name="scan id s", enabled=False
        )
        self.scan_id_s_info = widgets.PushButton(text="info card", enabled=False)
        self._scan_id_s_box.append(self.scan_id_s)
        self._scan_id_s_box.append(widgets.Label(value="    "))
        self._scan_id_s_box.append(self.scan_id_s_info)
        self._scan_id_s_box.native.setStyleSheet("""
            QComboBox { 
                width: 50%; 
                margin-right: 0;
            }
            QLabel { 
                margin-right: 0;
                margin-left: 0;
                min-width: 20%;
            }
            QPushButton { 
                width: 30%;
                margin-left: 0;
                margin-right: 0;
            }
        """)
        self._scan_id_e_box = widgets.HBox()
        self.scan_id_e = widgets.ComboBox(
            choices=get_tomo_xanes3d_rec_id_e_choices, name="scan id e", enabled=False
        )
        self.scan_id_e_info = widgets.PushButton(text="info card", enabled=False)
        self._scan_id_e_box.append(self.scan_id_e)
        self._scan_id_e_box.append(widgets.Label(value="    "))
        self._scan_id_e_box.append(self.scan_id_e_info)
        self._scan_id_e_box.native.setStyleSheet("""
            QComboBox { 
                width: 50%; 
                margin-right: 0;
            }
            QLabel { 
                margin-right: 0;
                margin-left: 0;
                min-width: 20%;
            }
            QPushButton { 
                width: 30%;
                margin-left: 0;
                margin-right: 0;
            }
        """)
        self.skip_auto_cen = widgets.CheckBox(
            value=False, text="skip auto cen", enabled=False,
            tooltip="check this on if you have already finished tomographic reconstructions of scans."
        )
        self.auto_cen_dft_roi = widgets.CheckBox(
            value=False, text="default auto cen roi x/y", enabled=False
        )
        self.auto_cen_roix = widgets.RangeSlider(
            min=1, max=2560, name="auto cen roi x", value=[540, 740], enabled=False
        )
        self.auto_cen_roiy = widgets.RangeSlider(
            min=1, max=2560, name="auto cen roi y", value=[540, 740], enabled=False
        )
        self.ref_sli = widgets.Slider(
            min=1, max=2160, name="auto cen ref sli", value=540, enabled=False
        )
        self.opt_reg_roi = widgets.CheckBox(
            value=False, text="optional reg roi", enabled=False
        )
        self.rec_roix = widgets.RangeSlider(
            min=1, max=2560, name="rec roi x", value=[540, 740], enabled=False
        )
        self.rec_roiy = widgets.RangeSlider(
            min=1, max=2560, name="rec roi y", value=[540, 740], enabled=False
        )
        self.rec_roiz = widgets.RangeSlider(
            min=1, max=2160, name="rec roi z", value=[440, 640], enabled=False
        )
        self.sli_srch_range = widgets.SpinBox(
            min=0, max=30, name="sli srch rgn", value=10, enabled=False
        )
        self.cen_srch_range = widgets.SpinBox(
            min=0, max=30, name="cen srch rgn", value=15, enabled=False
        )
        self.ext_reg_params = widgets.CheckBox(
            value=False, text="extra reg params", enabled=False
        )
        self.ang_corr = widgets.CheckBox(value=False, text="Ang Corr", enabled=False)
        self.ang_corr_range = widgets.FloatSpinBox(
            min=0, max=5, step=0.5, name="ang rgn", value=2, enabled=False
        )
        self.test_run = widgets.PushButton(
            text="test run",
            tooltip="run autocen for the first, middle, and the last scans to verify the autocen roi is correctly set",
            enabled=False,
        )
        self.confirm_test_run = widgets.RadioButtons(
            name="confirm test run",
            choices=["Yes", "No"],
            orientation="horizontal",
            value="No",
            tooltip="confirm if the autocen results are good",
            enabled=False,
        )
        self.reg_run = widgets.PushButton(text="run")
        self.close = widgets.PushButton(text="close", enabled=False)
        self.op_status = widgets.LineEdit(name="operation status", enabled=False)

        self.data_type.changed.connect(self._sel_in_data_type)
        self.tomo_tplt_fn.changed.connect(self._xanes_set_fn)
        self.scan_id_s.changed.connect(self._3dxanes_check_scan_id_s)
        self.scan_id_e.changed.connect(self._3dxanes_check_scan_id_e)
        self.scan_id_s_info.changed.connect(self._3dxanes_show_scan_id_s_info)
        self.scan_id_e_info.changed.connect(self._3dxanes_show_scan_id_e_info)
        self.skip_auto_cen.changed.connect(self._3dxanes_tomo_skip_auto_cen)
        self.auto_cen_dft_roi.changed.connect(self._3dxanes_tomo_auto_cen_dft_roi)
        self.auto_cen_roix.changed.connect(self._xanes_tomo_auto_cen_roix)
        self.auto_cen_roiy.changed.connect(self._xanes_tomo_auto_cen_roiy)
        self.ref_sli.changed.connect(self._xanes_tomo_auto_cen_ref_sli)
        self.opt_reg_roi.changed.connect(self._3dxanes_set_opt_reg_roi)
        self.rec_roix.changed.connect(self._xanes_tomo_rec_roix)
        self.rec_roiy.changed.connect(self._xanes_tomo_rec_roiy)
        self.rec_roiz.changed.connect(self._xanes_tomo_rec_roiz)
        self.ext_reg_params.changed.connect(self._xanes_set_ext_reg_params)
        self.ang_corr.changed.connect(self._xanes_ang_corr)
        self.test_run.changed.connect(self._xanes_test_run)
        self.confirm_test_run.changed.connect(self._xanes_confirm_to_run)
        self.reg_run.changed.connect(self._xanes_reg_run)
        self.close.changed.connect(self._close)

        self.gui_layout = widgets.VBox(
            widgets=[
                self.label1,
                self.data_type,
                self.tomo_tplt_fn,
                self.ref_scan_id,
                # self.scan_id_s,
                # self.scan_id_e,
                self._scan_id_s_box,
                self._scan_id_e_box,
                self.skip_auto_cen,
                self.auto_cen_dft_roi,
                self.auto_cen_roix,
                self.auto_cen_roiy,
                self.ref_sli,
                self.opt_reg_roi,
                self.rec_roix,
                self.rec_roiy,
                self.rec_roiz,
                self.sli_srch_range,
                self.cen_srch_range,
                self.ext_reg_params,
                self.ang_corr,
                self.ang_corr_range,
                self.test_run,
                self.confirm_test_run,
                self.reg_run,
                self.close,
                self.op_status,
            ]
        )
        self.key_widgets = [
            self.ref_scan_id,
            self.scan_id_s,
            self.scan_id_s_info,
            self.scan_id_e,
            self.scan_id_e_info,
            self.skip_auto_cen,
            self.auto_cen_dft_roi,
            self.auto_cen_roix,
            self.auto_cen_roiy,
            self.ref_sli,
            self.opt_reg_roi,
            self.rec_roix,
            self.rec_roiy,
            self.rec_roiz,
            self.sli_srch_range,
            self.cen_srch_range,
            self.ext_reg_params,
            self.ang_corr,
            self.ang_corr_range,
            self.test_run,
            self.confirm_test_run,
            self.reg_run,
            self.close,
            self.op_status,
        ]

        self.scan_info_popup = scan_info_gui()

    def __3dxanes_tomo_check_avail_id_s(self, cfg_type, batch_ids=[]):
        global _TOMO_XANES3D_REC_ID_S_CHOICES
        if cfg_type == "xanes3d_tomo_tplt":
            ids = check_file_availability(
                self._ref_rec_tplt["file_params"]["raw_data_top_dir"],
                scan_id=None,
                signature=self._tomo_cfg["tomo_raw_fn_template"],
                return_idx=True,
            )
        elif cfg_type == "xanes3d_reg":
            ids = batch_ids
        if ids:
            _TOMO_XANES3D_REC_ID_S_CHOICES = sorted(ids)
        else:
            _TOMO_XANES3D_REC_ID_S_CHOICES = []
        self.scan_id_s.reset_choices()

    def __3dxanes_tomo_check_avail_id_e(self, cfg_type, batch_ids=[]):
        global _TOMO_XANES3D_REC_ID_E_CHOICES
        if cfg_type == "xanes3d_tomo_tplt":
            ids = check_file_availability(
            self._ref_rec_tplt["file_params"]["raw_data_top_dir"],
            scan_id=None,
            signature=self._tomo_cfg["tomo_raw_fn_template"],
            return_idx=True,
        )
        elif cfg_type == "xanes3d_reg":
            ids = batch_ids
        if ids:
            _TOMO_XANES3D_REC_ID_E_CHOICES = sorted(ids)
        else:
            _TOMO_XANES3D_REC_ID_E_CHOICES = []
        self.scan_id_e.reset_choices()

    def _3dxanes_check_scan_id_s(self):
        if int(self.scan_id_s.value) > int(self.ref_scan_id.value):
            self.scan_id_s.value = self.ref_scan_id.value
        self.__reset_run_states()
        self.__reset_run_buttons()

    def _3dxanes_check_scan_id_e(self):
        if int(self.scan_id_e.value) < int(self.ref_scan_id.value):
            self.scan_id_e.value = self.ref_scan_id.value
        self.__reset_run_states()
        self.__reset_run_buttons()

    def _3dxanes_show_scan_id_s_info(self):
        self.scan_info_popup.set_message(message=get_scan_info(Path(self._ref_rec_tplt["file_params"]["raw_data_top_dir"]) / self._ref_rec_tplt["file_params"]["io_confg"]["tomo_raw_fn_template"].format(self.scan_id_s.value), self._ref_rec_tplt["file_params"]["io_confg"]))
        self.scan_info_popup.show()
        
    def _3dxanes_show_scan_id_e_info(self):
        self.scan_info_popup.set_message(message=get_scan_info(Path(self._ref_rec_tplt["file_params"]["raw_data_top_dir"]) / self._ref_rec_tplt["file_params"]["io_confg"]["tomo_raw_fn_template"].format(self.scan_id_e.value), self._ref_rec_tplt["file_params"]["io_confg"]))
        self.scan_info_popup.show()

    def __3dxanes_tomo_if_new_rec(self):
        if (
            (self._tomo_tplt_fn_old_val != self.tomo_tplt_fn.value)
            or (self._scn_id_s_old_val != self.scan_id_s.value)
            or (self._scn_id_e_old_val != self.scan_id_e.value)
            or (self._3dxanes_rec_roix_old_val != self.rec_roix.value)
            or (self._3dxanes_rec_roiy_old_val != self.rec_roiy.value)
            or (self._3dxanes_rec_roiz_old_val != self.rec_roiz.value)
        ):
            self._3dxanes_new_rec_info = f"{self.scan_id_s.value}-{self.scan_id_e.value}_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
            self._tomo_tplt_fn_old_val = self.tomo_tplt_fn.value
            self._scn_id_s_old_val = self.scan_id_s.value
            self._scn_id_e_old_val = self.scan_id_e.value
            self._3dxanes_rec_roix_old_val = self.rec_roix.value
            self._3dxanes_rec_roiy_old_val = self.rec_roiy.value
            self._3dxanes_rec_roiz_old_val = self.rec_roiz.value

    def __3dxanes_comp_tomo_fntpl(self):
        self.scn_fntpl = (
            Path(self._ref_rec_tplt["file_params"]["raw_data_top_dir"])
            / self._tomo_cfg["tomo_raw_fn_template"]
        )
        self.rec_fntpl = (
            Path(self._ref_rec_tplt["file_params"]["raw_data_top_dir"])
            / self._tomo_cfg["xanes3D_recon_dir_template"]
            / self._tomo_cfg["xanes3D_recon_fn_template"]
        )

    def __3dxanes_set_scan_id_lims(self):
        try:
            if int(self.ref_scan_id.value) - 1 >= int(self.scan_id_s.choices[0]):
                self.scan_id_s.value = self.scan_id_s.choices[
                    self.scan_id_s.choices.index(self.ref_scan_id.value) - 1
                ]
            else:
                self.scan_id_s.value = self.scan_id_s.choices[0]

            if int(self.ref_scan_id.value) + 1 <= int(self.scan_id_s.choices[-1]):
                self.scan_id_e.value = self.scan_id_s.choices[
                    self.scan_id_s.choices.index(self.ref_scan_id.value) + 1
                ]
            else:
                self.scan_id_e.value = self.scan_id_s.choices[-1]
        except:
            self.op_status.value = "There is no valid scan series available for XANES3D autocent operation!"
            print(
                "There is no valid scan series available for XANES3D autocent operation!"
            )

    def __3dxanes_widgets_logic(self):
        if (self.rec_fntpl is None) or (
            not Path(
                str(self.rec_fntpl).format(
                    self.ref_scan_id.value,
                    str(self.ref_sli.value).zfill(5),
                )
            ).exists()
        ):
            for widget in self.key_widgets:
                widget.enabled = False
        else:
            self.scan_id_s.enabled = True
            self.scan_id_s_info.enabled = True
            self.scan_id_e.enabled = True
            self.scan_id_e_info.enabled = True
            self.auto_cen_dft_roi.enabled = True
            self.skip_auto_cen.enabled = True

            if self.skip_auto_cen.value:
                self.auto_cen_dft_roi.value = False
                self.auto_cen_dft_roi.enabled = False
                self.opt_reg_roi.value = False
                self.opt_reg_roi.enabled = False
                self.auto_cen_roix.name = "auto reg roi x"
                self.auto_cen_roiy.name = "auto reg roi y"
                self.opt_reg_roi.name = "auto reg ref sli"
                self.cen_srch_range.enabled = False
                self.test_run.enabled = False
                self.confirm_test_run.enabled = False
                self.reg_run.enabled = True
            else:
                self.auto_cen_dft_roi.enabled = True
                self.opt_reg_roi.enabled = True
                self.auto_cen_roix.name = "auto cen roi x"
                self.auto_cen_roiy.name = "auto cen roi y"
                self.opt_reg_roi.name = "auto cen ref sli"
                self.cen_srch_range.enabled = True
                self.test_run.enabled = True

            if self.auto_cen_dft_roi.value:
                self.auto_cen_roix.enabled = False
                self.auto_cen_roiy.enabled = False
            else:
                self.auto_cen_roix.enabled = True
                self.auto_cen_roiy.enabled = True
            self.ref_sli.enabled = True
            
            self.rec_roix.enabled = True
            self.rec_roiy.enabled = True
            self.rec_roiz.enabled = True
            self.sli_srch_range.enabled = True
            self.ext_reg_params.enabled = True
            self.ang_corr.enabled = True
            self.close.enabled = True

    def __3dxanes_tomo_show_sli(self, mode="auto_cen"):
        sta = False
        if mode == "auto_cen":
            try:
                update_layer_in_viewer(
                    self.viewer,
                    tifffile.imread(
                        str(self.rec_fntpl).format(
                            self.ref_scan_id.value,
                            str(self.ref_sli.value).zfill(5),
                        )
                    ),
                    "xanes_raw_viewer", 
                    data_type="image",
                )
                sta = True
            except Exception as e:
                self.op_status.value = (
                    "Something is wrong. Please check terminal for more information."
                )
                print(f"{str(e)=}")
                sta = False
        elif mode == "recon_roi":
            if self._3dxanes_rec_roiz_old_val[0] != self.rec_roiz.value[0]:
                try:
                    update_layer_in_viewer(
                        self.viewer,
                        tifffile.imread(
                            str(self.rec_fntpl).format(
                                self.ref_scan_id.value,
                                str(self.rec_roiz.value[0]).zfill(5),
                            )
                        ),
                        "xanes_raw_viewer", 
                        data_type="image",
                    )
                    sta = True
                except Exception as e:
                    self.op_status.value = "Something is wrong. Please check terminal for more information."
                    print(str(e))
                    sta = False
            elif self._3dxanes_rec_roiz_old_val[1] != self.rec_roiz.value[1]:
                try:
                    update_layer_in_viewer(
                        self.viewer,
                        tifffile.imread(
                            str(self.rec_fntpl).format(
                                self.ref_scan_id.value,
                                str(self.rec_roiz.value[1]).zfill(5),
                            )
                        ),
                        "xanes_raw_viewer", 
                        data_type="image",
                    )
                    sta = True
                except Exception as e:
                    self.op_status.value = "Something is wrong. Please check terminal for more information."
                    print(str(e))
                    sta = False
        if sta:
            rng = (
                self.viewer.layers["xanes_raw_viewer"].data.max()
                - self.viewer.layers["xanes_raw_viewer"].data.min()
            )
            self.viewer.layers["xanes_raw_viewer"].contrast_limits = [
                self.viewer.layers["xanes_raw_viewer"].data.min() + 0.1 * rng,
                self.viewer.layers["xanes_raw_viewer"].data.max() - 0.1 * rng,
            ]
            self._3dxanes_rec_roiz_old_val = self.rec_roiz.value
            self.viewer.reset_view()

    def __3dxnaes_tomo_def_autocent_cfg(self):
        with open(cfg_fn, "r") as f:
            tem = json.load(f)
            tem["xanes3d_auto_cen"]["cfg_file"] = str(
                Path(self._ref_rec_tplt["file_params"]["raw_data_top_dir"])
                / f"xanes3d_autocenreg-{self._3dxanes_new_rec_info}.json"
            )
        with open(cfg_fn, "w") as f:
            json.dump(tem, f, indent=4, separators=(",", ": "))

        xanes3d_tomo_autocent_cfg["template_file"] = str(self.tomo_tplt_fn.value)
        if self._continue_run_confirmed:
            xanes3d_tomo_autocent_cfg["run_type"] = "autocen&rec&reg"
            if self.skip_auto_cen.value:
                xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["cen_opt"] = None
            else:
                xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["cen_opt"] = "ABSOLUTE"
        else:
            xanes3d_tomo_autocent_cfg["run_type"] = "autocen"
        
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["rec_dir_tplt"] = str(
            Path(self._ref_rec_tplt["file_params"]["raw_data_top_dir"])
            / self._tomo_cfg["xanes3D_recon_dir_template"]
        )
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["rec_fn_tplt"] = str(self.rec_fntpl)
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["ref_scn_cen"] = self._ref_rec_tplt[
            "data_params"
        ]["rot_cen"]
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"][
            "use_dflt_ref_reg_roi"
        ] = self.auto_cen_dft_roi.value
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["ref_cen_roi"] = [
            self.auto_cen_roiy.value[0],
            self.auto_cen_roiy.value[1],
            self.auto_cen_roix.value[0],
            self.auto_cen_roix.value[1],
        ]
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["ref_cen_sli"] = self.ref_sli.value
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"][
            "use_opt_reg_roi"
        ] = self.opt_reg_roi.value
        if self.opt_reg_roi.value:
            xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["opt_reg_roi"] = (
                self._3dxanes_opt_reg_roi[:4]
            )
            xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["opt_reg_sli"] = (
                self._3dxanes_opt_reg_roi[4]
            )
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["rec_roi"] = [
            self.rec_roiy.value[0],
            self.rec_roiy.value[1],
            self.rec_roix.value[0],
            self.rec_roix.value[1],
            self.rec_roiz.value[0],
            self.rec_roiz.value[1],
        ]
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"][
            "ref_sli_srch_half_wz"
        ] = self.sli_srch_range.value
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"][
            "ref_cen_srch_half_wz"
        ] = self.cen_srch_range.value
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"][
            "ref_scn_id"
        ] = self.ref_scan_id.value
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["scn_id_s"] = self.scan_id_s.value
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["scn_id_e"] = self.scan_id_e.value

        ids = self.scan_id_e.choices.index(self.scan_id_s.value)
        ide = self.scan_id_e.choices.index(self.scan_id_e.value)
        if self._continue_run_confirmed or self.skip_auto_cen.value:
            xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["scn_id_lst"] = (
                self.scan_id_e.choices[ids : ide + 1]
            )
        else:
            if len(self.scan_id_e.choices[ids : ide + 1]) >= 3:
                xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["scn_id_lst"] = list(
                    set(
                        [
                            self.scan_id_e.choices[ids],
                            self.ref_scan_id.value,
                            self.scan_id_e.choices[ide],
                        ]
                    )
                )
            else:
                xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["scn_id_lst"] = [
                    self.scan_id_e.choices[ids],
                    self.scan_id_e.choices[ide],
                ]

        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["reg_chnk_sz"] = self._reg_chnk_sz
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["mrtv_knl_sz"] = self._reg_smth_krnl

        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["ang_corr"] = self.ang_corr.value
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"][
            "ang_corr_rgn"
        ] = self.ang_corr_range.value
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["xanes3d_sav_trl_reg_fn"] = str(
            Path(self._ref_rec_tplt["file_params"]["raw_data_top_dir"])
            / f"3D_trial_reg_scan_id_{self._3dxanes_new_rec_info}.h5"
        )
        xanes3d_tomo_autocent_cfg["aut_xns3d_pars"]["XANES_tmp_fn"] = ""

        with open(tem["xanes3d_auto_cen"]["cfg_file"], "w") as f:
            json.dump(xanes3d_tomo_autocent_cfg, f, indent=4, separators=(",", ": "))

    def __3dxanes_set_roi_lims(self):
        b = glob.glob(
            str(
                (
                    Path(self._ref_rec_tplt["file_params"]["raw_data_top_dir"])
                    / self._tomo_cfg["xanes3D_recon_dir_template"].format(
                        self.ref_scan_id.value
                    )
                ).joinpath("*.tiff")
            )
        )
        ref_rec_ids = sorted([int(str(Path(fn).stem).split("_")[-1]) for fn in b])

        if ref_rec_ids:
            set_data_widget(
                self.ref_sli,
                ref_rec_ids[0],
                ref_rec_ids[int(len(ref_rec_ids) / 2)],
                ref_rec_ids[-1],
            )
            set_data_widget(
                self.rec_roiz,
                ref_rec_ids[0],
                [
                    ref_rec_ids[0] + int(2 * self.sli_srch_range.value) + 15,
                    ref_rec_ids[-1] - int(2 * self.sli_srch_range.value) - 16,
                ],
                ref_rec_ids[-1],
            )
            self._3dxanes_rec_roiz_old_val = self.rec_roiz.value

            dim = tifffile.imread(
                str(self.rec_fntpl).format(
                    self.ref_scan_id.value,
                    str(self.ref_sli.value).zfill(5),
                )
            ).shape
            set_data_widget(
                self.auto_cen_roix,
                0,
                [
                    int(dim[1] / 4),
                    int(dim[1] * 3 / 4),
                ],
                dim[1] - 1,
            )
            set_data_widget(
                self.auto_cen_roiy,
                0,
                [
                    int(dim[0] / 4),
                    int(dim[0] * 3 / 4),
                ],
                dim[0] - 1,
            )
            set_data_widget(
                self.rec_roix,
                0,
                [
                    int(dim[1] / 4),
                    int(dim[1] * 3 / 4),
                ],
                dim[1] - 1,
            )
            set_data_widget(
                self.rec_roiy,
                0,
                [
                    int(dim[0] / 4),
                    int(dim[0] * 3 / 4),
                ],
                dim[0] - 1,
            )

    def _3dxanes_tomo_skip_auto_cen(self):
        self.__3dxanes_widgets_logic()
        if self.skip_auto_cen.value:
            self.confirm_test_run.enabled = False
            self.reg_run.enabled = True
            self.confirm_test_run.value = "Yes"
            self._continue_run_confirmed = True
        else:
            self.__reset_run_states()
            self.__reset_run_buttons()

    def _3dxanes_tomo_auto_cen_dft_roi(self):
        if self.auto_cen_dft_roi.value:
            self.auto_cen_roix.enabled = False
            self.auto_cen_roiy.enabled = False
        else:
            self.auto_cen_roix.enabled = True
            self.auto_cen_roiy.enabled = True
        if (self.rec_fntpl is not None) and (
            Path(
                str(self.rec_fntpl).format(
                    self.ref_scan_id.value,
                    str(self.ref_sli.value).zfill(5),
                )
            ).exists()
        ):
            overlap_roi(self.viewer, self, mode="auto_cen")
        self.__reset_run_states()
        self.__reset_run_buttons()

    def _3dxanes_set_opt_reg_roi(self):
        if self.opt_reg_roi.value:
            ans = opt_reg_roi_gui(self)
            if ans.rtn:
                self._3dxanes_opt_reg_roi = [
                    ans.opt_reg_roiy.value[0],
                    ans.opt_reg_roiy.value[1],
                    ans.opt_reg_roix.value[0],
                    ans.opt_reg_roix.value[1],
                    ans.opt_reg_ref_sli.value,
                ]
                self._3dxanes_opt_reg_roi_old_val = deepcopy(self._3dxanes_opt_reg_roi)
            else:
                self.opt_reg_roi.value = False
        else:
            if self._3dxanes_opt_reg_roi is None:
                self._3dxanes_opt_reg_roi_old_val = None
            else:
                self._3dxanes_opt_reg_roi_old_val = deepcopy(self._3dxanes_opt_reg_roi)
            self._3dxanes_opt_reg_roi = None

    @disp_progress_info("xanes2d data loading")
    def __2dxanes_check_in_file(self):
        if self.data_type.value == "2D XANES":
            if self._2dxanes_fn_p is None:
                try:
                    self._2dxanes_fn_p = h5py.File(self._2dxanes_fn, "r")
                except Exception as e:
                    self._2dxanes_fn_p = None
                    self.op_status.value = "Invalid data file!"
                    print(e)
            else:
                self._2dxanes_fn_p.close()
                self._2dxanes_fn_p = h5py.File(self._2dxanes_fn, "r")
            if (
                (self._2dxanes_fn_p is not None)
                and (
                    self._2dxanes_fn_p[
                        self._2dxanes_cfg["structured_h5_reader"]["io_data_structure"]["eng_path"]
                    ].shape[0]
                    > 1
                )
                and len(
                    self._2dxanes_fn_p[
                        self._2dxanes_cfg["structured_h5_reader"]["io_data_structure"]["data_path"]
                    ].shape
                )
                == 3
                and self._2dxanes_fn_p[
                    self._2dxanes_cfg["structured_h5_reader"]["io_data_structure"]["eng_path"]
                ].shape[0]
                == self._2dxanes_fn_p[
                    self._2dxanes_cfg["structured_h5_reader"]["io_data_structure"]["data_path"]
                ].shape[0]
            ):
                try:
                    self._2dxanes_eng_lst = self._2dxanes_fn_p[
                        self._2dxanes_cfg["structured_h5_reader"]["io_data_structure"]["eng_path"]
                    ][:]
                    dark = self._2dxanes_fn_p[
                        self._2dxanes_cfg["structured_h5_reader"]["io_data_structure"]["dark_path"]
                    ][:].squeeze()
                    flat = self._2dxanes_fn_p[
                        self._2dxanes_cfg["structured_h5_reader"]["io_data_structure"]["flat_path"]
                    ][:].squeeze()
                    tem = -np.log(
                        (
                            da.from_array(
                                self._2dxanes_fn_p[
                                    self._2dxanes_cfg["structured_h5_reader"]["io_data_structure"][
                                        "data_path"
                                    ]
                                ]
                            )
                            - dark
                        )
                        / (flat - dark)
                    )
                    tem[np.isinf(tem)] = 0
                    tem[np.isnan(tem)] = 0
                    self._2dxanes_data = tem.compute()
                    update_layer_in_viewer(
                        self.viewer,
                        self._2dxanes_data,
                        "xanes_raw_viewer", 
                        data_type="image",
                    )
                    self.viewer.reset_view()
                    self._2dxanes_data_ready = True
                except Exception as e:
                    self.op_status.value = "Something is wrong. Please check terminal for more information."
                    print(str(e))
                    self._2dxanes_fn_p.close()
                    self._2dxanes_fn_p = None
                    self._2dxanes_data = None
                    self._2dxanes_eng_lst = None
                    self._2dxanes_fn = None
                    self._2dxanes_data_ready = False
            else:
                self._2dxanes_fn_p = None
                self._2dxanes_data = None
                self._2dxanes_eng_lst = None
                self._2dxanes_fn = None
                self._2dxanes_data_ready = False
        elif self.data_type.value == "APS 2D XANES":
            top_dir = self._2dxanes_fn.parent
            fn_tplt = self._2dxanes_fn.stem.rsplit("_", maxsplit=1)[0]
            _cfg = deepcopy(APS_TXM_CFG)
            self._2dxanes_cfg = mk_aps_cfg(
                fn_tplt,
                _cfg,
                dtype="APS 2D XANES",
            )["io_data_structure_xanes2D"]
            ids = check_file_availability(
                top_dir,
                scan_id=None,
                signature=self._2dxanes_cfg["xanes2D_raw_fn_template"],
                return_idx=True,
            )
            if ids:
                ids = sorted(ids)
                try:
                    eng_lst = []
                    data = []
                    for ii in ids:
                        with h5py.File(
                            top_dir
                            / self._2dxanes_cfg["xanes2D_raw_fn_template"].format(ii),
                            "r",
                        ) as f:
                            if f[
                                self._2dxanes_cfg["structured_h5_reader"][
                                    "io_data_structure"
                                ]["eng_path"]
                            ].shape:
                                eng = f[
                                    self._2dxanes_cfg["structured_h5_reader"][
                                        "io_data_structure"
                                    ]["eng_path"]
                                ][()][0]
                            else:
                                eng = f[
                                    self._2dxanes_cfg["structured_h5_reader"][
                                        "io_data_structure"
                                    ]["eng_path"]
                                ][()]
                            eng_lst.append(eng)
                            dark = f[
                                self._2dxanes_cfg["structured_h5_reader"][
                                    "io_data_structure"
                                ]["dark_path"]
                            ][0].squeeze()
                            flat = f[
                                self._2dxanes_cfg["structured_h5_reader"][
                                    "io_data_structure"
                                ]["flat_path"]
                            ][0].squeeze()
                            tem = -np.log(
                                (
                                    f[
                                        self._2dxanes_cfg["structured_h5_reader"][
                                            "io_data_structure"
                                        ]["data_path"]
                                    ][0]
                                    - dark
                                )
                                / (flat - dark)
                            )
                            tem[np.isinf(tem)] = 0
                            tem[np.isnan(tem)] = 0
                            data.append(tem)
                    self._2dxanes_eng_lst = np.array(eng_lst)
                    self._2dxanes_data = np.array(data)
                    update_layer_in_viewer(
                        self.viewer,
                        self._2dxanes_data,
                        "xanes_raw_viewer", 
                        data_type="image",
                    )
                    self.viewer.reset_view()
                    self._2dxanes_data_ready = True
                except Exception as e:
                    self.op_status.value = "Something is wrong. Please check terminal for more information."
                    print(str(e))
                    self._2dxanes_data = None
                    self._2dxanes_eng_lst = None
                    self._2dxanes_fn = None
                    self._2dxanes_cfg = APS_TXM_CFG["io_data_structure_xanes2D"]
                    self._2dxanes_data_ready = False
            else:
                self._2dxanes_fn_p = None
                self._2dxanes_data = None
                self._2dxanes_eng_lst = None
                self._2dxanes_fn = None
                self._2dxanes_data_ready = False
        self._test_run_done = False
        self._continue_run_confirmed = False

    def __2dxanes_widgets_logic(self):
        if self._2dxanes_data_ready:
            self.scan_id_s.enabled = False
            self.scan_id_e.enabled = False
            self.auto_cen_dft_roi.enabled = False
            self.auto_cen_dft_roi.value = False
            self.opt_reg_roi.enabled = False
            self.__2dxanes_set_roi_widgets()
            self.sli_srch_range.enabled = False
            self.cen_srch_range.enabled = False
            self.ext_reg_params.enabled = True
            self.ang_corr.enabled = False
            self.ang_corr_range.enabled = False
            self.test_run.enabled = True
            if self._test_run_done:
                self.confirm_test_run.enabled = True
            else:
                self.confirm_test_run.enabled = False
            if self._continue_run_confirmed:
                self.reg_run.enabled = True
            else:
                self.reg_run.enabled = False
            self.close.enabled = True
        else:
            for widget in self.key_widgets:
                widget.enabled = False

    def __2dxanes_show_sli(self, mode="auto_reg"):
        sta = False
        if mode == "auto_reg":
            if self.ref_sli.value < self.rec_roiz.value[0]:
                if self.rec_roiz.value[0] < len(self._2dxanes_eng_lst):
                    self.ref_sli.value = self.rec_roiz.value[0]
            if self.ref_sli.value > self.rec_roiz.value[1]:
                if self.rec_roiz.value[1] < len(self._2dxanes_eng_lst):
                    self.ref_sli.value = self.rec_roiz.value[1]
            try:
                tem = self.viewer.dims.current_step
                self.viewer.dims.current_step = [
                    self.ref_sli.value,
                    int(tem[1]),
                    int(tem[2]),
                ]
                self.ref_scan_id.value = (
                    f"{float(self._2dxanes_eng_lst[self.ref_sli.value]) * 1000}eV"
                )
                sta = True
            except Exception as e:
                self.op_status.value = (
                    "Something is wrong. Please check terminal for more information."
                )
                print(str(e))
                sta = False
        elif mode == "auto_algn":
            if self._2dxanes_reg_roiz_old_val[0] != self.rec_roiz.value[0]:
                if self.rec_roiz.value[0] > self.ref_sli.value:
                    self.rec_roiz.value = [self.ref_sli.value, self.rec_roiz.value[1]]
                try:
                    tem = self.viewer.dims.current_step
                    self.viewer.dims.current_step = [
                        self.rec_roiz.value[0],
                        int(tem[1]),
                        int(tem[2]),
                    ]
                    self.ref_scan_id.value = f"{float(self._2dxanes_eng_lst[self.rec_roiz.value[0]]) * 1000}eV"
                    sta = True
                except Exception as e:
                    self.op_status.value = "Something is wrong. Please check terminal for more information."
                    print(str(e))
                    sta = False
            elif self._2dxanes_reg_roiz_old_val[1] != self.rec_roiz.value[1]:
                if self.rec_roiz.value[1] < self.ref_sli.value:
                    self.rec_roiz.value = [self.rec_roiz.value[0], self.ref_sli.value]
                try:
                    tem = self.viewer.dims.current_step
                    self.viewer.dims.current_step = [
                        self.rec_roiz.value[1],
                        int(tem[1]),
                        int(tem[2]),
                    ]
                    self.ref_scan_id.value = f"{float(self._2dxanes_eng_lst[self.rec_roiz.value[1]]) * 1000}eV"
                    sta = True
                except Exception as e:
                    self.op_status.value = "Something is wrong. Please check terminal for more information."
                    print(str(e))
                    sta = False
        if sta:
            self._2dxanes_reg_roiz_old_val = self.rec_roiz.value
            self.viewer.reset_view()

    def __2dxanes_set_roi_widgets(self):
        if not self._continue_run_confirmed:
            self.auto_cen_roix.enabled = True
            self.auto_cen_roiy.enabled = True
            self.ref_sli.enabled = True
            self.rec_roiz.enabled = True
            self.rec_roix.enabled = False
            self.rec_roiy.enabled = False
        else:
            self.auto_cen_roix.enabled = False
            self.auto_cen_roiy.enabled = False
            self.ref_sli.enabled = False
            self.rec_roiz.enabled = False
            self.rec_roix.enabled = True
            self.rec_roiy.enabled = True
        self.opt_reg_roi.enabled = False

    def __2dxanes_set_roi_lims(self):
        dim = self._2dxanes_data.shape
        set_data_widget(
            self.ref_sli,
            0,
            int(dim[0] / 2),
            dim[0] - 1,
        )
        set_data_widget(
            self.auto_cen_roix,
            0,
            [
                int(dim[2] / 4),
                int(dim[2] * 3 / 4),
            ],
            dim[2] - 1,
        )
        set_data_widget(
            self.auto_cen_roiy,
            0,
            [
                int(dim[1] / 4),
                int(dim[1] * 3 / 4),
            ],
            dim[1] - 1,
        )
        set_data_widget(
            self.rec_roix,
            0,
            [
                int(dim[2] / 4),
                int(dim[2] * 3 / 4),
            ],
            dim[2] - 1,
        )
        set_data_widget(
            self.rec_roiy,
            0,
            [
                int(dim[1] / 4),
                int(dim[1] * 3 / 4),
            ],
            dim[1] - 1,
        )
        set_data_widget(
            self.rec_roiz,
            0,
            [
                0,
                dim[0] - 1,
            ],
            dim[0] - 1,
        )
        self._2dxanes_reg_roiz_old_val = self.rec_roiz.value

    def __2dxanes_check_if_new_reg(self):
        if (
            (self._tomo_tplt_fn_old_val != self.tomo_tplt_fn.value)
            or (self._2dxanes_reg_roix_old_val != self.auto_cen_roix.value)
            or (self._2dxanes_reg_roiy_old_val != self.auto_cen_roiy.value)
            or (self._2dxanes_reg_ref_im_old_val != self.ref_sli.value)
        ):
            self._2dxanes_if_new_reg = True
            self._2dxanes_new_reg_info = (
                f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
            )
            self._tomo_tplt_fn_old_val = self.tomo_tplt_fn.value
            self._2dxanes_reg_roix_old_val = self.auto_cen_roix.value
            self._2dxanes_reg_roiy_old_val = self.auto_cen_roiy.value
            self._2dxanes_reg_ref_im_old_val = self.ref_sli.value
        else:
            self._2dxanes_if_new_reg = False

    def __2dxanes_check_if_new_align(self):
        if (
            (self._2dxanes_align_roix_old_val != self.rec_roix.value)
            or (self._2dxanes_align_roiy_old_val != self.rec_roiy.value)
            or (self._2dxanes_align_roiz_old_val != self.rec_roiz.value)
        ):
            self._2dxanes_if_new_align = True
            self._2dxanes_align_roix_old_val = self.rec_roix.value
            self._2dxanes_align_roiy_old_val = self.rec_roiy.value
            self._2dxanes_align_roiz_old_val = self.rec_roiz.value
        else:
            self._2dxanes_if_new_reg = False

    def __2dxanes_def_img_autoreg_cfg(self):
        with open(cfg_fn, "r") as f:
            tem = json.load(f)
            tem["xanes2d_reg"]["cfg_file"] = str(
                Path(self._2dxanes_fn).parent
                / (
                    "2D_trial_reg_cfg_"
                    + Path(self._2dxanes_fn).stem
                    + "_"
                    + self._2dxanes_new_reg_info
                    + ".json"
                )
            )
        with open(cfg_fn, "w") as f:
            json.dump(tem, f, indent=4, separators=(",", ": "))

        xanes2d_image_autocent_cfg["data"]["im_id_s"] = self.rec_roiz.value[0]
        xanes2d_image_autocent_cfg["data"]["im_id_e"] = self.rec_roiz.value[1]
        xanes2d_image_autocent_cfg["data"]["im_id_fixed"] = self.ref_sli.value

        if self._continue_run_confirmed:
            xanes2d_image_autocent_cfg["reg_type"] = "align"
            xanes2d_image_autocent_cfg["data"]["roi"] = [
                self.rec_roiy.value[0],
                self.rec_roiy.value[1],
                self.rec_roix.value[0],
                self.rec_roix.value[1],
            ]
        else:
            xanes2d_image_autocent_cfg["reg_type"] = "auto_reg"
            xanes2d_image_autocent_cfg["data"]["roi"] = [
                self.auto_cen_roiy.value[0],
                self.auto_cen_roiy.value[1],
                self.auto_cen_roix.value[0],
                self.auto_cen_roix.value[1],
            ]

        xanes2d_image_autocent_cfg["file"]["XANES2D_raw_fn"] = str(
            Path(self._2dxanes_fn).resolve()
        )
        xanes2d_image_autocent_cfg["file"]["sav_fn"] = str(
            Path(self._2dxanes_fn).parent
            / (
                "2D_trial_reg_"
                + Path(self._2dxanes_fn).stem
                + "_"
                + self._2dxanes_new_reg_info
                + ".h5"
            )
        )
        xanes2d_image_autocent_cfg["meta"]["eng_list"] = list(
            self._2dxanes_eng_lst[self.rec_roiz.value[0] : self.rec_roiz.value[1]]
        )

        with open(tem["xanes2d_reg"]["cfg_file"], "w") as f:
            json.dump(xanes2d_image_autocent_cfg, f, indent=4, separators=(",", ": "))

    def __init_widgets(self):
        self.ref_scan_id.value = ""
        global _TOMO_XANES3D_REC_ID_S_CHOICES
        _TOMO_XANES3D_REC_ID_S_CHOICES = []
        self.scan_id_s.reset_choices()
        global _TOMO_XANES3D_REC_ID_E_CHOICES
        _TOMO_XANES3D_REC_ID_E_CHOICES = []
        self.scan_id_e.reset_choices()
        self.auto_cen_dft_roi.value = False
        set_data_widget(
            self.auto_cen_roix,
            1,
            [540, 740],
            1280,
        )
        set_data_widget(
            self.auto_cen_roiy,
            1,
            [540, 740],
            1280,
        )
        set_data_widget(
            self.ref_sli,
            1,
            540,
            1080,
        )
        set_data_widget(
            self.rec_roix,
            1,
            [540, 740],
            1280,
        )
        set_data_widget(
            self.rec_roiy,
            1,
            [540, 740],
            1280,
        )
        set_data_widget(
            self.rec_roiz,
            1,
            [440, 640],
            1080,
        )
        self.opt_reg_roi.value = False
        self.sli_srch_range.value = 10
        self.cen_srch_range.value = 15
        self.ext_reg_params.value = False
        self.ang_corr.value = False
        self.ang_corr_range.value = 2.0
        self.op_status.value = ""
        for widget in self.key_widgets:
            widget.enabled = False
        self.data_type.enabled = True
        self.tomo_tplt_fn.enabled = True

    def __reset_run_states(self):
        if self.skip_auto_cen.value:
            pass
        else:
            self._test_run_done = False
            self._continue_run_confirmed = False

    def __reset_run_buttons(self):
        if not self.skip_auto_cen.value:
            self.test_run.enabled = True
            if self._test_run_done:
                self.confirm_test_run.enabled = True
            else:
                self.confirm_test_run.enabled = False
                self.confirm_test_run.value = "No"
                self._continue_run_confirmed = False
            if self._continue_run_confirmed:
                self.reg_run.enabled = True
            else:
                self.reg_run.enabled = False

    def __reset_data_states(self):
        self.rec_fntpl = None

        self._2dxanes_data_ready = False
        if self._2dxanes_fn_p is not None:
            self._2dxanes_fn_p.close()
            self._2dxanes_fn_p = None
        self._2dxanes_fn = None
        if self._2dxanes_reg_fn_p is not None:
            self._2dxanes_reg_fn_p.close()
            self._2dxanes_reg_fn_p = None
        self._2dxanes_reg_fn = None

    def __close_file(self):
        if self._2dxanes_reg_fn_p is not None:
            self._2dxanes_reg_fn_p.close()
            self._2dxanes_reg_fn = None
        if self._2dxanes_fn_p is not None:
            self._2dxanes_fn_p.close()
            self._2dxanes_fn_p = None
        rm_gui_viewers(self.viewer, self._viewers)

    def _sel_in_data_type(self):
        if "3D XANES" in self.data_type.value:
            self.tomo_tplt_fn.filter = "*.json"
            self.__3dxanes_widgets_logic()
        else:
            self.tomo_tplt_fn.filter = "*.h5"
            self.__2dxanes_widgets_logic()
        self.tomo_tplt_fn.value = "''"

    @disp_progress_info("data directory info read")
    def _xanes_set_fn(self):
        self.__reset_run_states()
        self.__reset_run_buttons()
        self.__reset_data_states()
        self.__close_file()
        self.__init_widgets()
        try:
            if self.data_type.value == "3D XANES":
                self._tomo_tplt_fn = self.tomo_tplt_fn.value
                cfg_type = check_cfg_type(self._tomo_tplt_fn)
                if cfg_type in ["xanes3d_tomo_tplt", "xanes3d_reg"]:
                    with open(self._tomo_tplt_fn, "r") as f:
                        tem = json.load(f)
                        if cfg_type == "xanes3d_tomo_tplt":  
                            self.ref_scan_id.value = list(tem.keys())[0]
                            batch_ids = []
                        elif cfg_type == "xanes3d_reg":
                            batch_ids = tem.keys()
                            for ii in batch_ids:
                                if tem[ii]["ref_scn_id"]:
                                    self.ref_scan_id.value = ii                             
                        self._ref_rec_tplt = tem[list(tem.keys())[0]]

                    if (
                        "tomo_zfly"
                        in self._ref_rec_tplt["file_params"]["io_confg"][
                            "tomo_raw_fn_template"
                        ]
                    ):
                        self._tomo_cfg = ZFLY_CFG["io_data_structure_xanes3D"]
                    elif (
                        "fly_scan"
                        in self._ref_rec_tplt["file_params"]["io_confg"][
                            "tomo_raw_fn_template"
                        ]
                    ):
                        self._tomo_cfg = FLY_CFG["io_data_structure_xanes3D"]
                    
                    self.__3dxanes_comp_tomo_fntpl()
                    self.__3dxanes_tomo_check_avail_id_s(cfg_type, batch_ids=batch_ids)
                    self.__3dxanes_tomo_check_avail_id_e(cfg_type, batch_ids=batch_ids)
                    self.__3dxanes_set_scan_id_lims()
                    self.__3dxanes_set_roi_lims()
                    self.__3dxanes_widgets_logic()
                    if (self.rec_fntpl is None) or (
                        not Path(
                            str(self.rec_fntpl).format(
                                self.ref_scan_id.value,
                                str(self.ref_sli.value).zfill(5),
                            )
                        ).exists()
                    ):
                        self.__3dxanes_tomo_show_sli(mode="auto_cen")
                else:
                    self.op_status.value = (
                        "wrong type of json cfg file. check error message in terminal"
                    )
                    print(
                        "The required json file should have file name starting with 'xanes3d_tomo_tplt_cfg'."
                    )
            elif self.data_type.value == "APS 3D XANES":
                _cfg = deepcopy(APS_TXM_CFG)
                self._tomo_tplt_fn = self.tomo_tplt_fn.value
                cfg_type = check_cfg_type(self._tomo_tplt_fn)
                if cfg_type in ["xanes3d_tomo_tplt", "xanes3d_reg"]:
                    with open(self._tomo_tplt_fn, "r") as f:
                        tem = json.load(f)
                        if cfg_type == "xanes3d_tomo_tplt":  
                            self.ref_scan_id.value = list(tem.keys())[0]
                            batch_ids = []
                        elif cfg_type == "xanes3d_reg":
                            batch_ids = tem.keys()
                            for ii in batch_ids:
                                if tem[ii]["ref_scn_id"]:
                                    self.ref_scan_id.value = ii                             
                        self._ref_rec_tplt = tem[list(tem.keys())[0]]
                    fn_tplt = Path(
                        tem[list(tem.keys())[0]]["file_params"]["io_confg"][
                            "tomo_raw_fn_template"
                        ]
                    ).stem.rsplit("_", maxsplit=1)[0]
                    self._tomo_cfg = mk_aps_cfg(fn_tplt, _cfg, dtype="APS 3D XANES")[
                        "io_data_structure_xanes3D"
                    ]
                    self.__3dxanes_comp_tomo_fntpl()
                    self.__3dxanes_tomo_check_avail_id_s(cfg_type, batch_ids=batch_ids)
                    self.__3dxanes_tomo_check_avail_id_e(cfg_type, batch_ids=batch_ids)
                    self.__3dxanes_set_scan_id_lims()
                    self.__3dxanes_set_roi_lims()
                    self.__3dxanes_widgets_logic()
                    if (self.rec_fntpl is None) or (
                        not Path(
                            str(self.rec_fntpl).format(
                                self.ref_scan_id.value,
                                str(self.ref_sli.value).zfill(5),
                            )
                        ).exists()
                    ):
                        self.__3dxanes_tomo_show_sli(mode="auto_cen")
                else:
                    self.op_status.value = (
                        "wrong type of json cfg file. check error message in terminal"
                    )
                    print(
                        "The required json file should have file name starting with 'xanes3d_tomo_tplt_cfg'."
                    )
            elif self.data_type.value == "2D XANES":
                self._2dxanes_cfg = ZFLY_CFG["io_data_structure_xanes2D"]
                self._2dxanes_fn = self.tomo_tplt_fn.value
                self.__2dxanes_check_in_file()
                self.__2dxanes_widgets_logic()
                if self._2dxanes_data_ready:
                    self.__2dxanes_set_roi_lims()
                    self.__2dxanes_show_sli(mode="auto_reg")
                    _min = (
                        self.viewer.layers["xanes_raw_viewer"]
                        .data[self.ref_sli.value]
                        .min()
                    )
                    _max = (
                        self.viewer.layers["xanes_raw_viewer"]
                        .data[self.ref_sli.value]
                        .max()
                    )
                    rng = _max - _min
                    self.viewer.layers["xanes_raw_viewer"].contrast_limits = [
                        _min + 0.1 * rng,
                        _max - 0.1 * rng,
                    ]
            elif self.data_type.value == "APS 2D XANES":
                self._2dxanes_cfg = APS_TXM_CFG["io_data_structure_xanes2D"]
                self._2dxanes_fn = self.tomo_tplt_fn.value
                self.__2dxanes_check_in_file()
                self.__2dxanes_widgets_logic()
                if self._2dxanes_data_ready:
                    self.__2dxanes_set_roi_lims()
                    self.__2dxanes_show_sli(mode="auto_reg")
                    _min = (
                        self.viewer.layers["xanes_raw_viewer"]
                        .data[self.ref_sli.value]
                        .min()
                    )
                    _max = (
                        self.viewer.layers["xanes_raw_viewer"]
                        .data[self.ref_sli.value]
                        .max()
                    )
                    rng = _max - _min
                    self.viewer.layers["xanes_raw_viewer"].contrast_limits = [
                        _min + 0.1 * rng,
                        _max - 0.1 * rng,
                    ]
        except Exception as e:
            self.op_status.value = "Invalide file!"
            print(e)

    def _xanes_tomo_auto_cen_roix(self):
        if "3D XANES" in self.data_type.value:
            if (self.rec_fntpl is not None) and (
                Path(
                    str(self.rec_fntpl).format(
                        self.ref_scan_id.value,
                        str(self.ref_sli.value).zfill(5),
                    )
                ).exists()
            ):
                overlap_roi(self.viewer, self, mode="auto_cen")
                show_layers_in_viewer(self.viewer, ["xanes_raw_viewer", "auto_cen_roi"])
        else:
            if self._2dxanes_data_ready:
                overlap_roi(self.viewer, self, mode="auto_cen")
                show_layers_in_viewer(self.viewer, ["xanes_raw_viewer", "auto_cen_roi"])
        self.__reset_run_states()
        self.__reset_run_buttons()

    def _xanes_tomo_auto_cen_roiy(self):
        if "3D XANES" in self.data_type.value:
            if (self.rec_fntpl is not None) and (
                Path(
                    str(self.rec_fntpl).format(
                        self.ref_scan_id.value,
                        str(self.ref_sli.value).zfill(5),
                    )
                ).exists()
            ):
                overlap_roi(self.viewer, self, mode="auto_cen")
                show_layers_in_viewer(self.viewer, ["xanes_raw_viewer", "auto_cen_roi"])
        else:
            if self._2dxanes_data_ready:
                overlap_roi(self.viewer, self, mode="auto_cen")
                show_layers_in_viewer(self.viewer, ["xanes_raw_viewer", "auto_cen_roi"])
        self.__reset_run_states()
        self.__reset_run_buttons()

    def _xanes_tomo_auto_cen_ref_sli(self):
        if "3D XANES" in self.data_type.value:
            if (self.rec_fntpl is not None) and (
                Path(
                    str(self.rec_fntpl).format(
                        self.ref_scan_id.value,
                        str(self.ref_sli.value).zfill(5),
                    )
                ).exists()
            ):
                if not self.opt_reg_roi.value:
                    if self.ref_sli.value < self.rec_roiz.value[0]:
                        self.ref_sli.value = self.rec_roiz.value[0]
                    if self.ref_sli.value > self.rec_roiz.value[1]:
                        self.ref_sli.value = self.rec_roiz.value[1]
                
                self.__3dxanes_tomo_show_sli(mode="auto_cen")
                overlap_roi(self.viewer, self, mode="auto_cen")
                show_layers_in_viewer(self.viewer, ["xanes_raw_viewer", "auto_cen_roi"])
        else:
            if self._2dxanes_data_ready:
                self.__2dxanes_show_sli(mode="auto_reg")
                overlap_roi(self.viewer, self, mode="auto_cen")
                show_layers_in_viewer(self.viewer, ["xanes_raw_viewer", "auto_cen_roi"])
        self.__reset_run_states()
        self.__reset_run_buttons()

    def _xanes_tomo_rec_roix(self):
        if "3D XANES" in self.data_type.value:
            if (self.rec_fntpl is not None) and (
                Path(
                    str(self.rec_fntpl).format(
                        self.ref_scan_id.value,
                        str(self.ref_sli.value).zfill(5),
                    )
                ).exists()
            ):
                overlap_roi(self.viewer, self, mode="recon_roi")
                show_layers_in_viewer(self.viewer, ["xanes_raw_viewer", "recon_roi"])
        else:
            if self._2dxanes_data_ready:
                overlap_roi(self.viewer, self, mode="recon_roi")
                show_layers_in_viewer(self.viewer, ["xanes_raw_viewer", "recon_roi"])
            # self.confirm_test_run.value = "No"

    def _xanes_tomo_rec_roiy(self):
        if "3D XANES" in self.data_type.value:
            if (self.rec_fntpl is not None) and (
                Path(
                    str(self.rec_fntpl).format(
                        self.ref_scan_id.value,
                        str(self.ref_sli.value).zfill(5),
                    )
                ).exists()
            ):
                overlap_roi(self.viewer, self, mode="recon_roi")
                show_layers_in_viewer(self.viewer, ["xanes_raw_viewer", "recon_roi"])
        else:
            if self._2dxanes_data_ready:
                overlap_roi(self.viewer, self, mode="recon_roi")
                show_layers_in_viewer(self.viewer, ["xanes_raw_viewer", "recon_roi"])
            # self.confirm_test_run.value = "No"

    def _xanes_tomo_rec_roiz(self):
        if "3D XANES" in self.data_type.value:
            if self.rec_roiz.value[0] > (
                self.ref_sli.value - self.sli_srch_range.value
            ):
                self.rec_roiz.value = [
                    self.ref_sli.value - self.sli_srch_range.value,
                    self.rec_roiz.value[1],
                ]
            if self.rec_roiz.value[1] < (
                self.ref_sli.value + self.sli_srch_range.value
            ):
                self.rec_roiz.value = [
                    self.rec_roiz.value[0],
                    self.ref_sli.value + self.sli_srch_range.value,
                ]
            if (self.rec_fntpl is not None) and (
                Path(
                    str(self.rec_fntpl).format(
                        self.ref_scan_id.value,
                        str(self.ref_sli.value).zfill(5),
                    )
                ).exists()
            ):
                self.__3dxanes_tomo_show_sli(mode="recon_roi")
                overlap_roi(self.viewer, self, mode="recon_roi")
                show_layers_in_viewer(self.viewer, ["xanes_raw_viewer", "recon_roi"])
        else:
            if self._2dxanes_data_ready:
                self.__2dxanes_show_sli(mode="auto_algn")
                overlap_roi(self.viewer, self, mode="recon_roi")
                show_layers_in_viewer(self.viewer, ["xanes_raw_viewer", "recon_roi"])
            self.confirm_test_run.value = "No"

    def _xanes_set_ext_reg_params(self):
        if self.ext_reg_params.value:
            ans = ext_reg_params_gui(self)
            if ans.rtn:
                self._reg_smth_krnl = ans.smth_krnl_val
                self._reg_chnk_sz = ans.chnk_sz_val
            else:
                self._reg_smth_krnl = 1
                self._reg_chnk_sz = 5
        else:
            self._reg_smth_krnl = 1
            self._reg_chnk_sz = 5

    def _xanes_ang_corr(self):
        if self.ang_corr.value:
            self.ang_corr_range.enabled = True
        else:
            self.ang_corr_range.enabled = False

    @disp_progress_info("xanes auto registration test run")
    def _xanes_test_run(self):
        if "3D XANES" in self.data_type.value:
            self.__reset_run_states()
            self.__3dxanes_tomo_if_new_rec()
            self.__3dxnaes_tomo_def_autocent_cfg()
            
            sig = os.system(f"python {xanes3d_auto_cen_reg_script_fn}")
            print(f"{sig=}")

            if sig == 0:
                with open(cfg_fn, "r") as f:
                    tem = json.load(f)
                with open(tem["xanes3d_auto_cen"]["cfg_file"], "r") as f:
                    tem = json.load(f)
                trial_imgs = []
                with h5py.File(
                    tem["aut_xns3d_pars"]["xanes3d_sav_trl_reg_fn"], "r"
                ) as f:
                    for key in f["/auto_centering/"].keys():
                        trial_imgs.append(
                            f[f"/auto_centering/{key}/optimization itr 1/trial_rec"][:]
                        )
                update_layer_in_viewer(
                    self.viewer, np.array(trial_imgs), "autocent_check", data_type="image"
                )
                show_layers_in_viewer(self.viewer, ["autocent_check"])
                self._test_run_done = True
            else:
                self._test_run_done = False
                self.op_status.value = "auto centering fails"
                print("auto centering fails")
            self.confirm_test_run.value == "No"
            self._continue_run_confirmed = False
            self.__reset_run_buttons()
        elif "2D XANES" in self.data_type.value:
            self.__reset_run_states()
            self.__2dxanes_check_if_new_reg()
            self.__2dxanes_def_img_autoreg_cfg()

            if self._2dxanes_if_new_reg:
                if self.data_type.value == "2D XANES":
                    sig = os.system(f"python {xanes2d_img_auto_reg_script_fn}")
                elif self.data_type.value == "APS 2D XANES":
                    sig = os.system(f"python {aps_xanes2d_img_auto_reg_script_fn}")

                if sig == 0:
                    with open(cfg_fn, "r") as f:
                        tem = json.load(f)
                    with open(tem["xanes2d_reg"]["cfg_file"], "r") as f:
                        tem = json.load(f)
                    if self._2dxanes_reg_fn_p is None:
                        self._2dxanes_reg_fn_p = h5py.File(tem["file"]["sav_fn"], "r")
                    else:
                        self._2dxanes_reg_fn_p.close()
                        self._2dxanes_reg_fn_p = h5py.File(tem["file"]["sav_fn"], "r")

                    reg_rlt = da.from_array(
                        self._2dxanes_reg_fn_p[
                            "/registration_results/reg_results/registered_xanes2D"
                        ]
                    )
                    update_layer_in_viewer(self.viewer, reg_rlt, "autoreg_check", data_type="image")
                    show_layers_in_viewer(self.viewer, ["autoreg_check"])
                    self._test_run_done = True
                else:
                    self._test_run_done = False
                    self.op_status.value = "auto alignment fails"
                    print("auto alignment fails")
                self.confirm_test_run.value == "No"
                self._continue_run_confirmed = False
                self.__2dxanes_set_roi_widgets()
                self.__reset_run_buttons()
            else:
                self.op_status.value = "Nothing is changed from last auto-registration."
                print("Nothing is changed from last auto-registration.")

    def _xanes_confirm_to_run(self):
        if self.confirm_test_run.value == "Yes":
            self._continue_run_confirmed = True
            if "3D XANES" in self.data_type.value:
                self.reg_run.enabled = True
            else:
                self.__2dxanes_set_roi_widgets()
                if (self.auto_cen_roix.value == self.rec_roix.value) and (
                    self.auto_cen_roiy.value == self.rec_roiy.value
                ):
                    self.reg_run.enabled = False
                    self.op_status.value = (
                        "2D XANES registration is done! Nothing is left in this page."
                    )
                    print(
                        "2D XANES registration is done! Nothing is left in this page."
                    )
                else:
                    self.reg_run.enabled = True
        else:
            self._continue_run_confirmed = False
            if "3D XANES" in self.data_type.value:
                if not self.skip_auto_cen.value:
                    self.reg_run.enabled = False
            else:
                self.__2dxanes_set_roi_widgets()

    @disp_progress_info("xanes auto registration")
    def _xanes_reg_run(self):
        if "3D XANES" in self.data_type.value:
            self.__3dxanes_tomo_if_new_rec()
            self.__3dxnaes_tomo_def_autocent_cfg()            
            
            sig = os.system(f"python {xanes3d_auto_cen_reg_script_fn}")
            if sig == 0:
                self.op_status.value = "autocen and registration are finished. please check the results in 'XANES Analysis'."
                print(
                    "autocen and registration are finished. please check the results in 'XANES Analysis'."
                )
            else:
                self.op_status.value = (
                    "something went wrong during autocen or registration processes."
                )
                print("something went wrong during autocen or registration processes.")
                self.reg_run.enabled = False
        else:
            self.__2dxanes_def_img_autoreg_cfg()
            self.__2dxanes_check_if_new_align()

            if self._2dxanes_if_new_align:
                rm_gui_viewers(self.viewer, ["autocent_check"])
                if self._2dxanes_reg_fn_p is not None:
                    self._2dxanes_reg_fn_p.close()

                if self.data_type.value == "2D XANES":
                    sig = os.system(f"python {xanes2d_img_auto_reg_script_fn}")
                elif self.data_type.value == "APS 2D XANES":
                    sig = os.system(f"python {aps_xanes2d_img_auto_reg_script_fn}")

                if sig == 0:
                    with open(cfg_fn, "r") as f:
                        tem = json.load(f)
                    with open(tem["xanes2d_reg"]["cfg_file"], "r") as f:
                        tem = json.load(f)
                    if self._2dxanes_reg_fn_p is None:
                        self._2dxanes_reg_fn_p = h5py.File(tem["file"]["sav_fn"], "r")
                    else:
                        self._2dxanes_reg_fn_p.close()
                        self._2dxanes_reg_fn_p = h5py.File(tem["file"]["sav_fn"], "r")

                    reg_rlt = da.from_array(
                        self._2dxanes_reg_fn_p[
                            "/registration_results/reg_results/registered_xanes2D"
                        ]
                    )
                    update_layer_in_viewer(self.viewer, reg_rlt, "autocent_check", data_type="image")
                    show_layers_in_viewer(self.viewer, ["autocent_check"])
                else:
                    self._test_run_done = False
                    self.op_status.value = "Alignment fails"
                    print("Alignment fails")
            else:
                self.op_status.value = "Nothing is changed from last alignment."
                print("Nothing is changed from last alignment.")

    def _close(self):
        self.tomo_tplt_fn.value = ""
        self._3dxanes_new_rec_info = ""
        self._tomo_tplt_fn_old_val = ""
        self._scn_id_s_old_val = ""
        self._scn_id_e_old_val = ""
        self._3dxanes_rec_roix_old_val = ""
        self._3dxanes_rec_roiy_old_val = ""
        self._3dxanes_rec_roiz_old_val = ""

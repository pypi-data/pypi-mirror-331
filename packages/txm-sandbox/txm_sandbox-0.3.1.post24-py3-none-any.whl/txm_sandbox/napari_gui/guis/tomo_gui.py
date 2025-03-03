import numpy as np
import os
import sys
from copy import deepcopy

import json
import glob
import h5py
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from magicgui import widgets

from qtpy import QtCore

from ...utils.io import data_reader, tomo_h5_reader
from ...utils.tomo_recon_tools import rm_redundant
from ...gui.gui_components import (
    check_file_availability,
)
from ..utils.misc import (
    set_data_widget,
    rm_gui_viewers,
    disp_progress_info,
    info_reader,
    update_layer_in_viewer,
    show_layers_in_viewer,
)
from ...dicts.data_struct_dict import ZFLY_CFG, FLY_CFG, APS_TXM_CFG

from ..utils.ext_io_lib import show_io_win, mk_aps_cfg, scan_info_gui, get_scan_info


h5_reader = data_reader(tomo_h5_reader)

cfg_fn = Path(__file__).parents[1] / "configs/txm_simple_gui_script_cfg.json"
tomo_rec_script_fn = Path(__file__).parents[1] / "scripts/tomo_recon_cmd.py"
tomo_batch_rec_script_fn = Path(__file__).parents[1] / "scripts/tomo_batch_recon_cmd.py"
xanes3d_auto_cen_reg_script_fn = (
    Path(__file__).parents[1] / "scripts/xanes3d_tomo_autocent_cmd.py"
)
xanes3d_fit_script_fn = Path(__file__).parents[1] / "scripts/xanes3D_fit_cmd.py"

with open(Path(__file__).parents[1] / "configs/xanes3d_tomo_template_cfg.json") as f:
    xanes3d_tomo_tplt_cfg = json.load(f)

with open(Path(__file__).parents[1] / "configs/xanes3d_tomo_autocent_cfg.json") as f:
    xanes3d_tomo_autocen_cfg = json.load(f)

with open(Path(__file__).parents[1] / "configs/xanes_proc_data_struct_cfg.json") as f:
    xanes_proc_data_struct = json.load(f)


_TOMO_TRL_SCN_ID_CHOICES = []


def get_self_avail_scn_id_choices(ComboBox):
    global _TOMO_TRL_SCN_ID_CHOICES
    return _TOMO_TRL_SCN_ID_CHOICES


################################################################################
#             do trial recon for a single slice of a given scan                #
################################################################################
class tomo_gui(QtCore.QObject):
    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self._io_win_dir = ""
        self._tomo_cfg = ZFLY_CFG["io_data_structure_tomo"]
        self._scn_fn = None
        self._xanes3d_ref_scn_id = None
        self._wedge_data_avg = 0
        self._trial_cen_rec_done = False
        self._multi_trial_cen_rec_done = False
        self._cen = None
        self._wedge_autodet_fig = None
        self._viewers = ["proj_prev", "data_center", "tomo_viewer"]

        self.label0 = widgets.Label(
            value="-------------------     Tomo Recon    --------------------",
        )
        self.label1 = widgets.Label(
            name="Step 1",
            value="--------------------     Trial Cen    --------------------",
        )
        self.top_dir = widgets.FileEdit(mode="d", value=Path.home())
        self.file_type = widgets.ComboBox(
            choices=["tomo_zfly", "fly_scan", "APS_tomo"],
            value="tomo_zfly",
            name="scan type",
        )
        self.find_multi_cen = widgets.CheckBox(
            value=False, text="find cen for multiple scans", enabled=False
        )
        self._scan_id_box = widgets.HBox()
        self.scan_id = widgets.ComboBox(
            enabled=False, choices=get_self_avail_scn_id_choices, name="scan id"
        )
        self.scan_id_info = widgets.PushButton(text="info card", enabled=False)
        self._scan_id_box.append(self.scan_id)
        self._scan_id_box.append(widgets.Label(value="    "))
        self._scan_id_box.append(self.scan_id_info)
        self._scan_id_box.native.setStyleSheet("""
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
        self.set_ref_id = widgets.PushButton(
            text="set as ref scan", enabled=False,
            tooltip="set current scan as the reference scan for XANES3D registration"
        )
        self.rm_ref_id = widgets.PushButton(
            text="remove set ref scan", enabled=False,
            tooltip="remove the previous set reference scan id; you can remove the ref scan id anytime even the current scan id is different from the previous set reference scan id"
        )
        self.proj_prev = widgets.CheckBox(value=False, text="proj prev", enabled=False)
        self.cen_sch_s = widgets.SpinBox(
            min=1, max=2500, value=600, step=1, enabled=False, name="cen srch s"
        )
        self.ref_sli = widgets.SpinBox(
            min=1, max=2560, value=540, step=1, enabled=False, name="ref sli"
        )
        self.is_wedge = widgets.CheckBox(value=False, text="is wedge", enabled=False)
        self.wedge_thsh = widgets.FloatSpinBox(
            min=0, max=1, step=0.05, value=0.1, enabled=False, name="wedge thrsh"
        )
        self.phase_retrieval = widgets.CheckBox(
            value=False, text="use phase retrieval filter", enabled=False
        )
        self.beta_gamma_ratio = widgets.LineEdit(
            value=0.01, label="beta / gamma", enabled=False
        )
        self.trial_cen_rec = widgets.PushButton(
            text="trial center recon", enabled=False
        )
        self.label2 = widgets.Label(
            name="Step 2",
            value="--------------------     Vol Recon    --------------------",
        )
        self.cen = widgets.LineEdit(name="picked cen", enabled=False)
        self.pick_cen = widgets.PushButton(text="pick center", enabled=False)
        self.trial_cen_done = widgets.RadioButtons(
            name="trial cen done",
            choices=["Yes", "No"],
            orientation="horizontal",
            value="No",
            tooltip="confirm if all trial centering works are finished",
            enabled=False,
        )
        self.vol_rec = widgets.PushButton(text="vol recon", enabled=False)
        self.close = widgets.PushButton(text="close", enabled=False)
        self.op_status = widgets.LineEdit(name="operation status", enabled=False)

        self.file_type.changed.connect(self._sel_in_file_type)
        self.top_dir.changed.connect(self._sel_top_dir)
        self.find_multi_cen.changed.connect(self._find_multi_cen)
        self.scan_id.changed.connect(self._sel_scn_id)
        self.scan_id_info.changed.connect(self._scan_id_info)
        self.set_ref_id.changed.connect(self._set_ref_scn_id)
        self.rm_ref_id.changed.connect(self._rm_ref_scn_id)
        self.proj_prev.changed.connect(self._proj_prev)
        self.is_wedge.changed.connect(self._is_wedge)
        self.wedge_thsh.changed.connect(self._set_wedge_thsh)
        self.phase_retrieval.changed.connect(self._use_phase_retrieval)
        self.trial_cen_rec.changed.connect(self._trial_cen_rec)
        self.cen.changed.connect(self._cen_chgd)
        self.pick_cen.changed.connect(self._pick_cen)
        self.trial_cen_done.changed.connect(self._trial_cen_done)
        self.vol_rec.changed.connect(self._vol_rec)
        self.close.changed.connect(self._close)

        self.gui_layout = widgets.VBox(
            widgets=[
                self.label0,
                self.label1,
                self.file_type,
                self.top_dir,
                self.find_multi_cen,
                self._scan_id_box,
                self.set_ref_id,
                self.rm_ref_id,
                self.proj_prev,
                self.cen_sch_s,
                self.ref_sli,
                self.is_wedge,
                self.wedge_thsh,
                self.phase_retrieval,
                self.beta_gamma_ratio,
                self.trial_cen_rec,
                self.label2,
                self.cen,
                self.pick_cen,
                self.trial_cen_done,
                self.vol_rec,
                self.close,
                self.op_status,
            ]
        )

        self.key_widgets = [
            self.find_multi_cen,
            self.scan_id, 
            self.scan_id_info,
            self.set_ref_id,
            self.rm_ref_id,
            self.proj_prev,
            self.cen_sch_s,
            self.ref_sli,
            self.is_wedge,
            self.wedge_thsh,
            self.phase_retrieval,
            self.beta_gamma_ratio,
            self.trial_cen_rec,
            self.cen,
            self.pick_cen,
            self.trial_cen_done,
            self.vol_rec,
            self.close,
            self.op_status,
        ]

        self.scan_info_popup = scan_info_gui()

    @disp_progress_info("data directory info read")
    def __check_avail_data(self):
        global _TOMO_TRL_SCN_ID_CHOICES
        ids = check_file_availability(
            str(self.top_dir.value),
            scan_id=None,
            signature=self._tomo_cfg["tomo_raw_fn_template"],
            return_idx=True,
        )
        if ids:
            _TOMO_TRL_SCN_ID_CHOICES = ids
        else:
            _TOMO_TRL_SCN_ID_CHOICES = []
        self.scan_id.reset_choices()

    def __comp_scn_fn(self):
        if self.scan_id.value:
            if self.file_type.value == "APS_tomo":
                self._scn_fn = self.top_dir.value / self._tomo_cfg[
                    "tomo_raw_fn_template"
                ].format(str(self.scan_id.value).zfill(3))
            else:
                self._scn_fn = self.top_dir.value / self._tomo_cfg[
                    "tomo_raw_fn_template"
                ].format(self.scan_id.value)
        else:
            self._scn_fn = None

    def __set_trial_cen_rec_widgets(self):
        print(f"__set_trial_cen_rec_widgets: {self._scn_fn=}")
        if (self._scn_fn is None) or (not self._scn_fn.exists()):
            self.__init_widgets()
            self.__reset_data_states()
            self.__reset_run_states()
            self.__close_file()
        else:
            self.find_multi_cen.enabled = True
            self.scan_id.enabled = True
            self.scan_id_info.enabled = True
            self.proj_prev.enabled = True
            self.cen_sch_s.enabled = True
            self.ref_sli.enabled = True
            self.is_wedge.enabled = True
            if self.is_wedge.value:
                self.wedge_thsh.enabled = True
            else:
                self.wedge_thsh.enabled = False
            self.phase_retrieval.enabled = True
            if self.phase_retrieval.value:
                self.beta_gamma_ratio.enabled = True
            else:
                self.beta_gamma_ratio.enabled = False
            if self.find_multi_cen.value:
                self.trial_cen_done.enabled = True
            else:
                self.trial_cen_done.enabled = False

            self.trial_cen_rec.enabled = True
            self.close.enabled = True
            self.__preset_dflt()

    def __set_vol_rec_widgets(self):
        if self.find_multi_cen.value:
            self.set_ref_id.enabled = True
            self.rm_ref_id.enabled = True
            if self._trial_cen_rec_done:
                self.pick_cen.enabled = True
            else:
                self.pick_cen.enabled = False
            if self._multi_trial_cen_rec_done:
                self.vol_rec.enabled = True
            else:
                self.vol_rec.enabled = False
        else:
            self.set_ref_id.enabled = False
            self.rm_ref_id.enabled = False
            if self._trial_cen_rec_done:
                self.pick_cen.enabled = True
            else:
                self.pick_cen.enabled = False
            if self._cen is None:
                self.vol_rec.enabled = False
            else:
                self.vol_rec.enabled = True
            self.trial_cen_done.enabled = False
        self.close.enabled = True

    def __preset_dflt(self):
        self._data_dim = info_reader(self._scn_fn, dtype="data", cfg=self._tomo_cfg)
        if (not self.find_multi_cen.value) or (
            (self._data_dim[2] / 2 - self.cen_sch_s.value) > (self._data_dim[2] / 6)
        ):
            self.cen_sch_s.value = int(self._data_dim[2] / 2 - 40)
        self.ref_sli.value = int(self._data_dim[1] / 2)

    def __reset_data_states(self):
        self._scn_fn = None
        self._wedge_data_avg = 0
        self._cen = None
        self._wedge_autodet_fig = None
        self._trial_cen_dir = None

    def __reset_run_states(self):
        self._trial_cen_rec_done = False
        self._multi_trial_cen_rec_done = False

    def __init_widgets(self):
        set_data_widget(
            self.cen_sch_s,
            1,
            600,
            2500,
        )
        set_data_widget(
            self.ref_sli,
            1,
            540,
            2560,
        )
        self.find_multi_cen.value = False
        self.proj_prev.value = False
        self.is_wedge.value = False
        self.phase_retrieval.value = False
        self.wedge_thsh.value = 0.1
        self.beta_gamma_ratio.value = 0.01
        self.cen.value = ""
        self.trial_cen_done.value = "No"
        global _TOMO_TRL_SCN_ID_CHOICES
        _TOMO_TRL_SCN_ID_CHOICES = []
        self.scan_id.reset_choices()
        for widget in self.key_widgets:
            widget.enabled = False
        self.top_dir.enabled = True
        self.file_type.enabled = True

    def __close_file(self):
        if self._wedge_autodet_fig is not None:
            plt.close(self._wedge_autodet_fig)
        rm_gui_viewers(self.viewer, self._viewers)

    def _sel_in_file_type(self):
        self.__init_widgets()
        self.__reset_data_states()
        self.__reset_run_states()
        self.__close_file()
        if self.file_type.value == "tomo_zfly":
            self._tomo_cfg = ZFLY_CFG["io_data_structure_tomo"]
            self.top_dir.enabled = True
        elif self.file_type.value == "fly_scan":
            self._tomo_cfg = FLY_CFG["io_data_structure_tomo"]
            self.top_dir.enabled = True
        elif self.file_type.value == "APS_tomo":
            _cfg = deepcopy(APS_TXM_CFG)
            name = show_io_win(dtype="APS_tomo")
            if name is not None:
                fn_tplt = name["name"].stem.rsplit("_", maxsplit=1)[0]
                self._tomo_cfg = mk_aps_cfg(fn_tplt, _cfg, dtype="APS 3D XANES")[
                    "io_data_structure_tomo"
                ]
                self.top_dir.value = name["name"].parent
                self.top_dir.enabled = False
            else:
                self.top_dir.value = "''"
                self.close.enabled = False

        self.__check_avail_data()
        self.__comp_scn_fn()
        self.__set_trial_cen_rec_widgets()
        self.__set_vol_rec_widgets()

    def _sel_top_dir(self):
        self.__init_widgets()
        self.__reset_data_states()
        self.__reset_run_states()
        self.__close_file()
        self.__check_avail_data()
        self.__comp_scn_fn()
        self.__set_trial_cen_rec_widgets()
        self.__set_vol_rec_widgets()

    def _find_multi_cen(self):
        self._xanes3d_ref_scn_id = None
        self._multi_trial_cen_rec_done = False
        self.__set_vol_rec_widgets()
        if self.find_multi_cen.value:
            with open(cfg_fn, "r") as f:
                tem = json.load(f)
                tem["tomo_batch_recon"]["cfg_file"] = str(
                    self.top_dir.value
                    / f"tomo_batch_trial_cen_cfg_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
                )
            with open(cfg_fn, "w") as f:
                json.dump(tem, f, indent=4, separators=(",", ": "))
        else:
            self._trial_cen_rec_done = False
            self.pick_cen.enabled = False
            self.vol_rec.enabled = False
            self.trial_cen_done.value = "No"

    def _sel_scn_id(self):
        self._cen = None
        self._trial_cen_rec_done = False
        self.proj_prev.value = False
        self.is_wedge.value = False
        self.__comp_scn_fn()
        self.__set_trial_cen_rec_widgets()
        self.__set_vol_rec_widgets()

    def _scan_id_info(self):
        if self._scn_fn is not None and self._tomo_cfg:
            self.scan_info_popup.set_message(message=get_scan_info(self._scn_fn, self._tomo_cfg))
            self.scan_info_popup.show()
        else:
            self.op_status.value = "Please select a valid scan id first!"

    def _set_ref_scn_id(self):
        self._xanes3d_ref_scn_id = self.scan_id.value

    def _rm_ref_scn_id(self):
        self._xanes3d_ref_scn_id = None

    @disp_progress_info("data file read")
    def _proj_prev(self):
        if self.proj_prev.value:
            rm_gui_viewers(self.viewer, ["proj_prev"])
            update_layer_in_viewer(
                self.viewer,
                h5py.File(self._scn_fn, "r")[
                    self._tomo_cfg["structured_h5_reader"]["io_data_structure"][
                        "data_path"
                    ]
                ],
                "proj_prev",
                data_type="image",
            )
            show_layers_in_viewer(self.viewer, ["proj_prev"])
        else:
            rm_gui_viewers(self.viewer, ["proj_prev"])

    @disp_progress_info("missing angle calculate")
    def _is_wedge(self):
        self._cen = None
        self._trial_cen_rec_done = False
        self.__set_vol_rec_widgets()
        if self.is_wedge.value:
            self.wedge_thsh.enabled = True

            theta = h5_reader(
                self._scn_fn, dtype="theta", sli=[None], cfg=self._tomo_cfg
            ).astype(np.float32)
            if self.file_type.value == "tomo_zfly":
                idx = np.ones(self._data_dim[0], dtype=bool)
            else:
                idx = rm_redundant(theta)
                theta = theta[idx]
                if self._data_dim[0] > theta.shape[0]:
                    idx = np.concatenate(
                        (
                            idx,
                            np.zeros(self._data_dim[0] - theta.shape[0], dtype=bool),
                        )
                    )
            data = h5_reader(
                self._scn_fn,
                dtype="data",
                sli=[
                    None,
                    [self.ref_sli.value, self.ref_sli.value + 1],
                    [0, self._data_dim[2] - 1],
                ],
                cfg=self._tomo_cfg,
            ).astype(np.float32)[idx]
            white = (
                h5_reader(
                    self._scn_fn,
                    dtype="flat",
                    sli=[
                        None,
                        [self.ref_sli.value, self.ref_sli.value + 1],
                        [0, self._data_dim[2] - 1],
                    ],
                    cfg=self._tomo_cfg,
                )
                .mean(axis=0)
                .astype(np.float32)
            )

            dark = (
                h5_reader(
                    self._scn_fn,
                    dtype="dark",
                    sli=[
                        None,
                        [self.ref_sli.value, self.ref_sli.value + 1],
                        [0, self._data_dim[2] - 1],
                    ],
                    cfg=self._tomo_cfg,
                )
                .mean(axis=0)
                .astype(np.float32)
            )

            data[:] = (data - dark[np.newaxis, :]) / (
                white[np.newaxis, :] - dark[np.newaxis, :]
            )[:]
            data[np.isinf(data)] = 0
            data[np.isnan(data)] = 0
            self._wedge_data_avg = data.mean(axis=2).astype(np.float32)

            plt.close("all")
            plt.figure(0)
            plt.plot(self._wedge_data_avg)
            plt.plot(
                np.ones(self._wedge_data_avg.shape[0]) * self.wedge_thsh.value,
            )
            plt.show()
        else:
            self.wedge_thsh.enabled = False
            self._wedge_data_avg = 0
        self.vol_rec.enabled = False

    def _set_wedge_thsh(self):
        self._cen = None
        self._trial_cen_rec_done = False
        self.__set_vol_rec_widgets()
        if self._wedge_autodet_fig is not None:
            plt.close(self._wedge_autodet_fig)
        self._wedge_autodet_fig, ax = plt.subplots()
        ax.plot(self._wedge_data_avg)
        ax.set_title("spec in roi")
        ax.plot(
            np.ones(self._wedge_data_avg.shape[0]) * self.wedge_thsh.value,
        )
        ax.set_title("wedge detection")
        plt.show()
        self.vol_rec.enabled = False

    def _use_phase_retrieval(self):
        self._cen = None
        self._trial_cen_rec_done = False
        self.__set_vol_rec_widgets()
        if self.phase_retrieval.value:
            self.beta_gamma_ratio.enabled = True
        else:
            self.beta_gamma_ratio.enabled = False
        self.vol_rec.enabled = False

    @disp_progress_info("trial center reconstruction")
    def _trial_cen_rec(self):
        if self.find_multi_cen.value:
            with open(cfg_fn, "r") as f:
                tem = json.load(f)
                tem["tomo_recon"]["cfg_file"] = str(
                    tomo_rec_script_fn.parent
                    / f"tomo_tplt_cfg.json"
                )
            with open(cfg_fn, "w") as f:
                json.dump(tem, f, indent=4, separators=(",", ": "))
        else:
            with open(cfg_fn, "r") as f:
                tem = json.load(f)
                tem["tomo_recon"]["cfg_file"] = str(
                    self.top_dir.value
                    / f"xanes3d_tomo_tplt_cfg_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
                )
            with open(cfg_fn, "w") as f:
                json.dump(tem, f, indent=4, separators=(",", ": "))

        xanes3d_tomo_tplt_cfg["scan id"]["file_params"]["raw_data_top_dir"] = str(
            self.top_dir.value
        )
        xanes3d_tomo_tplt_cfg["scan id"]["file_params"]["data_center_dir"] = str(
            self.top_dir.value / "data_center"
        )
        xanes3d_tomo_tplt_cfg["scan id"]["file_params"]["recon_top_dir"] = str(
            self.top_dir.value
        )
        xanes3d_tomo_tplt_cfg["scan id"]["file_params"]["wedge_ang_auto_det_ref_fn"] = (
            str(
                self.top_dir.value
                / self._tomo_cfg["tomo_raw_fn_template"].format(self.scan_id.value)
            )
        )

        xanes3d_tomo_tplt_cfg["scan id"]["file_params"]["io_confg"] = self._tomo_cfg
        xanes3d_tomo_tplt_cfg["scan id"]["file_params"]["hardware_trig_type"] = (
            True if self.file_type.value in ["tomo_zfly", "APS_tomo"] else False
        )

        xanes3d_tomo_tplt_cfg["scan id"]["recon_config"]["recon_type"] = "Trial Cent"
        xanes3d_tomo_tplt_cfg["scan id"]["recon_config"][
            "is_wedge"
        ] = self.is_wedge.value

        xanes3d_tomo_tplt_cfg["scan id"]["data_params"]["scan_id"] = self.scan_id.value
        xanes3d_tomo_tplt_cfg["scan id"]["data_params"][
            "rot_cen"
        ] = self.cen_sch_s.value
        xanes3d_tomo_tplt_cfg["scan id"]["data_params"][
            "cen_win_s"
        ] = self.cen_sch_s.value
        xanes3d_tomo_tplt_cfg["scan id"]["data_params"]["sli_s"] = (
            self.ref_sli.value - 10
        )
        xanes3d_tomo_tplt_cfg["scan id"]["data_params"]["sli_e"] = (
            self.ref_sli.value + 10
        )
        xanes3d_tomo_tplt_cfg["scan id"]["data_params"]["col_s"] = 0
        xanes3d_tomo_tplt_cfg["scan id"]["data_params"]["col_e"] = self._data_dim[2]
        xanes3d_tomo_tplt_cfg["scan id"]["data_params"]["wedge_col_s"] = 0
        xanes3d_tomo_tplt_cfg["scan id"]["data_params"]["wedge_col_e"] = self._data_dim[
            2
        ]
        xanes3d_tomo_tplt_cfg["scan id"]["data_params"][
            "wedge_ang_auto_det_thres"
        ] = self.wedge_thsh.value

        if self.file_type.value == "tomo_zfly":
            xanes3d_tomo_tplt_cfg["scan id"]["file_params"]["io_confg"][
                "structured_h5_reader"
            ]["io_data_structure"]["eng_path"] = ZFLY_CFG["io_data_structure_xanes3D"][
                "structured_h5_reader"
            ][
                "io_data_structure"
            ][
                "eng_path"
            ]
        elif self.file_type.value == "fly_scan":
            xanes3d_tomo_tplt_cfg["scan id"]["file_params"]["io_confg"][
                "structured_h5_reader"
            ]["io_data_structure"]["eng_path"] = FLY_CFG["io_data_structure_xanes3D"][
                "structured_h5_reader"
            ][
                "io_data_structure"
            ][
                "eng_path"
            ]
        elif self.file_type.value == "APS_tomo":
            xanes3d_tomo_tplt_cfg["scan id"]["file_params"]["io_confg"][
                "structured_h5_reader"
            ]["io_data_structure"]["eng_path"] = APS_TXM_CFG[
                "io_data_structure_xanes3D"
            ][
                "structured_h5_reader"
            ][
                "io_data_structure"
            ][
                "eng_path"
            ]

        if self.phase_retrieval.value:
            xanes3d_tomo_tplt_cfg["scan id"]["flt_params"]["2"] = {
                "filter_name": "phase retrieval",
                "params": {
                    "filter": "paganin",
                    "pad": "True",
                    "pixel_size": 6.5e-05,
                    "dist": 15.0,
                    "energy": 35.0,
                    "alpha": float(self.beta_gamma_ratio.value),
                },
            }
        else:
            if "2" in xanes3d_tomo_tplt_cfg["scan id"]["flt_params"].keys():
                del xanes3d_tomo_tplt_cfg["scan id"]["flt_params"]["2"]

        if self.find_multi_cen.value:
            try:
                with open(tem["tomo_batch_recon"]["cfg_file"], "r") as f:
                    tem1 = json.load(f)
                with open(tem["tomo_batch_recon"]["cfg_file"], "w") as f:
                    tem1[str(self.scan_id.value)] = xanes3d_tomo_tplt_cfg["scan id"]
                    json.dump(tem1, f, indent=4, separators=(",", ": "))
            except:
                with open(tem["tomo_batch_recon"]["cfg_file"], "w") as f:
                    tem1 = {}
                    tem1[str(self.scan_id.value)] = xanes3d_tomo_tplt_cfg["scan id"]
                    json.dump(tem1, f, indent=4, separators=(",", ": "))

        xanes3d_tomo_cfg = {str(self.scan_id.value): xanes3d_tomo_tplt_cfg["scan id"]}
        with open(tem["tomo_recon"]["cfg_file"], "w") as f:
            json.dump(xanes3d_tomo_cfg, f, indent=4, separators=(",", ": "))

        sig = os.system(f"python {tomo_rec_script_fn}")
        if sig == 0:
            rm_gui_viewers(self.viewer, ["data_center"])
            self._trial_cen_dir = self.top_dir.value / "data_center"
            self.viewer.open(self._trial_cen_dir)

            rng = float(self.viewer.layers["data_center"].data[0].max()) - float(
                self.viewer.layers["data_center"].data[0].min()
            )
            self.viewer.layers["data_center"].contrast_limits = [
                float(self.viewer.layers["data_center"].data[0].min()) + 0.1 * rng,
                float(self.viewer.layers["data_center"].data[0].max()) - 0.1 * rng,
            ]
            show_layers_in_viewer(self.viewer, ["data_center"])
            self._cen = None
            self._trial_cen_rec_done = True
            self.__set_vol_rec_widgets()

    def _cen_chgd(self):
        self._cen = None
        self.__set_vol_rec_widgets()

    def _pick_cen(self):
        fns = glob.glob(str(Path(self._trial_cen_dir) / "*.tiff"))
        self._trial_cens = sorted([float(Path(fn).stem) for fn in fns])
        self.cen.value = self._trial_cens[int(self.viewer.dims.point[0])]
        self._cen = float(self.cen.value)
        if self.find_multi_cen.value:
            with open(cfg_fn, "r") as f:
                batch_tplt_fn = json.load(f)["tomo_batch_recon"]["cfg_file"]
            with open(batch_tplt_fn, "r") as ft:
                tem = json.load(ft)
            with open(batch_tplt_fn, "w") as ft:
                tem[str(self.scan_id.value)]["data_params"]["rot_cen"] = self._cen
                tem[str(self.scan_id.value)]["data_params"]["sli_s"] = 0
                tem[str(self.scan_id.value)]["data_params"]["sli_e"] = self._data_dim[1]
                tem[str(self.scan_id.value)]["recon_config"]["recon_type"] = "Vol Recon"
                json.dump(tem, ft, indent=4, separators=(",", ": "))
            self.trial_cen_done.enabled = True
        else:
            with open(cfg_fn, "r") as f:
                tomo_tplt_fn = json.load(f)["tomo_recon"]["cfg_file"]
            with open(tomo_tplt_fn, "r") as ft:
                tem = json.load(ft)
            tem[list(tem.keys())[0]]["data_params"]["rot_cen"] = self._cen
            tem[list(tem.keys())[0]]["data_params"]["sli_s"] = 0
            tem[list(tem.keys())[0]]["data_params"]["sli_e"] = self._data_dim[1]
            tem[list(tem.keys())[0]]["recon_config"]["recon_type"] = "Vol Recon"
            with open(tomo_tplt_fn, "w") as ft:
                json.dump(tem, ft, indent=4, separators=(",", ": "))
            self.trial_cen_done.enabled = False

        self.__set_vol_rec_widgets()

    def _trial_cen_done(self):
        if self.trial_cen_done.value == "Yes":
            self._multi_trial_cen_rec_done = True
            with open(cfg_fn, "r") as f:
                batch_tplt_fn = json.load(f)["tomo_batch_recon"]["cfg_file"]
            with open(batch_tplt_fn, "r") as ft:
                tem = json.load(ft)
            if self._xanes3d_ref_scn_id is None:
                ids = sorted(tem.keys())
                ref_scn_id = ids[int(len(ids) / 2)]
            else:
                ref_scn_id = str(self._xanes3d_ref_scn_id)
            for ii in tem.keys():
                tem[ii]["ref_scn_id"] = True if ref_scn_id == ii else False
            with open(batch_tplt_fn, "w") as ft:
                json.dump(tem, ft, indent=4, separators=(",", ": "))
        else:
            self._multi_trial_cen_rec_done = False
        self.__set_vol_rec_widgets()

    @disp_progress_info("volume reconstruction")
    def _vol_rec(self):
        if self._cen is None:
            self.viewer.status = (
                "Please pick the best center for volume reconstruction."
            )
            print("Please pick the best center for volume reconstruction.")
        else:
            rm_gui_viewers(self.viewer, ["data_center"])

            if self.find_multi_cen.value:
                sig = os.system(f"python {tomo_batch_rec_script_fn}")
            else:
                sig = os.system(f"python {tomo_rec_script_fn}")
                if sig == 0:
                    with open(cfg_fn, "r") as f:
                        with open(json.load(f)["tomo_recon"]["cfg_file"], "r") as ft:
                            tem = json.load(ft)
                    rec_path = Path(
                        tem[list(tem.keys())[0]]["file_params"]["recon_top_dir"]
                    ) / (
                        "recon_"
                        + Path(
                            tem[list(tem.keys())[0]]["file_params"]["io_confg"][
                                "tomo_raw_fn_template"
                            ].format(list(tem.keys())[0])
                        ).stem
                    )
                    try:
                        # rm_gui_viewers(self.viewer, ["tomo_viewer"])
                        # self.viewer.open(rec_path, name="tomo_viewer")
                        # self.viewer.reset_view()
                        update_layer_in_viewer(self.viewer, rec_path, "tomo_viewer", data_type="folder")
                        show_layers_in_viewer(self.viewer, ["tomo_viewer"])
                    except Exception as e:
                        self.viewer.status = "Something is wrong. Please check terminal for more information."
                        print(str(e))

    def _close(self):
        self.top_dir.value = "''"
        self.close.enabled = False

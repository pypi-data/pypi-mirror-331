#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 21 19:33:11 2020

@author: xiao
"""

import os
import json
import shutil
import glob
from datetime import datetime
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
from scipy.ndimage import zoom

import traitlets
from ipywidgets import widgets, GridspecLayout
from collections import OrderedDict

from .gui_components import (
    SelectFilesButton,
    enable_disable_boxes,
    check_file_availability,
    get_raw_img_info,
    restart,
    fiji_viewer_state,
    fiji_viewer_on,
    fiji_viewer_off,
    gen_external_py_script,
    update_json_content,
    set_data_widget,
)
from ..utils.tomo_recon_tools import (
    read_data,
    get_file,
)
from ..dicts.customized_struct_dict import (
    TOMO_FILTERLIST,
    TOMO_RECON_PARAM_DICT,
    TOMO_FILTER_PARAM_DICT,
    TOMO_ALG_PARAM_DICT,
)
from ..utils.io import data_reader, tomo_h5_reader, data_info, tomo_h5_info


class tomo_recon_gui:
    def __init__(self, parent_h, form_sz=[650, 740]):
        self.hs = {}
        self.form_sz = form_sz
        self.global_h = parent_h

        if self.global_h.io_tomo_cfg["use_h5_reader"]:
            self.reader = data_reader(tomo_h5_reader)
            self.info_reader = data_info(tomo_h5_info)
        else:
            from ..external.user_io import user_tomo_reader, user_tomo_info_reader

            self.reader = data_reader(user_tomo_reader)
            self.info_reader = data_info(user_tomo_info_reader)

        self.tomo_recon_external_command_name = str(
            Path(self.global_h.script_dir) / "tomo_recon_external_command.py"
        )
        self.tomo_msg_on = False

        self.tomo_raw_data_top_dir_set = False
        self.tomo_recon_path_set = False
        self.tomo_data_center_path_set = False
        self.tomo_debug_path_set = False
        self.recon_finish = False
        self.tomo_xns3d_rec_ref = True
        self.tomo_xns3d_reg_rec = True
        self.tomo_xns3d_corr_ang = True
        self.auto_cen_tplt_dict_rd = False
        self.auto_cen_rec_all_sli = True
        self.auto_cen_rec = True
        self.xns3d_init_rec_done = False

        self.tomo_filepath_configured = False
        self.tomo_data_configured = False

        self.tomo_left_box_selected_flt = "phase retrieval"
        self.tomo_selected_alg = "gridrec"
        self.tomo_xns3d_reg_mode = "single"
        self.tomo_xns3d_cent_opt = "Absolute"

        self.tomo_recon_param_dict = TOMO_RECON_PARAM_DICT

        self.tomo_raw_data_top_dir = None
        self.tomo_raw_data_file_template = None
        self.tomo_data_center_path = None
        self.tomo_recon_top_dir = None
        self.tomo_debug_top_dir = None
        self.tomo_cen_list_file = None
        self.tomo_xns3d_tplt_fn = None
        self.tomo_alt_flat_file = None
        self.tomo_alt_dark_file = None
        self.tomo_recon_dir = "None"
        self.tomo_wedge_ang_auto_det_ref_fn = None

        self.tomo_recon_type = "Trial Cent"
        self.tomo_use_debug = False
        self.tomo_use_alt_flat = False
        self.tomo_use_alt_dark = False
        self.tomo_use_fake_flat = False
        self.tomo_use_fake_dark = False
        self.tomo_use_blur_flat = False
        self.tomo_use_rm_zinger = False
        self.tomo_use_mask = True
        self.tomo_use_read_config = True
        self.tomo_use_downsample = False
        self.tomo_is_wedge = False
        self.tomo_use_wedge_ang_auto_det = False
        self.tomo_use_as_xns3d_tplt = False
        self.auto_cen_use_ds = False
        self.tomo_xns3d_use_deflt_reg_sli_roi = False
        # self.tomo_read_config = False

        self.tomo_right_filter_dict = {0: {}}

        self.raw_proj_0 = None
        self.raw_proj_180 = None
        self.raw_proj = None
        self.load_raw_in_mem = False
        self.raw_is_in_mem = False
        self.tomo_trial_cen_dict_fn = None
        self.tomo_scan_id = 0
        self.tomo_ds_fac = 1
        self.tomo_rot_cen = 1280
        self.tomo_cen_win_s = 1240
        self.tomo_cen_win_w = 80
        self.tomo_fake_flat_val = 1e4
        self.tomo_fake_dark_val = 100
        self.tomo_fake_flat_roi = None
        self.tomo_sli_s = 1280
        self.tomo_sli_e = 1300
        self.tomo_col_s = 0
        self.tomo_col_e = 100
        self.tomo_chunk_sz = 200
        self.tomo_margin = 15
        self.tomo_flat_blur_kernel = 1
        self.tomo_zinger_val = 500
        self.tomo_mask_ratio = 1
        self.tomo_wedge_missing_s = 500
        self.tomo_wedge_missing_e = 600
        self.tomo_wedge_auto_ref_col_s = 0
        self.tomo_wedge_auto_ref_col_e = 10
        self.tomo_wedge_ang_auto_det_thres = 0.1
        self.data_info = {}
        self.tomo_xns3d_tplt_dict = {}
        self.tomo_xns3d_reg_chnk_sz = 5
        self.tomo_xns3d_reg_knl_sz = 0.5
        self.tomo_xns3d_sli_srch_half_wz = 10
        self.tomo_xns3d_cen_srch_half_wz = 15
        self.tomo_xns3d_corr_ang_rgn = 3
        self.auto_cen_ds_fac = 1
        self.napari_viewer = None

        self.alg_param_dict = {}

    def build_gui(self):
        #################################################################################################################
        #                                                                                                               #
        #                                                    TOMO RECON                                                 #
        #                                                                                                               #
        #################################################################################################################
        ## ## ## define TOMO_RECON_tabs layout -- start
        layout = {
            "border": "3px solid #FFCC00",
            "width": "auto",
            "height": f"{self.form_sz[0] - 136}px",
        }
        self.hs["Config&Input form"] = widgets.VBox()
        self.hs["Filter&Recon form"] = widgets.VBox()

        self.hs["Config&Input form"].layout = layout
        self.hs["Filter&Recon form"].layout = layout

        ## ## ## define boxes in config_input_form -- start
        ## ## ## ## define functional widget tabs in each sub-tab - configure file settings -- start
        self.hs["CfgInpt&Rev acc"] = widgets.Accordion(
            layout={
                "width": "auto",
                "height": "auto",
                "border": "3px solid #8855AA",
                "align-content": "center",
                "align-items": "center",
                "justify-content": "center",
            }
        )

        layout = {
            "border": "3px solid #8855AA",
            "width": "auto",
            "height": "auto",
        }
        self.hs["SelFile&Path box"] = widgets.VBox()
        self.hs["SelFile&Path box"].layout = layout

        ## ## ## ## ## label configure file settings box
        layout = {"border": "3px solid #FFCC00", "width": "auto", "height": "auto"}
        self.hs["SelFile&PathTitle box"] = widgets.HBox()
        self.hs["SelFile&PathTitle box"].layout = layout
        self.hs["SelFile&PathTitle label"] = widgets.HTML(
            value='<b><p style="font-weight: bold; font-size: 125%; color: green; background-color: lightblue; text-align:center">Config Dirs & Files</p></b>',
            layout={"height": "90%", "width": "100%"},
        )
        layout = {"background-color": "white", "color": "cyan", "left": "40%"}
        self.hs["SelFile&PathTitle label"].layout = layout
        self.hs["SelFile&PathTitle box"].children = [self.hs["SelFile&PathTitle label"]]

        ## ## ## ## ## raw h5 top directory
        layout = {"border": "3px solid #FFCC00", "width": "auto", "height": "auto"}
        self.hs["SelRaw box"] = widgets.HBox()
        self.hs["SelRaw box"].layout = layout
        self.hs["SelRawH5TopDir text"] = widgets.Text(
            value="Choose raw h5 top dir ...", description="", disabled=True
        )
        layout = {"width": "66%", "display": "inline_flex"}
        self.hs["SelRawH5TopDir text"].layout = layout
        self.hs["SelRawH5TopDir btn"] = SelectFilesButton(
            option="askdirectory", text_h=self.hs["SelRawH5TopDir text"]
        )
        self.hs["SelRawH5TopDir btn"].description = "Raw Top Dir"
        self.hs["SelRawH5TopDir btn"].description_tooltip = (
            "Select the top directory in which the raw h5 files are located."
        )
        layout = {"width": "15%"}
        self.hs["SelRawH5TopDir btn"].layout = layout
        self.hs["SelRawH5TopDir btn"].on_click(self.SelRawH5TopDir_btn_clk)
        self.hs["SelRaw box"].children = [
            self.hs["SelRawH5TopDir text"],
            self.hs["SelRawH5TopDir btn"],
        ]

        ## ## ## ## ##  save recon directory
        layout = {"border": "3px solid #FFCC00", "width": "auto", "height": "auto"}
        self.hs["SelSavRecon box"] = widgets.HBox()
        self.hs["SelSavRecon box"].layout = layout
        self.hs["SelSavReconDir text"] = widgets.Text(
            value="Select top directory where data_center directory will be created...",
            description="",
            disabled=True,
        )
        layout = {"width": "66%", "display": "inline_flex"}
        self.hs["SelSavReconDir text"].layout = layout
        self.hs["SelSavReconDir btn"] = SelectFilesButton(
            option="askdirectory", text_h=self.hs["SelSavReconDir text"]
        )
        self.hs["SelSavReconDir btn"].description = "Save Rec File"
        self.hs["SelSavReconDir btn"].disabled = False
        layout = {"width": "15%"}
        self.hs["SelSavReconDir btn"].layout = layout
        self.hs["SelSavReconDir btn"].on_click(self.SelSavReconDir_btn_clk)
        self.hs["SelSavRecon box"].children = [
            self.hs["SelSavReconDir text"],
            self.hs["SelSavReconDir btn"],
        ]

        ## ## ## ## ##  save debug directory
        layout = {"border": "3px solid #FFCC00", "width": "auto", "height": "auto"}
        self.hs["SelSavDebug box"] = widgets.HBox()
        self.hs["SelSavDebug box"].layout = layout
        self.hs["SelSavDebugDir text"] = widgets.Text(
            value="Debug is disabled...", description="", disabled=True
        )
        layout = {"width": "66%", "display": "inline_flex"}
        self.hs["SelSavDebugDir text"].layout = layout
        self.hs["SelSavDebugDir btn"] = SelectFilesButton(
            option="askdirectory", text_h=self.hs["SelSavDebugDir text"]
        )
        self.hs["SelSavDebugDir btn"].description = "Save Debug Dir"
        self.hs["SelSavDebugDir btn"].disabled = True
        layout = {"width": "15%"}
        self.hs["SelSavDebugDir btn"].layout = layout
        self.hs["SavDebug chbx"] = widgets.Checkbox(
            value=False, description="Save Debug", disabled=False, indent=False
        )
        layout = {"left": "1%", "width": "13%", "display": "inline_flex"}
        self.hs["SavDebug chbx"].layout = layout
        self.hs["SelSavDebugDir btn"].on_click(self.SelSavDebugDir_btn_clk)
        self.hs["SavDebug chbx"].observe(self.SavDebug_chbx_chg, names="value")
        self.hs["SelSavDebug box"].children = [
            self.hs["SelSavDebugDir text"],
            self.hs["SelSavDebugDir btn"],
            self.hs["SavDebug chbx"],
        ]

        ## ## ## ## ## confirm file configuration
        layout = {"border": "3px solid #FFCC00", "width": "auto", "height": "auto"}
        self.hs["SelFile&PathCfm box"] = widgets.HBox()
        self.hs["SelFile&PathCfm box"].layout = layout
        self.hs["SelFile&PathCfm text"] = widgets.Text(
            value="After setting directories, confirm to proceed ...",
            description="",
            disabled=True,
        )
        layout = {"width": "66%"}
        self.hs["SelFile&PathCfm text"].layout = layout
        self.hs["SelFile&PathCfm btn"] = widgets.Button(
            description="Confirm",
            tooltip="Confirm: Confirm after you finish file configuration",
        )
        self.hs["SelFile&PathCfm btn"].style.button_color = "darkviolet"
        self.hs["SelFile&PathCfm btn"].on_click(self.SelFilePathCfm_btn_clk)
        layout = {"width": "15%"}
        self.hs["SelFile&PathCfm btn"].layout = layout

        self.hs["File&PathOptn drpdn"] = widgets.Dropdown(
            value="Trial Cent",
            options=["Trial Cent", "Vol Recon", "Auto Cent", "XANES3D Tomo"],
            description="",
            disabled=False,
            description_tooltip="'Trial Cent': doing trial recon on a single slice to find rotation center; 'Vol Recon': doing volume recon of a series of  scan datasets.",
        )
        layout = {"width": "15%", "top": "0%"}
        self.hs["File&PathOptn drpdn"].layout = layout

        self.hs["File&PathOptn drpdn"].observe(
            self.FilePathOptn_drpdn_chg, names="value"
        )
        self.hs["SelFile&PathCfm box"].children = [
            self.hs["SelFile&PathCfm text"],
            self.hs["SelFile&PathCfm btn"],
            self.hs["File&PathOptn drpdn"],
        ]

        self.hs["SelFile&Path box"].children = [
            self.hs["SelFile&PathTitle box"],
            self.hs["SelRaw box"],
            self.hs["SelSavRecon box"],
            self.hs["SelSavDebug box"],
            self.hs["SelFile&PathCfm box"],
        ]
        ## ## ## ## bin widgets in hs["SelFile&Path box"] -- configure file settings -- end

        ## ## ## ## define widgets recon_options_box -- start
        layout = {"border": "3px solid #8855AA", "width": "auto", "height": "auto"}
        self.hs["Data tab"] = widgets.Tab()
        self.hs["Data tab"].layout = layout

        ## ## ## ## ## define sub-tabs in data_tab -- start
        layout = {"border": "3px solid #FFCC00", "width": "auto", "height": "auto"}
        self.hs["DataConfig tab"] = widgets.VBox()
        self.hs["DataConfig tab"].layout = layout
        self.hs["AlgConfig tab"] = widgets.VBox()
        self.hs["AlgConfig tab"].layout = layout
        self.hs["DataInfo tab"] = widgets.VBox()
        self.hs["DataInfo tab"].layout = layout
        self.hs["DataPrev tab"] = widgets.VBox()
        self.hs["DataPrev tab"].layout = layout
        self.hs["VolRecon tab"] = widgets.VBox()
        self.hs["VolRecon tab"].layout = layout
        self.hs["Data tab"].children = [
            self.hs["DataConfig tab"],
            self.hs["AlgConfig tab"],
            self.hs["DataInfo tab"],
            self.hs["DataPrev tab"],
            self.hs["VolRecon tab"],
        ]
        self.hs["Data tab"].titles = [
            "||..Data Config..|",
            "|..Alg Config..|",
            "|..Data Info..|",
            "|..Data Preview..|",
            "|..View Recon..||",
        ]
        """self.hs["Data tab"].set_title(0, "Data Config")
        self.hs["Data tab"].set_title(1, "Alg Config")
        self.hs["Data tab"].set_title(2, "Data Info")
        self.hs["Data tab"].set_title(3, "Data Preview")
        self.hs["Data tab"].set_title(4, "View Recon")"""
        ## ## ## ## ## define sub-tabs in data_tab -- end

        ## ## ## ## ## ## config data parameters in data_config_box in data_config_tab -- start
        layout = {"border": "3px solid #FFCC00", "width": "auto", "height": "auto"}
        self.hs["DataConfig box"] = widgets.VBox()
        self.hs["DataConfig box"].layout = layout

        ## ## ## ## ## ## ## config sub-boxes in data_config_box -- start
        layout = {"border": "3px solid #FFCC00", "height": "auto"}
        self.hs["ReconConfig box"] = widgets.HBox()
        self.hs["ReconConfig box"].layout = layout
        self.hs["ScanId drpdn"] = widgets.Dropdown(
            value=0, options=[0], description="Scan id", disabled=True
        )
        layout = {"width": "19%"}
        self.hs["ScanId drpdn"].layout = layout
        self.hs["RotCen text"] = widgets.BoundedFloatText(
            value=1280.0, min=0, max=2500, description="Center", disabled=True
        )
        layout = {"width": "19%"}
        self.hs["RotCen text"].layout = layout
        self.hs["CenWinLeft text"] = widgets.BoundedIntText(
            value=1240,
            min=0,
            max=2500,
            description="Cen Win L",
            disabled=True,
            tooltip="Center search window starting position relative to the image left handside edge.",
        )
        layout = {"width": "19%"}
        self.hs["CenWinLeft text"].layout = layout
        self.hs["CenWinWz text"] = widgets.BoundedIntText(
            value=80,
            min=1,
            max=200,
            description="Cen Win W",
            disabled=True,
            tooltip="Center search window width",
        )
        layout = {"width": "19%"}
        self.hs["CenWinWz text"].layout = layout

        self.hs["ReadConfig_btn"] = SelectFilesButton(
            option="askopenfilename", **{"open_filetypes": (("json files", "*.json"),)}
        )
        layout = {"width": "15%", "height": "85%", "visibility": "hidden"}
        self.hs["ReadConfig_btn"].layout = layout
        self.hs["ReadConfig_btn"].disabled = True

        self.hs["UseConfig chbx"] = widgets.Checkbox(
            value=False,
            description="Use",
            description_tooltip="Use configuration read from the file",
            disabled=True,
            indent=False,
            layout={"width": "7%", "visibility": "hidden"},
        )

        self.hs["ScanId drpdn"].observe(self.ScanId_drpdn_chg, names="value")
        self.hs["RotCen text"].observe(self.RotCen_text_chg, names="value")
        self.hs["CenWinLeft text"].observe(self.CenWinLeft_text_chg, names="value")
        self.hs["CenWinWz text"].observe(self.CenWinWz_text_chg, names="value")
        self.hs["ReadConfig_btn"].on_click(self.ReadConfig_btn_clk)
        self.hs["UseConfig chbx"].observe(self.UseConfig_chbx_chg, names="value")
        self.hs["ReconConfig box"].children = [
            self.hs["ScanId drpdn"],
            self.hs["RotCen text"],
            self.hs["CenWinLeft text"],
            self.hs["CenWinWz text"],
            self.hs["ReadConfig_btn"],
            self.hs["UseConfig chbx"],
        ]

        layout = {"border": "3px solid #FFCC00", "height": "auto"}
        self.hs["RoiConfig box"] = widgets.HBox()
        self.hs["RoiConfig box"].layout = layout
        self.hs["RoiSliStart text"] = widgets.BoundedIntText(
            value=1280, min=0, max=2100, description="Sli Start", disabled=True
        )
        layout = {"width": "19%"}
        self.hs["RoiSliStart text"].layout = layout
        self.hs["RoiSliEnd text"] = widgets.BoundedIntText(
            value=1300, min=0, max=2200, description="Sli End", disabled=True
        )
        layout = {"width": "19%"}
        self.hs["RoiSliEnd text"].layout = layout
        self.hs["RoiColStart text"] = widgets.BoundedIntText(
            value=0, min=0, max=400, description="Col Start", disabled=True
        )
        layout = {"width": "19%"}
        self.hs["RoiColStart text"].layout = layout
        self.hs["RoiColEnd text"] = widgets.BoundedIntText(
            value=10, min=0, max=400, description="Col_End", disabled=True
        )
        layout = {"width": "19%"}
        self.hs["RoiColEnd text"].layout = layout
        self.hs["DnSampFac text"] = widgets.BoundedIntText(
            value=1, description="Down Sam R", min=1, max=10, step=1, disabled=True
        )
        layout = {"width": "19%"}
        self.hs["DnSampFac text"].layout = layout

        self.hs["RoiSliStart text"].observe(self.RoiSliStart_text_chg, names="value")
        self.hs["RoiSliEnd text"].observe(self.RoiSliEnd_text_chg, names="value")
        self.hs["RoiColStart text"].observe(self.RoiColStart_text_chg, names="value")
        self.hs["RoiColEnd text"].observe(self.RoiColEnd_text_chg, names="value")
        self.hs["DnSampFac text"].observe(self.DnSampFac_text_chg, names="value")
        self.hs["RoiConfig box"].children = [
            self.hs["RoiSliStart text"],
            self.hs["RoiSliEnd text"],
            self.hs["RoiColStart text"],
            self.hs["RoiColEnd text"],
            self.hs["DnSampFac text"],
        ]

        layout = {"border": "3px solid #FFCC00", "height": "auto"}
        self.hs["AltFlatDarkOptn box"] = widgets.HBox()
        self.hs["AltFlatDarkOptn box"].layout = layout
        layout = {"width": "24%"}
        self.hs["UseAltFlat chbx"] = widgets.Checkbox(
            value=False, description="Alt Flat", disabled=True, indent=False
        )
        self.hs["UseAltFlat chbx"].layout = layout
        layout = {"width": "15%"}
        self.hs["AltFlatFile btn"] = SelectFilesButton(
            option="askopenfilename", **{"open_filetypes": (("h5 files", "*.h5"),)}
        )
        self.hs["AltFlatFile btn"].description = "Alt Flat File"
        self.hs["AltFlatFile btn"].disabled = True
        self.hs["AltFlatFile btn"].layout = layout
        layout = {"left": "9%", "width": "24%"}
        self.hs["UseAltDark chbx"] = widgets.Checkbox(
            value=False, description="Alt Dark", disabled=True, indent=False
        )
        self.hs["UseAltDark chbx"].layout = layout
        layout = {"left": "9%", "width": "15%"}
        self.hs["AltDarkFile btn"] = SelectFilesButton(
            option="askopenfilename", **{"open_filetypes": (("h5 files", "*.h5"),)}
        )
        self.hs["AltDarkFile btn"].description = "Alt Dark File"
        self.hs["AltDarkFile btn"].disabled = True
        self.hs["AltDarkFile btn"].layout = layout

        self.hs["UseAltFlat chbx"].observe(self.UseAltFlat_chbx_chg, names="value")
        self.hs["AltFlatFile btn"].observe(self.AltFlatFile_btn_clk, names="value")
        self.hs["UseAltDark chbx"].observe(self.UseAltDark_chbx_chg, names="value")
        self.hs["AltDarkFile btn"].observe(self.AltDarkFile_btn_clk, names="value")
        self.hs["AltFlatDarkOptn box"].children = [
            self.hs["UseAltFlat chbx"],
            self.hs["AltFlatFile btn"],
            self.hs["UseAltDark chbx"],
            self.hs["AltDarkFile btn"],
        ]

        layout = {"border": "3px solid #FFCC00", "height": "auto"}
        self.hs["FakeFlatDarkOptn box"] = widgets.HBox()
        self.hs["FakeFlatDarkOptn box"].layout = layout
        layout = {"width": "19%"}
        self.hs["UseFakeFlat chbx"] = widgets.Checkbox(
            value=False, description="Fake Flat", disabled=True, indent=False
        )
        self.hs["UseFakeFlat chbx"].layout = layout
        layout = {"width": "19%"}
        self.hs["FakeFlatVal text"] = widgets.BoundedFloatText(
            value=10000.0, description="Flat Val", min=100, max=65000, disabled=True
        )
        self.hs["FakeFlatVal text"].layout = layout
        layout = {"left": "10%", "width": "19%"}
        self.hs["UseFakeDark chbx"] = widgets.Checkbox(
            value=False, description="Fake Dark", disabled=True, indent=False
        )
        self.hs["UseFakeDark chbx"].layout = layout
        layout = {"left": "19%", "width": "19%"}
        self.hs["FakeDarkVal text"] = widgets.BoundedFloatText(
            value=100.0, description="Dark Val", min=0, max=500, disabled=True
        )
        self.hs["FakeDarkVal text"].layout = layout

        self.hs["UseFakeFlat chbx"].observe(self.UseFakeFlat_chbx_chg, names="value")
        self.hs["FakeFlatVal text"].observe(self.FakeFlatVal_text_chg, names="value")
        self.hs["UseFakeDark chbx"].observe(self.UseFakeDark_chbx_chg, names="value")
        self.hs["FakeDarkVal text"].observe(self.FakeDarkVal_text_chg, names="value")
        self.hs["FakeFlatDarkOptn box"].children = [
            self.hs["UseFakeFlat chbx"],
            self.hs["FakeFlatVal text"],
            self.hs["UseFakeDark chbx"],
            self.hs["FakeDarkVal text"],
        ]

        layout = {"border": "3px solid #FFCC00", "height": "auto"}
        self.hs["MiscOptn box"] = widgets.HBox()
        self.hs["MiscOptn box"].layout = layout
        layout = {"width": "10%"}
        self.hs["UseBlurFlat chbx"] = widgets.Checkbox(
            value=False, description="Blur Flat", disabled=True, indent=False
        )
        self.hs["UseBlurFlat chbx"].layout = layout
        layout = {"width": "17%"}
        self.hs["BlurKern text"] = widgets.BoundedIntText(
            value=20, description="Blur Kernel", min=2, max=200, disabled=True
        )
        self.hs["BlurKern text"].layout = layout
        layout = {"left": "5%", "width": "10%"}
        self.hs["UseRmZinger chbx"] = widgets.Checkbox(
            value=False, description="Rm Zinger", disabled=True, indent=False
        )
        self.hs["UseRmZinger chbx"].layout = layout
        layout = {"left": "5%", "width": "17%"}
        self.hs["ZingerLevel text"] = widgets.BoundedFloatText(
            value=500.0, description="Zinger Lev", min=10, max=1000, disabled=True
        )
        self.hs["ZingerLevel text"].layout = layout
        layout = {"left": "10%", "width": "10%"}
        self.hs["UseMask chbx"] = widgets.Checkbox(
            value=True, description="Use Mask", disabled=True, indent=False
        )
        self.hs["UseMask chbx"].layout = layout
        layout = {"left": "10%", "width": "17%"}
        self.hs["MaskRat text"] = widgets.BoundedFloatText(
            value=1, description="Mask R", min=0, max=1, step=0.05, disabled=True
        )
        self.hs["MaskRat text"].layout = layout

        self.hs["UseRmZinger chbx"].observe(self.UseRmZinger_chbx_chg, names="value")
        self.hs["ZingerLevel text"].observe(self.ZingerLevel_text_chg, names="value")
        self.hs["UseMask chbx"].observe(self.UseMask_chbx_chg, names="value")
        self.hs["MaskRat text"].observe(self.MaskRat_text_chg, names="value")
        self.hs["UseBlurFlat chbx"].observe(self.BlurFlat_chbx_chg, names="value")
        self.hs["BlurKern text"].observe(self.BlurKern_text_chg, names="value")
        self.hs["MiscOptn box"].children = [
            self.hs["UseBlurFlat chbx"],
            self.hs["BlurKern text"],
            self.hs["UseRmZinger chbx"],
            self.hs["ZingerLevel text"],
            self.hs["UseMask chbx"],
            self.hs["MaskRat text"],
        ]

        layout = {"border": "3px solid #FFCC00", "height": "auto"}
        self.hs["WedgeOptn box"] = widgets.HBox()
        self.hs["WedgeOptn box"].layout = layout
        layout = {"width": "10%"}
        self.hs["IsWedge chbx"] = widgets.Checkbox(
            value=False, description="Is Wedge", disabled=True, indent=False
        )
        self.hs["IsWedge chbx"].layout = layout
        layout = {"width": "20%"}
        self.hs["MissIdxStart text"] = widgets.BoundedIntText(
            value=500,
            min=0,
            max=5000,
            description="Miss S",
            disabled=True,
        )
        self.hs["MissIdxStart text"].layout = layout
        layout = {"width": "20%"}
        self.hs["MissIdxEnd text"] = widgets.BoundedIntText(
            value=600, min=0, max=5000, description="Miss E", disabled=True
        )
        self.hs["MissIdxEnd text"].layout = layout
        layout = {"width": "20%"}
        self.hs["AutoDet chbx"] = widgets.Checkbox(
            value=True, description="Auto Det", disabled=True, indent=True
        )
        self.hs["AutoDet chbx"].layout = layout
        layout = {"left": "5%", "width": "20%"}
        self.hs["AutoThres text"] = widgets.BoundedFloatText(
            value=0.1, min=0, max=1, description="Auto Thres", disabled=True
        )
        self.hs["AutoThres text"].layout = layout

        self.hs["IsWedge chbx"].observe(self.IsWedge_chbx_chg, names="value")
        self.hs["MissIdxStart text"].observe(self.MissIdxStart_text_chg, names="value")
        self.hs["MissIdxEnd text"].observe(self.MissIdxEnd_text_chg, names="value")
        self.hs["AutoDet chbx"].observe(self.AutoDet_chbx_chg, names="value")
        self.hs["AutoThres text"].observe(self.AutoThres_text_chg, names="value")
        self.hs["WedgeOptn box"].children = [
            self.hs["IsWedge chbx"],
            self.hs["MissIdxStart text"],
            self.hs["MissIdxEnd text"],
            self.hs["AutoDet chbx"],
            self.hs["AutoThres text"],
        ]

        layout = {"border": "3px solid #FFCC00", "height": "auto"}
        self.hs["WedgeRef box"] = widgets.HBox()
        self.hs["WedgeRef box"].layout = layout

        layout = {"width": "15%"}
        self.hs["AutoRefFn btn"] = SelectFilesButton(
            option="askopenfilename", **{"open_filetypes": (("h5 files", "*.h5"),)}
        )
        self.hs["AutoRefFn btn"].layout = layout
        self.hs["AutoRefFn btn"].disabled = True

        layout = {"width": "40%"}
        self.hs["AutoRefSli sldr"] = widgets.IntSlider(
            description="slice #",
            min=0,
            max=10,
            value=0,
            disabled=True,
            continuous_update=False,
        )
        self.hs["AutoRefSli sldr"].layout = layout

        self.hs["AutoRefColStart text"] = widgets.BoundedIntText(
            value=0, min=0, max=400, description="W Col_Start", disabled=True
        )
        layout = {"left": "2.5%", "width": "19%"}
        self.hs["AutoRefColStart text"].layout = layout
        self.hs["AutoRefColEnd text"] = widgets.BoundedIntText(
            value=10, min=1, max=401, description="W Col_End", disabled=True
        )
        layout = {"left": "2.5%", "width": "19%"}
        self.hs["AutoRefColEnd text"].layout = layout

        self.hs["AutoRefFn btn"].on_click(self.AutoRefFn_btn_clk)
        self.hs["AutoRefSli sldr"].observe(self.AutoRefSli_sldr_chg, names="value")
        self.hs["AutoRefColStart text"].observe(
            self.AutoRefColStart_text_chg, names="value"
        )
        self.hs["AutoRefColEnd text"].observe(
            self.AutoRefColEnd_text_chg, names="value"
        )
        self.hs["WedgeRef box"].children = [
            self.hs["AutoRefFn btn"],
            self.hs["AutoRefSli sldr"],
            self.hs["AutoRefColStart text"],
            self.hs["AutoRefColEnd text"],
        ]
        ## ## ## ## ## ## ## config sub-boxes in data_config_box -- end

        self.hs["DataConfig box"].children = [
            self.hs["ReconConfig box"],
            self.hs["RoiConfig box"],
            self.hs["AltFlatDarkOptn box"],
            self.hs["FakeFlatDarkOptn box"],
            self.hs["MiscOptn box"],
            self.hs["WedgeOptn box"],
            self.hs["WedgeRef box"],
        ]
        ## ## ## ## ## ## config data parameters in data_config_box in data_config_tab -- end

        self.hs["DataConfig tab"].children = [self.hs["DataConfig box"]]
        ## ## ## ## ## config data_config_tab -- end

        ## ## ## ## ## ## config alg_config_box in alg_config tab -- start
        layout = {
            "border": "3px solid #8855AA",
            "width": "auto",
            "height": f"{0.21 * (self.form_sz[0] - 136)}px",
        }
        self.hs["AlgConfig box"] = widgets.VBox()
        self.hs["AlgConfig box"].layout = layout

        layout = {"border": "3px solid #FFCC00", "height": "auto"}
        self.hs["AlgOptn box0"] = widgets.HBox()
        self.hs["AlgOptn box0"].layout = layout
        layout = {"width": "24%"}
        self.hs["AlgOptn drpdn"] = widgets.Dropdown(
            value="gridrec",
            options=["gridrec", "sirt", "tv", "mlem", "astra"],
            description="algs",
            disabled=True,
        )
        self.hs["AlgOptn drpdn"].layout = layout
        layout = {"width": "23.5%"}
        self.hs["AlgPar00 drpdn"] = widgets.Dropdown(
            value="", options=[""], description="p00", disabled=True
        )
        self.hs["AlgPar00 drpdn"].layout = layout
        layout = {"width": "23.5%"}
        self.hs["AlgPar01 drpdn"] = widgets.Dropdown(
            value="", options=[""], description="p01", disabled=True
        )
        self.hs["AlgPar01 drpdn"].layout = layout
        layout = {"width": "23.5%"}
        self.hs["AlgPar02 drpdn"] = widgets.Dropdown(
            value="", options=[""], description="p02", disabled=True
        )
        self.hs["AlgPar02 drpdn"].layout = layout

        self.hs["AlgOptn drpdn"].observe(self.AlgOptn_drpdn_chg, names="value")
        self.hs["AlgPar00 drpdn"].observe(self.AlgPar00_drpdn_chg, names="value")
        self.hs["AlgPar01 drpdn"].observe(self.AlgPar01_drpdn_chg, names="value")
        self.hs["AlgPar02 drpdn"].observe(self.AlgPar02_drpdn_chg, names="value")
        self.hs["AlgOptn box0"].children = [
            self.hs["AlgOptn drpdn"],
            self.hs["AlgPar00 drpdn"],
            self.hs["AlgPar01 drpdn"],
            self.hs["AlgPar02 drpdn"],
        ]

        layout = {"border": "3px solid #FFCC00", "height": "auto"}
        self.hs["AlgOptn box1"] = widgets.HBox()
        self.hs["AlgOptn box1"].layout = layout
        layout = {"width": "23.5%"}
        self.hs["AlgPar03 text"] = widgets.FloatText(
            value=0, description="p03", disabled=True
        )
        self.hs["AlgPar03 text"].layout = layout
        layout = {"width": "23.5%"}
        self.hs["AlgPar04 text"] = widgets.FloatText(
            value=0, description="p04", disabled=True
        )
        self.hs["AlgPar04 text"].layout = layout
        layout = {"width": "23.5%"}
        self.hs["AlgPar05 text"] = widgets.FloatText(
            value=0, description="p05", disabled=True
        )
        self.hs["AlgPar05 text"].layout = layout
        layout = {"width": "23.5%"}
        self.hs["AlgPar06 text"] = widgets.FloatText(
            value=0.0, description="p06", disabled=True
        )
        self.hs["AlgPar06 text"].layout = layout

        self.hs["AlgPar03 text"].observe(self.AlgPar03_text_chg, names="value")
        self.hs["AlgPar04 text"].observe(self.AlgPar04_text_chg, names="value")
        self.hs["AlgPar05 text"].observe(self.AlgPar05_text_chg, names="value")
        self.hs["AlgPar06 text"].observe(self.AlgPar06_text_chg, names="value")
        self.hs["AlgOptn box1"].children = [
            self.hs["AlgPar03 text"],
            self.hs["AlgPar04 text"],
            self.hs["AlgPar05 text"],
            self.hs["AlgPar06 text"],
        ]

        self.hs["AlgConfig box"].children = [
            self.hs["AlgOptn box0"],
            self.hs["AlgOptn box1"],
        ]
        ## ## ## ## ## ## config alg_config_box in alg_config tab -- end

        self.hs["AlgConfig tab"].children = [self.hs["AlgConfig box"]]
        ## ## ## ## ## define alg_config tab -- end

        ## ## ## ## ## define data info tab -- start
        ## ## ## ## ## ## define data info box -- start
        layout = {
            "border": "3px solid #FFCC00",
            "height": f"{0.42 * (self.form_sz[0] - 136)}px",
        }
        self.hs["DataInfo box"] = widgets.HBox()
        self.hs["DataInfo box"].layout = layout
        layout = {"width": "90%", "height": "90%"}
        self.hs["DataInfo text"] = widgets.Textarea(
            value="Data Info",
            placeholder="Data Info",
            description="Data Info",
            disabled=True,
        )
        self.hs["DataInfo text"].layout = layout
        self.hs["DataInfo box"].children = [self.hs["DataInfo text"]]
        ## ## ## ## ## ## define data info box -- end
        self.hs["DataInfo tab"].children = [self.hs["DataInfo box"]]
        ## ## ## ## ## define data info tab -- end

        ## ## ## ## ## define data_preview tab -- start
        ## ## ## ## ## ## define data_preview_box -- start
        layout = {"border": "3px solid #8855AA", "width": "auto", "height": "auto"}
        self.hs["DataPrev box"] = widgets.VBox()
        self.hs["DataPrev box"].layout = layout

        ## ## ## ## ## ## ## define functional box widgets in data_prevew_box3 -- start
        layout = {"border": "3px solid #FFCC00", "width": "auto", "height": "auto"}
        self.hs["ProjPrev box"] = widgets.HBox()
        self.hs["ProjPrev box"].layout = layout
        layout = {"width": "50%", "height": "auto"}
        self.hs["RawProj sldr"] = widgets.IntSlider(
            value=0,
            description="proj",
            description_tooltip="offset the image at 180 deg to overlap with the image at 0 deg. rotation center can be determined from the offset.",
            min=-100,
            max=100,
            disabled=True,
            indent=False,
            continuous_update=False,
        )
        self.hs["RawProj sldr"].layout = layout

        self.hs["RawProjInMem chbx"] = widgets.Checkbox(
            description="read in mem",
            description_tooltip="Optional read entire raw proj dataset into memory for display",
            value=False,
            disabled=True,
            indent=False,
            layout={"width": "20%", "height": "auto"},
        )

        self.hs["RawProjViewerClose btn"] = widgets.Button(
            description="Close/Confirm",
            description_tooltip="Optional confrimation of roi (slices and columns) definition",
            disabled=True,
            layout={"width": "20%", "height": "auto"},
        )
        self.hs["RawProjViewerClose btn"].style.button_color = "darkviolet"

        self.hs["RawProj sldr"].observe(self.RawProj_sldr_chg, names="value")
        self.hs["RawProjInMem chbx"].observe(self.RawProjInMem_chbx_chg, names="value")
        self.hs["RawProjViewerClose btn"].on_click(self.RawProjViewerClose_btn_clk)
        self.hs["ProjPrev box"].children = [
            self.hs["RawProj sldr"],
            self.hs["RawProjInMem chbx"],
            self.hs["RawProjViewerClose btn"],
        ]
        ## ## ## ## ## ## ## define functional box widgets in data_prevew_box3 -- end

        ## ## ## ## ## ## ## define functional box widgets in data_prevew_box0 -- start
        layout = {"border": "3px solid #FFCC00", "width": "auto", "height": "auto"}
        self.hs["CenPrev box"] = widgets.HBox()
        self.hs["CenPrev box"].layout = layout
        layout = {"width": "50%", "height": "auto"}
        self.hs["CenOffsetRange sldr"] = widgets.IntSlider(
            value=0,
            description="offset",
            description_tooltip="offset the image at 180 deg to overlap with the image at 0 deg. rotation center can be determined from the offset.",
            min=-100,
            max=100,
            disabled=True,
            indent=False,
            continuous_update=False,
        )
        self.hs["CenOffsetRange sldr"].layout = layout
        layout = {"width": "20%", "height": "auto"}
        self.hs["CenOffsetCfm btn"] = widgets.Button(
            description="Confirm",
            description_tooltip="Optional confrimation of the rough center",
            disabled=True,
        )
        self.hs["CenOffsetCfm btn"].layout = layout
        self.hs["CenOffsetCfm btn"].style.button_color = "darkviolet"
        layout = {"width": "20%", "height": "auto"}
        self.hs["CenViewerClose btn"] = widgets.Button(
            description="Close",
            description_tooltip="Optional close the viewer window",
            disabled=True,
        )
        self.hs["CenViewerClose btn"].layout = layout
        self.hs["CenViewerClose btn"].style.button_color = "darkviolet"

        self.hs["CenOffsetRange sldr"].observe(
            self.CenOffsetRange_sldr_chg, names="value"
        )
        self.hs["CenOffsetCfm btn"].on_click(self.CenOffsetCfm_btn_clk)
        self.hs["CenViewerClose btn"].on_click(self.CenViewerClose_btn_clk)
        self.hs["CenPrev box"].children = [
            self.hs["CenOffsetRange sldr"],
            self.hs["CenOffsetCfm btn"],
            self.hs["CenViewerClose btn"],
        ]
        ## ## ## ## ## ## ## define functional box widgets in data_prevew_box0 -- end

        ## ## ## ## ## ## ## define functional box widgets in data_prevew_box1 -- start
        layout = {"border": "3px solid #FFCC00", "width": "auto", "height": "auto"}
        self.hs["TrialCenPrev box"] = widgets.HBox()
        self.hs["TrialCenPrev box"].layout = layout

        self.hs["TrialCenPrev sldr"] = widgets.IntSlider(
            value=0,
            description="trial cen",
            description_tooltip="offset the image at 180 deg to overlap with the image at 0 deg. rotation center can be determined from the offset.",
            min=-100,
            max=100,
            disabled=True,
            indent=False,
            continuous_update=False,
            layout={"width": "50%", "height": "auto"},
        )

        self.hs["UseAsXNS3DTplt chbx"] = widgets.Checkbox(
            description="use as template",
            description_tooltip="Use the current scan and its configuration as a template to reconstruct the rest of scans in a XANES3D scan series",
            value=False,
            disabled=True,
            indent=False,
            layout={"width": "20%", "height": "auto"},
        )

        self.hs["TrialCenCfm btn"] = widgets.Button(
            description="Confirm",
            description_tooltip="Optional confrimation of the rough center",
            disabled=True,
            layout={"width": "20%", "height": "auto"},
        )
        self.hs["TrialCenCfm btn"].style.button_color = "darkviolet"

        self.hs["TrialCenPrev sldr"].observe(self.TrialCenPrev_sldr_chg, names="value")
        self.hs["TrialCenCfm btn"].on_click(self.TrialCenCfm_btn_clk)
        self.hs["UseAsXNS3DTplt chbx"].observe(
            self.UseAsXNS3DTplt_chbx_chg, names="value"
        )

        self.hs["TrialCenPrev box"].children = [
            self.hs["TrialCenPrev sldr"],
            self.hs["UseAsXNS3DTplt chbx"],
            self.hs["TrialCenCfm btn"],
        ]
        ## ## ## ## ## ## ## define functional box widgets in data_prevew_box1 -- end

        # ## ## ## ## ## ## ## define functional box widgets in data_prevew_box2 -- start
        self.hs["DataPrev box"].children = [
            self.hs["ProjPrev box"],
            self.hs["CenPrev box"],
            self.hs["TrialCenPrev box"],
        ]
        ## ## ## ## ## ## define data_preview_box-- end

        self.hs["DataPrev tab"].children = [self.hs["DataPrev box"]]
        ## ## ## ## ## define data_preview tab -- end

        ## ## ## ## ## define VolView tab -- start
        ## ## ## ## ## ## define VolView_box -- start
        layout = {"border": "3px solid #8855AA", "width": "auto", "height": "auto"}
        self.hs["VolRecon box"] = widgets.VBox()
        self.hs["VolRecon box"].layout = layout

        ## ## ## ## ## ## ## define vol viewer box -- start
        layout = {"border": "3px solid #FFCC00", "width": "auto", "height": "auto"}
        self.hs["VolViewOpt box"] = widgets.HBox()
        self.hs["VolViewOpt box"].layout = layout
        layout = {"width": "60%", "height": "auto"}
        self.hs["VolViewOpt tgbtn"] = widgets.ToggleButtons(
            description="viewer options",
            disabled=True,
            description_tooltip="napari: provides 3D visualization; fiji: provides better slice visualization",
            options=["fiji", "napari"],
            value="fiji",
        )
        self.hs["VolViewOpt tgbtn"].layout = layout

        self.hs["VolViewOpt tgbtn"].observe(self.VolViewOpt_tgbtn_chg, names="value")
        self.hs["VolViewOpt box"].children = [
            self.hs["VolViewOpt tgbtn"],
        ]
        ## ## ## ## ## ## ## define vol viewer box -- end

        self.hs["VolRecon box"].children = [self.hs["VolViewOpt box"]]
        ## ## ## ## ## ## define VolView_box -- end
        self.hs["VolRecon tab"].children = [self.hs["VolRecon box"]]
        ## ## ## ## ## define VolView tab -- end

        ## ## ## ## ## XANES3D specific tomo recon -- start
        self.hs["XNS3DRec box"] = widgets.VBox(
            layout={"border": "3px solid #8855AA", "width": "auto", "height": "auto"}
        )

        XNS3DTemp_GridspecLayout = widgets.GridspecLayout(
            12, 100, layout={"width": "100%", "height": "100%"}
        )

        XNS3DTemp_GridspecLayout[0, :73] = widgets.IntProgress(
            value=0,
            min=0,
            max=10,
            step=1,
            description="Completing:",
            bar_style="info",  # "success", "info", "warning", "danger" or ""
            orientation="horizontal",
            layout={"width": "100%", "height": "auto", "visibility": "visible"},
        )
        self.hs["XNS3DInitPgr pgr"] = XNS3DTemp_GridspecLayout[0, :73]

        XNS3DTemp_GridspecLayout[0, 75:86] = widgets.Checkbox(
            value=True,
            description="Full rec?",
            tooltip="Check on to do full reconstruction of the reference scan; it will take some time to finish",
            layout={"width": "100%", "height": "auto", "visibility": "visible"},
            indent=False,
            disabled=True,
        )
        self.hs["XNS3DInitRec chb"] = XNS3DTemp_GridspecLayout[0, 75:86]

        XNS3DTemp_GridspecLayout[0, 86:] = SelectFilesButton(
            option="askopenfilename",
            open_filetypes=(("json file", "*.json"),),
            layout={
                "width": "auto",
                "height": "80%",
                "display": "flex",
                "justify_content": "flex_end",
            },
            description="Sel Template",
        )
        self.hs["XNS3DRecTpltFn btn"] = XNS3DTemp_GridspecLayout[0, 86:]
        self.hs["XNS3DRecTpltFn btn"].tooltip = (
            "Select the recon template file for reconstructing all tomo scans automatically"
        )
        self.hs["XNS3DRecTpltFn btn"].disabled = True

        XNS3DTemp_GridspecLayout[1, 40:70] = widgets.GridBox(
            layout={
                "width": "100%",
                "height": "100%",
                "grid_template_columns": "80% auto",
                "grid_template_rows": "auto",
                "grid_gap": "0px 2px",
            }
        )
        self.hs["XNS3DAutoCen ttl"] = XNS3DTemp_GridspecLayout[1, 40:70]
        self.hs["XNS3DAutoCen txt"] = widgets.HTML(
            value='<b><p style="font-weight: bold; font-size: 125%; color: green; background-color: lightblue; text-align:center">Auto Center Cfg</p></b>',
            layout={"height": "90%", "width": "100%"},
        )
        self.hs["XNS3DAutoCen ttl"].children = [self.hs["XNS3DAutoCen txt"]]

        XNS3DTemp_GridspecLayout[2, 4:29] = widgets.Dropdown(
            options=["Relative", "Absolute"],
            value="Absolute",
            layout={"width": "auto", "height": "auto"},
            description="Auto Cent Opt",
            disabled=True,
        )
        self.hs["XNS3DRecCenOpt drpn"] = XNS3DTemp_GridspecLayout[2, 4:29]

        XNS3DTemp_GridspecLayout[2, 37:62] = widgets.Dropdown(
            value=0,
            options=[0],
            min=0,
            layout={"width": "100%", "height": "auto"},
            description="ScanID s",
            tooltip="Scan starting ID in a XANES3D scan series",
            disabled=True,
        )
        self.hs["XNS3DRecScnIDs drpn"] = XNS3DTemp_GridspecLayout[2, 37:62]

        XNS3DTemp_GridspecLayout[2, 70:95] = widgets.Dropdown(
            value=0,
            options=[0],
            min=0,
            layout={"width": "100%", "height": "auto"},
            description="ScanID e",
            tooltip="Scan ending ID in a XANES3D scan series",
            disabled=True,
        )
        self.hs["XNS3DRecScnIDe drpn"] = XNS3DTemp_GridspecLayout[2, 70:95]

        XNS3DTemp_GridspecLayout[3, 35:75] = widgets.GridBox(
            layout={
                "width": "100%",
                "height": "100%",
                "grid_template_columns": "80% auto",
                "grid_template_rows": "auto",
                "grid_gap": "0px 2px",
            }
        )
        self.hs["XNS3DRefSli ttl"] = XNS3DTemp_GridspecLayout[3, 35:75]
        self.hs["XNS3DRefSli txt"] = widgets.HTML(
            value='<b><p style="font-weight: bold; font-size: 125%; color: green; background-color: lightblue; text-align:center">Ref Slice and ROI for Auto Cent</p></b>',
            layout={"height": "90%", "width": "100%"},
        )
        self.hs["XNS3DRefSli ttl"].children = [self.hs["XNS3DRefSli txt"]]

        XNS3DTemp_GridspecLayout[4, :7] = widgets.Checkbox(
            value=True,
            description="Deflt",
            tooltip="Use default slice (middle slice) and region of interest (a circel of a diameter 0.9 times of the full slice image size )",
            layout={"width": "100%", "height": "auto", "visibility": "visible"},
            indent=False,
            disabled=True,
        )
        self.hs["XNS3DDefRefSli&ROI chb"] = XNS3DTemp_GridspecLayout[4, :7]

        XNS3DTemp_GridspecLayout[4, 7:39] = widgets.IntRangeSlider(
            value=[10, 40],
            min=1,
            max=50,
            step=1,
            description="ROI X",
            tooltip="region of interest for maching images",
            disabled=True,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format="d",
            layout={"width": "100%"},
        )
        self.hs["XNS3DRefSliROIX sldr"] = XNS3DTemp_GridspecLayout[4, 7:39]

        XNS3DTemp_GridspecLayout[4, 40:72] = widgets.IntRangeSlider(
            value=[10, 40],
            min=1,
            max=50,
            step=1,
            description="ROI Y",
            tooltip="region of interest for maching images",
            disabled=True,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format="d",
            layout={"width": "100%"},
        )
        self.hs["XNS3DRefSliROIY sldr"] = XNS3DTemp_GridspecLayout[4, 40:72]

        XNS3DTemp_GridspecLayout[4, 73:99] = widgets.IntSlider(
            value=10,
            min=1,
            max=50,
            step=1,
            description="Ref Sli",
            tooltip="reference slice for maching images",
            disabled=True,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format="d",
            layout={"width": "100%"},
        )
        self.hs["XNS3DRefSli sldr"] = XNS3DTemp_GridspecLayout[4, 73:99]

        # XNS3DTemp_GridspecLayout[4, :33] = widgets.IntRangeSlider(
        #     value=[10, 40],
        #     min=1,
        #     max=50,
        #     step=1,
        #     description="ROI X",
        #     tooltip='region of interest for maching images',
        #     disabled=True,
        #     continuous_update=False,
        #     orientation="horizontal",
        #     readout=True,
        #     readout_format="d",
        #     layout={"width": "100%"})
        # self.hs['XNS3DRefSliROIX sldr'] = XNS3DTemp_GridspecLayout[4, :33]

        # XNS3DTemp_GridspecLayout[4, 33:66] = widgets.IntRangeSlider(
        #     value=[10, 40],
        #     min=1,
        #     max=50,
        #     step=1,
        #     description="ROI Y",
        #     tooltip='region of interest for maching images',
        #     disabled=True,
        #     continuous_update=False,
        #     orientation="horizontal",
        #     readout=True,
        #     readout_format="d",
        #     layout={"width": "100%"})
        # self.hs['XNS3DRefSliROIY sldr'] = XNS3DTemp_GridspecLayout[4, 33:66]

        # XNS3DTemp_GridspecLayout[4, 66:99] = widgets.IntSlider(
        #     value=10,
        #     min=1,
        #     max=50,
        #     step=1,
        #     description="Ref Sli",
        #     tooltip='reference slice for maching images',
        #     disabled=True,
        #     continuous_update=False,
        #     orientation="horizontal",
        #     readout=True,
        #     readout_format="d",
        #     layout={"width": "100%"})
        # self.hs['XNS3DRefSli sldr'] = XNS3DTemp_GridspecLayout[4, 66:99]

        XNS3DTemp_GridspecLayout[5, 40:70] = widgets.GridBox(
            layout={
                "width": "auto",
                "height": "100%",
                "grid_template_columns": "80% auto",
                "grid_template_rows": "auto",
                "grid_gap": "0px 2px",
            }
        )
        self.hs["XNS3DRecROI ttl"] = XNS3DTemp_GridspecLayout[5, 40:70]
        self.hs["XNS3DRecROI txt"] = widgets.HTML(
            value='<b><p style="font-weight: bold; font-size: 125%; color: green; background-color: lightblue; text-align:center">Reconstruction ROI Cfg</p></b>',
            layout={"height": "90%", "width": "100%"},
        )
        self.hs["XNS3DRecROI ttl"].children = [self.hs["XNS3DRecROI txt"]]

        XNS3DTemp_GridspecLayout[6, :33] = widgets.IntRangeSlider(
            value=[10, 40],
            min=1,
            max=50,
            step=1,
            description="ROI X",
            tooltip="region of interest for maching images",
            disabled=True,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format="d",
            layout={"width": "100%"},
        )
        self.hs["XNS3DRecROIX sldr"] = XNS3DTemp_GridspecLayout[6, :33]

        XNS3DTemp_GridspecLayout[6, 33:66] = widgets.IntRangeSlider(
            value=[10, 40],
            min=1,
            max=50,
            step=1,
            description="ROI Y",
            tooltip="region of interest for maching images",
            disabled=True,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format="d",
            layout={"width": "100%"},
        )
        self.hs["XNS3DRecROIY sldr"] = XNS3DTemp_GridspecLayout[6, 33:66]

        XNS3DTemp_GridspecLayout[6, 66:99] = widgets.IntRangeSlider(
            value=[10, 40],
            min=1,
            max=50,
            step=1,
            description="ROI Z",
            tooltip="region of interest for maching images",
            disabled=True,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format="d",
            layout={"width": "100%"},
        )
        self.hs["XNS3DRecROIZ sldr"] = XNS3DTemp_GridspecLayout[6, 66:99]
        self.hs["XNS3DRecROIZ sldr"].add_traits(
            mylower=traitlets.traitlets.Any(self.hs["XNS3DRecROIZ sldr"].lower)
        )
        self.hs["XNS3DRecROIZ sldr"].add_traits(
            myupper=traitlets.traitlets.Any(self.hs["XNS3DRecROIZ sldr"].upper)
        )

        XNS3DTemp_GridspecLayout[7, 40:70] = widgets.GridBox(
            layout={
                "width": "auto",
                "height": "100%",
                "grid_template_columns": "80% auto",
                "grid_template_rows": "auto",
                "grid_gap": "0px 2px",
            }
        )
        self.hs["XNS3DRegCfg ttl"] = XNS3DTemp_GridspecLayout[7, 40:70]
        self.hs["XNS3DRegCfg txt"] = widgets.HTML(
            value='<b><p style="font-weight: bold; font-size: 125%; color: green; background-color: lightblue; text-align:center">Registration Cfg</p></b>',
            layout={"height": "90%", "width": "100%"},
        )
        self.hs["XNS3DRegCfg ttl"].children = [self.hs["XNS3DRegCfg txt"]]

        XNS3DTemp_GridspecLayout[8, 4:29] = widgets.Dropdown(
            options=["single", "neighbor", "average"],
            value="single",
            layout={"width": "auto", "height": "auto"},
            description="ref mode",
            disabled=True,
        )
        self.hs["XNS3DRecRegMode drpn"] = XNS3DTemp_GridspecLayout[8, 4:29]

        XNS3DTemp_GridspecLayout[8, 37:62] = widgets.IntSlider(
            value=5,
            min=1,
            max=10,
            layout={"width": "120%", "height": "auto"},
            description="chunk size",
            tooltip="chunk size for MRTV calculation",
            disabled=True,
        )
        self.hs["XNS3DRecRegChnkSz sldr"] = XNS3DTemp_GridspecLayout[8, 37:62]

        XNS3DTemp_GridspecLayout[8, 70:95] = widgets.BoundedFloatText(
            value=0.5,
            min=0.1,
            max=20,
            step=0.1,
            layout={"width": "100%", "height": "70%"},
            description="kernel wz",
            tooltip="kernel wz: Gaussian blurring width before TV minimization",
            disabled=True,
        )
        self.hs["XNS3DRecRegKnlSz txt"] = XNS3DTemp_GridspecLayout[8, 70:95]

        XNS3DTemp_GridspecLayout[9, :49] = widgets.IntSlider(
            value=10,
            min=1,
            max=50,
            step=1,
            description="Z Depth",
            tooltip="Half number of slices for searching the matched slice to the reference slice",
            disabled=True,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format="d",
            layout={"width": "90%"},
        )
        self.hs["XNS3DRecZSrchDpth sldr"] = XNS3DTemp_GridspecLayout[9, :49]

        XNS3DTemp_GridspecLayout[9, 51:] = widgets.IntSlider(
            value=15,
            min=1,
            max=50,
            step=1,
            description="Cen Width",
            tooltip="Half center searching width in pixel for searching the matched slice to the reference slice",
            disabled=True,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format="d",
            layout={"width": "90%"},
        )
        self.hs["XNS3DRecCenWzSrch sldr"] = XNS3DTemp_GridspecLayout[9, 51:]

        XNS3DTemp_GridspecLayout[10, 4:29] = widgets.Checkbox(
            value=True,
            description="Rec All Sli",
            tooltip="Reconstruct full volumes",
            disabled=True,
            layout={"width": "auto", "height": "auto", "visibility": "visible"},
        )
        self.hs["AutoCenFullRec chb"] = XNS3DTemp_GridspecLayout[10, 4:29]

        XNS3DTemp_GridspecLayout[10, 37:62] = widgets.BoundedIntText(
            value=0,
            min=0,
            max=50,
            step=1,
            description="Sli Start",
            tooltip="Starting slice index for tomography reconstructions",
            disabled=True,
            readout_format="d",
            layout={"width": "100%", "height": "70%", "visibility": "visible"},
        )
        self.hs["AutoCenSliS txt"] = XNS3DTemp_GridspecLayout[10, 37:62]

        XNS3DTemp_GridspecLayout[10, 70:95] = widgets.BoundedIntText(
            value=0,
            min=0,
            max=50,
            step=1,
            description="Sli End",
            tooltip="Ending slice index for tomography reconstructions",
            disabled=True,
            readout_format="d",
            layout={"width": "100%", "height": "70%", "visibility": "visible"},
        )
        self.hs["AutoCenSliE txt"] = XNS3DTemp_GridspecLayout[10, 70:95]

        XNS3DTemp_GridspecLayout[11, :73] = widgets.IntProgress(
            value=0,
            min=0,
            max=10,
            step=1,
            description="Completing:",
            bar_style="info",  # "success", "info", "warning", "danger" or ""
            orientation="horizontal",
            layout={"width": "100%", "height": "auto"},
        )
        self.hs["XNS3DRecPgr pgr"] = XNS3DTemp_GridspecLayout[11, :73]

        XNS3DTemp_GridspecLayout[11, 75:86] = widgets.Checkbox(
            value=True,
            description="Rec?",
            tooltip="Check on to do full reconstructions of the scan in the selected range; it will take significant time to finish",
            layout={"width": "100%", "height": "auto"},
            indent=False,
            disabled=True,
        )
        self.hs["XNS3DRegRec chb"] = XNS3DTemp_GridspecLayout[11, 75:86]

        XNS3DTemp_GridspecLayout[11, 86:] = widgets.Button(
            description="Run", disabled=True
        )
        self.hs["XNS3DRecRun btn"] = XNS3DTemp_GridspecLayout[11, 86:]
        self.hs["XNS3DRecRun btn"].style.button_color = "darkviolet"

        self.hs["XNS3DInitRec chb"].observe(self.XNS3DInitRec_chb_chg, names="value")
        self.hs["XNS3DRecCenOpt drpn"].observe(
            self.XNS3DRecCenOpt_drpn_chg, names="value"
        )
        self.hs["XNS3DRecScnIDs drpn"].observe(
            self.XNS3DRecScnIDs_drpn_chg, names="value"
        )
        self.hs["XNS3DRecScnIDe drpn"].observe(
            self.XNS3DRecScnIDe_drpn_chg, names="value"
        )
        self.hs["XNS3DRecTpltFn btn"].on_click(self.XNS3DRecTpltFn_btn_clk)
        self.hs["XNS3DRecRegMode drpn"].observe(
            self.XNS3DRecRegMode_drpn_chg, names="value"
        )
        self.hs["XNS3DDefRefSli&ROI chb"].observe(
            self.XNS3DDefRefSliROI_chb_chg, names="value"
        )
        self.hs["XNS3DRefSliROIX sldr"].observe(
            self.XNS3DRefSliROIX_sldr_chg, names="value"
        )
        self.hs["XNS3DRefSliROIY sldr"].observe(
            self.XNS3DRefSliROIY_sldr_chg, names="value"
        )
        self.hs["XNS3DRefSli sldr"].observe(self.XNS3DRefSli_sldr_chg, names="value")

        self.hs["XNS3DRecRegChnkSz sldr"].observe(
            self.XNS3DRecRegChnkSz_sldr_chg, names="value"
        )
        self.hs["XNS3DRecRegKnlSz txt"].observe(
            self.XNS3DRecRegKnlSz_txt_chg, names="value"
        )
        self.hs["XNS3DRecROIX sldr"].observe(self.XNS3DRecROIX_sldr_chg, names="value")
        self.hs["XNS3DRecROIY sldr"].observe(self.XNS3DRecROIY_sldr_chg, names="value")
        self.hs["XNS3DRecROIZ sldr"].observe(self.XNS3DRecROIZ_sldr_chg, names="value")
        self.hs["XNS3DRecROIZ sldr"].observe(
            self.XNS3DRecROIZ_upr_sldr_chg, names="myupper"
        )
        self.hs["XNS3DRecROIZ sldr"].observe(
            self.XNS3DRecROIZ_lwr_sldr_chg, names="mylower"
        )
        self.hs["XNS3DRecZSrchDpth sldr"].observe(
            self.XNS3DRecZSrchDpth_sldr_chg, names="value"
        )
        self.hs["XNS3DRecCenWzSrch sldr"].observe(
            self.XNS3DRecCenWzSrch_sldr_chg, names="value"
        )
        self.hs["XNS3DRegRec chb"].observe(self.XNS3DRegRec_chb_chg, names="value")
        self.hs["AutoCenFullRec chb"].observe(
            self.AutoCenFullRec_chb_chg, names="value"
        )
        self.hs["AutoCenSliS txt"].observe(self.AutoCenSliS_txt_chg, names="value")
        self.hs["AutoCenSliE txt"].observe(self.AutoCenSliE_txt_chg, names="value")
        self.hs["XNS3DRecRun btn"].on_click(self.XNS3DRecRun_btn_clk)

        self.hs["XNS3DRec box"].children = [XNS3DTemp_GridspecLayout]
        ## ## ## ## ## XANES3D specific tomo recon -- end

        self.hs["CfgInpt&Rev acc"].children = [
            self.hs["SelFile&Path box"],
            self.hs["Data tab"],
            self.hs["XNS3DRec box"],
        ]
        self.hs["CfgInpt&Rev acc"].titles = [
            "START: Config Input/Output File Path",
            "STEP 1: Config Data & Algorithm",
            "XANES3D Tomo Recon with Automatic Centering",
        ]

        """self.hs["CfgInpt&Rev acc"].set_title(0, "START: Config Input/Output File Path")
        self.hs["CfgInpt&Rev acc"].set_title(1, "STEP 1: Config Data & Algorithm")
        self.hs["CfgInpt&Rev acc"].set_title(
            2, "XANES3D Tomo Recon with Automatic Centering"
        )"""
        self.hs["CfgInpt&Rev acc"].selected_index = 0

        self.hs["Config&Input form"].children = [self.hs["CfgInpt&Rev acc"]]
        ## ## ## config config_input_form -- end

        ## ## ## ## config Filter&Recon form -- start
        layout = {"border": "3px solid #8855AA", "width": "auto", "height": "auto"}
        self.hs["Filter&Recon form"] = widgets.VBox()
        self.hs["Filter&Recon form"].layout = layout

        self.hs["Flt&Rec acc"] = widgets.Accordion(
            layout={
                "width": "auto",
                "height": "auto",
                "border": "3px solid #8855AA",
                "align-content": "center",
                "align-items": "center",
                "justify-content": "center",
            }
        )

        ## ## ## ## ## config filter_config_box -- start
        layout = {"border": "3px solid #8855AA", "height": "auto"}
        self.hs["Filter&Recon box"] = widgets.VBox()
        self.hs["Filter&Recon box"].layout = layout

        ## ## ## ## ## ## label recon_box -- start
        grid_recon_chunk = GridspecLayout(
            2,
            100,
            layout={
                "border": "3px solid #FFCC00",
                "height": "auto",
                "width": "auto",
                "grid_row_gap": "4px",
                "grid_column_gap": "8px",
                "align_items": "flex-start",
                "justify_items": "flex-start",
            },
        )
        self.hs["ReconChunk box"] = grid_recon_chunk

        grid_recon_chunk[0, 40:70] = widgets.HTML(
            value='<b><p style="font-weight: bold; font-size: 125%; color: green; background-color: lightblue; text-align:center">Chunk&Margin</p></b>',
            layout={"height": "90%", "width": "100%"},
        )
        self.hs["ChunkMargTitle label"] = grid_recon_chunk[0, 40:70]

        grid_recon_chunk[1, :30] = widgets.BoundedIntText(
            description="Chunk Sz",
            disabled=True,
            min=1,
            max=2000,
            layout={"width": "100%", "height": "auto"},
            value=200,
            description_tooltip="how many slices will be loaded into memory for reconstruction each time",
        )
        self.hs["ReconChunkSz text"] = grid_recon_chunk[1, :30]

        grid_recon_chunk[1, 30:60] = widgets.BoundedIntText(
            description="Margin Sz",
            disabled=True,
            min=0,
            max=50,
            layout={"width": "100%", "height": "auto"},
            value=15,
            description_tooltip="how many slices will be loaded into memory for reconstruction each time",
        )
        self.hs["ReconMargSz text"] = grid_recon_chunk[1, 30:60]

        self.hs["ReconChunkSz text"].observe(self.ReconChunkSz_text_chg, names="value")
        self.hs["ReconMargSz text"].observe(self.ReconMargSz_text_chg, names="value")
        self.hs["ReconChunk box"].children = [
            self.hs["ChunkMargTitle label"],
            self.hs["ReconChunkSz text"],
            self.hs["ReconMargSz text"],
        ]
        ## ## ## ## ## ## label recon_box -- end

        ## ## ## ## ## ## label filter_config_box -- start
        layout = {
            "justify-content": "center",
            "align-items": "center",
            "align-contents": "center",
            "border": "3px solid #FFCC00",
            "height": "auto",
        }
        self.hs["FilterConfigTitle box"] = widgets.HBox()
        self.hs["FilterConfigTitle box"].layout = layout
        self.hs["FilterConfigTitle label"] = widgets.HTML(
            value='<b><p style="font-weight: bold; font-size: 125%; color: green; background-color: lightblue; text-align:center">Filter Config</p></b>',
            layout={"height": "90%", "width": "100%"},
        )
        layout = {"left": "40%"}
        self.hs["FilterConfigTitle label"].layout = layout
        self.hs["FilterConfigTitle box"].children = [self.hs["FilterConfigTitle label"]]
        ## ## ## ## ## ## label filter_config_box -- end

        ## ## ## ## ## ## config filters with GridspecLayout-- start
        FilterConfigGrid = GridspecLayout(
            8,
            200,
            layout={
                "border": "3px solid #FFCC00",
                "width": "auto",
                # "height": "70%",
                "height": f"{0.6*(self.form_sz[0] - 136)}px",
                "align_items": "flex-start",
                "justify_items": "flex-start",
            },
        )

        ## ## ## ## ## ## ## config filters: left-hand side box in GridspecLayout -- start
        FilterConfigGrid[:7, :100] = GridspecLayout(
            10,
            20,
            grid_gap="8px",
            layout={
                "border": "3px solid #FFCC00",
                "width": "100%",
                "height": "100%",
                "grid_row_gap": "8px",
                "align_items": "flex-start",
                "justify_items": "flex-start",
                "grid_column_gap": "8px",
            },
        )
        self.hs["FilterConfigLeft box"] = FilterConfigGrid[:7, :100]

        FilterConfigGrid[:7, :100][0, :16] = widgets.Dropdown(
            value="phase retrieval",
            layout={"width": "auto"},
            options=TOMO_FILTERLIST,
            description="Filter List",
            indent=False,
            disabled=True,
        )
        self.hs["FilterConfigLeftFltList drpdn"] = FilterConfigGrid[:7, :100][0, :16]

        FilterConfigGrid[:7, :100][0, 16:19] = widgets.Button(
            description="==>", disabled=True, layout={"width": "auto"}
        )
        self.hs["FilterConfigLeftAddTo btn"] = FilterConfigGrid[:7, :100][0, 16:19]
        FilterConfigGrid[:7, :100][0, 16:19].style.button_color = "#0000FF"
        for ii in range(3):
            for jj in range(2):
                FilterConfigGrid[:7, :100][1 + ii, jj * 8 : (jj + 1) * 8] = (
                    widgets.Dropdown(
                        value="",
                        options=[""],
                        description="p" + str(ii * 2 + jj).zfill(2),
                        disabled=True,
                        layout={"width": "90%"},
                    )
                )
        for ii in range(3):
            for jj in range(2):
                FilterConfigGrid[:7, :100][4 + ii, jj * 8 : (jj + 1) * 8] = (
                    widgets.FloatText(
                        value=0,
                        disabled=True,
                        description="p" + str((ii + 3) * 2 + jj).zfill(2),
                        layout={"width": "90%"},
                    )
                )

        self.hs["FilterConfigLeftPar00 text"] = FilterConfigGrid[:7, :100][1, 0:8]
        self.hs["FilterConfigLeftPar01 text"] = FilterConfigGrid[:7, :100][1, 8:16]
        self.hs["FilterConfigLeftPar02 text"] = FilterConfigGrid[:7, :100][2, 0:8]
        self.hs["FilterConfigLeftPar03 text"] = FilterConfigGrid[:7, :100][2, 8:16]
        self.hs["FilterConfigLeftPar04 text"] = FilterConfigGrid[:7, :100][3, 0:8]
        self.hs["FilterConfigLeftPar05 text"] = FilterConfigGrid[:7, :100][3, 8:16]
        self.hs["FilterConfigLeftPar06 text"] = FilterConfigGrid[:7, :100][4, 0:8]
        self.hs["FilterConfigLeftPar07 text"] = FilterConfigGrid[:7, :100][4, 8:16]
        self.hs["FilterConfigLeftPar08 text"] = FilterConfigGrid[:7, :100][5, 0:8]
        self.hs["FilterConfigLeftPar09 text"] = FilterConfigGrid[:7, :100][5, 8:16]
        self.hs["FilterConfigLeftPar10 text"] = FilterConfigGrid[:7, :100][6, 0:8]
        self.hs["FilterConfigLeftPar11 text"] = FilterConfigGrid[:7, :100][6, 8:16]

        FilterConfigGrid[:7, :100][7:, :] = widgets.HTML(
            value='<b><p style="font-weight: bold; font-size: 125%; color: green; background-color: lightblue; text-align:center">Hover mouse over params for the description of the param for each filter</p></b>',
            layout={"height": "90%", "width": "100%"},
        )
        self.hs["FilterConfigLeftFltList drpdn"].observe(
            self.FilterConfigLeftFltList_drpdn_chg, names="value"
        )
        self.hs["FilterConfigLeftAddTo btn"].on_click(
            self.FilterConfigLeftAddTo_btn_clk
        )
        self.hs["FilterConfigLeftPar00 text"].observe(
            self.FilterConfigLeftPar00_text_chg, names="value"
        )
        self.hs["FilterConfigLeftPar01 text"].observe(
            self.FilterConfigLeftPar01_text_chg, names="value"
        )
        self.hs["FilterConfigLeftPar02 text"].observe(
            self.FilterConfigLeftPar02_text_chg, names="value"
        )
        self.hs["FilterConfigLeftPar03 text"].observe(
            self.FilterConfigLeftPar03_text_chg, names="value"
        )
        self.hs["FilterConfigLeftPar04 text"].observe(
            self.FilterConfigLeftPar04_text_chg, names="value"
        )
        self.hs["FilterConfigLeftPar05 text"].observe(
            self.FilterConfigLeftPar05_text_chg, names="value"
        )
        self.hs["FilterConfigLeftPar06 text"].observe(
            self.FilterConfigLeftPar06_text_chg, names="value"
        )
        self.hs["FilterConfigLeftPar07 text"].observe(
            self.FilterConfigLeftPar07_text_chg, names="value"
        )
        self.hs["FilterConfigLeftPar08 text"].observe(
            self.FilterConfigLeftPar08_text_chg, names="value"
        )
        self.hs["FilterConfigLeftPar09 text"].observe(
            self.FilterConfigLeftPar09_text_chg, names="value"
        )
        self.hs["FilterConfigLeftPar10 text"].observe(
            self.FilterConfigLeftPar10_text_chg, names="value"
        )
        self.hs["FilterConfigLeftPar11 text"].observe(
            self.FilterConfigLeftPar11_text_chg, names="value"
        )
        self.hs["FilterConfigLeft box"].children = [
            self.hs["FilterConfigLeftFltList drpdn"],
            self.hs["FilterConfigLeftAddTo btn"],
            self.hs["FilterConfigLeftPar00 text"],
            self.hs["FilterConfigLeftPar01 text"],
            self.hs["FilterConfigLeftPar02 text"],
            self.hs["FilterConfigLeftPar03 text"],
            self.hs["FilterConfigLeftPar04 text"],
            self.hs["FilterConfigLeftPar05 text"],
            self.hs["FilterConfigLeftPar06 text"],
            self.hs["FilterConfigLeftPar07 text"],
            self.hs["FilterConfigLeftPar08 text"],
            self.hs["FilterConfigLeftPar09 text"],
            self.hs["FilterConfigLeftPar10 text"],
            self.hs["FilterConfigLeftPar11 text"],
        ]
        ## ## ## ## ## ## ## config filters: left-hand side box in GridspecLayout -- end

        ## ## ## ## ## ## ## config filters: right-hand side box in GridspecLayout -- start
        FilterConfigGrid[:7, 100:] = GridspecLayout(
            10,
            10,
            grid_gap="8px",
            layout={"border": "3px solid #FFCC00", "width": "100%", "height": "100%"},
        )
        self.hs["FilterConfigRight box"] = FilterConfigGrid[:7, 100:]

        FilterConfigGrid[:7, 100:][:7, :8] = widgets.SelectMultiple(
            value=["None"],
            options=["None"],
            description="Filter Seq",
            disabled=True,
            layout={"height": "100%"},
        )
        self.hs["FilterConfigRightFlt mulsel"] = FilterConfigGrid[:7, 100:][:7, :8]

        FilterConfigGrid[:7, 100:][1, 9] = widgets.Button(
            description="Move Up", disabled=True, layout={"width": "auto"}
        )
        FilterConfigGrid[:7, 100:][1, 9].style.button_color = "#0000FF"
        self.hs["FilterConfigRightMvUp btn"] = FilterConfigGrid[:7, 100:][1, 9]

        FilterConfigGrid[:7, 100:][2, 9] = widgets.Button(
            description="Move Dn", disabled=True, layout={"width": "auto"}
        )
        FilterConfigGrid[:7, 100:][2, 9].style.button_color = "#0000FF"
        self.hs["FilterConfigRightMvDn btn"] = FilterConfigGrid[:7, 100:][2, 9]

        FilterConfigGrid[:7, 100:][3, 9] = widgets.Button(
            description="Remove",
            disabled=True,
            layout={"width": f"{int(2 * (self.form_sz[1] - 98) / 20)}px"},
        )
        FilterConfigGrid[:7, 100:][3, 9].style.button_color = "#0000FF"
        self.hs["FilterConfigRightRm btn"] = FilterConfigGrid[:7, 100:][3, 9]

        FilterConfigGrid[:7, 100:][4, 9] = widgets.Button(
            description="Finish", disabled=True, layout={"width": "auto"}
        )
        FilterConfigGrid[:7, 100:][4, 9].style.button_color = "#0000FF"
        self.hs["FilterConfigRightFnsh btn"] = FilterConfigGrid[:7, 100:][4, 9]

        self.hs["FilterConfigRightFlt mulsel"].observe(
            self.FilterConfigRightFlt_mulsel_chg, names="value"
        )
        self.hs["FilterConfigRightMvUp btn"].on_click(
            self.FilterConfigRightMvUp_btn_clk
        )
        self.hs["FilterConfigRightMvDn btn"].on_click(
            self.FilterConfigRightMvDn_btn_clk
        )
        self.hs["FilterConfigRightRm btn"].on_click(self.FilterConfigRightRm_btn_clk)
        self.hs["FilterConfigRightFnsh btn"].on_click(
            self.FilterConfigRightFnsh_btn_clk
        )
        self.hs["FilterConfigRight box"].children = [
            self.hs["FilterConfigRightFlt mulsel"],
            self.hs["FilterConfigRightMvUp btn"],
            self.hs["FilterConfigRightMvDn btn"],
            self.hs["FilterConfigRightRm btn"],
            self.hs["FilterConfigRightFnsh btn"],
        ]
        ## ## ## ## ## ## ## config filters: right-hand side box in GridspecLayout -- end

        ## ## ## ## ## ## ## config confirm box in GridspecLayout -- start
        FilterConfigGrid[7, :141] = widgets.Text(
            value="Confirm to proceed after you finish data and algorithm configuration...",
            layout={"top": "20%", "width": "100%", "height": "auto"},
            disabled=True,
        )
        self.hs["FilterConfigCfm text"] = FilterConfigGrid[7, :141]

        FilterConfigGrid[7, 142:172] = widgets.Button(
            description="Confirm",
            disabled=True,
            layout={"top": "20%", "width": "100%", "height": "auto"},
        )
        FilterConfigGrid[7, 142:171].style.button_color = "darkviolet"
        self.hs["FilterConfigCfm btn"] = FilterConfigGrid[7, 142:172]
        self.hs["FilterConfigCfm btn"].on_click(self.FilterConfigCfm_btn_clk)
        ## ## ## ## ## ## ## config confirm box in GridspecLayout -- end

        self.hs["FilterConfig box"] = FilterConfigGrid
        self.hs["FilterConfig box"].children = [
            self.hs["FilterConfigLeft box"],
            self.hs["FilterConfigRight box"],
            self.hs["FilterConfigCfm text"],
            self.hs["FilterConfigCfm btn"],
        ]
        ## ## ## ## ## ## config filters with GridspecLayout-- end

        self.hs["Filter&Recon box"].children = [
            self.hs["FilterConfig box"],
        ]
        ## ## ## ## ## config  filter_config_box -- end

        ## ## ## ## ## config recon_box -- start
        layout = {"border": "3px solid #8855AA", "height": "auto"}
        self.hs["Recon box"] = widgets.VBox()
        self.hs["Recon box"].layout = layout

        ## ## ## ## ## ## ## config widgets in recon_box -- start
        layout = {
            "justify-content": "center",
            "align-items": "center",
            "align-contents": "center",
            "border": "3px solid #FFCC00",
            "height": "auto",
        }
        self.hs["ReconDo box"] = widgets.HBox()
        self.hs["ReconDo box"].layout = layout
        layout = {"width": "70%", "height": "auto"}
        self.hs["ReconPrgr bar"] = widgets.IntProgress(
            value=0,
            min=0,
            max=10,
            step=1,
            description="Completing:",
            bar_style="info",  # "success", "info", "warning", "danger" or ""
            orientation="horizontal",
        )
        self.hs["ReconPrgr bar"].layout = layout
        layout = {"width": "15%", "height": "auto"}
        self.hs["Recon btn"] = widgets.Button(description="Recon", disabled=True)
        self.hs["Recon btn"].style.button_color = "darkviolet"
        self.hs["Recon btn"].layout = layout

        self.hs["Recon btn"].on_click(self.Recon_btn_clk)
        self.hs["ReconDo box"].children = [
            self.hs["ReconPrgr bar"],
            self.hs["Recon btn"],
        ]
        ## ## ## ## ## ## ## config widgets in recon_box -- end

        self.hs["Recon box"].children = [
            self.hs["Filter&Recon box"],
            self.hs["ReconDo box"],
        ]
        ## ## ## ## ## config recon box -- end
        ## ## ## ## config Filter&Recon form -- end

        ## ## ## ## config Filter&Recon form -- start
        layout = {
            "border": "3px solid #8855AA",
            "width": "auto",
            # "height": "50%",
            "height": f"{0.7*(self.form_sz[0] - 136)}px",
        }
        self.hs["ReconConfigSumm form"] = widgets.VBox()
        self.hs["ReconConfigSumm form"].layout = layout

        ## ## ## ## ## config filter&recon text -- start
        layout = {"width": "95%", "height": "90%"}
        self.hs["ReconConfigSumm text"] = widgets.Textarea(
            value="Recon Config Info",
            placeholder="Recon Config Info",
            description="Recon Config Info",
            disabled=True,
        )
        self.hs["ReconConfigSumm text"].layout = layout
        ## ## ## ## ## config filter&recon text -- start
        self.hs["ReconConfigSumm form"].children = [self.hs["ReconConfigSumm text"]]
        ## ## ## ## config Filter&Recon form -- end

        self.hs["Flt&Rec acc"].children = [
            self.hs["ReconChunk box"],
            self.hs["Recon box"],
            self.hs["ReconConfigSumm form"],
        ]
        self.hs["Flt&Rec acc"].titles = [
            "STEP 2: Config for Memory Management",
            "StEP 3: Config Preprocessing & Recon",
            "Recon Summary",
        ]
        """self.hs["Flt&Rec acc"].set_title(0, "STEP 2: Config for Memory Management")
        self.hs["Flt&Rec acc"].set_title(1, "StEP 3: Config Preprocessing & Recon")
        self.hs["Flt&Rec acc"].set_title(2, "Recon Summary")"""
        self.hs["Flt&Rec acc"].selected_index = None

        self.hs["Filter&Recon form"].children = [self.hs["Flt&Rec acc"]]
        ## ## ## define boxes in filter&recon_form -- end
        self.bundle_param_handles()

        self.hs["SelRawH5TopDir btn"].initialdir = self.global_h.cwd
        self.hs["SelSavReconDir btn"].initialdir = self.global_h.cwd
        self.hs["SelSavDebugDir btn"].initialdir = self.global_h.cwd
        self.hs["AltFlatFile btn"].initialdir = self.global_h.cwd
        self.hs["AltDarkFile btn"].initialdir = self.global_h.cwd
        self.hs["XNS3DRecTpltFn btn"].initialdir = self.global_h.cwd

    def bundle_param_handles(self):
        self.flt_phs = [
            self.hs["FilterConfigLeftPar00 text"],
            self.hs["FilterConfigLeftPar01 text"],
            self.hs["FilterConfigLeftPar02 text"],
            self.hs["FilterConfigLeftPar03 text"],
            self.hs["FilterConfigLeftPar04 text"],
            self.hs["FilterConfigLeftPar05 text"],
            self.hs["FilterConfigLeftPar06 text"],
            self.hs["FilterConfigLeftPar07 text"],
            self.hs["FilterConfigLeftPar08 text"],
            self.hs["FilterConfigLeftPar09 text"],
            self.hs["FilterConfigLeftPar10 text"],
            self.hs["FilterConfigLeftPar11 text"],
        ]
        self.alg_phs = [
            self.hs["AlgPar00 drpdn"],
            self.hs["AlgPar01 drpdn"],
            self.hs["AlgPar02 drpdn"],
            self.hs["AlgPar03 text"],
            self.hs["AlgPar04 text"],
            self.hs["AlgPar05 text"],
            self.hs["AlgPar06 text"],
        ]

    def reset_config(self):
        self.hs["AlgOptn drpdn"].value = "gridrec"
        self.tomo_selected_alg = "gridrec"
        self.set_alg_param_widgets()
        self.hs["FilterConfigLeftFltList drpdn"].value = "phase retrieval"
        self.tomo_left_box_selected_flt = "phase retrieval"
        self.hs["FilterConfigRightFlt mulsel"].options = ["None"]
        self.hs["FilterConfigRightFlt mulsel"].value = ["None"]
        self.tomo_right_filter_dict = {0: {}}
        self.set_flt_param_widgets()

    def lock_message_text_boxes(self):
        boxes = ["DataInfo text"]
        enable_disable_boxes(self.hs, boxes, disabled=True, level=-1)

    def boxes_logic(self):
        def component_logic():
            if self.tomo_recon_type == "Trial Cent":
                # boxes = ["SavDebug chbx", "XNS3DRec box"]
                boxes = ["XNS3DRec box"]
                enable_disable_boxes(self.hs, boxes, disabled=True, level=-1)
                boxes = ["SelRawH5TopDir btn", "SelSavReconDir btn"]
                enable_disable_boxes(self.hs, boxes, disabled=False, level=-1)
            elif self.tomo_recon_type == "Vol Recon":
                boxes = ["SavDebug chbx", "XNS3DRec box"]
                enable_disable_boxes(self.hs, boxes, disabled=True, level=-1)
                self.tomo_use_debug = False
                self.hs["SavDebug chbx"].value = False
                boxes = ["SelRawH5TopDir btn", "SelSavReconDir btn"]
                enable_disable_boxes(self.hs, boxes, disabled=False, level=-1)
            elif self.tomo_recon_type == "XANES3D Tomo":
                if self.tomo_filepath_configured:
                    if self.xns3d_init_rec_done:
                        boxes = ["XNS3DRec box"]
                        enable_disable_boxes(self.hs, boxes, disabled=False, level=-1)
                        boxes = ["AutoCenSliE txt"]
                        if self.tomo_xns3d_corr_ang:
                            enable_disable_boxes(
                                self.hs, boxes, disabled=False, level=-1
                            )
                        else:
                            enable_disable_boxes(
                                self.hs, boxes, disabled=True, level=-1
                            )
                        boxes = ["AutoCenFullRec chb", "AutoCenSliE txt"]
                        if (
                            self.hs["XNS3DRecScnIDs drpn"].value
                            == self.hs["XNS3DRecScnIDe drpn"].value
                        ):
                            self.hs["AutoCenFullRec chb"].vlaue = False
                            enable_disable_boxes(
                                self.hs, boxes, disabled=True, level=-1
                            )
                        else:
                            self.hs["AutoCenFullRec chb"].vlaue = True
                            enable_disable_boxes(
                                self.hs, boxes, disabled=False, level=-1
                            )
                        boxes = ["XNS3DRefSliROIX sldr", "XNS3DRefSliROIY sldr"]
                        if self.hs["XNS3DDefRefSli&ROI chb"].value:
                            enable_disable_boxes(
                                self.hs, boxes, disabled=True, level=-1
                            )
                        else:
                            enable_disable_boxes(
                                self.hs, boxes, disabled=False, level=-1
                            )
                    else:
                        boxes = ["XNS3DRec box"]
                        enable_disable_boxes(self.hs, boxes, disabled=True, level=-1)
                        boxes = ["XNS3DRecTpltFn btn", "XNS3DInitRec chb"]
                        enable_disable_boxes(self.hs, boxes, disabled=False, level=-1)
            elif self.tomo_recon_type == "Auto Cent":
                if self.tomo_filepath_configured:
                    if self.auto_cen_tplt_dict_rd:
                        boxes = ["AutoCenSliS txt", "AutoCenSliE txt"]
                        if self.auto_cen_rec and not self.auto_cen_rec_all_sli:
                            enable_disable_boxes(
                                self.hs, boxes, disabled=False, level=-1
                            )
                        else:
                            enable_disable_boxes(
                                self.hs, boxes, disabled=True, level=-1
                            )
                        boxes = ["AutoCenFullRec chb"]
                        if not self.auto_cen_rec:
                            enable_disable_boxes(
                                self.hs, boxes, disabled=True, level=-1
                            )
                        else:
                            enable_disable_boxes(
                                self.hs, boxes, disabled=False, level=-1
                            )
                        boxes = ["XNS3DRefSliROIX sldr", "XNS3DRefSliROIY sldr"]
                        if self.hs["XNS3DDefRefSli&ROI chb"].value:
                            enable_disable_boxes(
                                self.hs, boxes, disabled=True, level=-1
                            )
                        else:
                            enable_disable_boxes(
                                self.hs, boxes, disabled=False, level=-1
                            )

                        if Path(self.tomo_recon_dir).exists() and any(
                            Path(self.tomo_recon_dir).iterdir()
                        ):
                            boxes = ["XNS3DDefRefSli&ROI chb", "XNS3DRefSli sldr"]
                            enable_disable_boxes(
                                self.hs, boxes, disabled=False, level=-1
                            )
                        else:
                            boxes = ["XNS3DDefRefSli&ROI chb", "XNS3DRefSli sldr"]
                            enable_disable_boxes(
                                self.hs, boxes, disabled=True, level=-1
                            )

                        self.hs["XNS3DRecCenOpt drpn"].value = "Absolute"
                        boxes = ["XNS3DRecCenOpt drpn"]
                        enable_disable_boxes(self.hs, boxes, disabled=True, level=-1)
                    else:
                        boxes = ["XNS3DRec box"]
                        enable_disable_boxes(self.hs, boxes, disabled=True, level=-1)
                        boxes = ["XNS3DRecTpltFn btn"]
                        enable_disable_boxes(self.hs, boxes, disabled=False, level=-1)

        if not self.tomo_filepath_configured:
            boxes = ["Data tab", "Filter&Recon form", "XNS3DRec box"]
            enable_disable_boxes(self.hs, boxes, disabled=True, level=-1)
            if self.tomo_recon_type in ["XANES3D Tomo", "Auto Cent"]:
                boxes = [
                    "SelRawH5TopDir btn",
                    "SelSavReconDir btn",
                    "Data tab",
                    "Filter&Recon form",
                ]
                enable_disable_boxes(self.hs, boxes, disabled=True, level=-1)
        elif self.tomo_filepath_configured and (
            self.tomo_recon_type in ["XANES3D Tomo", "Auto Cent"]
        ):
            boxes = ["XNS3DRec box"]
            enable_disable_boxes(self.hs, boxes, disabled=False, level=-1)
            boxes = [
                "SelRawH5TopDir btn",
                "SelSavReconDir btn",
                "Data tab",
                "Filter&Recon form",
            ]
            enable_disable_boxes(self.hs, boxes, disabled=True, level=-1)
        elif self.tomo_filepath_configured and (not self.tomo_data_configured):
            boxes = [
                "DataConfig tab",
                "AlgOptn drpdn",
                "DataInfo tab",
                "CenPrev box",
                "ProjPrev box",
                "ReconChunk box",
                "FilterConfigLeftFltList drpdn",
                "FilterConfigLeftAddTo btn",
                "FilterConfigRight box",
                "FilterConfigCfm btn",
            ]
            enable_disable_boxes(self.hs, boxes, disabled=False, level=-1)
            boxes = ["ReconDo box", "TrialCenPrev box", "XNS3DRec box"]
            enable_disable_boxes(self.hs, boxes, disabled=True, level=-1)
        elif (self.tomo_filepath_configured and self.tomo_data_configured) and (
            not self.recon_finish
        ):
            boxes = [
                "DataConfig tab",
                "AlgOptn drpdn",
                "DataInfo tab",
                "CenPrev box",
                "ProjPrev box",
                "ReconChunk box",
                "FilterConfigLeftFltList drpdn",
                "FilterConfigLeftAddTo btn",
                "FilterConfigRight box",
                "Recon box",
            ]
            enable_disable_boxes(self.hs, boxes, disabled=False, level=-1)
            boxes = ["TrialCenPrev box", "XNS3DRec box"]
            enable_disable_boxes(self.hs, boxes, disabled=True, level=-1)
        elif (
            (self.tomo_filepath_configured and self.tomo_data_configured)
            and (self.recon_finish)
            and (self.tomo_recon_type == "Trial Cent")
        ):
            boxes = [
                "DataConfig tab",
                "AlgOptn drpdn",
                "DataInfo tab",
                "CenPrev box",
                "TrialCenPrev box",
                "ProjPrev box",
                "ReconChunk box",
                "FilterConfigLeftFltList drpdn",
                "FilterConfigLeftAddTo btn",
                "FilterConfigRight box",
                "Recon box",
            ]
            enable_disable_boxes(self.hs, boxes, disabled=False, level=-1)
            boxes = ["XNS3DRec box"]
            enable_disable_boxes(self.hs, boxes, disabled=True, level=-1)
        component_logic()
        self.lock_message_text_boxes()

    def cal_set_srch_win(self):
        try:
            self.data_info = get_raw_img_info(
                self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                self.global_h.io_tomo_cfg,
                scan_type="tomo",
            )

            info = ""
            for key, item in self.data_info.items():
                info = info + str(key) + ":" + str(item) + "\n"
            self.hs["DataInfo text"].value = info
            if self.data_info:
                if self.hs["CenWinLeft text"].value >= (
                    self.data_info["img_dim"][2] - self.hs["CenWinWz text"].value - 1
                ):
                    self.hs["CenWinLeft text"].value = 0
                    self.hs["CenWinLeft text"].max = (
                        self.data_info["img_dim"][2]
                        - self.hs["CenWinWz text"].value
                        - 1
                    )
                    self.hs["CenWinLeft text"].value = (
                        int(self.data_info["img_dim"][2] / 2) - 40
                    )
                else:
                    self.hs["CenWinLeft text"].max = (
                        self.data_info["img_dim"][2]
                        - self.hs["CenWinWz text"].value
                        - 1
                    )
        except:
            self.hs["SelFile&PathCfm text"].value = "Cannot open the file..."
            self.hs["DataInfo text"].value = ""

        # if not self.data_info:
        #     self.data_info = get_raw_img_info(
        #         self.tomo_raw_data_file_template.format(self.tomo_scan_id),
        #         self.global_h.io_tomo_cfg,
        #         scan_type="tomo",
        #     )
        #     info = ""
        #     for key, item in self.data_info.items():
        #         info = info + str(key) + ":" + str(item) + "\n"
        #     self.hs["DataInfo text"].value = info
        #     if self.data_info:
        #         if self.hs["CenWinLeft text"].value >= (
        #             self.data_info["img_dim"][2] - self.hs["CenWinWz text"].value - 1
        #         ):
        #             self.hs["CenWinLeft text"].value = 0
        #             self.hs["CenWinLeft text"].max = (
        #                 self.data_info["img_dim"][2]
        #                 - self.hs["CenWinWz text"].value
        #                 - 1
        #             )
        #             self.hs["CenWinLeft text"].value = (
        #                 int(self.data_info["img_dim"][2] / 2) - 40
        #             )
        #         else:
        #             self.hs["CenWinLeft text"].max = (
        #                 self.data_info["img_dim"][2]
        #                 - self.hs["CenWinWz text"].value
        #                 - 1
        #             )
        # else:
        #     di = get_raw_img_info(
        #         self.tomo_raw_data_file_template.format(self.tomo_scan_id),
        #         self.global_h.io_tomo_cfg,
        #         scan_type="tomo",
        #     )
        #     if di:
        #         info = ""
        #         for key, item in di.items():
        #             info = info + str(key) + ":" + str(item) + "\n"
        #         self.hs["DataInfo text"].value = info
        #         if (not self.data_info) or (
        #             list(self.data_info["img_dim"][1:]) != list(di["img_dim"][1:])
        #         ):
        #             self.data_info = di
        #             if self.hs["CenWinLeft text"].value >= (
        #                 self.data_info["img_dim"][2]
        #                 - self.hs["CenWinWz text"].value
        #                 - 1
        #             ):
        #                 self.hs["CenWinLeft text"].value = 0
        #                 self.hs["CenWinLeft text"].max = (
        #                     self.data_info["img_dim"][2]
        #                     - self.hs["CenWinWz text"].value
        #                     - 1
        #                 )
        #             else:
        #                 self.hs["CenWinLeft text"].max = (
        #                     self.data_info["img_dim"][2]
        #                     - self.hs["CenWinWz text"].value
        #                     - 1
        #                 )
        #             self.hs["CenWinLeft text"].value = (
        #                 int(self.data_info["img_dim"][2] / 2) - 40
        #             )
        #         else:
        #             self.data_info = di
        #     else:
        #         self.hs["SelFile&PathCfm text"].value = "Cannot open the file..."

    def set_rois(self):
        s = self.data_info["img_dim"]
        if self.tomo_recon_type == "Trial Cent":
            new_min = 1
            new_val = int(s[1] / self.tomo_ds_fac / 2) + 10
            new_max = int(s[1] / self.tomo_ds_fac)
            set_data_widget(self, "RoiSliEnd text", new_min, new_val, new_max)

            new_min = 0
            new_val = int(s[1] / self.tomo_ds_fac / 2) - 10
            new_max = int(s[1] / self.tomo_ds_fac) - 1
            set_data_widget(self, "RoiSliStart text", new_min, new_val, new_max)

            new_min = 0
            new_val = 0
            new_max = int(s[2] / self.tomo_ds_fac) - 1
            set_data_widget(self, "RoiColStart text", new_min, new_val, new_max)

            new_min = 0
            new_val = int(s[2] / self.tomo_ds_fac)
            new_max = int(s[2] / self.tomo_ds_fac)
            set_data_widget(self, "RoiColEnd text", new_min, new_val, new_max)

            new_min = 0
            new_val = 0
            new_max = int(s[2] / self.tomo_ds_fac)
            set_data_widget(self, "AutoRefColStart text", new_min, new_val, new_max)

            new_min = 0
            new_val = int(s[2] / self.tomo_ds_fac)
            new_max = int(s[2] / self.tomo_ds_fac)
            set_data_widget(self, "AutoRefColEnd text", new_min, new_val, new_max)

            new_min = 0
            new_val = np.round(s[2] / self.tomo_ds_fac) / 2
            new_max = int(s[2] / self.tomo_ds_fac)
            set_data_widget(self, "RotCen text", new_min, new_val, new_max)

            new_min = 0
            new_val = int(np.round(s[2] / self.tomo_ds_fac / 2)) - 40
            new_max = int(np.round(s[2] / self.tomo_ds_fac))
            set_data_widget(self, "CenWinLeft text", new_min, new_val, new_max)
        elif self.tomo_recon_type == "Vol Recon":
            new_min = 1
            new_val = int(s[1] / self.tomo_ds_fac)
            new_max = int(s[1] / self.tomo_ds_fac)
            set_data_widget(self, "RoiSliEnd text", new_min, new_val, new_max)

            new_min = 0
            new_val = 0
            new_max = int(s[1] / self.tomo_ds_fac) - 1
            set_data_widget(self, "RoiSliStart text", new_min, new_val, new_max)

            new_min = 0
            new_val = 0
            new_max = int(s[2] / self.tomo_ds_fac) - 1
            set_data_widget(self, "RoiColStart text", new_min, new_val, new_max)

            new_min = 1
            new_val = int(s[2] / self.tomo_ds_fac)
            new_max = int(s[2] / self.tomo_ds_fac)
            set_data_widget(self, "RoiColEnd text", new_min, new_val, new_max)

            new_min = 0
            new_val = 0
            new_max = int(s[2] / self.tomo_ds_fac) - 1
            set_data_widget(self, "AutoRefColStart text", new_min, new_val, new_max)

            new_min = 1
            new_val = int(s[2] / self.tomo_ds_fac)
            new_max = int(s[2] / self.tomo_ds_fac)
            set_data_widget(self, "AutoRefColEnd text", new_min, new_val, new_max)
        # elif self.tomo_recon_type == "XANES3D Tomo":
        #     new_min = 0
        #     new_val = [
        #         int(s[2] / self.tomo_ds_fac / 4),
        #         int(3 * s[2] / self.tomo_ds_fac / 4)
        #     ]
        #     new_max = int(s[2] / self.tomo_ds_fac)
        #     set_data_widget(self, "XNS3DRecROIX sldr", new_min, new_val,
        #                          new_max)

        #     new_min = 0
        #     new_val = [
        #         int(s[2] / self.tomo_ds_fac / 4),
        #         int(3 * s[2] / self.tomo_ds_fac / 4)
        #     ]
        #     new_max = int(s[2] / self.tomo_ds_fac)
        #     set_data_widget(self, "XNS3DRecROIY sldr", new_min, new_val,
        #                          new_max)

        #     new_min = 0
        #     new_val = [
        #         int(s[1] / self.tomo_ds_fac / 4),
        #         int(3 * s[1] / self.tomo_ds_fac / 4)
        #     ]
        #     new_max = int(s[1] / self.tomo_ds_fac)
        #     set_data_widget(self, "XNS3DRecROIZ sldr", new_min, new_val,
        #                          new_max)

    # def set_data_widget(self, wn, new_min, new_val, new_max):
    #     self.hs[wn].min = min(new_min, self.hs[wn].min)
    #     self.hs[wn].max = max(new_max, self.hs[wn].max)
    #     self.hs[wn].value = new_val
    #     self.hs[wn].min = new_min
    #     self.hs[wn].max = new_max

    def tomo_compound_logic(self):
        self.hs["RotCen text"].disabled = True
        if self.tomo_recon_type == "Trial Cent":
            if self.tomo_raw_data_top_dir_set and self.tomo_data_center_path_set:
                self.hs["ScanId drpdn"].disabled = False
                self.hs["CenWinLeft text"].disabled = False
                self.hs["CenWinWz text"].disabled = False
                self.hs["ReconChunkSz text"].disabled = True
                self.hs["ReconMargSz text"].disabled = True
                self.hs["RoiSliEnd text"].disabled = True
        elif self.tomo_recon_type == "Vol Recon":
            if self.tomo_raw_data_top_dir_set and self.tomo_recon_path_set:
                self.hs["ScanId drpdn"].disabled = True
                self.hs["CenWinLeft text"].disabled = True
                self.hs["CenWinWz text"].disabled = True
                self.hs["ReconChunkSz text"].disabled = False
                self.hs["ReconMargSz text"].disabled = False
                self.hs["RoiSliStart text"].disabled = False
                self.hs["RoiSliEnd text"].disabled = False
                self.hs["UseConfig chbx"].value = True
                self.hs["UseConfig chbx"].disabled = True
                self.hs["RoiColStart text"].disabled = True
                self.hs["RoiColEnd text"].disabled = True
            self.tomo_use_read_config = True

        if self.tomo_filepath_configured:
            if self.tomo_use_alt_flat:
                self.hs["AltFlatFile btn"].disabled = False
            else:
                self.hs["AltFlatFile btn"].disabled = True

            if self.tomo_use_fake_flat:
                self.hs["FakeFlatVal text"].disabled = False
            else:
                self.hs["FakeFlatVal text"].disabled = True

            if self.tomo_use_alt_dark:
                self.hs["AltDarkFile btn"].disabled = False
            else:
                self.hs["AltDarkFile btn"].disabled = True

            if self.tomo_use_fake_dark:
                self.hs["FakeDarkVal text"].disabled = False
            else:
                self.hs["FakeDarkVal text"].disabled = True

            if self.tomo_use_blur_flat:
                self.hs["BlurKern text"].disabled = False
            else:
                self.hs["BlurKern text"].disabled = True

            if self.tomo_use_rm_zinger:
                self.hs["ZingerLevel text"].disabled = False
            else:
                self.hs["ZingerLevel text"].disabled = True

            if self.tomo_use_mask:
                self.hs["MaskRat text"].disabled = False
            else:
                self.hs["MaskRat text"].disabled = True

            if self.tomo_is_wedge:
                self.hs["AutoDet chbx"].disabled = False
                if self.tomo_use_wedge_ang_auto_det:
                    self.hs["MissIdxStart text"].disabled = True
                    self.hs["MissIdxEnd text"].disabled = True
                    self.hs["AutoThres text"].disabled = False
                    self.hs["AutoRefFn btn"].disabled = False
                    if self.tomo_wedge_ang_auto_det_ref_fn is not None:
                        self.hs["AutoRefSli sldr"].disabled = False
                    else:
                        self.hs["AutoRefSli sldr"].disabled = True
                else:
                    self.hs["MissIdxStart text"].disabled = False
                    self.hs["MissIdxEnd text"].disabled = False
                    self.hs["AutoThres text"].disabled = True
                    self.hs["AutoRefFn btn"].disabled = True
                    self.hs["AutoRefSli sldr"].disabled = True
            else:
                self.hs["AutoDet chbx"].value = False
                self.hs["AutoDet chbx"].disabled = True
                self.hs["MissIdxStart text"].disabled = True
                self.hs["MissIdxEnd text"].disabled = True
                self.hs["AutoThres text"].disabled = True
                self.hs["AutoRefFn btn"].disabled = True

    def set_rec_params_from_rec_dict(self, recon_param_dict):
        self.tomo_raw_data_top_dir = recon_param_dict["file_params"]["raw_data_top_dir"]
        self.tomo_data_center_path = recon_param_dict["file_params"]["data_center_dir"]
        self.tomo_recon_top_dir = recon_param_dict["file_params"]["recon_top_dir"]
        self.tomo_debug_top_dir = recon_param_dict["file_params"]["debug_top_dir"]
        self.tomo_alt_flat_file = recon_param_dict["file_params"]["alt_flat_file"]
        self.tomo_alt_dark_file = recon_param_dict["file_params"]["alt_dark_file"]
        self.tomo_wedge_ang_auto_det_ref_fn = recon_param_dict["file_params"][
            "wedge_ang_auto_det_ref_fn"
        ]
        self.global_h.io_tomo_cfg = recon_param_dict["file_params"]["io_confg"]
        self.tomo_use_debug = recon_param_dict["recon_config"]["use_debug"]

        self.tomo_use_alt_flat = recon_param_dict["recon_config"]["use_alt_flat"]
        self.tomo_use_alt_dark = recon_param_dict["recon_config"]["use_alt_dark"]
        self.tomo_use_fake_flat = recon_param_dict["recon_config"]["use_fake_flat"]
        self.tomo_use_fake_dark = recon_param_dict["recon_config"]["use_fake_dark"]
        if "use_flat_blur" in recon_param_dict["recon_config"]:
            self.tomo_use_blur_flat = recon_param_dict["recon_config"]["use_flat_blur"]
        else:
            self.tomo_use_blur_flat = False
        self.tomo_use_rm_zinger = recon_param_dict["recon_config"]["use_rm_zinger"]
        self.tomo_use_mask = recon_param_dict["recon_config"]["use_mask"]
        self.tomo_use_wedge_ang_auto_det = recon_param_dict["recon_config"][
            "use_wedge_ang_auto_det"
        ]
        self.tomo_is_wedge = recon_param_dict["recon_config"]["is_wedge"]
        self.tomo_use_read_config = recon_param_dict["recon_config"]["use_config_file"]

        self.tomo_right_filter_dict = recon_param_dict["flt_params"]
        self.tomo_scan_id = recon_param_dict["data_params"]["scan_id"]
        self.tomo_ds_fac = recon_param_dict["data_params"]["downsample"]
        self.tomo_rot_cen = recon_param_dict["data_params"]["rot_cen"]
        self.tomo_cen_win_s = recon_param_dict["data_params"]["cen_win_s"]
        self.tomo_cen_win_w = recon_param_dict["data_params"]["cen_win_w"]
        self.tomo_fake_flat_val = recon_param_dict["data_params"]["fake_flat_val"]
        self.tomo_fake_dark_val = recon_param_dict["data_params"]["fake_dark_val"]
        self.tomo_sli_s = recon_param_dict["data_params"]["sli_s"]
        self.tomo_sli_e = recon_param_dict["data_params"]["sli_e"]
        self.tomo_col_s = recon_param_dict["data_params"]["col_s"]
        self.tomo_col_e = recon_param_dict["data_params"]["col_e"]
        self.tomo_chunk_sz = recon_param_dict["data_params"]["chunk_sz"]
        self.tomo_margin = recon_param_dict["data_params"]["margin"]
        if "blur_kernel" in recon_param_dict["data_params"]:
            self.tomo_flat_blur_kernel = recon_param_dict["data_params"]["blur_kernel"]
        else:
            self.tomo_flat_blur_kernel = 1
        self.tomo_zinger_val = recon_param_dict["data_params"]["zinger_val"]
        self.tomo_mask_ratio = recon_param_dict["data_params"]["mask_ratio"]
        self.tomo_wedge_missing_s = recon_param_dict["data_params"]["wedge_missing_s"]
        self.tomo_wedge_missing_e = recon_param_dict["data_params"]["wedge_missing_e"]
        self.tomo_wedge_auto_ref_col_s = recon_param_dict["data_params"]["wedge_col_s"]
        self.tomo_wedge_auto_ref_col_e = recon_param_dict["data_params"]["wedge_col_e"]
        self.tomo_wedge_ang_auto_det_thres = recon_param_dict["data_params"][
            "wedge_ang_auto_det_thres"
        ]
        self.tomo_selected_alg = recon_param_dict["alg_params"]["algorithm"]
        self.alg_param_dict = recon_param_dict["alg_params"]["params"]

    def set_rec_dict_from_rec_params(self):
        self.tomo_recon_param_dict["file_params"][
            "raw_data_top_dir"
        ] = self.tomo_raw_data_top_dir
        self.tomo_recon_param_dict["file_params"][
            "data_center_dir"
        ] = self.tomo_data_center_path
        self.tomo_recon_param_dict["file_params"][
            "recon_top_dir"
        ] = self.tomo_recon_top_dir
        self.tomo_recon_param_dict["file_params"][
            "debug_top_dir"
        ] = self.tomo_debug_top_dir
        self.tomo_recon_param_dict["file_params"][
            "cen_list_file"
        ] = self.tomo_cen_list_file
        self.tomo_recon_param_dict["file_params"][
            "alt_flat_file"
        ] = self.tomo_alt_flat_file
        self.tomo_recon_param_dict["file_params"][
            "alt_dark_file"
        ] = self.tomo_alt_dark_file
        self.tomo_recon_param_dict["file_params"][
            "wedge_ang_auto_det_ref_fn"
        ] = self.tomo_wedge_ang_auto_det_ref_fn
        self.tomo_recon_param_dict["file_params"][
            "io_confg"
        ] = self.global_h.io_tomo_cfg
        self.tomo_recon_param_dict["file_params"]["use_struc_h5_reader"] = (
            self.global_h.io_tomo_cfg["use_h5_reader"]
        )
        self.tomo_recon_param_dict["file_params"]["hardware_trig_type"] = (
            True
            if "zfly" in self.global_h.io_tomo_cfg["tomo_raw_fn_template"]
            else False
        )
        self.tomo_recon_param_dict["recon_config"]["recon_type"] = self.tomo_recon_type
        self.tomo_recon_param_dict["recon_config"]["use_debug"] = self.tomo_use_debug
        self.tomo_recon_param_dict["recon_config"][
            "use_alt_flat"
        ] = self.tomo_use_alt_flat
        self.tomo_recon_param_dict["recon_config"][
            "use_alt_dark"
        ] = self.tomo_use_alt_dark
        self.tomo_recon_param_dict["recon_config"][
            "use_fake_flat"
        ] = self.tomo_use_fake_flat
        self.tomo_recon_param_dict["recon_config"][
            "use_fake_dark"
        ] = self.tomo_use_fake_dark
        self.tomo_recon_param_dict["recon_config"][
            "use_flat_blur"
        ] = self.tomo_use_blur_flat
        self.tomo_recon_param_dict["recon_config"][
            "use_rm_zinger"
        ] = self.tomo_use_rm_zinger
        self.tomo_recon_param_dict["recon_config"]["use_mask"] = self.tomo_use_mask
        self.tomo_recon_param_dict["recon_config"][
            "use_wedge_ang_auto_det"
        ] = self.tomo_use_wedge_ang_auto_det
        self.tomo_recon_param_dict["recon_config"]["is_wedge"] = self.tomo_is_wedge
        self.tomo_recon_param_dict["recon_config"][
            "use_config_file"
        ] = self.tomo_use_read_config
        self.tomo_recon_param_dict["flt_params"] = self.tomo_right_filter_dict
        self.tomo_recon_param_dict["data_params"]["scan_id"] = self.tomo_scan_id
        self.tomo_recon_param_dict["data_params"]["downsample"] = self.tomo_ds_fac
        self.tomo_recon_param_dict["data_params"]["rot_cen"] = self.tomo_rot_cen
        self.tomo_recon_param_dict["data_params"]["cen_win_s"] = self.tomo_cen_win_s
        self.tomo_recon_param_dict["data_params"]["cen_win_w"] = self.tomo_cen_win_w
        self.tomo_recon_param_dict["data_params"][
            "fake_flat_val"
        ] = self.tomo_fake_flat_val
        self.tomo_recon_param_dict["data_params"][
            "fake_dark_val"
        ] = self.tomo_fake_dark_val
        self.tomo_recon_param_dict["data_params"]["fake_flat_roi"] = None
        self.tomo_recon_param_dict["data_params"]["sli_s"] = self.tomo_sli_s
        self.tomo_recon_param_dict["data_params"]["sli_e"] = self.tomo_sli_e
        self.tomo_recon_param_dict["data_params"]["col_s"] = self.tomo_col_s
        self.tomo_recon_param_dict["data_params"]["col_e"] = self.tomo_col_e
        self.tomo_recon_param_dict["data_params"]["chunk_sz"] = self.tomo_chunk_sz
        self.tomo_recon_param_dict["data_params"]["margin"] = self.tomo_margin
        self.tomo_recon_param_dict["data_params"][
            "blur_kernel"
        ] = self.tomo_flat_blur_kernel
        self.tomo_recon_param_dict["data_params"]["zinger_val"] = self.tomo_zinger_val
        self.tomo_recon_param_dict["data_params"]["mask_ratio"] = self.tomo_mask_ratio
        self.tomo_recon_param_dict["data_params"][
            "wedge_missing_s"
        ] = self.tomo_wedge_missing_s
        self.tomo_recon_param_dict["data_params"][
            "wedge_missing_e"
        ] = self.tomo_wedge_missing_e
        self.tomo_recon_param_dict["data_params"][
            "wedge_col_s"
        ] = self.tomo_wedge_auto_ref_col_s
        self.tomo_recon_param_dict["data_params"][
            "wedge_col_e"
        ] = self.tomo_wedge_auto_ref_col_e
        self.tomo_recon_param_dict["data_params"][
            "wedge_ang_auto_det_thres"
        ] = self.tomo_wedge_ang_auto_det_thres
        self.tomo_recon_param_dict["alg_params"] = {
            "algorithm": self.tomo_selected_alg,
            "params": self.alg_param_dict,
        }

    def set_widgets_from_rec_params(self, recon_param_dict):
        self.hs["UseAltFlat chbx"].value = self.tomo_use_alt_flat
        if self.tomo_use_alt_flat and self.tomo_alt_flat_file is not None:
            self.hs["AltFlatFile btn"].files = [self.tomo_alt_flat_file]
            self.hs["AltFlatFile btn"].style.button_color = "lightgreen"
        else:
            self.hs["AltFlatFile btn"].files = []
            self.hs["AltFlatFile btn"].style.button_color = "orange"
        self.hs["UseAltDark chbx"].value = self.tomo_use_alt_dark
        if self.tomo_use_alt_dark and self.tomo_alt_dark_file is not None:
            self.hs["AltDarkFile btn"].files = [self.tomo_alt_dark_file]
            self.hs["AltDarkFile btn"].style.button_color = "lightgreen"
        else:
            self.hs["AltDarkFile btn"].files = []
            self.hs["AltDarkFile btn"].style.button_color = "orange"
        self.hs["UseFakeFlat chbx"].value = self.tomo_use_fake_flat
        self.hs["UseFakeDark chbx"].value = self.tomo_use_fake_dark
        self.hs["UseBlurFlat chbx"].value = self.tomo_use_blur_flat
        self.hs["UseRmZinger chbx"].value = self.tomo_use_rm_zinger
        self.hs["UseMask chbx"].value = self.tomo_use_mask
        self.hs["AutoDet chbx"].value = self.tomo_use_wedge_ang_auto_det
        self.hs["IsWedge chbx"].value = self.tomo_is_wedge

        a = []
        for ii in sorted(self.tomo_right_filter_dict.keys()):
            a.append(self.tomo_right_filter_dict[ii]["filter_name"])
        self.hs["FilterConfigRightFlt mulsel"].options = a
        self.hs["FilterConfigRightFlt mulsel"].value = (a[0],)
        self.hs["FilterConfigLeftFltList drpdn"].value = a[0]
        self.tomo_left_box_selected_flt = a[0]
        self.set_flt_param_widgets(par_dict=self.tomo_right_filter_dict["0"]["params"])

        self.hs["AlgOptn drpdn"].value = self.tomo_selected_alg
        self.set_alg_param_widgets(par_dict=self.alg_param_dict)

        self.hs["ScanId drpdn"].value = str(self.tomo_scan_id)
        self.hs["RoiColStart text"].value = self.tomo_col_s
        self.hs["RoiColEnd text"].value = self.tomo_col_e
        self.hs["DnSampFac text"].value = self.tomo_ds_fac
        self.hs["RotCen text"].value = self.tomo_rot_cen
        self.hs["CenWinLeft text"].value = self.tomo_cen_win_s
        self.hs["CenWinWz text"].value = self.tomo_cen_win_w
        self.hs["FakeFlatVal text"].value = self.tomo_fake_flat_val
        self.hs["FakeDarkVal text"].value = self.tomo_fake_dark_val
        self.hs["ReconChunkSz text"].value = self.tomo_chunk_sz
        self.hs["ReconMargSz text"].value = self.tomo_margin
        self.hs["BlurKern text"].value = self.tomo_flat_blur_kernel
        self.hs["ZingerLevel text"].value = self.tomo_zinger_val
        if (
            self.tomo_use_wedge_ang_auto_det
            and self.tomo_is_wedge
            and self.tomo_wedge_ang_auto_det_ref_fn is not None
        ):
            self.hs["AutoRefFn btn"].files = [self.tomo_wedge_ang_auto_det_ref_fn]
            self.hs["AutoRefFn btn"].style.button_color = "lightgreen"
        else:
            self.hs["AutoRefFn btn"].files = []
            self.hs["AutoRefFn btn"].style.button_color = "orange"
        self.hs["MaskRat text"].value = self.tomo_mask_ratio
        self.hs["MissIdxStart text"].value = self.tomo_wedge_missing_s
        self.hs["MissIdxEnd text"].value = self.tomo_wedge_missing_e
        self.hs["AutoRefColStart text"].value = self.tomo_wedge_auto_ref_col_s
        self.hs["AutoRefColEnd text"].value = self.tomo_wedge_auto_ref_col_e
        self.hs["AutoThres text"].value = self.tomo_wedge_ang_auto_det_thres

    def set_rec_params_from_widgets(self):
        self.tomo_use_alt_flat = self.hs["UseAltFlat chbx"].value
        self.tomo_use_alt_dark = self.hs["UseAltDark chbx"].value
        self.tomo_use_fake_flat = self.hs["UseFakeFlat chbx"].value
        self.tomo_use_fake_dark = self.hs["UseFakeDark chbx"].value
        self.tomo_use_blur_flat = self.hs["UseBlurFlat chbx"].value
        self.tomo_use_rm_zinger = self.hs["UseRmZinger chbx"].value
        self.tomo_use_mask = self.hs["UseMask chbx"].value
        self.tomo_use_wedge_ang_auto_det = self.hs["AutoDet chbx"].value
        self.tomo_is_wedge = self.hs["IsWedge chbx"].value
        self.tomo_use_read_config = self.hs["UseConfig chbx"].value

        a = list(self.hs["FilterConfigRightFlt mulsel"].options)
        d = {}
        if len(a) > 0:
            cnt = 0
            for ii in sorted(self.tomo_right_filter_dict.keys()):
                d[cnt] = self.tomo_right_filter_dict[ii]
                cnt += 1
            self.tomo_right_filter_dict = d
        else:
            self.tomo_right_filter_dict = {0: {}}

        self.tomo_scan_id = self.hs["ScanId drpdn"].value
        self.tomo_ds_fac = self.hs["DnSampFac text"].value
        self.tomo_rot_cen = self.hs["RotCen text"].value
        self.tomo_cen_win_s = self.hs["CenWinLeft text"].value
        self.tomo_cen_win_w = self.hs["CenWinWz text"].value
        self.tomo_fake_flat_val = self.hs["FakeFlatVal text"].value
        self.tomo_fake_dark_val = self.hs["FakeDarkVal text"].value
        if not self.hs["AltFlatFile btn"].files:
            self.tomo_alt_flat_file = None
        else:
            self.tomo_alt_flat_file = self.hs["AltFlatFile btn"].files[0]
        if not self.hs["AltDarkFile btn"].files:
            self.tomo_alt_dark_file = None
        else:
            self.tomo_alt_dark_file = self.hs["AltDarkFile btn"].files[0]
        self.tomo_sli_s = self.hs["RoiSliStart text"].value
        self.tomo_sli_e = self.hs["RoiSliEnd text"].value
        self.tomo_col_s = self.hs["RoiColStart text"].value
        self.tomo_col_e = self.hs["RoiColEnd text"].value
        self.tomo_chunk_sz = self.hs["ReconChunkSz text"].value
        self.tomo_margin = self.hs["ReconMargSz text"].value
        self.tomo_flat_blur_kernel = self.hs["BlurKern text"].value
        self.tomo_zinger_val = self.hs["ZingerLevel text"].value
        self.tomo_mask_ratio = self.hs["MaskRat text"].value
        self.tomo_wedge_missing_s = self.hs["MissIdxStart text"].value
        self.tomo_wedge_missing_e = self.hs["MissIdxEnd text"].value
        self.tomo_wedge_auto_ref_col_s = self.hs["AutoRefColStart text"].value
        self.tomo_wedge_auto_ref_col_e = self.hs["AutoRefColEnd text"].value
        self.tomo_wedge_ang_auto_det_thres = self.hs["AutoThres text"].value

    def reset_alg_param_widgets(self):
        for ii in range(3):
            self.alg_phs[ii].options = ""
            self.alg_phs[ii].description_tooltip = "p" + str(ii).zfill(2)
        for ii in range(3, 7):
            self.alg_phs[ii].value = 0
            self.alg_phs[ii].description_tooltip = "p" + str(ii).zfill(2)

    def set_alg_param_widgets(self, par_dict=None):
        self.reset_alg_param_widgets()
        for h in self.alg_phs:
            h.disabled = True
            layout = {"width": "23.5%", "visibility": "hidden"}
            h.layout = layout
        alg = TOMO_ALG_PARAM_DICT[self.tomo_selected_alg]
        for idx in alg.keys():
            self.alg_phs[idx].disabled = False
            layout = {"width": "23.5%", "visibility": "visible"}
            self.alg_phs[idx].layout = layout
            if idx < 3:
                self.alg_phs[idx].options = alg[idx][1]
                if par_dict is None:
                    self.alg_phs[idx].value = alg[idx][1][0]
                else:
                    self.alg_phs[idx].value = par_dict[alg[idx][0]]
            else:
                if par_dict is None:
                    self.alg_phs[idx].value = alg[idx][1]
                else:
                    self.alg_phs[idx].value = par_dict[alg[idx][0]]
            self.alg_phs[idx].description_tooltip = alg[idx][2]

    def read_alg_param_widgets(self):
        self.alg_param_dict = {}
        alg = TOMO_ALG_PARAM_DICT[self.tomo_selected_alg]
        for idx in alg.keys():
            self.alg_param_dict[alg[idx][0]] = alg[idx][-1](self.alg_phs[idx].value)
        self.alg_param_dict = dict(OrderedDict(self.alg_param_dict))

    def reset_flt_param_widgets(self):
        for ii in range(6):
            self.flt_phs[ii].options = ""
            self.flt_phs[ii].description_tooltip = "p" + str(ii).zfill(2)
        for ii in range(6, 12):
            self.flt_phs[ii].value = 0
            self.flt_phs[ii].description_tooltip = "p" + str(ii).zfill(2)

    def set_flt_param_widgets(self, par_dict=None):
        self.reset_flt_param_widgets()
        for h in self.flt_phs:
            h.disabled = True
        flt = TOMO_FILTER_PARAM_DICT[self.tomo_left_box_selected_flt]
        for idx in flt.keys():
            self.flt_phs[idx].disabled = False
            if idx < 6:
                self.flt_phs[idx].options = flt[idx][1]
                if par_dict is None:
                    self.flt_phs[idx].value = flt[idx][1][0]
                else:
                    self.flt_phs[idx].value = par_dict[flt[idx][0]]
            else:
                if par_dict is None:
                    self.flt_phs[idx].value = flt[idx][1]
                else:
                    self.flt_phs[idx].value = par_dict[flt[idx][0]]
            self.flt_phs[idx].description_tooltip = flt[idx][2]

    def read_flt_param_widgets(self):
        self.flt_param_dict = {}
        flt = TOMO_FILTER_PARAM_DICT[self.tomo_left_box_selected_flt]
        for idx in flt.keys():
            self.flt_param_dict[flt[idx][0]] = self.flt_phs[idx].value
        self.flt_param_dict = dict(OrderedDict(self.flt_param_dict))

    def read_config(self, fn=None):
        if fn is None:
            if Path(self.tomo_cen_list_file).suffix.strip(".") == "json":
                with open(self.tomo_cen_list_file, "r") as f:
                    tem = dict(OrderedDict(json.load(f)))
                return tem
            else:
                print("json is the only allowed configuration file type.")
                return None
        else:
            if Path(fn).suffix.strip(".") == "json":
                with open(fn, "r") as f:
                    tem = dict(OrderedDict(json.load(f)))
                return tem
            else:
                print("json is the only allowed configuration file type.")
                return None

    def SelRawH5TopDir_btn_clk(self, a):
        self.reset_config()
        if len(a.files[0]) != 0:
            self.tomo_raw_data_top_dir = a.files[0]
            self.tomo_recon_top_dir = a.files[0]
            self.tomo_raw_data_file_template = str(
                Path(self.tomo_raw_data_top_dir)
                / self.global_h.io_tomo_cfg["tomo_raw_fn_template"],
            )
            b = "{date:%Y-%m-%d-%H-%M-%S}".format(date=datetime.now())
            self.tomo_trial_cen_dict_fn = str(
                Path(self.tomo_raw_data_top_dir) / "trial_cen_dict_{}.json".format(b)
            )
            self.tomo_recon_dict_fn = str(
                Path(self.tomo_raw_data_top_dir) / "recon_dict_{}.json".format(b)
            )
            self.tomo_raw_data_top_dir_set = True
            self.tomo_recon_path_set = True
            self.hs["SelRawH5TopDir btn"].initialdir = str(Path(a.files[0]).absolute())
            self.hs["SelSavReconDir btn"].initialdir = str(Path(a.files[0]).absolute())
            self.hs["SelSavDebugDir btn"].initialdir = str(Path(a.files[0]).absolute())
            self.hs["ReadConfig_btn"].initialdir = str(Path(a.files[0]).absolute())
            self.hs["AltFlatFile btn"].initialdir = str(Path(a.files[0]).absolute())
            self.hs["AltDarkFile btn"].initialdir = str(Path(a.files[0]).absolute())
            self.hs["AutoRefFn btn"].initialdir = str(Path(a.files[0]).absolute())
            self.hs["XNS3DRecTpltFn btn"].initialdir = str(Path(a.files[0]).absolute())
            update_json_content(
                self.global_h.GUI_cfg_file, {"cwd": str(Path(a.files[0]).absolute())}
            )
            self.global_h.cwd = str(Path(a.files[0]).absolute())
        else:
            self.tomo_raw_data_top_dir = None
            self.tomo_raw_data_top_dir_set = False
            self.tomo_recon_top_dir = None
            self.tomo_recon_path_set = False
            self.hs["SelRawH5TopDir text"].value = "Choose raw h5 top dir ..."
        self.tomo_filepath_configured = False
        self.recon_finish = False
        self.hs["SelFile&PathCfm text"].value = (
            "After setting directories, confirm to proceed ..."
        )
        self.boxes_logic()

    def SelSavReconDir_btn_clk(self, a):
        self.reset_config()
        if not self.tomo_raw_data_top_dir_set:
            self.hs["SelFile&PathCfm text"].value = (
                "Please specify raw h5 top directory first ..."
            )
            self.hs["SelSavReconDir text"].value = (
                "Choose top directory where recon subdirectories are saved..."
            )
            self.tomo_recon_path_set = False
        else:
            if len(a.files[0]) != 0:
                self.tomo_recon_top_dir = a.files[0]
                self.tomo_recon_path_set = True
                update_json_content(
                    self.global_h.GUI_cfg_file,
                    {"cwd": str(Path(a.files[0]).absolute())},
                )
                self.global_h.cwd = str(Path(a.files[0]).absolute())
            else:
                self.tomo_recon_top_dir = None
                self.tomo_recon_path_set = False
                self.hs["SelSavReconDir text"].value = (
                    "Select top directory where recon subdirectories are saved..."
                )
            self.hs["SelFile&PathCfm text"].value = (
                "After setting directories, confirm to proceed ..."
            )
        self.tomo_filepath_configured = False
        self.recon_finish = False
        self.boxes_logic()

    def SelSavDebugDir_btn_clk(self, a):
        self.reset_config()
        if not self.tomo_raw_data_top_dir_set:
            self.hs["SelFile&PathCfm text"].value = (
                "Please specify raw h5 top directory first ..."
            )
            self.hs["SelSavDebugDir text"].value = (
                "Select top directory where debug dir will be created..."
            )
            self.tomo_debug_path_set = False
        else:
            if len(a.files[0]) != 0:
                self.tomo_debug_top_dir = a.files[0]
                self.tomo_debug_path_set = True
                update_json_content(
                    self.global_h.GUI_cfg_file,
                    {"cwd": str(Path(a.files[0]).absolute())},
                )
                self.global_h.cwd = str(Path(a.files[0]).absolute())
            else:
                self.tomo_debug_top_dir = None
                self.tomo_debug_path_set = False
                self.hs["SelSavDebugDir text"].value = (
                    "Select top directory where debug dir will be created..."
                )
            self.hs["SelFile&PathCfm text"].value = (
                "After setting directories, confirm to proceed ..."
            )
        self.tomo_filepath_configured = False
        self.recon_finish = False
        self.boxes_logic()

    def SavDebug_chbx_chg(self, a):
        self.reset_config()
        if a["owner"].value:
            self.tomo_use_debug = True
            self.hs["SelSavDebugDir btn"].disabled = False
            self.hs["SelSavDebugDir text"].value = (
                "Select top directory where debug dir will be created..."
            )
            self.hs["SelSavDebugDir btn"].style.button_color = "orange"
        else:
            self.tomo_use_debug = False
            self.hs["SelSavDebugDir btn"].disabled = True
            self.hs["SelSavDebugDir text"].value = "Debug is disabled..."
            self.hs["SelSavDebugDir btn"].style.button_color = "orange"
        self.tomo_filepath_configured = False
        self.recon_finish = False
        self.boxes_logic()

    def FilePathOptn_drpdn_chg(self, a):
        restart(self, dtype="TOMO")
        self.reset_config()
        self.tomo_recon_type = a["owner"].value
        self.hs["SelSavReconDir btn"].disabled = False
        self.hs["SelSavReconDir btn"].style.button_color = "orange"
        if self.tomo_recon_type == "Trial Cent":
            layout = {"width": "15%", "height": "85%", "visibility": "hidden"}
            self.hs["ReadConfig_btn"].layout = layout
            layout = {"width": "7%", "visibility": "hidden"}
            self.hs["UseConfig chbx"].layout = layout
            layout = {"width": "19%", "visibility": "visible"}
            self.hs["CenWinLeft text"].layout = layout
            self.hs["CenWinWz text"].layout = layout

            self.hs["SelSavReconDir text"].value = (
                "Select top directory where data_center directory will be created..."
            )
            self.hs["UseConfig chbx"].value = False

            self.hs["CfgInpt&Rev acc"].set_title(1, "STEP 1: Config Data & Algorithm")
            self.hs["CfgInpt&Rev acc"].set_title(
                2, "XANES3D Tomo Recon with Automatic Centering"
            )
            self.hs["Flt&Rec acc"].set_title(0, "STEP 2: Config for Memory Management")
            self.hs["Flt&Rec acc"].set_title(1, "STEP 3: Config Preprocessing & Recon")
            self.tomo_use_read_config = False
        elif self.tomo_recon_type == "Vol Recon":
            self.hs["SelSavReconDir text"].value = (
                "Select top directory where recon subdirectories will be created..."
            )
            layout = {"width": "15%", "height": "85%", "visibility": "visible"}
            self.hs["ReadConfig_btn"].layout = layout
            layout = {"width": "7%", "visibility": "visible"}
            self.hs["UseConfig chbx"].layout = layout
            layout = {"width": "19%", "visibility": "hidden"}
            self.hs["CenWinLeft text"].layout = layout
            self.hs["CenWinWz text"].layout = layout

            self.hs["UseConfig chbx"].value = True

            self.hs["CfgInpt&Rev acc"].set_title(1, "STEP 1: Config Data & Algorithm")
            self.hs["CfgInpt&Rev acc"].set_title(
                2, "XANES3D Tomo Recon with Automatic Centering"
            )
            self.hs["Flt&Rec acc"].set_title(0, "STEP 2: Config for Memory Management")
            self.hs["Flt&Rec acc"].set_title(1, "STEP 3: Config Preprocessing & Recon")
            self.tomo_use_read_config = True
        elif self.tomo_recon_type == "Auto Cent":
            self.hs["XNS3DRecTpltFn btn"].style.button_color = "orange"
            self.hs["XNS3DInitPgr pgr"].layout.visibility = "hidden"
            self.hs["XNS3DInitRec chb"].layout.visibility = "hidden"
            self.hs["XNS3DRecROIX sldr"].layout.visibility = "hidden"
            self.hs["XNS3DRecROIY sldr"].layout.visibility = "hidden"
            self.hs["XNS3DRecROIZ sldr"].layout.visibility = "hidden"
            self.hs["XNS3DRecRegChnkSz sldr"].layout.visibility = "hidden"
            self.hs["XNS3DDefRefSli&ROI chb"].value = True
            self.hs["XNS3DRecROI txt"].layout.visibility = "hidden"
            self.hs["AutoCenFullRec chb"].description = "Rec All Sli"
            self.hs["AutoCenSliS txt"].layout.visibility = "visible"
            self.hs["AutoCenSliS txt"].layout.height = "70%"
            self.hs["AutoCenSliE txt"].layout.height = "70%"
            self.hs["AutoCenSliE txt"].description = "Sli End"
            self.hs["AutoCenSliE txt"].value = 0

            self.hs["XNS3DRecCenOpt drpn"].value = "Absolute"
            self.hs["XNS3DRecCenOpt drpn"].disabled = True

            self.hs["XNS3DRecZSrchDpth sldr"].description = "Down Sam R"
            self.hs["XNS3DRecZSrchDpth sldr"].tooltip = "Image downsampling factor"
            self.hs["XNS3DRecZSrchDpth sldr"].value = 1
            self.hs["XNS3DRecZSrchDpth sldr"].max = 10

            self.hs["XNS3DRecCenWzSrch sldr"].max = 160

            self.hs["CfgInpt&Rev acc"].set_title(1, "Config Data & Algorithm")
            self.hs["CfgInpt&Rev acc"].set_title(
                2, "STEP 1: XANES3D Tomo Recon with Automatic Centering"
            )
            self.hs["Flt&Rec acc"].set_title(0, "Config for Memory Management")
            self.hs["Flt&Rec acc"].set_title(1, "Config Preprocessing & Recon")
            self.recon_finish = False
        elif self.tomo_recon_type == "XANES3D Tomo":
            self.hs["SelSavReconDir text"].value = (
                "Select top directory where recon subdirectories will be created..."
            )
            self.hs["XNS3DRecTpltFn btn"].style.button_color = "orange"
            self.hs["XNS3DInitPgr pgr"].layout.visibility = "visible"
            self.hs["XNS3DInitRec chb"].layout.visibility = "visible"
            self.hs["XNS3DRecROIX sldr"].layout.visibility = "visible"
            self.hs["XNS3DRecROIY sldr"].layout.visibility = "visible"
            self.hs["XNS3DRecROIZ sldr"].layout.visibility = "visible"
            self.hs["XNS3DRecRegChnkSz sldr"].layout.visibility = "visible"
            # self.hs['XNS3DRefSli txt'].layout.visibility = 'visible'
            # self.hs['XNS3DRefSliROIX sldr'].layout.visibility = 'visible'
            # self.hs['XNS3DRefSliROIY sldr'].layout.visibility = 'visible'
            # self.hs['XNS3DRefSli sldr'].layout.visibility = 'visible'
            self.hs["XNS3DDefRefSli&ROI chb"].value = False
            self.hs["XNS3DRecROI txt"].layout.visibility = "visible"
            # self.hs['AutoCenFullRec chb'].layout.visibility = 'hidden'
            # self.hs['AutoCenSliS txt'].layout.visibility = 'hidden'
            # self.hs['AutoCenSliE txt'].layout.visibility = 'hidden'
            self.hs["AutoCenFullRec chb"].description = "Ang Corr"
            self.hs["AutoCenFullRec chb"].value = False
            self.hs["AutoCenSliS txt"].layout.visibility = "hidden"
            self.hs["AutoCenSliE txt"].description = "Ang Range"
            self.hs["AutoCenSliE txt"].value = 3

            self.hs["XNS3DRecCenOpt drpn"].value = "Absolute"
            # self.hs['XNS3DRecCenOpt drpn'].disabled = False

            self.hs["XNS3DRecZSrchDpth sldr"].description = "Z Depth"
            self.hs["XNS3DRecZSrchDpth sldr"].tooltip = (
                "Half number of slices for searching the matched slice to the reference slice"
            )
            self.hs["XNS3DRecZSrchDpth sldr"].max = 50
            self.hs["XNS3DRecZSrchDpth sldr"].value = 10

            self.hs["XNS3DRecCenWzSrch sldr"].max = 50

            self.hs["CfgInpt&Rev acc"].set_title(1, "Config Data & Algorithm")
            self.hs["CfgInpt&Rev acc"].set_title(
                2, "STEP 1: XANES3D Tomo Recon with Automatic Centering"
            )
            self.hs["Flt&Rec acc"].set_title(0, "Config for Memory Management")
            self.hs["Flt&Rec acc"].set_title(1, "Config Preprocessing & Recon")
            self.recon_finish = False
        self.tomo_filepath_configured = False
        self.recon_finish = False
        self.boxes_logic()

    def SelFilePathCfm_btn_clk(self, a):
        if self.tomo_recon_type == "Trial Cent":
            if self.tomo_raw_data_top_dir_set and self.tomo_recon_path_set:
                self.tomo_available_raw_idx = check_file_availability(
                    self.tomo_raw_data_top_dir,
                    scan_id=None,
                    signature=self.global_h.io_tomo_cfg["tomo_raw_fn_template"],
                    return_idx=True,
                )
                if len(self.tomo_available_raw_idx) == 0:
                    self.tomo_filepath_configured = False
                    return
                else:
                    self.hs["ScanId drpdn"].options = self.tomo_available_raw_idx
                    self.tomo_scan_id = self.tomo_available_raw_idx[0]
                    self.hs["ScanId drpdn"].value = self.tomo_scan_id
                    self.cal_set_srch_win()
                    if self.tomo_use_debug:
                        if self.tomo_debug_path_set:
                            self.tomo_data_center_path = str(
                                Path(self.tomo_recon_top_dir) / "data_center"
                            )
                            self.tomo_filepath_configured = True
                            self.set_alg_param_widgets()
                            self.set_flt_param_widgets()
                        else:
                            self.hs["SelFile&PathCfm text"].value = (
                                "You need to select the top directory to create debug dir..."
                            )
                            self.tomo_filepath_configured = False
                    else:
                        self.tomo_data_center_path = str(
                            Path(self.tomo_recon_top_dir) / "data_center"
                        )
                        self.tomo_filepath_configured = True
                        self.set_alg_param_widgets()
                        self.set_flt_param_widgets()
                    self.hs["CfgInpt&Rev acc"].selected_index = 1
                    self.hs["Flt&Rec acc"].selected_index = 0
            else:
                self.hs["SelFile&PathCfm text"].value = (
                    "You need to select the top raw dir and top dir where debug dir can be created..."
                )
                self.tomo_filepath_configured = False
            self.recon_finish = False
        elif self.tomo_recon_type == "Vol Recon":
            if self.tomo_raw_data_top_dir_set and self.tomo_recon_path_set:
                self.tomo_available_raw_idx = check_file_availability(
                    self.tomo_raw_data_top_dir,
                    scan_id=None,
                    signature=self.global_h.io_tomo_cfg["tomo_raw_fn_template"],
                    return_idx=True,
                )
                if len(self.tomo_available_raw_idx) == 0:
                    print(
                        'No data file available in {self.tomo_raw_data_top_dir} with filename pattern of {self.global_h.io_tomo_cfg["tomo_raw_fn_template"]}'
                    )
                    self.tomo_filepath_configured = False
                    self.hs["CfgInpt&Rev acc"].selected_index = None
                    self.hs["Flt&Rec acc"].selected_index = None
                    return
                else:
                    self.hs["ScanId drpdn"].options = self.tomo_available_raw_idx
                    self.hs["ScanId drpdn"].value = self.tomo_available_raw_idx[0]
                    self.tomo_filepath_configured = True
                    self.set_alg_param_widgets()
                    self.set_flt_param_widgets()
                    self.hs["CfgInpt&Rev acc"].selected_index = 1
                    self.hs["Flt&Rec acc"].selected_index = 0
            else:
                self.hs["SelFile&PathCfm text"].value = (
                    "You need to select the top raw dir and top dir where recon dir can be created..."
                )
                self.tomo_filepath_configured = False
                self.hs["CfgInpt&Rev acc"].selected_index = None
                self.hs["Flt&Rec acc"].selected_index = None
            self.recon_finish = False
        elif self.tomo_recon_type == "XANES3D Tomo":
            self.hs["XNS3DRecCenWzSrch sldr"].value = 15
            self.tomo_filepath_configured = True
            self.xns3d_init_rec_done = False
            self.hs["CfgInpt&Rev acc"].selected_index = 2
            self.hs["Flt&Rec acc"].selected_index = None
        elif self.tomo_recon_type == "Auto Cent":
            self.hs["XNS3DRecCenWzSrch sldr"].value = 15
            self.tomo_filepath_configured = True
            self.auto_cen_tplt_dict_rd = False
            self.hs["CfgInpt&Rev acc"].selected_index = 2
            self.hs["Flt&Rec acc"].selected_index = None
        self.boxes_logic()
        self.tomo_compound_logic()

    def ScanId_drpdn_chg(self, a):
        self.tomo_scan_id = a["owner"].value
        self.cal_set_srch_win()
        if self.data_info:
            self.set_rois()

            if self.tomo_recon_type == "Trial Cent":
                set_data_widget(
                    self,
                    "RoiSliEnd text",
                    20,
                    (int(self.data_info["img_dim"][1] / 2) + 10),
                    self.data_info["img_dim"][1] - 1,
                )
                set_data_widget(
                    self,
                    "RoiSliStart text",
                    0,
                    (int(self.data_info["img_dim"][1] / 2) - 10),
                    self.data_info["img_dim"][1] - 20,
                )
                set_data_widget(
                    self, "RoiColStart text", 0, 0, self.data_info["img_dim"][2] - 2
                )
                set_data_widget(
                    self,
                    "RoiColEnd text",
                    1,
                    self.data_info["img_dim"][2] - 1,
                    self.data_info["img_dim"][2] - 1,
                )
                set_data_widget(
                    self, "AutoRefColStart text", 0, 0, self.data_info["img_dim"][2] - 2
                )
                set_data_widget(
                    self,
                    "AutoRefColEnd text",
                    1,
                    self.data_info["img_dim"][2] - 1,
                    self.data_info["img_dim"][2] - 1,
                )
            elif self.tomo_recon_type == "Vol Recon":
                if self.hs["RoiSliEnd text"].value > (self.data_info["img_dim"][1] - 1):
                    set_data_widget(
                        self,
                        "RoiSliEnd text",
                        20,
                        self.data_info["img_dim"][1] - 1,
                        self.data_info["img_dim"][1] - 1,
                    )
                self.hs["RoiSliEnd text"].max = self.data_info["img_dim"][1] - 1
                if self.hs["RoiSliStart text"].value > (
                    self.data_info["img_dim"][1] - 2
                ):
                    set_data_widget(
                        self,
                        "RoiSliStart text",
                        0,
                        self.data_info["img_dim"][1] - 2,
                        self.data_info["img_dim"][1] - 2,
                    )
                self.hs["RoiSliStart text"].max = self.data_info["img_dim"][1] - 2
                if self.hs["RoiColStart text"].value > (
                    self.data_info["img_dim"][2] - 2
                ):
                    set_data_widget(
                        self,
                        "RoiColStart text",
                        0,
                        self.data_info["img_dim"][2] - 2,
                        self.data_info["img_dim"][2] - 2,
                    )
                self.hs["RoiColStart text"].max = self.data_info["img_dim"][2] - 2
                if self.hs["RoiColEnd text"].value > (self.data_info["img_dim"][2]):
                    set_data_widget(
                        self,
                        "RoiColEnd text",
                        1,
                        self.data_info["img_dim"][2],
                        self.data_info["img_dim"][2],
                    )
                self.hs["RoiColEnd text"].max = self.data_info["img_dim"][2] - 1

                if self.hs["AutoRefColStart text"].value > (
                    self.data_info["img_dim"][2] - 2
                ):
                    set_data_widget(
                        self,
                        "AutoRefColStart text",
                        0,
                        0,
                        self.data_info["img_dim"][2] - 2,
                    )
                self.hs["AutoRefColStart text"].max = self.data_info["img_dim"][2] - 2
                if self.hs["AutoRefColEnd text"].value > (self.data_info["img_dim"][2]):
                    set_data_widget(
                        self,
                        "AutoRefColEnd text",
                        1,
                        self.data_info["img_dim"][2],
                        self.data_info["img_dim"][2],
                    )
                self.hs["AutoRefColEnd text"].max = self.data_info["img_dim"][2] - 2
            set_data_widget(
                self, "RawProj sldr", 0, 0, self.data_info["img_dim"][0] - 1
            )
            self.hs["RawProjInMem chbx"].value = False
            self.raw_proj = np.ndarray(
                [self.data_info["img_dim"][1], self.data_info["img_dim"][2]],
                dtype=np.float32,
            )
            self.raw_proj_0 = np.ndarray(
                [self.data_info["img_dim"][1], self.data_info["img_dim"][2]],
                dtype=np.float32,
            )
            self.raw_proj_180 = np.ndarray(
                [self.data_info["img_dim"][1], self.data_info["img_dim"][2]],
                dtype=np.float32,
            )
            self.raw_is_in_mem = False
        else:
            print(
                "Cannot read metadata from the available files with the pre-defined Tomo Data Info Configuration."
            )
            self.tomo_filepath_configured = False
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def RotCen_text_chg(self, a):
        self.tomo_rot_cen = [a["owner"].value]
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def CenWinLeft_text_chg(self, a):
        if a["owner"].value > (
            self.data_info["img_dim"][2] - self.hs["CenWinWz text"].value - 1
        ):
            a["owner"].value = (
                self.data_info["img_dim"][2] - self.hs["CenWinWz text"].value - 1
            )
        self.tomo_cen_win_s = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def CenWinWz_text_chg(self, a):
        if a["owner"].value > (
            self.data_info["img_dim"][2] - self.hs["CenWinLeft text"].value - 1
        ):
            a["owner"].value = (
                self.data_info["img_dim"][2] - self.hs["CenWinLeft text"].value - 1
            )
        self.tomo_cen_win_w = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def ReadConfig_btn_clk(self, a):
        if self.tomo_use_read_config and (a.files[0] is not None):
            self.tomo_cen_list_file = a.files[0]
            tem = self.read_config()
            if tem is not None:
                key = sorted(list(tem.keys()))[0]
                recon_param_dict = tem[key]
                self.set_rec_params_from_rec_dict(recon_param_dict)
                self.set_widgets_from_rec_params(recon_param_dict)
                self.hs["RoiSliStart text"].value = 0
                self.hs["RoiSliEnd text"].value = self.data_info["img_dim"][1] - 1
                self.set_rec_params_from_widgets()
                self.set_rec_dict_from_rec_params()
            else:
                print("Fail to read the configuration file.")
                self.tomo_cen_list_file = None
                return
        else:
            self.tomo_cen_list_file = None
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def UseConfig_chbx_chg(self, a):
        self.tomo_use_read_config = a["owner"].value
        if not self.tomo_use_read_config:
            self.tomo_cen_list_file = None
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def RoiSliStart_text_chg(self, a):
        if self.tomo_recon_type == "Trial Cent":
            if (a["owner"].value + 20) > self.hs["RoiSliEnd text"].max:
                self.hs["RoiSliEnd text"].value = self.hs["RoiSliEnd text"].max
            else:
                self.hs["RoiSliEnd text"].value = a["owner"].value + 20
        else:
            if a["owner"].value >= self.hs["RoiSliEnd text"].value:
                a["owner"].value = self.hs["RoiSliEnd text"].value - 1
        self.tomo_sli_s = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def RoiSliEnd_text_chg(self, a):
        if a["owner"].value <= self.hs["RoiSliStart text"].value:
            a["owner"].value = self.hs["RoiSliStart text"].value + 1
        self.tomo_sli_e = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def RoiColStart_text_chg(self, a):
        if a["owner"].value > self.hs["RoiColEnd text"].value:
            a["owner"].value = self.hs["RoiColEnd text"].value
        self.tomo_col_s = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def RoiColEnd_text_chg(self, a):
        if a["owner"].value <= self.hs["RoiColStart text"].value:
            a["owner"].value = self.hs["RoiColStart text"].value + 1
        self.tomo_col_e = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def DnSampFac_text_chg(self, a):
        self.tomo_ds_fac = a["owner"].value
        if self.tomo_ds_fac == 1:
            self.tomo_use_downsample = False
        else:
            self.tomo_use_downsample = True
        self.set_rois()
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def UseAltFlat_chbx_chg(self, a):
        self.tomo_use_alt_flat = a["owner"].value
        if self.tomo_use_alt_flat:
            self.hs["UseFakeFlat chbx"].value = False
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AltFlatFile_btn_clk(self, a):
        if len(a.files[0]) != 0:
            self.tomo_alt_flat_file = a.files[0]
        else:
            self.tomo_alt_flat_file = None
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def UseAltDark_chbx_chg(self, a):
        self.tomo_use_alt_dark = a["owner"].value
        if self.tomo_use_alt_dark:
            self.hs["UseFakeDark chbx"].value = False
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AltDarkFile_btn_clk(self, a):
        if len(a.files[0]) != 0:
            self.tomo_alt_dark_file = a.files[0]
        else:
            self.tomo_alt_dark_file = None
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def UseFakeFlat_chbx_chg(self, a):
        self.tomo_use_fake_flat = a["owner"].value
        if self.tomo_use_fake_flat:
            self.hs["UseAltFlat chbx"].value = False
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FakeFlatVal_text_chg(self, a):
        self.tomo_fake_flat_val = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def UseFakeDark_chbx_chg(self, a):
        self.tomo_use_fake_dark = a["owner"].value
        if self.tomo_use_fake_dark:
            self.hs["UseAltDark chbx"].value = False
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FakeDarkVal_text_chg(self, a):
        self.tomo_fake_dark_val = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def BlurFlat_chbx_chg(self, a):
        self.tomo_use_blur_flat = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def BlurKern_text_chg(self, a):
        self.tomo_flat_blur_kernel = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def UseRmZinger_chbx_chg(self, a):
        self.tomo_use_rm_zinger = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def ZingerLevel_text_chg(self, a):
        self.tomo_zinger_val = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def UseMask_chbx_chg(self, a):
        self.tomo_use_mask = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def MaskRat_text_chg(self, a):
        self.tomo_mask_ratio = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AlgOptn_drpdn_chg(self, a):
        self.tomo_selected_alg = a["owner"].value
        self.set_alg_param_widgets()
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AlgPar00_drpdn_chg(self, a):
        self.tomo_alg_p01 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AlgPar01_drpdn_chg(self, a):
        self.tomo_alg_p02 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AlgPar02_drpdn_chg(self, a):
        self.tomo_alg_p03 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AlgPar03_text_chg(self, a):
        self.tomo_alg_p04 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AlgPar04_text_chg(self, a):
        self.tomo_alg_p05 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AlgPar05_text_chg(self, a):
        self.tomo_alg_p06 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AlgPar06_text_chg(self, a):
        self.tomo_alg_p07 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def IsWedge_chbx_chg(self, a):
        self.tomo_is_wedge = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def MissIdxStart_text_chg(self, a):
        self.tomo_wedge_missing_s = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def MissIdxEnd_text_chg(self, a):
        self.tomo_wedge_missing_e = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AutoDet_chbx_chg(self, a):
        self.tomo_use_wedge_ang_auto_det = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AutoThres_text_chg(self, a):
        self.tomo_wedge_ang_auto_det_thres = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AutoRefFn_btn_clk(self, a):
        if len(a.files[0]) != 0:
            self.tomo_wedge_ang_auto_det_ref_fn = a.files[0]
            self.set_rec_dict_from_rec_params()
            cfg = deepcopy(self.tomo_recon_param_dict)
            cfg["file_params"][
                "wedge_ang_auto_det_ref_fn"
            ] = self.tomo_wedge_ang_auto_det_ref_fn
            cfg["file_params"]["reader"] = self.reader
            cfg["file_params"]["info_reader"] = data_info(tomo_h5_info)
            cfg["recon_config"]["use_ds"] = (
                True if self.tomo_use_downsample == 1 else False
            )
            self.wedge_eva_data, _, _, _ = read_data(
                cfg,
                mean_axis=2,
            )
            print(self.wedge_eva_data.shape)
            self.hs["AutoRefSli sldr"].value = 0
            self.hs["AutoRefSli sldr"].max = self.wedge_eva_data.shape[1] - 1
        else:
            self.tomo_wedge_ang_auto_det_ref_fn = None
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def AutoRefSli_sldr_chg(self, a):
        plt.figure(0)
        plt.plot(self.wedge_eva_data[:, a["owner"].value])
        plt.plot(
            np.arange(self.wedge_eva_data.shape[0]),
            np.ones(self.wedge_eva_data.shape[0]) * self.tomo_wedge_ang_auto_det_thres,
        )
        plt.show()
        self.boxes_logic()
        self.tomo_compound_logic()

    def AutoRefColStart_text_chg(self, a):
        if a["owner"].value > self.hs["AutoRefColEnd text"].value:
            a["owner"].value = self.hs["AutoRefColEnd text"].value
        self.tomo_wedge_auto_ref_col_s = a["owner"].value

    def AutoRefColEnd_text_chg(self, a):
        if a["owner"].value <= self.hs["AutoRefColStart text"].value:
            a["owner"].value = self.hs["AutoRefColStart text"].value + 1
        self.tomo_wedge_auto_ref_col_e = a["owner"].value

    def RawProj_sldr_chg(self, a):
        idx = a["owner"].value
        if self.load_raw_in_mem:
            if not self.raw_is_in_mem:
                self.raw = (
                    (
                        self.reader(
                            self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                            dtype="data",
                            sli=[None, None, None],
                            cfg=self.global_h.io_tomo_cfg,
                        )
                        - self.reader(
                            self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                            dtype="dark",
                            sli=[None, None, None],
                            cfg=self.global_h.io_tomo_cfg,
                        ).mean(axis=0)
                    )
                    / (
                        self.reader(
                            self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                            dtype="flat",
                            sli=[None, None, None],
                            cfg=self.global_h.io_tomo_cfg,
                        ).mean(axis=0)
                        - self.reader(
                            self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                            dtype="dark",
                            sli=[None, None, None],
                            cfg=self.global_h.io_tomo_cfg,
                        ).mean(axis=0)
                    )
                ).astype(np.float32)
                self.raw[:] = np.where(self.raw < 0, 1, self.raw)[:]
                self.raw[np.isinf(self.raw)] = 1
                self.raw_is_in_mem = True

            data_state, viewer_state = fiji_viewer_state(
                self.global_h, self, viewer_name="tomo_raw_img_viewer"
            )
            if (not data_state) | (not viewer_state):
                fiji_viewer_on(self.global_h, self, viewer_name="tomo_raw_img_viewer")
                self.global_h.tomo_fiji_windows["tomo_raw_img_viewer"]["ip"].setImage(
                    self.global_h.ij.convert().convert(
                        self.global_h.ij.dataset().create(
                            self.global_h.ij.py.to_java(self.raw)
                        ),
                        self.global_h.ImagePlusClass,
                    )
                )
            self.global_h.tomo_fiji_windows["tomo_raw_img_viewer"]["ip"].setSlice(idx)
            self.global_h.ij.py.run_macro(
                """run("Enhance Contrast", "saturated=0.35")"""
            )
            self.global_h.tomo_fiji_windows["tomo_raw_img_viewer"]["ip"].setRoi(
                self.tomo_col_s,
                self.tomo_sli_s,
                self.tomo_col_e - self.tomo_col_s,
                self.tomo_sli_e - self.tomo_sli_s,
            )
        else:
            self.raw_proj[:] = (
                (
                    self.reader(
                        self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                        dtype="data",
                        sli=[[idx, idx + 1], None, None],
                        cfg=self.global_h.io_tomo_cfg,
                    )
                    - self.reader(
                        self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                        dtype="dark",
                        sli=[None, None, None],
                        cfg=self.global_h.io_tomo_cfg,
                    ).mean(axis=0)
                )
                / (
                    self.reader(
                        self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                        dtype="flat",
                        sli=[None, None, None],
                        cfg=self.global_h.io_tomo_cfg,
                    ).mean(axis=0)
                    - self.reader(
                        self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                        dtype="dark",
                        sli=[None, None, None],
                        cfg=self.global_h.io_tomo_cfg,
                    ).mean(axis=0)
                )
            ).astype(np.float32)
            self.raw_proj[:] = np.where(self.raw_proj < 0, 1, self.raw_proj)[:]
            self.raw_proj[np.isinf(self.raw_proj)] = 1

            data_state, viewer_state = fiji_viewer_state(
                self.global_h, self, viewer_name="tomo_raw_img_viewer"
            )
            if (not data_state) | (not viewer_state):
                fiji_viewer_on(self.global_h, self, viewer_name="tomo_raw_img_viewer")
            # self.global_h.tomo_fiji_windows["tomo_raw_img_viewer"][
            #     "ip"].setImage(self.global_h.ij.convert().convert(
            #         self.global_h.ij.dataset().create(
            #             self.global_h.ij.py.to_java(self.raw_proj)),
            #         self.global_h.ImagePlusClass,
            #     ))
            self.global_h.tomo_fiji_windows["tomo_raw_img_viewer"]["ip"].setImage(
                self.global_h.ij.convert().convert(
                    self.global_h.ij.dataset().create(
                        self.global_h.ij.py.to_java(
                            zoom(self.raw_proj, 1 / self.tomo_ds_fac)
                        )
                    ),
                    self.global_h.ImagePlusClass,
                )
            )
            self.global_h.ij.py.run_macro(
                """run("Enhance Contrast", "saturated=0.35")"""
            )
            self.global_h.tomo_fiji_windows["tomo_raw_img_viewer"]["ip"].setRoi(
                self.tomo_col_s,
                self.tomo_sli_s,
                self.tomo_col_e - self.tomo_col_s,
                self.tomo_sli_e - self.tomo_sli_s,
            )

    def RawProjInMem_chbx_chg(self, a):
        self.load_raw_in_mem = a["owner"].value
        fiji_viewer_off(self.global_h, self, viewer_name="tomo_raw_img_viewer")

    def RawProjViewerClose_btn_clk(self, a):
        data_state, viewer_state = fiji_viewer_state(
            self.global_h, self, viewer_name="tomo_raw_img_viewer"
        )
        if viewer_state is not None:
            self.set_rec_params_from_widgets()
            x = (
                self.global_h.tomo_fiji_windows["tomo_raw_img_viewer"]["ip"]
                .getRoi()
                .getFloatPolygon()
                .xpoints
            )
            y = (
                self.global_h.tomo_fiji_windows["tomo_raw_img_viewer"]["ip"]
                .getRoi()
                .getFloatPolygon()
                .ypoints
            )
            self.hs["AutoRefColStart text"].value = int(x[0]) - 1
            self.hs["AutoRefColEnd text"].value = int(x[2])
        fiji_viewer_off(self.global_h, self, viewer_name="tomo_raw_img_viewer")

    def CenOffsetRange_sldr_chg(self, a):
        self.raw_proj_0[:] = (
            (
                self.reader(
                    self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                    dtype="data",
                    sli=[[0, 1], None, None],
                    cfg=self.global_h.io_tomo_cfg,
                )
                - self.reader(
                    self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                    dtype="dark",
                    sli=[None, None, None],
                    cfg=self.global_h.io_tomo_cfg,
                ).mean(axis=0)
            )
            / (
                self.reader(
                    self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                    dtype="flat",
                    sli=[None, None, None],
                    cfg=self.global_h.io_tomo_cfg,
                ).mean(axis=0)
                - self.reader(
                    self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                    dtype="dark",
                    sli=[None, None, None],
                    cfg=self.global_h.io_tomo_cfg,
                ).mean(axis=0)
            )
        ).astype(np.float32)
        self.raw_proj_0[:] = np.where(self.raw_proj_0 < 0, 1, self.raw_proj_0)[:]
        self.raw_proj_0[np.isinf(self.raw_proj_0)] = 1
        self.raw_proj_180[:] = (
            (
                self.reader(
                    self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                    dtype="data",
                    sli=[[-2, -1], None, None],
                    cfg=self.global_h.io_tomo_cfg,
                )
                - self.reader(
                    self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                    dtype="dark",
                    sli=[None, None, None],
                    cfg=self.global_h.io_tomo_cfg,
                ).mean(axis=0)
            )
            / (
                self.reader(
                    self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                    dtype="flat",
                    sli=[None, None, None],
                    cfg=self.global_h.io_tomo_cfg,
                ).mean(axis=0)
                - self.reader(
                    self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                    dtype="dark",
                    sli=[None, None, None],
                    cfg=self.global_h.io_tomo_cfg,
                ).mean(axis=0)
            )
        ).astype(np.float32)
        self.raw_proj_180[:] = np.where(self.raw_proj_180 < 0, 1, self.raw_proj_180)[:]
        self.raw_proj_180[np.isinf(self.raw_proj_180)] = 1

        data_state, viewer_state = fiji_viewer_state(
            self.global_h, self, viewer_name="tomo_0&180_viewer"
        )
        if (not data_state) | (not viewer_state):
            fiji_viewer_on(self.global_h, self, viewer_name="tomo_0&180_viewer")
        self.global_h.tomo_fiji_windows["tomo_0&180_viewer"]["ip"].setImage(
            self.global_h.ij.convert().convert(
                self.global_h.ij.dataset().create(
                    self.global_h.ij.py.to_java(
                        np.roll(self.raw_proj_180[:, ::-1], a["owner"].value, axis=1)
                        - self.raw_proj_0
                    )
                ),
                self.global_h.ImagePlusClass,
            )
        )
        self.global_h.ij.py.run_macro("""run("Enhance Contrast", "saturated=0.35")""")

    def CenOffsetCfm_btn_clk(self, a):
        self.manual_cen = self.hs["CenOffsetRange sldr"].value / 2.0
        self.hs["RotCen text"].value = (
            self.manual_cen + self.data_info["img_dim"][2] / 2
        )
        self.hs["CenWinLeft text"].value = self.hs["RotCen text"].value - 10
        self.hs["CenWinWz text"].value = 80
        fiji_viewer_off(self.global_h, self, viewer_name="tomo_0&180_viewer")

    def CenViewerClose_btn_clk(self, a):
        fiji_viewer_off(self.global_h, self, viewer_name="tomo_0&180_viewer")

    def TrialCenPrev_sldr_chg(self, a):
        data_state, viewer_state = fiji_viewer_state(
            self.global_h, self, viewer_name="tomo_cen_review_viewer"
        )
        if (not data_state) | (not viewer_state):
            fiji_viewer_on(self.global_h, self, viewer_name="tomo_cen_review_viewer")
        self.global_h.tomo_fiji_windows["tomo_cen_review_viewer"]["ip"].setSlice(
            a["owner"].value
        )
        self.global_h.ij.py.run_macro("""run("Enhance Contrast", "saturated=0.35")""")

    def UseAsXNS3DTplt_chbx_chg(self, a):
        if a["owner"].value:
            b = "{date:%Y-%m-%d-%H-%M-%S}".format(date=datetime.now())
            self.tomo_xns3d_tplt_fn = str(
                Path(self.tomo_raw_data_top_dir)
                / "xanes3d_tomo_template_dict_{}.json".format(b),
            )
            self.tomo_use_as_xns3d_tplt = True
        else:
            self.tomo_xns3d_tplt_fn = None
            self.tomo_use_as_xns3d_tplt = False

    def TrialCenCfm_btn_clk(self, a):
        self.trial_cen = (
            self.hs["CenWinLeft text"].value
            + (
                self.global_h.tomo_fiji_windows["tomo_cen_review_viewer"]["ip"].getZ()
                - 1
            )
            * 0.5
        )
        self.hs["RotCen text"].value = self.trial_cen

        self.read_alg_param_widgets()
        self.set_rec_params_from_widgets()
        self.set_rec_dict_from_rec_params()

        if self.tomo_use_as_xns3d_tplt:
            fn = self.tomo_xns3d_tplt_fn
            tem = {}
        else:
            fn = self.tomo_trial_cen_dict_fn
            try:
                with open(self.tomo_trial_cen_dict_fn, "r") as f:
                    tem = json.load(f)
            except:
                tem = {}
        with open(fn, "w") as f:
            tem[str(self.tomo_recon_param_dict["data_params"]["scan_id"])] = (
                self.tomo_recon_param_dict
            )
            tem[str(self.tomo_recon_param_dict["data_params"]["scan_id"])][
                "file_params"
            ]["io_confg"]["customized_reader"]["user_tomo_reader"] = ""
            tem[str(self.tomo_recon_param_dict["data_params"]["scan_id"])][
                "file_params"
            ]["io_confg"]["structured_h5_reader"]["io_data_structure"][
                "eng_path"
            ] = self.global_h.io_xanes3D_cfg[
                "structured_h5_reader"
            ][
                "io_data_structure"
            ][
                "eng_path"
            ]
            tem[str(self.tomo_recon_param_dict["data_params"]["scan_id"])][
                "file_params"
            ]["reader"] = ""
            tem[str(self.tomo_recon_param_dict["data_params"]["scan_id"])][
                "file_params"
            ]["info_reader"] = ""
            self.tomo_recon_param_dict["recon_config"]["recon_type"] = "Vol Recon"
            json.dump(tem, f, indent=4, separators=(",", ": "))
        fiji_viewer_off(self.global_h, self, viewer_name="tomo_cen_review_viewer")

    def VolViewOpt_tgbtn_chg(self, a):
        pass

    def VolSliViewerClose_btn_clk(self, a):
        pass

    def XNS3DInitRec_chb_chg(self, a):
        self.tomo_xns3d_rec_ref = a["owner"].value

    def XNS3DRecTpltFn_btn_clk(self, a):
        if len(a.files) != 0:
            self.tomo_xns3d_tplt_fn = a.files[0]
            tem = self.read_config(self.tomo_xns3d_tplt_fn)
            if (tem is not None) and (len(tem.keys()) == 1):
                self.global_h.cwd = str(Path(self.tomo_xns3d_tplt_fn).resolve().parent)

                if self.tomo_recon_type == "XANES3D Tomo":
                    self.tomo_xns3d_tplt_dict = tem[list(tem.keys())[0]]

                    self.tomo_xns3d_tplt_dict["recon_config"][
                        "recon_type"
                    ] = "Vol Recon"
                    c = int(
                        (
                            self.tomo_xns3d_tplt_dict["data_params"]["sli_e"]
                            + self.tomo_xns3d_tplt_dict["data_params"]["sli_s"]
                        )
                        / 2
                    )
                    s = (
                        c
                        - 2 * self.tomo_xns3d_tplt_dict["data_params"]["margin"]
                        - self.tomo_xns3d_sli_srch_half_wz
                    )
                    e = (
                        c
                        + 2 * self.tomo_xns3d_tplt_dict["data_params"]["margin"]
                        + self.tomo_xns3d_sli_srch_half_wz
                    )

                    self.tomo_scan_id = self.tomo_xns3d_tplt_dict["data_params"][
                        "scan_id"
                    ]

                    self.tomo_xanes3d_raw_top_dir = self.tomo_xns3d_tplt_dict[
                        "file_params"
                    ]["raw_data_top_dir"]

                    self.tomo_raw_data_file_template = str(
                        Path(self.tomo_xanes3d_raw_top_dir).joinpath(
                            str(
                                Path(
                                    self.tomo_xns3d_tplt_dict["file_params"][
                                        "io_confg"
                                    ]["tomo_raw_fn_template"]
                                )
                            )
                        )
                    )

                    if self.tomo_xns3d_rec_ref:
                        di = get_raw_img_info(
                            self.tomo_raw_data_file_template.format(self.tomo_scan_id),
                            self.tomo_xns3d_tplt_dict["file_params"]["io_confg"],
                            scan_type="tomo",
                        )
                        if di:
                            self.tomo_xns3d_tplt_dict["data_params"]["sli_s"] = 0
                            self.tomo_xns3d_tplt_dict["data_params"]["sli_e"] = di[
                                "img_dim"
                            ][1]
                        else:
                            self.tomo_xns3d_tplt_dict["data_params"]["sli_s"] = s
                            self.tomo_xns3d_tplt_dict["data_params"]["sli_e"] = e
                    else:
                        self.tomo_xns3d_tplt_dict["data_params"]["sli_s"] = s
                        self.tomo_xns3d_tplt_dict["data_params"]["sli_e"] = e

                    self.tomo_recon_dir_tplt = str(
                        Path(
                            self.tomo_xns3d_tplt_dict["file_params"]["recon_top_dir"]
                        ).joinpath(
                            "recon_"
                            + str(
                                Path(
                                    self.tomo_xns3d_tplt_dict["file_params"][
                                        "io_confg"
                                    ]["tomo_raw_fn_template"]
                                ).stem
                            )
                        )
                    )

                    self.tomo_recon_fn_tplt = str(
                        Path(self.tomo_recon_dir_tplt).joinpath(
                            "recon_"
                            + str(
                                Path(
                                    self.tomo_xns3d_tplt_dict["file_params"][
                                        "io_confg"
                                    ]["tomo_raw_fn_template"]
                                ).stem
                            )
                            + "_{1}.tiff"
                        )
                    )

                    self.tomo_recon_dir = self.tomo_recon_dir_tplt.format(
                        self.tomo_xns3d_tplt_dict["data_params"]["scan_id"]
                    )
                    if Path(self.tomo_recon_dir).exists():
                        shutil.rmtree(self.tomo_recon_dir)

                    try:
                        fiji_viewer_off(
                            self.global_h, self, viewer_name="tomo_cen_review_viewer"
                        )
                        code = {}
                        ln = 0
                        code[ln] = (
                            f"from txm_sandbox.utils.tomo_recon_tools import run_engine"
                        )
                        ln += 1
                        code[ln] = (
                            f"from txm_sandbox.utils.io import data_reader, tomo_h5_reader, data_info, tomo_h5_info"
                        )
                        ln += 1
                        code[ln] = f"if __name__ == '__main__':"
                        ln += 1
                        code[ln] = f"    params = {self.tomo_xns3d_tplt_dict}"
                        ln += 1
                        code[ln] = (
                            f"    params['file_params']['reader'] = data_reader(tomo_h5_reader)"
                        )
                        ln += 1
                        code[ln] = (
                            f"    params['file_params']['info_reader'] = data_info(tomo_h5_info)"
                        )
                        ln += 1
                        code[ln] = f"    run_engine(**params)"
                        ln += 1
                        gen_external_py_script(
                            self.tomo_recon_external_command_name, code
                        )
                        sig = os.system(
                            f"ipython {self.tomo_recon_external_command_name}"
                        )
                        if sig == 0:
                            self.xns3d_init_rec_done = True
                            if self.tomo_xns3d_rec_ref:
                                self.tomo_xns3d_tplt_dict["data_params"]["sli_s"] = s
                                self.tomo_xns3d_tplt_dict["data_params"]["sli_e"] = e

                            b = glob.glob(
                                str(Path(self.tomo_recon_dir).joinpath("*.tiff"))
                            )
                            self.tomo_xns3d_ref_rec_ids = sorted(
                                [int(str(Path(fn).stem).split("_")[-1]) for fn in b]
                            )

                            set_data_widget(
                                self,
                                "XNS3DRefSli sldr",
                                self.tomo_xns3d_ref_rec_ids[0],
                                self.tomo_xns3d_ref_rec_ids[
                                    self.tomo_xns3d_ref_rec_ids.index(int((s + e) / 2))
                                ],
                                self.tomo_xns3d_ref_rec_ids[-1],
                            )
                            set_data_widget(
                                self,
                                "XNS3DRecROIZ sldr",
                                self.tomo_xns3d_ref_rec_ids[0],
                                [c - 3, c + 3],
                                self.tomo_xns3d_ref_rec_ids[-1],
                            )

                            _, viewer_state = fiji_viewer_state(
                                self.global_h, self, viewer_name="tomo_recon_viewer"
                            )
                            if viewer_state:
                                fiji_viewer_off(self.global_h, self, viewer_name="all")

                            fiji_viewer_on(
                                self.global_h, self, viewer_name="tomo_recon_viewer"
                            )
                            w = self.global_h.tomo_fiji_windows["tomo_recon_viewer"][
                                "ip"
                            ].getWidth()
                            h = self.global_h.tomo_fiji_windows["tomo_recon_viewer"][
                                "ip"
                            ].getHeight()

                            xs = int(w / 4)
                            xe = int(3 * w / 4)
                            set_data_widget(
                                self, "XNS3DRecROIX sldr", 0, [xs, xe], w - 1
                            )
                            set_data_widget(
                                self, "XNS3DRefSliROIX sldr", 0, (xs, xe), w - 1
                            )

                            ys = int(h / 4)
                            ye = int(3 * h / 4)
                            set_data_widget(
                                self, "XNS3DRecROIY sldr", 0, [ys, ye], h - 1
                            )
                            set_data_widget(
                                self, "XNS3DRefSliROIY sldr", 0, (ys, ye), h - 1
                            )

                            self.hs["XNS3DDefRefSli&ROI chb"].value = False
                            self.tomo_xns3d_use_deflt_reg_sli_roi = False

                            self.global_h.tomo_fiji_windows["tomo_recon_viewer"][
                                "ip"
                            ].setRoi(xs, ys, xe - xs, ye - ys)

                            print(
                                "XANES3D Tomo recon template file is read successfully."
                            )

                            self.tomo_available_raw_idx = check_file_availability(
                                self.tomo_xns3d_tplt_dict["file_params"][
                                    "raw_data_top_dir"
                                ],
                                scan_id=None,
                                signature=self.tomo_xns3d_tplt_dict["file_params"][
                                    "io_confg"
                                ]["tomo_raw_fn_template"],
                                return_idx=True,
                            )
                            if len(self.tomo_available_raw_idx) != 0:
                                self.hs["XNS3DRecScnIDs drpn"].options = (
                                    self.tomo_available_raw_idx
                                )
                                idx = self.tomo_available_raw_idx.index(
                                    str(
                                        self.tomo_xns3d_tplt_dict["data_params"][
                                            "scan_id"
                                        ]
                                    )
                                )
                                self.hs["XNS3DRecScnIDs drpn"].index = idx
                                self.hs["XNS3DRecScnIDe drpn"].options = (
                                    self.tomo_available_raw_idx[idx:]
                                )
                                self.hs["XNS3DRecScnIDe drpn"].value = self.hs[
                                    "XNS3DRecScnIDs drpn"
                                ].value
                        else:
                            self.xns3d_init_rec_done = False
                            print(
                                "The selected file is either not an XANES3D tomo recon template file or cannot be read."
                            )
                    except Exception as e:
                        self.xns3d_init_rec_done = False
                        print(e)
                        print(
                            "The selected file is either not an XANES3D tomo recon template file or cannot be read."
                        )
                elif self.tomo_recon_type == "Auto Cent":
                    self.auto_cen_tplt_dict = tem[list(tem.keys())[0]]

                    self.tomo_available_raw_idx = check_file_availability(
                        self.auto_cen_tplt_dict["file_params"]["raw_data_top_dir"],
                        scan_id=None,
                        signature=self.auto_cen_tplt_dict["file_params"]["io_confg"][
                            "tomo_raw_fn_template"
                        ],
                        return_idx=True,
                    )

                    if len(self.tomo_available_raw_idx) != 0:
                        self.hs["XNS3DRecScnIDs drpn"].options = (
                            self.tomo_available_raw_idx
                        )
                        idx = self.tomo_available_raw_idx.index(
                            str(self.auto_cen_tplt_dict["data_params"]["scan_id"])
                        )
                        self.hs["XNS3DRecScnIDs drpn"].index = idx
                        self.hs["XNS3DRecScnIDe drpn"].options = (
                            self.tomo_available_raw_idx[idx:]
                        )
                        self.hs["XNS3DRecScnIDe drpn"].value = self.hs[
                            "XNS3DRecScnIDs drpn"
                        ].value

                    self.hs["XNS3DRecZSrchDpth sldr"].value = self.auto_cen_tplt_dict[
                        "data_params"
                    ]["downsample"]

                    ds = self.auto_cen_tplt_dict["data_params"]["downsample"]
                    file_raw_fn, _ = get_file(self.auto_cen_tplt_dict)
                    di = get_raw_img_info(
                        file_raw_fn,
                        self.auto_cen_tplt_dict["file_params"]["io_confg"],
                        scan_type="tomo",
                    )

                    sli_sz = int(di["img_dim"][2] / ds)
                    sli_n = int(di["img_dim"][1] / ds)
                    set_data_widget(
                        self,
                        "XNS3DRefSliROIX sldr",
                        0,
                        (int(sli_sz / 4), int(3 * sli_sz / 4)),
                        sli_sz - 1,
                    )
                    set_data_widget(
                        self,
                        "XNS3DRefSliROIY sldr",
                        0,
                        (int(sli_sz / 4), int(3 * sli_sz / 4)),
                        sli_sz - 1,
                    )
                    set_data_widget(
                        self,
                        "XNS3DRefSli sldr",
                        0,
                        int(
                            self.auto_cen_tplt_dict["data_params"]["sli_s"]
                            + (
                                self.auto_cen_tplt_dict["data_params"]["sli_e"]
                                - self.auto_cen_tplt_dict["data_params"]["sli_s"]
                            )
                            / 2
                        ),
                        sli_n - 1,
                    )

                    set_data_widget(
                        self, "AutoCenSliS txt", 0, 0, int(di["img_dim"][1]) - 1
                    )
                    set_data_widget(
                        self,
                        "AutoCenSliE txt",
                        1,
                        int(di["img_dim"][1]) - 1,
                        int(di["img_dim"][1]) - 1,
                    )

                    self.tomo_recon_dir_tplt = str(
                        Path(
                            self.auto_cen_tplt_dict["file_params"]["recon_top_dir"]
                        ).joinpath(
                            "recon_"
                            + str(
                                Path(
                                    self.auto_cen_tplt_dict["file_params"]["io_confg"][
                                        "tomo_raw_fn_template"
                                    ]
                                ).stem
                            )
                        )
                    )

                    self.tomo_recon_dir = self.tomo_recon_dir_tplt.format(
                        self.auto_cen_tplt_dict["data_params"]["scan_id"]
                    )

                    if Path(self.tomo_recon_dir).exists() and any(
                        Path(self.tomo_recon_dir).iterdir()
                    ):
                        print("preview")
                        _, viewer_state = fiji_viewer_state(
                            self.global_h, self, viewer_name="tomo_recon_viewer"
                        )
                        if viewer_state:
                            fiji_viewer_off(self.global_h, self, viewer_name="all")

                        fiji_viewer_on(
                            self.global_h, self, viewer_name="tomo_recon_viewer"
                        )
                        self.hs["XNS3DDefRefSli&ROI chb"].disabled = False
                        self.hs["XNS3DDefRefSli&ROI chb"].value = False
                        self.hs["XNS3DDefRefSli&ROI chb"].value = True
                    else:
                        print("no preview")
                        self.hs["XNS3DDefRefSli&ROI chb"].value = True
                        self.hs["XNS3DDefRefSli&ROI chb"].disabled = True

                    self.auto_cen_cen_opt = self.hs["XNS3DRecCenOpt drpn"].value
                    self.auto_cen_scn_s = self.hs["XNS3DRecScnIDs drpn"].value
                    self.auto_cen_scn_e = self.hs["XNS3DRecScnIDe drpn"].value
                    self.auto_cen_reg_mode = self.hs["XNS3DRecRegMode drpn"].value
                    self.auto_cen_reg_knl_sz = self.hs["XNS3DRecRegKnlSz txt"].value
                    self.auto_cen_ds_fac = self.hs["XNS3DRecZSrchDpth sldr"].value
                    self.auto_cen_cen_srch_half_wz = self.hs[
                        "XNS3DRecCenWzSrch sldr"
                    ].value
                    self.auto_cen_rec = self.hs["XNS3DRegRec chb"].value
                    self.auto_cen_rec_all_sli = self.hs["AutoCenFullRec chb"].value
                    self.auto_cen_full_rec_sli_s = self.hs["AutoCenSliS txt"].value
                    self.auto_cen_full_rec_sli_e = self.hs["AutoCenSliE txt"].value
                    self.auto_cen_tplt_dict_rd = True
                    self.tomo_xns3d_use_deflt_reg_sli_roi = True
            else:
                if self.tomo_recon_type == "Auto Cent":
                    self.auto_cen_tplt_dict_rd = False
                    self.auto_cen_tplt_dict = {}
                    print(
                        "The selected file either cannot be read or includes reconstruction configuration for more than one scan so cannot be used as a template for reconstructions of other scans."
                    )
                elif self.tomo_recon_type == "XANES3D Tomo":
                    self.tomo_xns3d_tplt_dict = {}
                    self.tomo_xns3d_tplt_fn = None
                    self.xns3d_init_rec_done = False
                    print(
                        "The selected file is either not an XANES3D tomo recon template file or cannot be read."
                    )
        else:
            self.tomo_xns3d_tplt_dict = None
            self.tomo_xns3d_tplt_fn = None
            self.xns3d_init_rec_done = False
            self.auto_cen_tplt_dict_rd = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def XNS3DRecCenOpt_drpn_chg(self, a):
        if self.tomo_recon_type == "XANES3D Tomo":
            self.tomo_xns3d_cent_opt = a["owner"].value
            self.xns3d_init_rec_done = False
        elif self.tomo_recon_type == "Auto Cent":
            self.auto_cen_cen_opt = a["owner"].value
            self.auto_cen_tplt_dict_rd = False

    def XNS3DRecScnIDs_drpn_chg(self, a):
        tem = a["owner"].value
        idx = self.tomo_available_raw_idx.index(tem)
        ide = self.hs["XNS3DRecScnIDe drpn"].value
        self.hs["XNS3DRecScnIDe drpn"].options = self.tomo_available_raw_idx[idx:]
        if ide in self.tomo_available_raw_idx[idx:]:
            self.hs["XNS3DRecScnIDe drpn"].value = ide
        else:
            self.hs["XNS3DRecScnIDe drpn"].value = tem

        if self.tomo_recon_type == "XANES3D Tomo":
            self.tomo_xns3d_scn_s = tem
        elif self.tomo_recon_type == "Auto Cent":
            self.auto_cen_scn_s = tem
            tem_dict = deepcopy(self.auto_cen_tplt_dict)
            tem_dict["data_params"]["scan_id"] = self.auto_cen_scn_s
            file_raw_fn, _ = get_file(tem_dict)
            di = get_raw_img_info(
                file_raw_fn,
                tem_dict["file_params"]["io_confg"],
                scan_type="tomo",
            )
            set_data_widget(self, "AutoCenSliS txt", 0, 0, int(di["img_dim"][1]) - 1)
            set_data_widget(
                self,
                "AutoCenSliE txt",
                1,
                int(di["img_dim"][1]) - 1,
                int(di["img_dim"][1]) - 1,
            )
        self.boxes_logic()
        self.tomo_compound_logic()

    def XNS3DRecScnIDe_drpn_chg(self, a):
        if self.tomo_recon_type == "XANES3D Tomo":
            self.tomo_xns3d_scn_e = a["owner"].value
        elif self.tomo_recon_type == "Auto Cent":
            self.auto_cen_scn_e = a["owner"].value
            tem_dict = deepcopy(self.auto_cen_tplt_dict)
            tem_dict["data_params"]["scan_id"] = self.auto_cen_scn_e
            file_raw_fn, _ = get_file(tem_dict)
            di = get_raw_img_info(
                file_raw_fn,
                tem_dict["file_params"]["io_confg"],
                scan_type="tomo",
            )
            set_data_widget(self, "AutoCenSliS txt", 0, 0, int(di["img_dim"][1]) - 1)
            set_data_widget(
                self,
                "AutoCenSliE txt",
                1,
                int(di["img_dim"][1]) - 1,
                int(di["img_dim"][1]) - 1,
            )
        self.boxes_logic()
        self.tomo_compound_logic()

    def XNS3DDefRefSliROI_chb_chg(self, a):
        if self.xns3d_init_rec_done or self.auto_cen_tplt_dict_rd:
            if a["owner"].value:
                self.tomo_xns3d_use_deflt_reg_sli_roi = True
                im_dia = self.hs["XNS3DRefSliROIX sldr"].max
                roi_s = int(0.05 * im_dia)
                roi_r = int(0.9 * im_dia)
                self.hs["XNS3DRefSli sldr"].value = (
                    int(
                        (
                            self.hs["XNS3DRefSli sldr"].min
                            + self.hs["XNS3DRefSli sldr"].max
                        )
                        / 2
                    )
                    - 1
                )
                self.hs["XNS3DRefSli sldr"].value = int(
                    (self.hs["XNS3DRefSli sldr"].min + self.hs["XNS3DRefSli sldr"].max)
                    / 2
                )
                self.global_h.ij.py.run_macro(
                    f"""makeOval({roi_s}, {roi_s}, {roi_r}, {roi_r})"""
                )
            else:
                self.tomo_xns3d_use_deflt_reg_sli_roi = False
                roi_x = self.hs["XNS3DRefSliROIX sldr"].value
                roi_y = self.hs["XNS3DRefSliROIY sldr"].value
                self.hs["XNS3DRefSli sldr"].value = (
                    int(
                        (
                            self.hs["XNS3DRefSli sldr"].min
                            + self.hs["XNS3DRefSli sldr"].max
                        )
                        / 2
                    )
                    - 1
                )
                self.hs["XNS3DRefSli sldr"].value = int(
                    (self.hs["XNS3DRefSli sldr"].min + self.hs["XNS3DRefSli sldr"].max)
                    / 2
                )
                self.global_h.ij.py.run_macro(
                    f"""makeOval({roi_x[0]}, {roi_x[1]-roi_x[0]}, {roi_y[0]}, {roi_y[1]-roi_y[0]})"""
                )
        self.boxes_logic()
        self.tomo_compound_logic()

    def XNS3DRefSliROIX_sldr_chg(self, a):
        self.tomo_xns3d_ref_sli_roix = list(a["owner"].value)
        xs = self.tomo_xns3d_ref_sli_roix[0]
        xe = self.tomo_xns3d_ref_sli_roix[1]
        ys = self.hs["XNS3DRefSliROIY sldr"].value[0]
        ye = self.hs["XNS3DRefSliROIY sldr"].value[1]

        if self.xns3d_init_rec_done:
            data_state, viewer_state = fiji_viewer_state(
                self.global_h, self, viewer_name="tomo_recon_viewer"
            )
            if (not data_state) and (not viewer_state):
                fiji_viewer_on(self.global_h, self, viewer_name="tomo_recon_viewer")

            self.global_h.tomo_fiji_windows["tomo_recon_viewer"]["ip"].setRoi(
                xs, ys, xe - xs, ye - ys
            )

    def XNS3DRefSliROIY_sldr_chg(self, a):
        self.tomo_xns3d_ref_sli_roiy = list(a["owner"].value)
        ys = self.tomo_xns3d_ref_sli_roiy[0]
        ye = self.tomo_xns3d_ref_sli_roiy[1]
        xs = self.hs["XNS3DRefSliROIX sldr"].value[0]
        xe = self.hs["XNS3DRefSliROIX sldr"].value[1]

        if self.xns3d_init_rec_done:
            data_state, viewer_state = fiji_viewer_state(
                self.global_h, self, viewer_name="tomo_recon_viewer"
            )
            if (not data_state) and (not viewer_state):
                fiji_viewer_on(self.global_h, self, viewer_name="tomo_recon_viewer")

            self.global_h.tomo_fiji_windows["tomo_recon_viewer"]["ip"].setRoi(
                xs, ys, xe - xs, ye - ys
            )

    def XNS3DRefSli_sldr_chg(self, a):
        self.tomo_xns3d_ref_sli = a["owner"].value

        if self.xns3d_init_rec_done:
            data_state, viewer_state = fiji_viewer_state(
                self.global_h, self, viewer_name="tomo_recon_viewer"
            )
            if (not data_state) | (not viewer_state):
                fiji_viewer_on(self.global_h, self, viewer_name="tomo_recon_viewer")
            self.global_h.tomo_fiji_windows["tomo_recon_viewer"]["ip"].setSlice(
                a["owner"].value - a["owner"].min + 1
            )

    def XNS3DRecROIX_sldr_chg(self, a):
        self.tomo_xns3d_rec_roix = list(a["owner"].value)
        xs = self.tomo_xns3d_rec_roix[0]
        xe = self.tomo_xns3d_rec_roix[1]
        ys = self.hs["XNS3DRecROIY sldr"].value[0]
        ye = self.hs["XNS3DRecROIY sldr"].value[1]

        data_state, viewer_state = fiji_viewer_state(
            self.global_h, self, viewer_name="tomo_recon_viewer"
        )
        if (not data_state) and (not viewer_state):
            fiji_viewer_on(self.global_h, self, viewer_name="tomo_recon_viewer")

        self.global_h.tomo_fiji_windows["tomo_recon_viewer"]["ip"].setRoi(
            xs, ys, xe - xs, ye - ys
        )

    def XNS3DRecROIY_sldr_chg(self, a):
        self.tomo_xns3d_rec_roiy = list(a["owner"].value)
        ys = self.tomo_xns3d_rec_roiy[0]
        ye = self.tomo_xns3d_rec_roiy[1]
        xs = self.hs["XNS3DRecROIX sldr"].value[0]
        xe = self.hs["XNS3DRecROIX sldr"].value[1]

        data_state, viewer_state = fiji_viewer_state(
            self.global_h, self, viewer_name="tomo_recon_viewer"
        )
        if (not data_state) and (not viewer_state):
            fiji_viewer_on(self.global_h, self, viewer_name="tomo_recon_viewer")

        self.global_h.tomo_fiji_windows["tomo_recon_viewer"]["ip"].setRoi(
            xs, ys, xe - xs, ye - ys
        )

    def XNS3DRecROIZ_sldr_chg(self, a):
        if a["owner"].lower > self.tomo_xns3d_ref_sli:
            a["owner"].lower = self.tomo_xns3d_ref_sli
        if a["owner"].upper < self.tomo_xns3d_ref_sli:
            a["owner"].upper = self.tomo_xns3d_ref_sli

        self.tomo_xns3d_rec_roiz = list(a["owner"].value)
        a["owner"].mylower = a["owner"].lower
        a["owner"].myupper = a["owner"].upper

    def XNS3DRecROIZ_lwr_sldr_chg(self, a):
        if (
            a["owner"].value[0]
            > a["owner"].value[1] - self.tomo_xns3d_tplt_dict["data_params"]["margin"]
        ):
            a["owner"].lower = (
                a["owner"].value[1]
                - self.tomo_xns3d_tplt_dict["data_params"]["margin"]
                - 1
            )
        data_state, viewer_state = fiji_viewer_state(
            self.global_h, self, viewer_name="tomo_recon_viewer"
        )
        if (not data_state) | (not viewer_state):
            fiji_viewer_on(self.global_h, self, viewer_name="tomo_recon_viewer")
        self.global_h.tomo_fiji_windows["tomo_recon_viewer"]["ip"].setSlice(
            a["owner"].value[0] - a["owner"].min + 1
        )

    def XNS3DRecROIZ_upr_sldr_chg(self, a):
        if (
            a["owner"].value[1]
            < a["owner"].value[0] + self.tomo_xns3d_tplt_dict["data_params"]["margin"]
        ):
            a["owner"].upper = (
                a["owner"].value[0]
                + self.tomo_xns3d_tplt_dict["data_params"]["margin"]
                + 1
            )
        data_state, viewer_state = fiji_viewer_state(
            self.global_h, self, viewer_name="tomo_recon_viewer"
        )
        if (not data_state) | (not viewer_state):
            fiji_viewer_on(self.global_h, self, viewer_name="tomo_recon_viewer")
        self.global_h.tomo_fiji_windows["tomo_recon_viewer"]["ip"].setSlice(
            a["owner"].value[1] - a["owner"].min + 1
        )

    def XNS3DRecRegMode_drpn_chg(self, a):
        if self.tomo_recon_type == "XANES3D Tomo":
            self.tomo_xns3d_reg_mode = a["owner"].value
        elif self.tomo_recon_type == "Auto Cent":
            self.auto_cen_reg_mode = a["owner"].value

    def XNS3DRecRegChnkSz_sldr_chg(self, a):
        self.tomo_xns3d_reg_chnk_sz = a["owner"].value

    def XNS3DRecRegKnlSz_txt_chg(self, a):
        if self.tomo_recon_type == "XANES3D Tomo":
            self.tomo_xns3d_reg_knl_sz = a["owner"].value
        elif self.tomo_recon_type == "Auto Cent":
            self.auto_cen_reg_knl_sz = a["owner"].value

    def XNS3DRecZSrchDpth_sldr_chg(self, a):
        if self.tomo_recon_type == "XANES3D Tomo":
            self.tomo_xns3d_sli_srch_half_wz = a["owner"].value
        elif self.tomo_recon_type == "Auto Cent":
            self.auto_cen_ds_fac = a["owner"].value
            if self.auto_cen_ds_fac == 1:
                self.auto_cen_use_ds = False
            else:
                self.auto_cen_use_ds = True

    def XNS3DRecCenWzSrch_sldr_chg(self, a):
        if self.tomo_recon_type == "XANES3D Tomo":
            self.tomo_xns3d_cen_srch_half_wz = a["owner"].value
        elif self.tomo_recon_type == "Auto Cent":
            self.auto_cen_cen_srch_half_wz = a["owner"].value

    def AutoCenFullRec_chb_chg(self, a):
        if self.tomo_recon_type == "XANES3D Tomo":
            self.tomo_xns3d_corr_ang = a["owner"].value
        else:
            self.auto_cen_rec_all_sli = a["owner"].value
        self.boxes_logic()
        self.tomo_compound_logic()

    def AutoCenSliS_txt_chg(self, a):
        if a["owner"].value >= self.hs["AutoCenSliE txt"].value:
            a["owner"].value = self.hs["AutoCenSliE txt"].value - 1
        self.auto_cen_full_rec_sli_s = a["owner"].value

    def AutoCenSliE_txt_chg(self, a):
        if self.tomo_recon_type == "XANES3D Tomo":
            self.tomo_xns3d_corr_ang_rgn = a["owner"].value
        else:
            if a["owner"].value <= self.hs["AutoCenSliS txt"].value:
                a["owner"].value = self.hs["AutoCenSliS txt"].value + 1
            self.auto_cen_full_rec_sli_e = a["owner"].value

    def XNS3DRegRec_chb_chg(self, a):
        if self.tomo_recon_type == "XANES3D Tomo":
            self.tomo_xns3d_reg_rec = a["owner"].value
        elif self.tomo_recon_type == "Auto Cent":
            self.auto_cen_rec = a["owner"].value
            if not self.auto_cen_rec:
                self.hs["AutoCenFullRec chb"].value = False
            else:
                self.hs["AutoCenFullRec chb"].value = True
        self.boxes_logic()
        self.tomo_compound_logic()

    def XNS3DRecRun_btn_clk(self, a):
        if self.tomo_recon_type == "XANES3D Tomo":
            c = int(
                (
                    self.tomo_xns3d_tplt_dict["data_params"]["sli_e"]
                    + self.tomo_xns3d_tplt_dict["data_params"]["sli_s"]
                )
                / 2
            )
            s = (
                c
                - self.tomo_xns3d_tplt_dict["data_params"]["margin"]
                - self.tomo_xns3d_sli_srch_half_wz
            )
            e = (
                c
                + self.tomo_xns3d_tplt_dict["data_params"]["margin"]
                + self.tomo_xns3d_sli_srch_half_wz
            )
            self.tomo_xns3d_tplt_dict["data_params"]["sli_s"] = s
            self.tomo_xns3d_tplt_dict["data_params"]["sli_e"] = e

            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"] = {}
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "cen_opt"
            ] = self.tomo_xns3d_cent_opt
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "rec_dir_tplt"
            ] = self.tomo_recon_dir_tplt
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "rec_fn_tplt"
            ] = self.tomo_recon_fn_tplt
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"]["ref_scn_cen"] = (
                self.tomo_xns3d_tplt_dict["data_params"]["rot_cen"]
            )

            if self.tomo_xns3d_use_deflt_reg_sli_roi:
                self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                    "use_dflt_ref_reg_roi"
                ] = True
                self.tomo_xns3d_tplt_dict["aut_xns3d_pars"]["ref_cen_roi"] = None
            else:
                self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                    "use_dflt_ref_reg_roi"
                ] = False
                self.tomo_xns3d_tplt_dict["aut_xns3d_pars"]["ref_cen_roi"] = [
                    *self.tomo_xns3d_ref_sli_roiy,
                    *self.tomo_xns3d_ref_sli_roix,
                ]
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "ref_cen_sli"
            ] = self.tomo_xns3d_ref_sli

            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"]["rec_roi"] = [
                *self.tomo_xns3d_rec_roiy,
                *self.tomo_xns3d_rec_roix,
                *self.tomo_xns3d_rec_roiz,
            ]
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "ref_sli_srch_half_wz"
            ] = self.tomo_xns3d_sli_srch_half_wz
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "ref_cen_srch_half_wz"
            ] = self.tomo_xns3d_cen_srch_half_wz

            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"]["ref_scn_id"] = int(
                self.tomo_xns3d_tplt_dict["data_params"]["scan_id"]
            )

            ids = self.tomo_available_raw_idx.index(self.tomo_xns3d_scn_s)
            ide = self.tomo_available_raw_idx.index(self.tomo_xns3d_scn_e) + 1
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"]["scn_id_lst"] = [
                int(ii) for ii in self.tomo_available_raw_idx[ids:ide]
            ]
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "scn_id_s"
            ] = self.tomo_xns3d_scn_s
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "scn_id_e"
            ] = self.tomo_xns3d_scn_e

            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "reg_mode"
            ] = self.tomo_xns3d_reg_mode
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "reg_chnk_sz"
            ] = self.tomo_xns3d_reg_chnk_sz
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "mrtv_knl_sz"
            ] = self.tomo_xns3d_reg_knl_sz

            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "ang_corr"
            ] = self.tomo_xns3d_corr_ang
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "ang_corr_rgn"
            ] = self.tomo_xns3d_corr_ang_rgn

            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"][
                "reg&rec"
            ] = self.tomo_xns3d_reg_rec

            b = "{date:%Y-%m-%d-%H-%M-%S}".format(date=datetime.now())
            tem = f"3D_trial_reg_scan_id_{self.tomo_xns3d_scn_s}-{self.tomo_xns3d_scn_e}_{b}.h5"
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"]["xanes3d_sav_trl_reg_fn"] = str(
                Path(self.tomo_xanes3d_raw_top_dir).joinpath(tem)
            )
            self.tomo_xns3d_tplt_dict["aut_xns3d_pars"]["XANES_tmp_fn"] = str(
                Path(self.global_h.tmp_dir).joinpath("xanes3D_tmp.h5")
            )
            self.tomo_xns3d_tplt_dict["recon_config"]["recon_type"] = "XANES3D Tomo"

            print("ready")

            code = {}
            ln = 0
            code[ln] = (
                f"from txm_sandbox.utils.tomo_recon_tools import xanes3d_auto_tomo_rec"
            )
            ln += 1
            code[ln] = (
                f"from txm_sandbox.utils.io import data_reader, tomo_h5_reader, data_info, tomo_h5_info"
            )
            ln += 1
            code[ln] = f"if __name__ == '__main__':"
            ln += 1
            code[ln] = f"    params = {self.tomo_xns3d_tplt_dict}"
            ln += 1
            code[ln] = (
                f"    params['file_params']['reader'] = data_reader(tomo_h5_reader)"
            )
            ln += 1
            code[ln] = (
                f"    params['file_params']['info_reader'] = data_info(tomo_h5_info)"
            )
            ln += 1
            code[ln] = f"    xanes3d_auto_tomo_rec(params)"
            ln += 1
            self.xanes3d_tomo_autocent_cmd_nm = str(
                Path(self.global_h.script_dir).joinpath(
                    "xanes3d_tomo_autocent_cmd_nm.py"
                )
            )
            print("start")
            gen_external_py_script(self.xanes3d_tomo_autocent_cmd_nm, code)
            sig = os.system(f"ipython {self.xanes3d_tomo_autocent_cmd_nm}")
            print("end")
        elif self.tomo_recon_type == "Auto Cent":
            self.auto_cen_tplt_dict["data_params"][
                "sli_s"
            ] = self.auto_cen_full_rec_sli_s
            self.auto_cen_tplt_dict["data_params"][
                "sli_e"
            ] = self.auto_cen_full_rec_sli_e

            self.auto_cen_tplt_dict["aut_tomo_pars"] = {}
            self.auto_cen_tplt_dict["aut_tomo_pars"]["cen_opt"] = self.auto_cen_cen_opt
            ids = self.tomo_available_raw_idx.index(self.auto_cen_scn_s)
            ide = self.tomo_available_raw_idx.index(self.auto_cen_scn_e) + 1
            self.auto_cen_tplt_dict["aut_tomo_pars"]["scn_id_lst"] = [
                int(ii) for ii in self.tomo_available_raw_idx[ids:ide]
            ]
            self.auto_cen_tplt_dict["aut_tomo_pars"]["scn_id_s"] = self.auto_cen_scn_s
            self.auto_cen_tplt_dict["aut_tomo_pars"]["scn_id_e"] = self.auto_cen_scn_e

            if self.tomo_xns3d_use_deflt_reg_sli_roi:
                self.auto_cen_tplt_dict["aut_tomo_pars"]["use_dflt_ref_reg_roi"] = True
                self.auto_cen_tplt_dict["aut_tomo_pars"]["ref_cen_roi"] = None
            else:
                self.auto_cen_tplt_dict["aut_tomo_pars"]["use_dflt_ref_reg_roi"] = False
                self.auto_cen_tplt_dict["aut_tomo_pars"]["ref_cen_roi"] = [
                    *self.tomo_xns3d_ref_sli_roiy,
                    *self.tomo_xns3d_ref_sli_roix,
                ]
            self.auto_cen_tplt_dict["aut_tomo_pars"][
                "ref_cen_sli"
            ] = self.tomo_xns3d_ref_sli

            self.auto_cen_tplt_dict["aut_tomo_pars"][
                "reg_mode"
            ] = self.auto_cen_reg_mode
            self.auto_cen_tplt_dict["aut_tomo_pars"][
                "mrtv_knl_sz"
            ] = self.auto_cen_reg_knl_sz
            self.auto_cen_tplt_dict["aut_tomo_pars"]["ds_fac"] = self.auto_cen_ds_fac
            self.auto_cen_tplt_dict["aut_tomo_pars"][
                "cen_srch_half_wz"
            ] = self.auto_cen_cen_srch_half_wz
            self.auto_cen_tplt_dict["aut_tomo_pars"]["auto_rec"] = self.auto_cen_rec
            self.auto_cen_tplt_dict["aut_tomo_pars"][
                "rec_all_sli"
            ] = self.auto_cen_rec_all_sli
            # self.auto_cen_tplt_dict['aut_tomo_pars']['use_ref_sli'] = False

            b = "{date:%Y-%m-%d-%H-%M-%S}".format(date=datetime.now())
            tem = f"trial_cen_h5_{b}.h5"
            self.auto_cen_tplt_dict["aut_tomo_pars"]["trial_cen_h5_fn"] = str(
                Path(
                    self.auto_cen_tplt_dict["file_params"]["raw_data_top_dir"]
                ).joinpath(tem)
            )
            self.auto_cen_tplt_dict["recon_config"]["recon_type"] = "Auto Cent"

            print("ready")

            code = {}
            ln = 0
            code[ln] = (
                f"from txm_sandbox.utils.tomo_recon_tools import tomo_auto_center"
            )
            ln += 1
            code[ln] = (
                f"from txm_sandbox.utils.io import data_reader, tomo_h5_reader, data_info, tomo_h5_info"
            )
            ln += 1
            code[ln] = f"if __name__ == '__main__':"
            ln += 1
            code[ln] = f"    params = {self.auto_cen_tplt_dict}"
            ln += 1
            code[ln] = (
                f"    params['file_params']['reader'] = data_reader(tomo_h5_reader)"
            )
            ln += 1
            code[ln] = (
                f"    params['file_params']['info_reader'] = data_info(tomo_h5_info)"
            )
            ln += 1
            code[ln] = f"    cen_dict = tomo_auto_center(params)"
            ln += 1
            self.tomo_autocent_external_cmd = str(
                Path(self.global_h.script_dir).joinpath("tomo_autocent_external_cmd.py")
            )
            print("start")
            gen_external_py_script(self.tomo_autocent_external_cmd, code)
            sig = os.system(f"ipython {self.tomo_autocent_external_cmd}")
            print("end")

    def ReconChunkSz_text_chg(self, a):
        if a["owner"].value < self.hs["ReconMargSz text"].value * 2:
            a["owner"].value = self.hs["ReconMargSz text"].value * 2 + 1
        self.tomo_chunk_sz = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def ReconMargSz_text_chg(self, a):
        if 2 * a["owner"].value > self.hs["ReconChunkSz text"].value:
            a["owner"].value = int(self.hs["ReconChunkSz text"].value / 2) - 1
        self.tomo_margin = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftFltList_drpdn_chg(self, a):
        self.tomo_left_box_selected_flt = a["owner"].value
        self.set_flt_param_widgets()
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftAddTo_btn_clk(self, a):
        self.read_flt_param_widgets()
        if (
            len(self.hs["FilterConfigRightFlt mulsel"].options) == 1
            and self.hs["FilterConfigRightFlt mulsel"].options[0] == "None"
        ):
            self.hs["FilterConfigRightFlt mulsel"].options = [
                self.tomo_left_box_selected_flt,
            ]
            self.hs["FilterConfigRightFlt mulsel"].value = [
                self.tomo_left_box_selected_flt,
            ]
            self.tomo_right_filter_dict[0] = {
                "filter_name": self.tomo_left_box_selected_flt,
                "params": self.flt_param_dict,
            }
        else:
            a = list(self.hs["FilterConfigRightFlt mulsel"].options)
            a.append(self.tomo_left_box_selected_flt)
            self.hs["FilterConfigRightFlt mulsel"].options = a
            self.hs["FilterConfigRightFlt mulsel"].value = self.hs[
                "FilterConfigRightFlt mulsel"
            ].options
            idx = len(a) - 1
            self.tomo_right_filter_dict[idx] = {
                "filter_name": self.tomo_left_box_selected_flt,
                "params": self.flt_param_dict,
            }
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftPar00_text_chg(self, a):
        self.tomo_left_box_selected_flt_p00 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftPar01_text_chg(self, a):
        self.tomo_left_box_selected_flt_p01 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftPar02_text_chg(self, a):
        self.tomo_left_box_selected_flt_p02 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftPar03_text_chg(self, a):
        self.tomo_left_box_selected_flt_p03 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftPar04_text_chg(self, a):
        self.tomo_left_box_selected_flt_p04 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftPar05_text_chg(self, a):
        self.tomo_left_box_selected_flt_p05 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftPar06_text_chg(self, a):
        self.tomo_left_box_selected_flt_p06 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftPar07_text_chg(self, a):
        self.tomo_left_box_selected_flt_p07 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftPar08_text_chg(self, a):
        self.tomo_left_box_selected_flt_p08 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftPar09_text_chg(self, a):
        self.tomo_left_box_selected_flt_p09 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftPar10_text_chg(self, a):
        self.tomo_left_box_selected_flt_p10 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigLeftPar11_text_chg(self, a):
        self.tomo_left_box_selected_flt_p11 = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigRightFlt_mulsel_chg(self, a):
        self.tomo_right_list_filter = a["owner"].value
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigRightMvUp_btn_clk(self, a):
        if len(self.hs["FilterConfigRightFlt mulsel"].options) == 1:
            pass
        else:
            a = np.array(self.hs["FilterConfigRightFlt mulsel"].options)
            idxs = np.array(self.hs["FilterConfigRightFlt mulsel"].index)
            cnt = 0
            for b in idxs:
                if b == 0:
                    idxs[cnt] = b
                else:
                    a[b], a[b - 1] = a[b - 1], a[b]
                    (
                        self.tomo_right_filter_dict[b],
                        self.tomo_right_filter_dict[b - 1],
                    ) = (
                        self.tomo_right_filter_dict[b - 1],
                        self.tomo_right_filter_dict[b],
                    )
                    idxs[cnt] = b - 1
                cnt += 1
            self.hs["FilterConfigRightFlt mulsel"].options = list(a)
            self.hs["FilterConfigRightFlt mulsel"].value = list(a[idxs])
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigRightMvDn_btn_clk(self, a):
        if len(self.hs["FilterConfigRightFlt mulsel"].options) == 1:
            pass
        else:
            a = np.array(self.hs["FilterConfigRightFlt mulsel"].options)
            idxs = np.array(self.hs["FilterConfigRightFlt mulsel"].index)
            cnt = 0
            for b in idxs:
                if b == (len(a) - 1):
                    idxs[cnt] = b
                else:
                    a[b], a[b + 1] = a[b + 1], a[b]
                    (
                        self.tomo_right_filter_dict[b],
                        self.tomo_right_filter_dict[b + 1],
                    ) = (
                        self.tomo_right_filter_dict[b + 1],
                        self.tomo_right_filter_dict[b],
                    )
                    idxs[cnt] = b + 1
                cnt += 1
            self.hs["FilterConfigRightFlt mulsel"].options = list(a)
            self.hs["FilterConfigRightFlt mulsel"].value = list(a[idxs])
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigRightRm_btn_clk(self, a):
        a = list(self.hs["FilterConfigRightFlt mulsel"].options)
        idxs = list(self.hs["FilterConfigRightFlt mulsel"].index)
        d = {}
        for b in sorted(idxs, reverse=True):
            del a[b]
            del self.tomo_right_filter_dict[b]
        if len(a) > 0:
            self.hs["FilterConfigRightFlt mulsel"].options = list(a)
            self.hs["FilterConfigRightFlt mulsel"].value = [
                a[0],
            ]
            cnt = 0
            for ii in sorted(self.tomo_right_filter_dict.keys()):
                d[cnt] = self.tomo_right_filter_dict[ii]
                cnt += 1
            self.tomo_right_filter_dict = d
        else:
            self.hs["FilterConfigRightFlt mulsel"].options = [
                "None",
            ]
            self.hs["FilterConfigRightFlt mulsel"].value = [
                "None",
            ]
            self.tomo_right_filter_dict = {0: {}}
        self.tomo_data_configured = False
        self.recon_finish = False
        self.boxes_logic()
        self.tomo_compound_logic()

    def FilterConfigRightFnsh_btn_clk(self, a):
        pass

    def FilterConfigCfm_btn_clk(self, a):
        """
        enforce self.tomo_recon_param_dict has same structure as that in tomo_recon_tools
        """
        self.read_alg_param_widgets()
        self.set_rec_params_from_widgets()
        self.set_rec_dict_from_rec_params()

        self.tomo_data_configured = True
        if self.tomo_recon_type == "Trial Cent":
            info = ""
            for key, val in self.tomo_recon_param_dict.items():
                info = info + str(key) + ":" + str(val) + "\n\n"
            self.hs["ReconConfigSumm text"].value = info
        else:
            info = (
                "file_params:{} \n\n"
                + "recon_config:{} \n\n"
                + "flt_params:{} \n\n"
                + "data_params:{} \n\n"
                + "alg_params:{}"
            )
            self.hs["ReconConfigSumm text"].value = info
        self.boxes_logic()
        self.tomo_compound_logic()

    def Recon_btn_clk(self, a):
        if self.tomo_recon_type == "Trial Cent":
            fiji_viewer_off(self.global_h, self, viewer_name="tomo_cen_review_viewer")
            code = {}
            ln = 0
            code[ln] = f"from collections import OrderedDict"
            ln += 1
            code[ln] = f"from txm_sandbox.utils.tomo_recon_tools import run_engine"
            ln += 1
            code[ln] = (
                f"from txm_sandbox.utils.io import data_reader, tomo_h5_reader, data_info, tomo_h5_info"
            )
            ln += 1
            code[ln] = f"params = {self.tomo_recon_param_dict}"
            ln += 1
            code[ln] = f"if {self.global_h.io_tomo_cfg['use_h5_reader']}:"
            ln += 1
            code[ln] = (
                f"    params['file_params']['reader'] = data_reader(tomo_h5_reader)"
            )
            ln += 1
            code[ln] = (
                f"    params['file_params']['info_reader'] = data_info(tomo_h5_info)"
            )
            ln += 1
            code[ln] = f"else:"
            ln += 1
            code[ln] = (
                f"    from txm_sandbox.external.user_io import user_tomo_reader, user_tomo_info_reader"
            )
            ln += 1
            code[ln] = f"    self.reader = data_reader(user_tomo_reader)"
            ln += 1
            code[ln] = f"    self.info_reader = data_info(user_tomo_info_reader)"
            ln += 1
            code[ln] = f"run_engine(**params)"
            ln += 1
            gen_external_py_script(self.tomo_recon_external_command_name, code)
            sig = os.system(f"ipython {self.tomo_recon_external_command_name}")
            if sig == 0:
                boxes = ["TrialCenPrev box"]
                enable_disable_boxes(self.hs, boxes, disabled=False, level=-1)
                self.hs["TrialCenPrev sldr"].value = 0
                self.hs["TrialCenPrev sldr"].min = 0
                self.hs["TrialCenPrev sldr"].max = int(2 * self.tomo_cen_win_w - 1)
                data_state, viewer_state = fiji_viewer_state(
                    self.global_h, self, viewer_name="tomo_cen_review_viewer"
                )
                if (not data_state) | (not viewer_state):
                    fiji_viewer_on(
                        self.global_h, self, viewer_name="tomo_cen_review_viewer"
                    )
                self.global_h.ij.py.run_macro(
                    """run("Enhance Contrast", "saturated=0.35")"""
                )
            else:
                print("Something runs wrong during the reconstruction.")
        elif self.tomo_recon_type == "Vol Recon":
            if self.tomo_use_read_config and (self.tomo_cen_list_file is not None):
                tem = self.read_config()
                if tem is not None:
                    for key in tem.keys():
                        recon_param_dict = tem[key]
                        self.set_rec_params_from_rec_dict(recon_param_dict)
                        self.set_widgets_from_rec_params(recon_param_dict)
                        self.hs["UseConfig chbx"].value = True
                        self.hs["UseConfig chbx"].disabled = True
                        self.set_rec_params_from_widgets()
                        self.set_rec_dict_from_rec_params()

                        code = {}
                        ln = 0
                        code[ln] = f"from collections import OrderedDict"
                        ln += 1
                        code[ln] = (
                            f"from txm_sandbox.utils.tomo_recon_tools import run_engine"
                        )
                        ln += 1
                        code[ln] = (
                            f"from txm_sandbox.utils.io import data_reader, tomo_h5_reader, data_info, tomo_h5_info"
                        )
                        ln += 1
                        code[ln] = f"params = {self.tomo_recon_param_dict}"
                        ln += 1
                        code[ln] = (
                            f"params['file_params']['reader'] = data_reader(tomo_h5_reader)"
                        )
                        ln += 1
                        code[ln] = (
                            f"params['file_params']['info_reader'] = data_info(tomo_h5_info)"
                        )
                        ln += 1
                        code[ln] = f"run_engine(**params)"
                        ln += 1
                        gen_external_py_script(
                            self.tomo_recon_external_command_name, code
                        )
                        sig = os.system(
                            f"ipython {self.tomo_recon_external_command_name}"
                        )

                        if sig == 0:
                            print(f"Reconstruction of {key} is done.")
                        elif sig == -1:
                            print("Something runs wrong during the reconstruction.")
                            return
                else:
                    print("Fail to read the configuration file.")
                    return
            else:
                print('A configuration file is needed for "Vol Recon".')

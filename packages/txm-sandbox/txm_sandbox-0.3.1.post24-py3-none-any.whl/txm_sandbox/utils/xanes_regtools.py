#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 16:09:13 2019

@author: xiao
"""

import os, gc
import multiprocess as mp
from functools import partial
from pathlib import Path

from pystackreg import StackReg
import tifffile, h5py
from skimage.registration import phase_cross_correlation
from scipy.ndimage import fourier_shift
import numpy as np
from silx.io.dictdump import dicttoh5, h5todict

from .reg_algs import (
    mrtv_mpc_combo_reg,
    mrtv_reg_v4,
    mrtv_ls_combo_reg,
    shift_img,
    mrtv_rigid_reg,
    cal_rig_mrtv_ang,
)
from .io import tiff_vol_reader, cal_mem_lim
from .misc import parallelizing

N_CPU = os.cpu_count()
if N_CPU > 1:
    N_CPU -= 1

__all__ = ["regtools"]


class regtools:

    def __init__(self, reg_cfg):
        self.data_type = reg_cfg["data_type"].upper()
        self.reg_alg = reg_cfg["reg"]["alg"].upper()
        if self.reg_alg == "MPC":
            self.mpc_ovlp_r = reg_cfg["reg"]["alg_pars"]["MPC"]["ovlp_r"]
        else:
            self.mpc_ovlp_r = None
        if self.reg_alg == "SR":
            self.sr_mode = reg_cfg["reg"]["alg_pars"]["SR"]["mode"]
        else:
            self.sr_mode = None
        if self.reg_alg in ["MRTV", "RIG-MRTV"]:
            self.mrtv_lvl = reg_cfg["reg"]["alg_pars"][self.reg_alg]["lvl"]
            self.mrtv_wz = reg_cfg["reg"]["alg_pars"][self.reg_alg]["wz"]
            self.mrtv_sp_wz = reg_cfg["reg"]["alg_pars"][self.reg_alg]["sp_wz"]
            self.mrtv_smth_knl = reg_cfg["reg"]["alg_pars"][self.reg_alg]["smth_knl"]
        else:
            self.mrtv_lvl = None
            self.mrtv_wz = None
            self.mrtv_sp_wz = None
            self.mrtv_smth_knl = None

        self.ref_mode = reg_cfg["reg"]["ref_mode"]
        self.use_chunk = reg_cfg["reg"]["use_chnk"]
        self.chunk_sz = reg_cfg["reg"]["chnk_sz"]
        self.xanes3D_sli_srch_half_range = reg_cfg["reg"]["XANES3D_sli_srch_half_range"]
        self.xanes3D_fixed_ref_sli = reg_cfg["reg"]["XANES3D_fixed_ref_sli"]

        self.im_id_s = reg_cfg["data"]["im_id_s"]
        self.im_id_e = reg_cfg["data"]["im_id_e"]
        self.im_id_fxd = reg_cfg["data"]["im_id_fixed"]
        self.xanes3D_scn_ids = list(reg_cfg["data"]["XANES3D_scn_ids"])
        # self.im_roi = reg_cfg["reg"]["ref_reg_roi"]
        if self.data_type == "3D_XANES":
            self.im_roi = reg_cfg["reg"]["ref_reg_roi"]
        elif self.data_type == "2D_XANES":
            self.im_roi = reg_cfg["data"]["roi"]

        self.xanes3D_rec_path_tplt = reg_cfg["file"]["XANES3D_rec_path_tplt"]
        self.xanes3D_raw_h5_top_dir = reg_cfg["file"]["XANES3D_raw_h5_top_dir"]
        self.xanes2D_raw_fn = reg_cfg["file"]["XANES2D_raw_fn"]
        self.xanes_tmp_fn = reg_cfg["file"]["XANES_tmp_fn"]
        self.sav_fn = reg_cfg["file"]["sav_fn"]

        self.use_mask = reg_cfg["preproc"]["use_mask"]
        self.mask_thres = reg_cfg["preproc"]["mask_thres"]
        self.use_smth_im = reg_cfg["preproc"]["use_smth_im"]
        self.smth_im_sig = reg_cfg["preproc"]["smth_im_sig"]
        if self.reg_alg == "RIG-MRTV":
            if "ang_rgn" in reg_cfg["reg"]["alg_pars"]["RIG-MRTV"].keys():
                self.rig_mrtv_ang_rgn = reg_cfg["reg"]["alg_pars"]["RIG-MRTV"][
                    "ang_rgn"
                ]
            else:
                self.rig_mrtv_ang_rgn = 3
            if "pre_offset" in reg_cfg["reg"]["alg_pars"]["RIG-MRTV"].keys():
                self.rig_mrtv_pre_ofst = reg_cfg["reg"]["alg_pars"]["RIG-MRTV"][
                    "pre_offset"
                ]
            else:
                self.rig_mrtv_pre_ofst = None
            if "gm" in reg_cfg["reg"]["alg_pars"]["RIG-MRTV"].keys():
                self.rig_mrtv_gm = reg_cfg["reg"]["alg_pars"]["RIG-MRTV"]["gm"]
            else:
                self.rig_mrtv_gm = 1
            if "use_flt" in reg_cfg["reg"]["alg_pars"]["RIG-MRTV"].keys():
                self.rig_mrtv_use_flt = reg_cfg["reg"]["alg_pars"]["RIG-MRTV"][
                    "use_flt"
                ]
            else:
                self.rig_mrtv_use_flt = True
            if "use_norm" in reg_cfg["reg"]["alg_pars"]["RIG-MRTV"].keys():
                self.rig_mrtv_use_norm = reg_cfg["reg"]["alg_pars"]["RIG-MRTV"][
                    "use_norm"
                ]
            else:
                self.rig_mrtv_use_norm = False
        else:
            self.rig_mrtv_ang_rgn = None
            self.rig_mrtv_pre_ofst = None
            self.rig_mrtv_gm = None
            self.rig_mrtv_use_flt = None
            self.rig_mrtv_use_norm = None

        if self.reg_alg == "MRTV":
            if "pre_offset" in reg_cfg["reg"]["alg_pars"]["MRTV"].keys():
                self.mrtv_pre_ofst = reg_cfg["reg"]["alg_pars"]["MRTV"][
                    "pre_offset"
                ]
            else:
                self.mrtv_pre_ofst = None
            if "gm" in reg_cfg["reg"]["alg_pars"]["MRTV"].keys():
                self.mrtv_gm = reg_cfg["reg"]["alg_pars"]["MRTV"]["gm"]
            else:
                self.mrtv_gm = 1
            if "use_flt" in reg_cfg["reg"]["alg_pars"]["MRTV"].keys():
                self.mrtv_use_flt = reg_cfg["reg"]["alg_pars"]["MRTV"][
                    "use_flt"
                ]
            else:
                self.mrtv_use_flt = True
            if "use_norm" in reg_cfg["reg"]["alg_pars"]["MRTV"].keys():
                self.mrtv_use_norm = reg_cfg["reg"]["alg_pars"]["MRTV"][
                    "use_norm"
                ]
            else:
                self.mrtv_use_norm = False
        else:
            self.mrtv_pre_ofst = None
            self.mrtv_gm = None
            self.mrtv_use_flt = None
            self.mrtv_use_norm = None

        self.eng_list = reg_cfg["meta"]["eng_list"]

        if self.data_type == "3D_XANES":
            self.anchor_loc = self.xanes3D_scn_ids.index(self.im_id_fxd)
            self.data_pnts = len(self.xanes3D_scn_ids)
        else:
            self.anchor_loc = self.im_id_fxd - self.im_id_s
            self.data_pnts = self.im_id_e - self.im_id_s
        self.ref_im = None
        self.im = None
        self.msk = None
        self.eng_dict = {}
        self.im_ids_dict = {}

        self.chunks = {}
        self.num_chunk = None
        self.algn_pair_lst = []
        self.anchor_chunk_loc = None

        self.raw_data_info = {}

        self.error = None
        self.shift = None

        self.reg_cfged = False

    def read_xanes2D_tmp_file(self, mode="reg"):
        with h5py.File(self.xanes_tmp_fn, "r") as f:
            if mode == "reg":
                self.im = f["xanes2D_img"][
                    self.im_id_s : self.im_id_e,
                    self.im_roi[0] : self.im_roi[1],
                    self.im_roi[2] : self.im_roi[3],
                ]
            elif mode == "align":
                self.im = f["xanes2D_img"][self.im_id_s : self.im_id_e, :]
            self.msk = f["xanes2D_reg_mask"][:]
            if len(self.msk.shape) == 1:
                self.msk = None
            self.eng_list = f["analysis_eng_list"][:]

    def read_xanes3D_tmp_file(self):
        with h5py.File(self.xanes_tmp_fn, "r") as f:
            self.msk = f["xanes3D_reg_mask"][:]
            if len(self.msk.shape) == 1:
                self.msk = None
            self.eng_list = f["analysis_eng_list"][:]

    def compose_dicts(self):
        if self.data_type == "3D_XANES":
            self.anchor_id = self.xanes3D_scn_ids[self.anchor_loc]
            cnt = 0
            for ii in self.xanes3D_scn_ids:
                self.eng_dict[str(cnt).zfill(3)] = self.eng_list[cnt]
                self.im_ids_dict[str(cnt).zfill(3)] = ii
                cnt += 1
        elif self.data_type == "2D_XANES":
            cnt = 0
            for ii in range(self.im_id_s, self.im_id_e):
                self.eng_dict[str(cnt).zfill(3)] = self.eng_list[cnt]
                self.im_ids_dict[str(cnt).zfill(3)] = ii
                cnt += 1

    def reg_xanes2D_chunk(self, overlap_ratio=0.3):
        """
        chunk_sz: int, number of image in one chunk for alignment; each chunk
                  use the last image in that chunk as reference
        method:   str
                  'PC':   skimage.feature.register_translation
                  'MPC':  skimage.feature.masked_register_translation
                  'SR':   pystackreg.StackReg
        overlap_ratio: float, overlap_ratio for method == 'MPC'
        ref_mode: str, control how inter-chunk alignment is done
                  'average': the average of each chunk after intra-chunk
                             re-alignment is used for inter-chunk alignment
                  'single':  the last image in each chunk is used in
                             inter-chunk alignment

        imgs in self.im are registered relative to anchor img. self.im
        is the sub stack with self.im_id_s as its first image, and self.im_id_e
        as the last.
        """
        self.mpc_ovlp_r = overlap_ratio

        self.algn_pair_lst = regtools.alignment_scheduler(
            self.data_pnts,
            self.anchor_loc,
            self.chunk_sz,
            use_chnk=self.use_chunk,
            ref_mode=self.ref_mode,
        )

        print(f"The registration results will be saved in {self.sav_fn}")

        f = h5py.File(self.sav_fn, "a")
        if "trial_registration" not in f:
            g0 = f.create_group("trial_registration")
        else:
            del f["trial_registration"]
            g0 = f.create_group("trial_registration")

        g1 = g0.create_group("trial_reg_results")
        g2 = g0.create_group("trial_reg_parameters")

        g2.create_dataset("reg_method", data=str(self.reg_alg.upper()))
        g2.create_dataset("reg_ref_mode", data=str(self.ref_mode.upper()))
        g2.create_dataset("use_smooth_img", data=str(self.use_smth_im))
        g2.create_dataset("img_smooth_sigma", data=self.smth_im_sig)

        g2.create_dataset("alignment_pairs", data=self.algn_pair_lst)
        g2.create_dataset("scan_ids", data=self.xanes3D_scn_ids)
        g2.create_dataset("use_chunk", data=str(self.use_chunk))
        g2.create_dataset("chunk_sz", data=self.chunk_sz)
        g2.create_dataset("fixed_scan_id", data=self.anchor_loc)
        g2.create_dataset("slice_roi", data=self.im_roi)
        g2.create_dataset("eng_list", data=self.eng_list)
        dicttoh5(
            self.eng_dict,
            f,
            mode="a",
            update_mode="replace",
            h5path="/trial_registration/trial_reg_parameters/eng_dict",
        )
        dicttoh5(
            self.im_ids_dict,
            f,
            mode="a",
            update_mode="replace",
            h5path="/trial_registration/trial_reg_parameters/scan_ids_dict",
        )
        g2.create_dataset("use_mask", data=str(self.use_mask))
        g2.create_dataset("mask_thres", data=self.mask_thres)
        if self.use_mask:
            g2.create_dataset("mask", data=self.msk)

        g3 = g0.create_group("data_directory_info")
        for key, val in self.raw_data_info.items():
            g3.create_dataset(key, data=val)

        shifted_image = np.ndarray(self.im.shape)

        if self.im.ndim != 3:
            print(
                "XANES2D image stack is required. Please set XANES2D \
                      image stack first."
            )
        else:
            if self.reg_alg.upper() in {"PC", "MPC", "MRTV", "LS+MRTV", "MPC+MRTV"}:
                self.shift = np.ndarray([len(self.algn_pair_lst), 2])
            else:
                self.shift = np.ndarray([len(self.algn_pair_lst), 3, 3])

            self.error = np.ndarray(len(self.algn_pair_lst))
            if self.reg_alg.upper() == "PC":
                print('We are using "phase correlation" method for registration.')
                for ii in range(len(self.algn_pair_lst)):
                    self.shift[ii], self.error[ii], _ = phase_cross_correlation(
                        self.im[self.algn_pair_lst[ii][0]],
                        self.im[self.algn_pair_lst[ii][1]],
                        upsample_factor=100,
                    )
                    shifted_image[ii] = np.real(
                        np.fft.ifftn(
                            fourier_shift(
                                np.fft.fftn(self.im[self.algn_pair_lst[ii][1]]),
                                self.shift[ii],
                            )
                        )
                    )[:]
                    g11 = g1.create_group(str(ii).zfill(3))
                    g11.create_dataset("shift" + str(ii).zfill(3), data=self.shift[ii])
                    g11.create_dataset(
                        "trial_reg_img" + str(ii).zfill(3), data=shifted_image[ii]
                    )
                    g11.create_dataset(
                        "trial_reg_fixed" + str(ii).zfill(3),
                        data=self.im[self.algn_pair_lst[ii][0]],
                    )
            elif self.reg_alg.upper() == "MPC":
                print(
                    'We are using "masked phase correlation" method for registration.'
                )
                for ii in range(len(self.algn_pair_lst)):
                    self.shift[ii] = phase_cross_correlation(
                        self.im[self.algn_pair_lst[ii][0]],
                        self.im[self.algn_pair_lst[ii][1]],
                        reference_mask=self.msk,
                        overlap_ratio=self.mpc_ovlp_r,
                    )
                    shifted_image[ii] = np.real(
                        np.fft.ifftn(
                            fourier_shift(
                                np.fft.fftn(self.im[self.algn_pair_lst[ii][1]]),
                                self.shift[ii],
                            )
                        )
                    )[:]
                    g11 = g1.create_group(str(ii).zfill(3))
                    g11.create_dataset("shift" + str(ii).zfill(3), data=self.shift[ii])
                    g11.create_dataset(
                        "trial_reg_img" + str(ii).zfill(3), data=shifted_image[ii]
                    )
                    g11.create_dataset(
                        "trial_reg_fixed" + str(ii).zfill(3),
                        data=self.im[self.algn_pair_lst[ii][0]],
                    )
            elif self.reg_alg.upper() == "SR":
                print('We are using "stack registration" method for registration.')
                if self.sr_mode.upper() == "TRANSLATION":
                    sr = StackReg(StackReg.TRANSLATION)
                elif self.sr_mode.upper() == "RIGID_BODY":
                    sr = StackReg(StackReg.RIGID_BODY)
                elif self.sr_mode.upper() == "SCALED_ROTATION":
                    sr = StackReg(StackReg.SCALED_ROTATION)
                elif self.sr_mode.upper() == "AFFINE":
                    sr = StackReg(StackReg.AFFINE)
                elif self.sr_mode.upper() == "BILINEAR":
                    sr = StackReg(StackReg.BILINEAR)

                if self.msk is not None:
                    for ii in range(len(self.algn_pair_lst)):
                        self.shift[ii] = sr.register(
                            self.im[self.algn_pair_lst[ii][0]] * self.msk,
                            self.im[self.algn_pair_lst[ii][1]] * self.msk,
                        )
                        shifted_image[ii] = sr.transform(
                            self.im[self.algn_pair_lst[ii][1]], tmat=self.shift[ii]
                        )[:]
                        g11 = g1.create_group(str(ii).zfill(3))
                        g11.create_dataset(
                            "shift" + str(ii).zfill(3), data=self.shift[ii]
                        )
                        g11.create_dataset(
                            "trial_reg_img" + str(ii).zfill(3), data=shifted_image[ii]
                        )
                        g11.create_dataset(
                            "trial_reg_fixed" + str(ii).zfill(3),
                            data=self.im[self.algn_pair_lst[ii][0]],
                        )
                else:
                    for ii in range(len(self.algn_pair_lst)):
                        self.shift[ii] = sr.register(
                            self.im[self.algn_pair_lst[ii][0]],
                            self.im[self.algn_pair_lst[ii][1]],
                        )
                        shifted_image[ii] = sr.transform(
                            self.im[self.algn_pair_lst[ii][1]], tmat=self.shift[ii]
                        )[:]
                        g11 = g1.create_group(str(ii).zfill(3))
                        g11.create_dataset(
                            "shift" + str(ii).zfill(3), data=self.shift[ii]
                        )
                        g11.create_dataset(
                            "trial_reg_img" + str(ii).zfill(3), data=shifted_image[ii]
                        )
                        g11.create_dataset(
                            "trial_reg_fixed" + str(ii).zfill(3),
                            data=self.im[self.algn_pair_lst[ii][0]],
                        )
            elif self.reg_alg.upper() == "MRTV":
                print(
                    'We are using "multi-resolution total variation" method for registration.'
                )
                cfg = {}
                cfg["pxl_conf"] = {
                    "type": "area",
                    "levs": self.mrtv_lvl,
                    "wz": self.mrtv_wz,
                    "lsw": 10,
                }
                cfg["sub_conf"] = {
                    "use": True,
                    "type": "ana",
                    "sp_wz": self.mrtv_sp_wz,
                    "sp_us": 10,
                }
                cfg["smth_krnl"] = self.mrtv_smth_knl
                cfg["pre_offset"] = self.mrtv_pre_ofst
                cfg["gm"] = self.mrtv_gm
                cfg["use_flt"] = self.mrtv_use_flt
                cfg["use_norm"] = self.mrtv_use_norm
                with mp.Pool(N_CPU) as pool:
                    rlt = pool.map(
                        partial(mrtv_reg_v4, cfg),
                        [
                            [
                                self.im[self.algn_pair_lst[ii][0]],
                                self.im[self.algn_pair_lst[ii][1]],
                            ]
                            for ii in range(len(self.algn_pair_lst))
                        ],
                    )
                pool.close()
                pool.join()

                for ii in range(len(rlt)):
                    self.shift[ii] = rlt[ii][3]
                del rlt
                gc.collect()

                for ii in range(len(self.algn_pair_lst)):
                    shifted_image[ii] = np.real(
                        np.fft.ifftn(
                            fourier_shift(
                                np.fft.fftn(self.im[self.algn_pair_lst[ii][1]]),
                                self.shift[ii],
                            )
                        )
                    )[:]
                    g11 = g1.create_group(str(ii).zfill(3))
                    g11.create_dataset("shift" + str(ii).zfill(3), data=self.shift[ii])
                    g11.create_dataset(
                        "trial_reg_img" + str(ii).zfill(3), data=shifted_image[ii]
                    )
                    g11.create_dataset(
                        "trial_reg_fixed" + str(ii).zfill(3),
                        data=self.im[self.algn_pair_lst[ii][0]],
                    )
            elif self.reg_alg.upper() == "LS+MRTV":
                print(
                    'We are using "line search and multi-resolution total variation" method for registration.'
                )
                with mp.Pool(N_CPU) as pool:
                    rlt = pool.map(
                        partial(
                            mrtv_ls_combo_reg,
                            self.mrtv_wz,
                            2,
                            10,
                            self.mrtv_sp_wz,
                            self.mrtv_sp_wz,
                        ),
                        [
                            [
                                self.im[self.algn_pair_lst[ii][0]],
                                self.im[self.algn_pair_lst[ii][1]],
                            ]
                            for ii in range(len(self.algn_pair_lst))
                        ],
                    )
                pool.close()
                pool.join()

                for ii in range(len(rlt)):
                    self.shift[ii] = rlt[ii][3]
                del rlt
                gc.collect()

                for ii in range(len(self.algn_pair_lst)):
                    shifted_image[ii] = np.real(
                        np.fft.ifftn(
                            fourier_shift(
                                np.fft.fftn(self.im[self.algn_pair_lst[ii][1]]),
                                self.shift[ii],
                            )
                        )
                    )[:]
                    g11 = g1.create_group(str(ii).zfill(3))
                    g11.create_dataset("shift" + str(ii).zfill(3), data=self.shift[ii])
                    g11.create_dataset(
                        "trial_reg_img" + str(ii).zfill(3), data=shifted_image[ii]
                    )
                    g11.create_dataset(
                        "trial_reg_fixed" + str(ii).zfill(3),
                        data=self.im[self.algn_pair_lst[ii][0]],
                    )
            elif self.reg_alg.upper() == "MPC+MRTV":
                print(
                    'We are using combo of "masked phase correlation" and "multi-resolution total variation" method for registration.'
                )
                for ii in range(len(self.algn_pair_lst)):
                    _, _, _, self.shift[ii] = mrtv_mpc_combo_reg(
                        self.im[self.algn_pair_lst[ii][0]],
                        self.im[self.algn_pair_lst[ii][1]],
                        reference_mask=self.msk,
                        overlap_ratio=self.mpc_ovlp_r,
                        levs=self.mrtv_lvl,
                        wz=self.mrtv_wz,
                        sp_wz=self.mrtv_sp_wz,
                        sp_step=self.mrtv_sp_wz,
                    )
                    shifted_image[ii] = np.real(
                        np.fft.ifftn(
                            fourier_shift(
                                np.fft.fftn(self.im[self.algn_pair_lst[ii][1]]),
                                self.shift[ii],
                            )
                        )
                    )[:]
                    g11 = g1.create_group(str(ii).zfill(3))
                    g11.create_dataset("shift" + str(ii).zfill(3), data=self.shift[ii])
                    g11.create_dataset(
                        "trial_reg_img" + str(ii).zfill(3), data=shifted_image[ii]
                    )
                    g11.create_dataset(
                        "trial_reg_fixed" + str(ii).zfill(3),
                        data=self.im[self.algn_pair_lst[ii][0]],
                    )
        f.close()
        print("Done!")

    def apply_xanes2D_chunk_shift(self, shift_dict):
        """
        trialfn:    string; optional
                    trial registration filename
        savefn:     string; optional
                    filename to the file in which the shifted volume to be saved
        optional_shift_dict: dict; optional
                    user input shifts for specified scan ids. This is useful to
                    correct individual pairs that cannot be aligned with others
                    with the same registration method
        """
        with h5py.File(self.sav_fn, "a") as f:
            if "registration_results" not in f:
                g0 = f.create_group("registration_results")
            else:
                del f["registration_results"]
                g0 = f.create_group("registration_results")

            g1 = g0.create_group("reg_parameters")
            self.algn_pair_lst = f[
                "/trial_registration/trial_reg_parameters/alignment_pairs"
            ][:].tolist()
            g1.create_dataset("alignment_pairs", data=self.algn_pair_lst)
            self.xanes3D_scn_ids = f[
                "/trial_registration/trial_reg_parameters/scan_ids"
            ][:]
            g1.create_dataset("scan_ids", data=self.xanes3D_scn_ids)
            g1.create_dataset("slice_roi", data=self.im_roi)
            self.anchor_loc = f[
                "/trial_registration/trial_reg_parameters/fixed_scan_id"
            ][()]
            g1.create_dataset("fixed_scan_id", data=self.anchor_loc)
            self.chunk_sz = f["/trial_registration/trial_reg_parameters/chunk_sz"][()]
            g1.create_dataset("chunk_sz", data=self.chunk_sz)
            self.reg_alg = f["/trial_registration/trial_reg_parameters/reg_method"][
                ()
            ].decode("utf-8")
            g1.create_dataset("reg_method", data=self.reg_alg)
            self.ref_mode = f["/trial_registration/trial_reg_parameters/reg_ref_mode"][
                ()
            ].decode("utf-8")
            g1.create_dataset("reg_ref_mode", data=str(self.ref_mode.upper()))
            self.im_ids_dict = h5todict(
                self.sav_fn,
                path="/trial_registration/trial_reg_parameters/scan_ids_dict",
            )
            self.eng_dict = h5todict(
                self.sav_fn, path="/trial_registration/trial_reg_parameters/eng_dict"
            )
            dicttoh5(
                self.eng_dict,
                f,
                mode="a",
                update_mode="replace",
                h5path="/registration_results/reg_parameters/eng_dict",
            )
            dicttoh5(
                self.im_ids_dict,
                f,
                mode="a",
                update_mode="replace",
                h5path="/registration_results/reg_parameters/scan_ids_dict",
            )

            dicttoh5(
                shift_dict,
                f,
                mode="a",
                update_mode="replace",
                h5path="/registration_results/reg_parameters/user_determined_shift/relative_shift",
            )

            (self.abs_shift_dict, self.shift_chain_dict) = regtools.sort_absolute_shift(
                self.algn_pair_lst,
                shft_dict=shift_dict,
                data_type="2D_XANES",
                reg_alg=self.reg_alg,
            )

            shift = {}
            for key, item in self.abs_shift_dict.items():
                shift[key] = item["in_sli_shift"]

            dicttoh5(
                shift,
                f,
                mode="a",
                update_mode="replace",
                h5path="/registration_results/reg_parameters/user_determined_shift/absolute_shift",
            )

            g2 = g0.create_group("reg_results")
            g21 = g2.create_dataset(
                "registered_xanes2D",
                shape=(
                    len(self.im_ids_dict),
                    self.im_roi[1] - self.im_roi[0],
                    self.im_roi[3] - self.im_roi[2],
                ),
            )
            g22 = g2.create_dataset("eng_list", shape=(len(self.im_ids_dict),))

            cnt1 = 0
            for key in sorted(self.abs_shift_dict.keys()):
                shift = self.abs_shift_dict[key]["in_sli_shift"]
                regtools.translate_single_img(
                    shift, self.reg_alg, self.sr_mode, self.im[int(key)]
                )
                g21[cnt1] = self.im[int(key)][
                    self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                ]
                g22[cnt1] = self.eng_dict[key]
                cnt1 += 1

    def reg_xanes3D_chunk(self):
        """
        This function will align 3D XANES reconstructions chunk by chunk. Each
        3D dataset in each chunk will be aligned to the last dataset in the
        same chunk. Different chunks will be aligned in three different
        manners: 'single', 'neighbor', and 'average'.
        One way to do it is to make a checking order list according to the
        user input. The list is composed of a sequence of pairs. The alignment
        will be applied on each pair. A scheduler is therefore needed for this
        purpose.

        """
        fn = self.xanes3D_rec_path_tplt.format(
            self.xanes3D_scn_ids[self.anchor_loc],
            str(self.xanes3D_fixed_ref_sli).zfill(5),
        )
        self.ref_im = tifffile.imread(fn)[
            self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
        ]
        img = np.ndarray(
            [
                2 * self.xanes3D_sli_srch_half_range,
                self.im_roi[1] - self.im_roi[0],
                self.im_roi[3] - self.im_roi[2],
            ]
        )

        self.algn_pair_lst = regtools.alignment_scheduler(
            self.data_pnts,
            self.anchor_loc,
            self.chunk_sz,
            use_chnk=self.use_chunk,
            ref_mode=self.ref_mode,
        )

        sli_s = self.xanes3D_fixed_ref_sli - self.xanes3D_sli_srch_half_range
        sli_e = self.xanes3D_fixed_ref_sli + self.xanes3D_sli_srch_half_range

        f = h5py.File(self.sav_fn, "a")
        if "trial_registration" not in f:
            g0 = f.create_group("trial_registration")
        else:
            del f["trial_registration"]
            g0 = f.create_group("trial_registration")

        g1 = g0.create_group("trial_reg_results")

        g2 = g0.create_group("trial_reg_parameters")
        g2.create_dataset("reg_method", data=str(self.reg_alg.upper()))
        g2.create_dataset("reg_ref_mode", data=str(self.ref_mode.upper()))
        g2.create_dataset("use_smooth_img", data=str(self.use_smth_im))
        g2.create_dataset("img_smooth_sigma", data=self.smth_im_sig)

        g2.create_dataset("alignment_pairs", data=self.algn_pair_lst)
        g2.create_dataset("scan_ids", data=self.xanes3D_scn_ids)
        g2.create_dataset("use_chunk", data=str(self.use_chunk))
        g2.create_dataset("chunk_sz", data=self.chunk_sz)
        g2.create_dataset("fixed_scan_id", data=self.anchor_id)
        g2.create_dataset("slice_roi", data=self.im_roi)
        g2.create_dataset("fixed_slice", data=self.xanes3D_fixed_ref_sli)
        g2.create_dataset(
            "sli_search_half_range", data=self.xanes3D_sli_srch_half_range
        )
        g2.create_dataset("eng_list", data=self.eng_list)
        g2.create_dataset("use_mask", data=self.use_mask)
        if self.use_mask:
            g2.create_dataset("mask", data=self.msk)
            g2.create_dataset("mask_thres", data=self.mask_thres)
        else:
            g2.create_dataset("mask", data=str(self.msk))
            g2.create_dataset("mask_thres", data=self.mask_thres)

        dicttoh5(
            self.eng_dict,
            f,
            mode="a",
            update_mode="replace",
            h5path="/trial_registration/trial_reg_parameters/eng_dict",
        )
        dicttoh5(
            self.im_ids_dict,
            f,
            mode="a",
            update_mode="replace",
            h5path="/trial_registration/trial_reg_parameters/scan_ids_dict",
        )

        g3 = g0.create_group("data_directory_info")
        tem = ""
        for ii in self.xanes3D_rec_path_tplt.split("/")[:-2]:
            tem = os.path.join(tem, ii)
        g3.create_dataset("raw_h5_top_dir", data=self.xanes3D_raw_h5_top_dir)
        g3.create_dataset("recon_top_dir", data=tem)
        g3.create_dataset("recon_path_template", data=self.xanes3D_rec_path_tplt)
        for key, val in self.raw_data_info.items():
            try:
                g3.create_dataset(key, data=val)
            except:
                pass

        if self.reg_alg.upper() in {
            "PC",
            "MPC",
            "MRTV",
            "RIG-MRTV",
            "LS+MRTV",
            "MPC+MRTV",
        }:
            self.shift = np.ndarray(
                [len(self.algn_pair_lst), 2 * self.xanes3D_sli_srch_half_range, 2]
            )
        else:
            self.shift = np.ndarray(
                [len(self.algn_pair_lst), 2 * self.xanes3D_sli_srch_half_range, 3, 3]
            )
        self.error = np.ndarray(
            [len(self.algn_pair_lst), 2 * self.xanes3D_sli_srch_half_range]
        )

        if self.reg_alg.upper() == "PC":
            print('We are using "phase correlation" method for registration.')
            for ii in range(len(self.algn_pair_lst)):
                fn = self.xanes3D_rec_path_tplt.format(
                    self.im_ids_dict[str(self.algn_pair_lst[ii][0]).zfill(3)],
                    str(self.xanes3D_fixed_ref_sli).zfill(5),
                )
                self.ref_im[:] = tifffile.imread(fn)[
                    self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                ]
                jj_id = 0
                for jj in range(sli_s, sli_e):
                    fn = self.xanes3D_rec_path_tplt.format(
                        self.im_ids_dict[str(self.algn_pair_lst[ii][1]).zfill(3)],
                        str(jj).zfill(5),
                    )
                    img[jj_id] = tifffile.imread(fn)[
                        self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                    ]

                    self.shift[ii, jj_id], self.error[ii, jj_id], _ = (
                        phase_cross_correlation(
                            self.ref_im, img[jj_id], upsample_factor=100
                        )
                    )
                    img[jj_id] = np.real(
                        np.fft.ifftn(
                            fourier_shift(
                                np.fft.fftn(img[jj_id]), self.shift[ii, jj_id]
                            )
                        )
                    )[:]

                    jj_id += 1
                g11 = g1.create_group(str(ii).zfill(3))
                g11.create_dataset("shift" + str(ii).zfill(3), data=self.shift[ii])
                g11.create_dataset("error" + str(ii).zfill(3), data=self.error[ii])
                g11.create_dataset("trial_reg_img" + str(ii).zfill(3), data=img)
                g11.create_dataset(
                    "trial_fixed_img" + str(ii).zfill(3), data=self.ref_im
                )
        elif self.reg_alg.upper() == "MPC":
            print('We are using "masked phase correlation" method for registration.')
            for ii in range(len(self.algn_pair_lst)):
                fn = self.xanes3D_rec_path_tplt.format(
                    self.im_ids_dict[str(self.algn_pair_lst[ii][0]).zfill(3)],
                    str(self.xanes3D_fixed_ref_sli).zfill(5),
                )
                self.ref_im[:] = tifffile.imread(fn)[
                    self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                ]
                jj_id = 0
                for jj in range(sli_s, sli_e):
                    fn = self.xanes3D_rec_path_tplt.format(
                        self.im_ids_dict[str(self.algn_pair_lst[ii][1]).zfill(3)],
                        str(jj).zfill(5),
                    )
                    img[jj_id] = tifffile.imread(fn)[
                        self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                    ]

                    self.shift[ii, jj_id] = phase_cross_correlation(
                        self.ref_im,
                        img[jj_id],
                        reference_mask=self.msk,
                        overlap_ratio=self.mpc_ovlp_r,
                    )
                    img[jj_id] = np.real(
                        np.fft.ifftn(
                            fourier_shift(
                                np.fft.fftn(img[jj_id]), self.shift[ii, jj_id]
                            )
                        )
                    )[:]

                    jj_id += 1
                g11 = g1.create_group(str(ii).zfill(3))
                g11.create_dataset("shift" + str(ii).zfill(3), data=self.shift[ii])
                g11.create_dataset("trial_reg_img" + str(ii).zfill(3), data=img)
                g11.create_dataset(
                    "trial_fixed_img" + str(ii).zfill(3), data=self.ref_im
                )
        elif self.reg_alg.upper() == "SR":
            print('We are using "stack registration" method for registration.')
            if self.sr_mode.upper() == "TRANSLATION":
                sr = StackReg(StackReg.TRANSLATION)
            elif self.sr_mode.upper() == "RIGID_BODY":
                sr = StackReg(StackReg.RIGID_BODY)
            elif self.sr_mode.upper() == "SCALED_ROTATION":
                sr = StackReg(StackReg.SCALED_ROTATION)
            elif self.sr_mode.upper() == "AFFINE":
                sr = StackReg(StackReg.AFFINE)
            elif self.sr_mode.upper() == "BILINEAR":
                sr = StackReg(StackReg.BILINEAR)

            if self.msk is not None:
                for ii in range(len(self.algn_pair_lst)):
                    fn = self.xanes3D_rec_path_tplt.format(
                        self.im_ids_dict[str(self.algn_pair_lst[ii][0]).zfill(3)],
                        str(self.xanes3D_fixed_ref_sli).zfill(5),
                    )
                    self.ref_im[:] = tifffile.imread(fn)[
                        self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                    ]
                    jj_id = 0
                    for jj in range(sli_s, sli_e):
                        fn = self.xanes3D_rec_path_tplt.format(
                            self.im_ids_dict[str(self.algn_pair_lst[ii][1]).zfill(3)],
                            str(jj).zfill(5),
                        )
                        img[jj_id] = tifffile.imread(fn)[
                            self.im_roi[0] : self.im_roi[1],
                            self.im_roi[2] : self.im_roi[3],
                        ]

                        self.shift[ii, jj_id] = sr.register(
                            self.ref_im * self.msk, img[jj_id] * self.msk
                        )
                        img[jj_id] = sr.transform(img[jj_id], self.shift[ii, jj_id])[:]

                        jj_id += 1
                    g11 = g1.create_group(str(ii).zfill(3))
                    g11.create_dataset(
                        "shift" + str(ii).zfill(3),
                        data=self.shift[ii, :].astype(np.float32),
                    )
                    g11.create_dataset("trial_reg_img" + str(ii).zfill(3), data=img)
                    g11.create_dataset(
                        "trial_fixed_img" + str(ii).zfill(3), data=self.ref_im
                    )
            else:
                for ii in range(len(self.algn_pair_lst)):
                    fn = self.xanes3D_rec_path_tplt.format(
                        self.im_ids_dict[str(self.algn_pair_lst[ii][0]).zfill(3)],
                        str(self.xanes3D_fixed_ref_sli).zfill(5),
                    )
                    self.ref_im[:] = tifffile.imread(fn)[
                        self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                    ]
                    jj_id = 0
                    for jj in range(sli_s, sli_e):
                        fn = self.xanes3D_rec_path_tplt.format(
                            self.im_ids_dict[str(self.algn_pair_lst[ii][1]).zfill(3)],
                            str(jj).zfill(5),
                        )
                        img[jj_id] = tifffile.imread(fn)[
                            self.im_roi[0] : self.im_roi[1],
                            self.im_roi[2] : self.im_roi[3],
                        ]

                        self.shift[ii, jj_id] = sr.register(self.ref_im, img[jj_id])
                        img[jj_id] = sr.transform(img[jj_id], self.shift[ii, jj_id])[:]

                        jj_id += 1
                    g11 = g1.create_group(str(ii).zfill(3))
                    g11.create_dataset(
                        "shift" + str(ii).zfill(3),
                        data=self.shift[ii, :].astype(np.float32),
                    )
                    g11.create_dataset("trial_reg_img" + str(ii).zfill(3), data=img)
                    g11.create_dataset(
                        "trial_fixed_img" + str(ii).zfill(3), data=self.ref_im
                    )
        elif self.reg_alg.upper() == "MRTV":
            print(
                'We are using "multi-resolution total variation" method for registration.'
            )
            sli_s = self.xanes3D_fixed_ref_sli - self.xanes3D_sli_srch_half_range
            sli_e = self.xanes3D_fixed_ref_sli + self.xanes3D_sli_srch_half_range

            cfg = {}
            cfg["pxl_conf"] = dict(
                type="area", levs=self.mrtv_lvl, wz=self.mrtv_wz, lsw=10
            )
            cfg["sub_conf"] = dict(
                use=True, type="ana", sp_wz=self.mrtv_sp_wz, sp_us=10
            )
            cfg["smth_krnl"] = self.mrtv_smth_knl
            cfg["pre_offset"] = self.mrtv_pre_ofst
            cfg["gm"] = self.mrtv_gm
            cfg["use_flt"] = self.mrtv_use_flt  
            cfg["use_norm"] = self.mrtv_use_norm
            for ii in range(len(self.algn_pair_lst)):
                fn = self.xanes3D_rec_path_tplt.format(
                    self.im_ids_dict[str(self.algn_pair_lst[ii][0]).zfill(3)],
                    str(self.xanes3D_fixed_ref_sli).zfill(5),
                )
                self.ref_im[:] = tifffile.imread(fn)[
                    self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                ]

                jj_id = 0
                for jj in range(sli_s, sli_e):
                    fn = self.xanes3D_rec_path_tplt.format(
                        self.im_ids_dict[str(self.algn_pair_lst[ii][1]).zfill(3)],
                        str(jj).zfill(5),
                    )
                    img[jj_id] = tifffile.imread(fn)[
                        self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                    ]
                    jj_id += 1

                with mp.Pool(N_CPU) as pool:
                    rlt = pool.map(
                        partial(mrtv_reg_v4, cfg),
                        [[self.ref_im, img[jj]] for jj in range(sli_e - sli_s)],
                    )
                pool.close()
                pool.join()

                tvl = []
                for jj in range(len(rlt)):
                    self.shift[ii, jj] = rlt[jj][3]
                    tvl.append(rlt[jj][0][self.mrtv_lvl - 1].flatten()[rlt[jj][1][-1]])
                min_tv_id = np.array(tvl).argmin()
                del rlt
                gc.collect()

                with mp.Pool(N_CPU) as pool:
                    rlt = pool.map(
                        shift_img,
                        [[img[jj], self.shift[ii, jj]] for jj in range(sli_e - sli_s)],
                    )
                pool.close()
                pool.join()

                for jj in range(len(rlt)):
                    img[jj] = rlt[jj]
                del rlt
                gc.collect()

                g11 = g1.create_group(str(ii).zfill(3))
                g11.create_dataset("mrtv_best_shift_id", data=min_tv_id)
                g11.create_dataset("tv", data=tvl)
                g11.create_dataset("shift", data=self.shift[ii])
                g11.create_dataset("trial_reg_img", data=img)
                g11.create_dataset("trial_fixed_img", data=self.ref_im)
        elif self.reg_alg.upper() == "RIG-MRTV":
            print(
                'We are using "multi-resolution total variation" method for registration.'
            )
            sli_s = self.xanes3D_fixed_ref_sli - self.xanes3D_sli_srch_half_range
            sli_e = self.xanes3D_fixed_ref_sli + self.xanes3D_sli_srch_half_range

            cfg = {}
            cfg["pxl_conf"] = dict(
                type="area", levs=self.mrtv_lvl, wz=self.mrtv_wz, lsw=10
            )
            cfg["sub_conf"] = dict(
                use=True, type="ana", sp_wz=self.mrtv_sp_wz, sp_us=10
            )
            cfg["smth_krnl"] = self.mrtv_smth_knl
            cfg["pre_offset"] = None
            cfg["gm"] = 1
            cfg["use_flt"] = self.rig_mrtv_use_flt
            cfg["use_norm"] = self.rig_mrtv_use_norm

            rig_mrtv_cfg = {}
            rig_mrtv_cfg["pxl_conf"] = dict(type="area", levs=1, wz=4)
            rig_mrtv_cfg["sub_conf"] = dict(use=True, type="ana", sp_wz=3, sp_us=10)
            rig_mrtv_cfg["smth_krnl"] = self.mrtv_smth_knl
            rig_mrtv_cfg["ang_rgn"] = [-self.rig_mrtv_ang_rgn, self.rig_mrtv_ang_rgn]
            rig_mrtv_cfg["pre_offset"] = self.rig_mrtv_pre_ofst
            rig_mrtv_cfg["gm"] = self.rig_mrtv_gm
            rig_mrtv_cfg["use_flt"] = self.rig_mrtv_use_flt
            rig_mrtv_cfg["use_norm"] = self.rig_mrtv_use_norm
            for ii in range(len(self.algn_pair_lst)):
                fn = self.xanes3D_rec_path_tplt.format(
                    self.im_ids_dict[str(self.algn_pair_lst[ii][0]).zfill(3)],
                    str(self.xanes3D_fixed_ref_sli).zfill(5),
                )
                self.ref_im[:] = tifffile.imread(fn)[
                    self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                ]

                jj_id = 0
                for jj in range(sli_s, sli_e):
                    fn = self.xanes3D_rec_path_tplt.format(
                        self.im_ids_dict[str(self.algn_pair_lst[ii][1]).zfill(3)],
                        str(jj).zfill(5),
                    )
                    img[jj_id] = tifffile.imread(fn)[
                        self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                    ]
                    jj_id += 1

                with mp.Pool(N_CPU) as pool:
                    rlt = pool.map(
                        partial(mrtv_reg_v4, cfg),
                        [[self.ref_im, img[jj]] for jj in range(sli_e - sli_s)],
                    )
                pool.close()
                pool.join()

                tvl = []
                for jj in range(len(rlt)):
                    self.shift[ii, jj] = rlt[jj][3]
                    tvl.append(rlt[jj][0][self.mrtv_lvl - 1].flatten()[rlt[jj][1][-1]])
                min_tv_id = np.array(tvl).argmin()
                del rlt
                gc.collect()

                regtools.translate_single_img(
                    self.shift[ii, min_tv_id], "MRTV", None, img[min_tv_id]
                )

                mrtv_shift, out_src = mrtv_rigid_reg(
                    self.ref_im,
                    img[min_tv_id],
                    rig_mrtv_cfg,
                    itr=2,
                    mask=1,
                    roi=None,
                    popsize=100,
                    order="L1",
                    filt=True,
                    norm=True,
                )

                g11 = g1.create_group(str(ii).zfill(3))
                g11.create_dataset("mrtv_best_shift_id", data=min_tv_id)
                g11.create_dataset("tv", data=tvl)
                g11.create_dataset("shift", data=self.shift[ii])
                g11.create_dataset("rigid_reg_mat", data=mrtv_shift)
                g11.create_dataset(
                    "ang_correction", data=cal_rig_mrtv_ang(mrtv_shift, degree=True)
                )
                g11.create_dataset(
                    "combined_shift", data=self.shift[ii] + np.array(mrtv_shift[:2, 2])
                )
                g11.create_dataset("rigid_reg_img", data=out_src)
                g11.create_dataset("trial_fixed_img", data=self.ref_im)
        elif self.reg_alg.upper() == "LS+MRTV":
            print(
                'We are using "multi-resolution total variation" method for registration.'
            )
            sli_s = self.xanes3D_fixed_ref_sli - self.xanes3D_sli_srch_half_range
            sli_e = self.xanes3D_fixed_ref_sli + self.xanes3D_sli_srch_half_range
            for ii in range(len(self.algn_pair_lst)):
                fn = self.xanes3D_rec_path_tplt.format(
                    self.im_ids_dict[str(self.algn_pair_lst[ii][0]).zfill(3)],
                    str(self.xanes3D_fixed_ref_sli).zfill(5),
                )
                self.ref_im[:] = tifffile.imread(fn)[
                    self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                ]

                jj_id = 0
                for jj in range(sli_s, sli_e):
                    fn = self.xanes3D_rec_path_tplt.format(
                        self.im_ids_dict[str(self.algn_pair_lst[ii][1]).zfill(3)],
                        str(jj).zfill(5),
                    )
                    img[jj_id] = tifffile.imread(fn)[
                        self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                    ]
                    jj_id += 1

                with mp.Pool(N_CPU) as pool:
                    rlt = pool.map(
                        partial(
                            mrtv_ls_combo_reg,
                            self.mrtv_wz,
                            2,
                            10,
                            self.mrtv_sp_wz,
                            self.mrtv_sp_wz,
                        ),
                        [[self.ref_im, img[jj]] for jj in range(sli_e - sli_s)],
                    )
                pool.close()
                pool.join()

                tvl = []
                for jj in range(len(rlt)):
                    self.shift[ii, jj] = rlt[jj][3]
                    tvl.append(rlt[jj][0][self.mrtv_lvl - 1].flatten()[rlt[jj][1][-1]])
                min_tv_id = np.array(tvl).argmin()
                del rlt
                gc.collect()

                with mp.Pool(N_CPU) as pool:
                    rlt = pool.map(
                        shift_img,
                        [[img[jj], self.shift[ii, jj]] for jj in range(sli_e - sli_s)],
                    )
                pool.close()
                pool.join()

                for jj in range(len(rlt)):
                    img[jj] = rlt[jj]
                del rlt
                gc.collect()

                g11 = g1.create_group(str(ii).zfill(3))
                g11.create_dataset(
                    "mrtv_best_shift_id" + str(ii).zfill(3), data=min_tv_id
                )
                g11.create_dataset("tv" + str(ii).zfill(3), data=tvl)
                g11.create_dataset("shift" + str(ii).zfill(3), data=self.shift[ii])
                g11.create_dataset("trial_reg_img" + str(ii).zfill(3), data=img)
                g11.create_dataset(
                    "trial_fixed_img" + str(ii).zfill(3), data=self.ref_im
                )
        elif self.reg_alg.upper() == "MPC+MRTV":
            print(
                'We are using combo of "masked phase correlation" and "masked phase correlation" method for registration.'
            )
            for ii in range(len(self.algn_pair_lst)):
                fn = self.xanes3D_rec_path_tplt.format(
                    self.im_ids_dict[str(self.algn_pair_lst[ii][0]).zfill(3)],
                    str(self.xanes3D_fixed_ref_sli).zfill(5),
                )
                self.ref_im[:] = tifffile.imread(fn)[
                    self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                ]
                jj_id = 0
                for jj in range(sli_s, sli_e):
                    fn = self.xanes3D_rec_path_tplt.format(
                        self.im_ids_dict[str(self.algn_pair_lst[ii][1]).zfill(3)],
                        str(jj).zfill(5),
                    )
                    img[jj_id] = tifffile.imread(fn)[
                        self.im_roi[0] : self.im_roi[1], self.im_roi[2] : self.im_roi[3]
                    ]
                    _, _, _, self.shift[ii, jj_id] = mrtv_mpc_combo_reg(
                        self.ref_im,
                        img[jj_id],
                        reference_mask=self.msk,
                        overlap_ratio=self.mpc_ovlp_r,
                        levs=self.mrtv_lvl,
                        wz=self.mrtv_wz,
                        sp_wz=self.mrtv_sp_wz,
                        sp_step=self.mrtv_sp_wz,
                    )
                    img[jj_id] = np.real(
                        np.fft.ifftn(
                            fourier_shift(
                                np.fft.fftn(img[jj_id]), self.shift[ii, jj_id]
                            )
                        )
                    )[:]

                    jj_id += 1
                g11 = g1.create_group(str(ii).zfill(3))
                g11.create_dataset("shift" + str(ii).zfill(3), data=self.shift[ii])
                g11.create_dataset("trial_reg_img" + str(ii).zfill(3), data=img)
                g11.create_dataset(
                    "trial_fixed_img" + str(ii).zfill(3), data=self.ref_im
                )
        f.close()

    def apply_xanes3D_chunk_shift(
        self, shift_dict, sli_s=None, sli_e=None, mem_lim=None
    ):
        """
        shift_dict: disctionary;
                    user-defined shift list based on visual inspections of
                    trial registration results; it is configured as
            {'id1':    shift_id1,
             ...
             'idn':    shift_idn}
                  idn: xanes3D_trial_reg_results.h5['reg_results/xxx']
            shift_idn: used specified id in
                       xanes3D_trial_reg_results.h5['reg_results/shiftxxx']
        sli_s:      int
                    starting slice id of the volume to be shifted
        sli_e:      int
                    ending slice id of the volume to be shifted
        trialfn:    string; optional
                    trial registration filename
        savefn:     string; optional
                    filename to the file in which the shifted volume to be saved
        optional_shift_dict: dict; optional
                    user input shifts for specified scan ids. This is useful to
                    correct individual pairs that cannot be aligned with others
                    with the same registration method
        """
        if sli_s is None:
            sli_s = self.im_roi[4]
        if sli_e is None:
            sli_e = self.im_roi[5]

        with h5py.File(self.sav_fn, "a") as f:
            if "registration_results" not in f:
                g0 = f.create_group("registration_results")
            else:
                del f["registration_results"]
                g0 = f.create_group("registration_results")

            g1 = g0.create_group("reg_parameters")
            self.algn_pair_lst = f[
                "/trial_registration/trial_reg_parameters/alignment_pairs"
            ][:].tolist()
            g1.create_dataset("alignment_pairs", data=self.algn_pair_lst)
            self.xanes3D_scn_ids = f[
                "/trial_registration/trial_reg_parameters/scan_ids"
            ][:]
            g1.create_dataset("scan_ids", data=self.xanes3D_scn_ids)
            g1.create_dataset("slice_roi", data=self.im_roi)
            self.anchor_id = f[
                "/trial_registration/trial_reg_parameters/fixed_scan_id"
            ][()]
            g1.create_dataset("fixed_scan_id", data=self.anchor_id)
            self.chunk_sz = f["/trial_registration/trial_reg_parameters/chunk_sz"][()]
            g1.create_dataset("chunk_sz", data=self.chunk_sz)
            self.reg_alg = f["/trial_registration/trial_reg_parameters/reg_method"][
                ()
            ].decode("utf-8")
            g1.create_dataset("reg_method", data=self.reg_alg)
            self.ref_mode = f["/trial_registration/trial_reg_parameters/reg_ref_mode"][
                ()
            ].decode("utf-8")
            g1.create_dataset("reg_ref_mode", data=str(self.ref_mode.upper()))
            self.xanes3D_sli_srch_half_range = f[
                "/trial_registration/trial_reg_parameters/sli_search_half_range"
            ][()]
            self.im_ids_dict = h5todict(
                self.sav_fn,
                path="/trial_registration/trial_reg_parameters/scan_ids_dict",
            )
            self.eng_dict = h5todict(
                self.sav_fn, path="/trial_registration/trial_reg_parameters/eng_dict"
            )
            dicttoh5(
                self.eng_dict,
                f,
                mode="a",
                update_mode="replace",
                h5path="/registration_results/reg_parameters/eng_dict",
            )
            dicttoh5(
                self.im_ids_dict,
                f,
                mode="a",
                update_mode="replace",
                h5path="/registration_results/reg_parameters/scan_ids_dict",
            )

            (self.abs_shift_dict, self.shift_chain_dict) = regtools.sort_absolute_shift(
                self.algn_pair_lst,
                shft_dict=shift_dict,
                data_type="3D_XANES",
                reg_alg=self.reg_alg,
            )

            dicttoh5(
                self.abs_shift_dict,
                f,
                mode="a",
                update_mode="replace",
                h5path="/registration_results/reg_parameters/user_determined_shift/user_input_shift_lookup",
            )

            shift = {}
            slioff = {}
            for key in sorted(self.abs_shift_dict.keys()):
                shift[str(key).zfill(3)] = self.abs_shift_dict[key]["in_sli_shift"]
                slioff[str(key).zfill(3)] = self.abs_shift_dict[key]["out_sli_shift"]

            dicttoh5(
                shift,
                f,
                mode="a",
                update_mode="replace",
                h5path="/registration_results/reg_parameters/user_determined_shift/absolute_in_slice_shift",
            )
            dicttoh5(
                slioff,
                f,
                mode="a",
                update_mode="replace",
                h5path="/registration_results/reg_parameters/user_determined_shift/absolute_out_slice_shift",
            )

            g2 = g0.create_group("reg_results")
            g21 = g2.create_dataset(
                "registered_xanes3D",
                shape=(
                    len(self.im_ids_dict),
                    sli_e - sli_s + 1,
                    self.im_roi[1] - self.im_roi[0],
                    self.im_roi[3] - self.im_roi[2],
                ),
            )
            g22 = g2.create_dataset("eng_list", shape=(len(self.im_ids_dict),))

            img = np.ndarray(
                [self.im_roi[1] - self.im_roi[0], self.im_roi[3] - self.im_roi[2]]
            )
            cnt1 = 0
            for key in sorted(self.abs_shift_dict.keys()):
                shift = self.abs_shift_dict[key]["in_sli_shift"]
                slioff = self.abs_shift_dict[key]["out_sli_shift"]
                scan_id = self.im_ids_dict[key]

                if self.reg_alg == "SR":
                    yshift_int = int(shift[0, 2])
                    xshift_int = int(shift[1, 2])
                    shift[0, 2] -= yshift_int
                    shift[1, 2] -= xshift_int
                elif self.reg_alg in ["PC", "MPC", "MRTV", "RIG-MRTV", "MPC+MRTV"]:
                    yshift_int = int(shift[0])
                    xshift_int = int(shift[1])
                    shift[0] -= yshift_int
                    shift[1] -= xshift_int

                bdi, num_batch = regtools.chunking(
                    [
                        sli_e - sli_s + 1,
                        self.im_roi[1] - self.im_roi[0],
                        self.im_roi[3] - self.im_roi[2],
                    ],
                    mem_lim=mem_lim,
                )
                for i in range(num_batch):
                    img = tiff_vol_reader(
                        self.xanes3D_rec_path_tplt,
                        scan_id,
                        [
                            sli_s + slioff + bdi[i * N_CPU],
                            sli_s + slioff + bdi[(i + 1) * N_CPU],
                            self.im_roi[0] - yshift_int,
                            self.im_roi[1] - yshift_int,
                            self.im_roi[2] - xshift_int,
                            self.im_roi[3] - xshift_int,
                        ],
                    )

                    rlt = regtools.translate_vol_img(
                        shift, self.reg_alg, self.sr_mode, img
                    )
                    g21[cnt1, bdi[i * N_CPU] : bdi[(i + 1) * N_CPU], ...] = img[:]
                g22[cnt1] = self.eng_dict[key]
                cnt1 += 1

    def save_reg_result(self, dtype="2D_XANES", data=None):
        if dtype.upper() == "2D_XANES":
            print(f"The registration results will be saved in {self.sav_fn}")

            f = h5py.File(self.sav_fn, "a")
            if "trial_registration" not in f:
                g1 = f.create_group("trial_registration")
            else:
                g1 = f["trial_registration"]

            if "method" not in g1:
                dset = g1.create_dataset("method", data=str(self.reg_alg))
                dset.attrs["method"] = str(self.reg_alg)
            else:
                del g1["method"]
                dset = g1.create_dataset("method", data=str(self.reg_alg))
                dset.attrs["method"] = str(self.reg_alg)

            if "mode" not in g1:
                dset = g1.create_dataset("mode", data=str(self.sr_mode))
                dset.attrs["mode"] = str(self.sr_mode)
            else:
                del g1["mode"]
                dset = g1.create_dataset("mode", data=str(self.sr_mode))
                dset.attrs["mode"] = str(self.sr_mode)

            if "ref_mode" not in g1:
                dset = g1.create_dataset("ref_mode", data=str(self.ref_mode))
                dset.attrs["ref_mode"] = str(self.ref_mode)
            else:
                del g1["ref_mode"]
                dset = g1.create_dataset("ref_mode", data=str(self.ref_mode))
                dset.attrs["ref_mode"] = str(self.ref_mode)

            if "registered_image" not in g1:
                if data is None:
                    g1.create_dataset("registered_image", data=self.im)
                else:
                    g1.create_dataset("registered_image", data=data)
            else:
                del g1["registered_image"]
                if data is None:
                    g1.create_dataset("registered_image", data=self.im)
                else:
                    g1.create_dataset("registered_image", data=data)

            if "shift" not in g1:
                g1.create_dataset("shift", data=self.shift)
            else:
                del g1["shift"]
                g1.create_dataset("shift", data=self.shift)

            if "raw_data_info" not in f:
                g2 = f.create_group("raw_data_info")
            else:
                g2 = f["raw_data_info"]

            for key, val in self.raw_data_info.items():
                if key not in g2:
                    g2.create_dataset(key, data=val)
                else:
                    del g2[key]
                    g2.create_dataset(key, data=val)
            f.close()
        elif dtype.upper() == "3D_XANES":
            print(f"The registration results will be saved in {self.sav_fn}")

            f = h5py.File(self.sav_fn, "a")
            if "registration" not in f:
                g1 = f.create_group("registration")
            else:
                g1 = f["registration"]

            if "method" not in g1:
                dset = g1.create_dataset("method", data=str(self.reg_alg))
                dset.attrs["method"] = str(self.reg_alg)
            else:
                del g1["method"]
                dset = g1.create_dataset("method", data=str(self.reg_alg))
                dset.attrs["method"] = str(self.reg_alg)

            if "registered_image" not in g1:
                if data is None:
                    g1.create_dataset("registered_image", data=self.im)
                else:
                    g1.create_dataset("registered_image", data=data)
            else:
                del g1["registered_image"]
                if data is None:
                    g1.create_dataset("registered_image", data=self.im)
                else:
                    g1.create_dataset("registered_image", data=data)

            if "residual_image" not in g1:
                if data is None:
                    g1.create_dataset(
                        "residual_image", data=np.float32(self.ref_im) - self.im
                    )
                else:
                    g1.create_dataset(
                        "residual_image", data=np.float32(self.ref_im) - data
                    )
            else:
                del g1["residual_image"]
                if data is None:
                    g1.create_dataset(
                        "residual_image", data=np.float32(self.ref_im) - self.im
                    )
                else:
                    g1.create_dataset(
                        "residual_image", data=np.float32(self.ref_im) - data
                    )

            if "shift" not in g1:
                g1.create_dataset("shift", data=self.shift)
            else:
                del g1["shift"]
                g1.create_dataset("shift", data=self.shift)

            if "error" not in g1:
                g1.create_dataset("error", data=self.error)
            else:
                del g1["error"]
                g1.create_dataset("error", data=self.error)

            if "raw_data_info" not in f:
                g2 = f.create_group("raw_data_info")
            else:
                g2 = f["raw_data_info"]

            for key, val in self.raw_data_info.items():
                if key not in g2:
                    g2.create_dataset(key, data=val)
                else:
                    del g2[key]
                    g2.create_dataset(key, data=val)
            f.close()
        else:
            print("'dtype' can only be '2D_XANES' or '3D_XANES'. Quit!")

    @staticmethod
    def shift_registered_3D_chunk(im_fn_tplt, cfg):
        """
        shift_dict: disctionary;
                    user-defined shift list based on visual inspections of
                    trial registration results; it is configured as
            {'id1':    shift_id1,
             ...
             'idn':    shift_idn}
                  idn: xanes3D_trial_reg_results.h5['reg_results/xxx']
            shift_idn: used specified id in
                       xanes3D_trial_reg_results.h5['reg_results/shiftxxx']
        sli_s:      int
                    starting slice id of the volume to be shifted
        sli_e:      int
                    ending slice id of the volume to be shifted
        trialfn:    string; optional
                    trial registration filename
        savefn:     string; optional
                    filename to the file in which the shifted volume to be saved
        optional_shift_dict: dict; optional
                    user input shifts for specified scan ids. This is useful to
                    correct individual pairs that cannot be aligned with others
                    with the same registration method
        """
        if cfg["sli_s"] is None:
            cfg["sli_s"] = cfg["im_roi"][4]
        if cfg["sli_e"] is None:
            cfg["sli_e"] = cfg["im_roi"][5]

        cfg["shift_dict"]
        cfg["algn_pair_lst"]
        cfg["xanes3D_scn_ids"]
        cfg["anchor_id"]
        cfg["chunk_sz"]
        cfg["reg_alg"]
        cfg["ref_mode"]
        cfg["xanes3D_sli_srch_half_range"]
        cfg["im_ids_dict"]
        cfg["eng_dict"]
        cfg["eng_dict"]

        (abs_shift_dict, shift_chain_dict) = regtools.sort_absolute_shift(
            cfg["algn_pair_lst"],
            shft_dict=cfg["shift_dict"],
            data_type="3D_XANES",
            reg_alg=cfg["reg_alg"],
        )

        shift = {}
        slioff = {}
        for key in sorted(abs_shift_dict.keys()):
            shift[str(key).zfill(3)] = abs_shift_dict[key]["in_sli_shift"]
            slioff[str(key).zfill(3)] = abs_shift_dict[key]["out_sli_shift"]

        for key in sorted(abs_shift_dict.keys()):
            shift = abs_shift_dict[key]["in_sli_shift"]
            slioff = abs_shift_dict[key]["out_sli_shift"]
            scan_id = cfg["im_ids_dict"][key]

            if cfg["reg_alg"] == "SR":
                yshift_int = int(shift[0, 2])
                xshift_int = int(shift[1, 2])
                shift[0, 2] -= yshift_int
                shift[1, 2] -= xshift_int
            elif cfg["reg_alg"] in ["PC", "MPC", "MRTV", "MPC+MRTV"]:
                yshift_int = int(shift[0])
                xshift_int = int(shift[1])
                shift[0] -= yshift_int
                shift[1] -= xshift_int

            bdi, num_batch = regtools.chunking(
                [
                    cfg["sli_e"] - cfg["sli_s"] + 1,
                    cfg["im_roi"][1] - cfg["im_roi"][0],
                    cfg["im_roi"][3] - cfg["im_roi"][2],
                ],
                mem_lim=cfg["mem_lim"],
            )

            for i in range(num_batch):
                img = tiff_vol_reader(
                    im_fn_tplt,
                    scan_id,
                    [
                        cfg["sli_s"] + slioff + bdi[i * N_CPU],
                        cfg["sli_s"] + slioff + bdi[(i + 1) * N_CPU],
                        cfg["im_roi"][0] - yshift_int,
                        cfg["im_roi"][1] - yshift_int,
                        cfg["im_roi"][2] - xshift_int,
                        cfg["im_roi"][3] - xshift_int,
                    ],
                )

            regtools.translate_vol_img(shift, cfg["reg_alg"], cfg["sr_mode"], img)

    @staticmethod
    def chunking(dim, mem_lim=None):
        img_sz = dim[1] * dim[2] * 4
        mem_lim = cal_mem_lim(img_sz, mem_lim=mem_lim)
        while (dim[0] * img_sz % mem_lim) * mem_lim / img_sz < N_CPU:
            mem_lim += N_CPU * img_sz
        num_img_in_batch = np.round(mem_lim / img_sz / N_CPU) * N_CPU
        num_batch = int(np.ceil(dim[0] / num_img_in_batch))
        bdi = []
        chunk = int(np.round(num_img_in_batch / N_CPU))
        for ii in range(num_batch):
            if ii < num_batch - 1:
                for jj in range(N_CPU):
                    bdi.append(int(ii * num_img_in_batch + jj * chunk))
            else:
                chunk = int(np.ceil((dim[0] - ii * num_img_in_batch) / N_CPU))
                for jj in range(N_CPU + 1):
                    bdi.append(int(ii * num_img_in_batch + jj * chunk))
                bdi[-1] = min(dim[0], bdi[-1])
        return bdi, num_batch

    @staticmethod
    def default_3DXANES_best_shift(xns_trl_reg_fn):
        shft_dict = {"shft_by_pair_id": {}, "algn_pair_lst": []}
        with h5py.File(xns_trl_reg_fn, "r") as f:
            keys = f["/trial_registration/trial_reg_results"].keys()
            alg = (
                f["/trial_registration/trial_reg_parameters/reg_method"][()]
                .decode("utf-8")
                .upper()
            )
            for key in sorted(keys):
                if alg == "MRTV":
                    best_id = f[
                        f"/trial_registration/trial_reg_results/{key}/mrtv_best_shift_id"
                    ][()]
                    sli_shft = (
                        best_id
                        - f[
                            "/trial_registration/trial_reg_parameters/sli_search_half_range"
                        ]
                    )
                    tra_shft = f[f"/trial_registration/trial_reg_results/{key}/shift"][
                        best_id
                    ]
                    rot_shft = 0
                elif alg == "RIG-MRTV":
                    best_id = f[
                        f"/trial_registration/trial_reg_results/{key}/mrtv_best_shift_id"
                    ][()]
                    sli_shft = (
                        best_id
                        - f[
                            "/trial_registration/trial_reg_parameters/sli_search_half_range"
                        ]
                    )
                    tra_shft = f[
                        f"/trial_registration/trial_reg_results/{key}/combined_shift"
                    ][best_id]
                    rot_shft = f[
                        f"/trial_registration/trial_reg_results/{key}/ang_correction"
                    ][()]
                else:
                    sli_shft = 0
                    tra_shft = f[f"/trial_registration/trial_reg_results/{key}/shift"][
                        best_id
                    ]
                    rot_shft = 0

                shft_dict["shft_by_pair_id"][str(int(key))] = [
                    sli_shft,
                    *tra_shft,
                    rot_shft,
                ]
            shft_dict["algn_pair_lst"] = f[
                "/trial_registration/trial_reg_parameters/alignment_pairs"
            ][:]
        return shft_dict

    @staticmethod
    def default_2DXANES_best_shift(xns_trl_reg_fn):
        shft_dict = {"shft_by_pair_id": {}, "algn_pair_lst": []}
        with h5py.File(xns_trl_reg_fn, "r") as f:
            keys = f["/trial_registration/trial_reg_results"].keys()
            alg = (
                f["/trial_registration/trial_reg_parameters/reg_method"][()]
                .decode("utf-8")
                .upper()
            )
            for key in sorted(keys):
                shft_dict["shft_by_pair_id"][str(int(key))] = f[
                    f"/trial_registration/trial_reg_results/{key}/shift{key}"
                ][:]

            shft_dict["algn_pair_lst"] = [
                list(ii)
                for ii in f["/trial_registration/trial_reg_parameters/alignment_pairs"][
                    :
                ]
            ]
        return shft_dict

    @staticmethod
    def translate_single_img(shift, method, mode, img):
        if method.upper() in ["PC", "MPC", "MRTV", "RIG-MRTV", "MPC+MRTV"]:
            img[:] = np.real(np.fft.ifftn(fourier_shift(np.fft.fftn(img), shift)))[:]
        elif method == "SR":
            if mode is None:
                sr = StackReg(StackReg.TRANSLATION)
            elif mode.upper() == "TRANSLATION":
                sr = StackReg(StackReg.TRANSLATION)
            elif mode.upper() == "RIGID_BODY":
                sr = StackReg(StackReg.RIGID_BODY)
            elif mode.upper() == "SCALED_ROTATION":
                sr = StackReg(StackReg.SCALED_ROTATION)
            elif mode.upper() == "AFFINE":
                sr = StackReg(StackReg.AFFINE)
            elif mode.upper() == "BILINEAR":
                sr = StackReg(StackReg.BILINEAR)
            img[:] = sr.transform(img, tmat=shift)[:]
        else:
            print("Nonrecognized method. Quit!")

    @staticmethod
    @parallelizing(chunk_dim=0)
    def translate_vol_img(shift, method, mode, data):
        for ii in range(data.shape[0]):
            regtools.translate_single_img(shift, method, mode, data[ii])

    @staticmethod
    def set_chunks(n_pnts, anchor_loc, chnk_sz, use_chnk=True):
        if use_chnk:
            lst = []
            s = anchor_loc - 1
            left_num_chnk = 0
            for ii in range(int(np.ceil(anchor_loc / chnk_sz))):
                lst.append([max(s - chnk_sz + 1, 0), s])
                s -= chnk_sz
                left_num_chnk += 1

            s = anchor_loc
            right_num_chnk = 0
            for ii in range((n_pnts - anchor_loc) // chnk_sz):
                lst.append([s, s + chnk_sz - 1])
                s += chnk_sz
                right_num_chnk += 1

            lst.append([s if s <= n_pnts - 1 else n_pnts - 1, n_pnts - 1])
            right_num_chnk += 1

            num_chnk = left_num_chnk + right_num_chnk
            anchor_chnk = left_num_chnk
            lst = np.array(lst)
            lst = lst[lst[:, 0].argsort()]

            chnks = {
                ii: {"chunk_s": lst[ii, 0], "chunk_e": lst[ii, 1]}
                for ii in range(lst.shape[0])
            }
            return chnks, anchor_chnk, left_num_chnk, num_chnk
        else:
            chnks[0] = {"chunk_s": 0, "chunk_e": n_pnts - 1}
            return chnks, 0, 0, 1

    @staticmethod
    def alignment_scheduler(
        n_pnts, anchor_loc, chnk_sz, use_chnk=True, ref_mode="single"
    ):
        (chnks, anchor_chnk, left_num_chnk, num_chnk) = regtools.set_chunks(
            n_pnts, anchor_loc, chnk_sz
        )
        algn_pair_lst = []

        # print(f'{chnks=}\n{anchor_chnk=}\n{left_num_chnk=}\n{num_chnk=}')
        if use_chnk:
            if ref_mode.upper() == "SINGLE":
                # inter-chunk alignment pair
                for ii in range(left_num_chnk):
                    algn_pair_lst.append(
                        [
                            chnks[left_num_chnk - ii]["chunk_s"],
                            chnks[left_num_chnk - ii - 1]["chunk_s"],
                        ]
                    )
                algn_pair_lst.append([anchor_chnk, anchor_chnk])
                for ii in range(left_num_chnk, num_chnk - 1):
                    algn_pair_lst.append(
                        [chnks[ii]["chunk_s"], chnks[ii + 1]["chunk_s"]]
                    )
                # intra-chunk alignment pair
                for ii in range(num_chnk):
                    for jj in range(chnks[ii]["chunk_s"], chnks[ii]["chunk_e"] + 1):
                        algn_pair_lst.append([chnks[ii]["chunk_s"], jj])

                tem = []
                for ii in algn_pair_lst:
                    if ii[0] == ii[1]:
                        tem.append(ii)
                for ii in tem:
                    algn_pair_lst.remove(ii)
                algn_pair_lst.append([anchor_loc, anchor_loc])
                algn_pair_lst = regtools.rm_redundant(algn_pair_lst)
            elif ref_mode.upper() == "NEIGHBOR":
                # inter-chunk alignment pair
                for ii in range(left_num_chnk):
                    algn_pair_lst.append(
                        [
                            chnks[left_num_chnk - ii]["chunk_s"],
                            chnks[left_num_chnk - ii]["chunk_e"],
                        ]
                    )
                    algn_pair_lst.append(
                        [
                            chnks[left_num_chnk - ii]["chunk_e"],
                            chnks[left_num_chnk - ii - 1]["chunk_s"],
                        ]
                    )
                algn_pair_lst.append(
                    [chnks[anchor_chnk]["chunk_e"], chnks[anchor_chnk]["chunk_e"] + 1]
                )
                for ii in range(left_num_chnk + 1, num_chnk - 1):
                    algn_pair_lst.append([chnks[ii]["chunk_e"], chnks[ii]["chunk_s"]])
                    algn_pair_lst.append(
                        [chnks[ii]["chunk_s"], chnks[ii + 1]["chunk_e"]]
                    )
                algn_pair_lst.append(
                    [chnks[num_chnk - 1]["chunk_s"], chnks[num_chnk - 1]["chunk_e"]]
                )
                # inter-chunk alignment pair
                for ii in range(num_chnk):
                    for jj in range(chnks[ii]["chunk_s"], chnks[ii]["chunk_e"] + 1):
                        algn_pair_lst.append([chnks[ii]["chunk_e"], jj])

                tem = []
                for ii in algn_pair_lst:
                    if ii[0] == ii[1]:
                        tem.append(ii)
                for ii in tem:
                    algn_pair_lst.remove(ii)
                algn_pair_lst.append([anchor_loc, anchor_loc])
                algn_pair_lst = regtools.rm_redundant(algn_pair_lst)
        else:
            for ii in range(n_pnts - 1):
                algn_pair_lst.append([ii, ii + 1])
            algn_pair_lst.append([anchor_loc, anchor_loc])
        return algn_pair_lst

    @staticmethod
    def sort_absolute_shift(
        algn_pair_lst, shft_dict=None, data_type="3D_XANES", reg_alg="MRTV"
    ):
        shft_chn_dict = {}
        for ii in range(len(algn_pair_lst) - 1, -1, -1):
            shft_chn_dict[algn_pair_lst[ii][1]] = [algn_pair_lst[ii][0]]
            jj = ii - 1
            while jj >= 0:
                if shft_chn_dict[algn_pair_lst[ii][1]][-1] == algn_pair_lst[jj][1]:
                    shft_chn_dict[algn_pair_lst[ii][1]].append(algn_pair_lst[jj][0])
                jj -= 1

        abs_shft_dict = {}

        if data_type == "3D_XANES":
            if reg_alg == "SR":
                for key, item in shft_chn_dict.items():
                    item.insert(0, key)
                    tra_shft = np.identity(3)
                    sli_shft = 0
                    ang_shft = 0.0
                    for ii in range(len(item) - 1):
                        idx = algn_pair_lst.index([item[ii + 1], item[ii]])
                        tra_shft = np.matmul(tra_shft, np.array(shft_dict[str(idx)][1]))
                        sli_shft += int(shft_dict[str(idx)][0])
                        ang_shft += shft_dict[str(idx)][-1]
                    abs_shft_dict[str(key).zfill(3)] = {
                        "in_sli_shift": tra_shft,
                        "out_sli_shift": sli_shft,
                        "in_sli_rot": ang_shft,
                    }
            else:
                for key, item in shft_chn_dict.items():
                    item.insert(0, key)
                    tra_shft = 0.0
                    sli_shft = 0
                    ang_shft = 0.0
                    for ii in range(len(item) - 1):
                        idx = algn_pair_lst.index([item[ii + 1], item[ii]])
                        tra_shft += np.array(shft_dict[str(idx)][1:-1])
                        sli_shft += int(shft_dict[str(idx)][0])
                        ang_shft += shft_dict[str(idx)][-1]
                    abs_shft_dict[str(key).zfill(3)] = {
                        "in_sli_shift": tra_shft,
                        "out_sli_shift": sli_shft,
                        "in_sli_rot": ang_shft,
                    }
        if data_type == "2D_XANES":
            if reg_alg == "SR":
                for key, item in shft_chn_dict.items():
                    item.insert(0, key)
                    shft = np.identity(3)
                    for ii in range(len(item) - 1):
                        idx = algn_pair_lst.index([item[ii + 1], item[ii]])
                        shft = np.matmul(shft, np.array(shft_dict[str(idx)]))
                    abs_shft_dict[str(key).zfill(3)] = {"in_sli_shift": shft}
            else:
                for key, item in shft_chn_dict.items():
                    item.insert(0, key)
                    print(key, item)
                    shft = 0.0
                    for ii in range(len(item) - 1):
                        idx = algn_pair_lst.index([item[ii + 1], item[ii]])
                        shft += np.array(shft_dict[str(idx)])
                    abs_shft_dict[str(key).zfill(3)] = {"in_sli_shift": shft}
        return abs_shft_dict, shft_chn_dict

    @staticmethod
    def rm_redundant(list_of_lists):
        seen = set()
        result = []
        for sublist in list_of_lists:
            t = tuple(sublist)  # Convert sublist to a tuple to make it hashable
            if t not in seen:
                seen.add(t)
                result.append(sublist)  # Append the original sublist to preserve order
        return result

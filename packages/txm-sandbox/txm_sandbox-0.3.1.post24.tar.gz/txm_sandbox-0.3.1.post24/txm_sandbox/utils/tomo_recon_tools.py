#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 14:38:41 2020

@author: xiao
"""

import os, gc, time, shutil

import numpy as np
import scipy.interpolate as sci
from scipy.ndimage import binary_erosion, gaussian_filter as gf, median_filter
from pathlib import Path
import h5py, tifffile, json
import skimage.restoration as skr
from skimage.transform import rescale
import tomopy
from datetime import datetime

import multiprocess as mp
from functools import partial
from copy import deepcopy

from .io import (
    data_reader,
    tomo_h5_reader,
    data_info,
    tomo_h5_info,
    tif_seq_writer,
    cal_mem_lim,
)
from .misc import parallelizing

from .xanes_regtools import regtools as reg

N_CPU = os.cpu_count()
if N_CPU > 1:
    N_CPU -= 1

IF_LOG = True


def align_proj(data, data_ref=None, **kwargs):
    pass


@parallelizing(chunk_dim=0)
def data_downsampling(levs, data):
    if np.any((np.array(levs) - 1) > 0):
        return rescale(data, levs, mode="edge", order=4, anti_aliasing=False)
    else:
        return rescale(data, levs, mode="edge", order=4, anti_aliasing=True)


def binning(sz, ds):
    if isinstance(sz, int):
        return int(round(sz * ds))
    else:
        return [int(ii) for ii in np.round(np.array(sz) * ds)]


def ds_data_reader(cfg, dtype="data"):
    fn, _ = get_file(cfg)
    reader = cfg["file_params"]["reader"]
    io_cfg = cfg["file_params"]["io_confg"]
    sli_s = cfg["data_params"]["sli_s"]
    sli_e = cfg["data_params"]["sli_e"]
    ds = 1.0 / cfg["data_params"]["downsample"]
    levs = [1, ds, ds]

    if cfg["recon_config"]["recon_type"] == "Trial Cent":
        data = [
            data_downsampling(
                levs,
                reader(
                    fn,
                    dtype=dtype,
                    sli=[None, [int(sli_s / ds), int(sli_e / ds)], None],
                    cfg=io_cfg,
                ),
            )
        ]
    else:
        if dtype == "data":
            dim = cfg["file_params"]["info_reader"](
                fn, dtype="data", cfg=cfg["file_params"]["io_confg"]
            )
            im_sz = dim[1] * dim[2] * 4
            mem_lim = cal_mem_lim(im_sz, mem_lim=None)
            num_im_in_batch = int(np.round(mem_lim / im_sz))

            id_rgn = [0]
            cnt = 1
            while id_rgn[-1] < dim[0]:
                id_rgn.append(min(num_im_in_batch * cnt, dim[0]))
                cnt += 1
            if id_rgn[-1] - id_rgn[-2] == 1:
                id_rgn[-2] = id_rgn[-1]
                id_rgn.pop(-1)

            data = []
            print(f"ds start: {time.asctime()}")
            cnt = 0
            for ii in range(len(id_rgn) - 1):
                print(f"{ii=}")
                raw = reader(
                    fn,
                    dtype="data",
                    sli=[[id_rgn[ii], id_rgn[ii + 1]], None, None],
                    cfg=io_cfg,
                )
                data.append(data_downsampling(levs, raw))
                cnt += 1
            print(f"ds end: {time.asctime()}")
        else:
            data = [
                data_downsampling(
                    levs, reader(fn, dtype=dtype, sli=[None, None, None], cfg=io_cfg)
                )
            ]
    return np.vstack(data).astype(np.float32)


def find_sli_for_cen(cfg, sli_rng=None):
    tem_cfg = deepcopy(cfg)
    dim_info = tem_cfg["file_params"]["info_reader"]
    io_cfg = tem_cfg["file_params"]["io_confg"]
    thres = tem_cfg["data_params"]["wedge_ang_auto_det_thres"]
    ds = 1.0 / tem_cfg["data_params"]["downsample"]

    fn, _ = get_file(tem_cfg)
    im_shp = list(dim_info(fn, dtype="data", cfg=io_cfg))
    im_shp[1:] = binning(im_shp[1:], ds)
    tem_cfg["data_params"]["sli_s"] = 0
    tem_cfg["data_params"]["sli_e"] = im_shp[1]

    tem, _, _, _ = read_data(tem_cfg, mean_axis=2)
    if tem_cfg["recon_config"]["is_wedge"]:
        bad_angs = tem < thres
    else:
        bad_angs = 1
    sli = int(im_shp[1] / 4) + np.argmin(
        np.sum(tem * bad_angs, axis=0)[3 * int(im_shp[1] / 8) : 5 * int(im_shp[1] / 8)]
    )
    return int(sli)


def get_dark_angs_all_sli(cfg, data=None):
    tem_cfg = deepcopy(cfg)
    thres = tem_cfg["data_params"]["wedge_ang_auto_det_thres"]
    if data is None:
        ds = 1.0 / tem_cfg["data_params"]["downsample"]
        dim_info = tem_cfg["file_params"]["info_reader"]
        fn = tem_cfg["file_params"]["wedge_ang_auto_det_ref_fn"]
        io_cfg = tem_cfg["file_params"]["io_confg"]

        im_shp = list(dim_info(fn, dtype="data", cfg=io_cfg))
        im_shp[1:] = binning(im_shp[1:], ds)
        tem_cfg["data_params"]["sli_s"] = 0
        tem_cfg["data_params"]["sli_e"] = im_shp[1]

        if tem_cfg["data_params"]["wedge_col_s"] is None:
            tem_cfg["data_params"]["wedge_col_s"] = 0
        else:
            tem_cfg["data_params"]["wedge_col_s"] = int(
                tem_cfg["data_params"]["wedge_col_s"]
            )

        if tem_cfg["data_params"]["wedge_col_e"] is None:
            tem_cfg["data_params"]["wedge_col_e"] = im_shp[2]
        else:
            tem_cfg["data_params"]["wedge_col_e"] = int(
                tem_cfg["data_params"]["wedge_col_e"]
            )

        data, _, _, angs = read_data(tem_cfg, mean_axis=2)
    bad_angs = data < thres
    return bad_angs, angs


def get_file(cfg):
    scn_id = cfg["data_params"]["scan_id"]
    raw_data_top_dir = cfg["file_params"]["raw_data_top_dir"]
    io_cfg = cfg["file_params"]["io_confg"]
    recon_top_dir = cfg["file_params"]["recon_top_dir"]

    data_file = list(
        Path(raw_data_top_dir).glob(io_cfg["tomo_raw_fn_template"].format(scn_id))
    )

    if data_file is []:
        return None

    if recon_top_dir is None:
        output_file = str(
            Path(raw_data_top_dir)
            .joinpath("recon_" + str(data_file[0].stem))
            .joinpath("recon_" + str(data_file[0].stem) + "_{0}.tiff")
        )
    else:
        output_file = str(
            Path(recon_top_dir)
            .joinpath("recon_" + str(data_file[0].stem))
            .joinpath("recon_" + str(data_file[0].stem) + "_{0}.tiff")
        )
    if (not Path(output_file).parent.exists()) and (recon_top_dir is not None):
        Path(output_file).parent.mkdir(mode=0o777, parents=True, exist_ok=True)
    return str(data_file[0]), output_file


def get_algn_pair_lst(scn_id_lst, rec_cfg, ref_id=None):
    if ref_id is not None:
        n_pnts = len(scn_id_lst)
        anchor_loc = scn_id_lst.index(ref_id)
        chnk_sz = rec_cfg["aut_xns3d_pars"]["reg_chnk_sz"]
        ref_mode = rec_cfg["aut_xns3d_pars"]["reg_mode"]
        if chnk_sz > 1:
            scn_id_lst = reg.alignment_scheduler(
                n_pnts, anchor_loc, chnk_sz, use_chnk=True, ref_mode=ref_mode
            )
        else:
            scn_id_lst = reg.alignment_scheduler(
                n_pnts, anchor_loc, chnk_sz, use_chnk=False, ref_mode=ref_mode
            )
    print(f"alignment pair list: {scn_id_lst}")
    return scn_id_lst


def get_wedge_ref_fn_scn_id(cfg):
    ref_fn_set = set(
        str(Path(cfg["file_params"]["wedge_ang_auto_det_ref_fn"]).stem).split("_")
    )
    tplt_set = set(
        str(Path(cfg["file_params"]["io_confg"]["tomo_raw_fn_template"]).stem).split(
            "_"
        )
    )
    diff = tplt_set.symmetric_difference(ref_fn_set)
    diff_copy = deepcopy(diff)
    for ii in diff_copy:
        if "{" in ii:
            diff.remove(ii)
    return list(diff)[0]


def if_log(flt_dict):
    if 0 != len(flt_dict.keys()):
        for key in sorted(flt_dict.keys()):
            if "phase retrieval" == flt_dict[key]["filter_name"]:
                if "bronnikov" == flt_dict[key]["params"]["filter"]:
                    return False
            else:
                return True
    else:
        return True


@parallelizing(chunk_dim=0)
def median(sz, im3d):
    return median_filter(im3d, size=sz)


def minus_log(data):
    data[:] = tomopy.prep.normalize.minus_log(data)[:]
    data[np.isnan(data)] = 0
    data[np.isinf(data)] = 0


def normalize(
    arr, flat, dark, fake_flat_roi=None, padval=1, cutoff=None, ncore=None, out=None
):
    """
    Normalize raw projection data using the flat and dark field projections.

    Parameters
    ----------
    arr : ndarray
        3D stack of projections.
    flat : ndarray
        3D flat field data.
    dark : ndarray
        3D dark field data.
    cutoff : float, optional
        Permitted maximum vaue for the normalized data.
    ncore : int, optional
        Number of cores that will be assigned to jobs.
    out : ndarray, optional
        Output array for result. If same as arr,
        process will be done in-place.

    Returns
    -------
    ndarray
        Normalized 3D tomographic data.
    """
    if fake_flat_roi is not None:
        out = []
        flat = np.ndarray(arr.shape[1:])
        data = np.ndarray(arr.shape[1:])
        dark = np.mean(dark, axis=0, dtype=np.float32)
        for ii in range(arr.shape[0]):
            flat_val = arr[ii][fake_flat_roi].mean()
            flat[:] = (flat_val * np.ones(arr.shape[1:]))[:]
            data[:] = ((arr[ii] - dark) / (flat - dark))[:]
            data[np.isnan(data)] = padval
            data[np.isinf(data)] = padval
            data[data <= 0] = padval
            out.append(data)
    else:
        flat = np.mean(flat, axis=0, dtype=np.float32)
        dark = np.mean(dark, axis=0, dtype=np.float32)
        with tomopy.util.mproc.set_numexpr_threads(ncore):
            denom = (flat - dark).astype(np.float32)
            out = (arr - dark).astype(np.float32)
            out[:] = (out / denom)[:]
            out[np.isnan(out)] = padval
            out[np.isinf(out)] = padval
            out[out <= 0] = padval
            if cutoff is not None:
                cutoff = np.float32(cutoff)
                out[:] = np.where(out > cutoff, cutoff, out)[:]
    return np.array(out)


def preproc_data(data, white, dark, theta, cfg, ref_bad_angs=None, ref_angs=None):
    if cfg["recon_config"]["use_rm_zinger"]:
        data[:] = tomopy.misc.corr.remove_outlier(
            data, cfg["data_params"]["zinger_val"], size=15, axis=0
        )[:]
        white[:] = tomopy.misc.corr.remove_outlier(
            white, cfg["data_params"]["zinger_val"], size=15, axis=0
        )[:]

    if cfg["recon_config"]["use_flat_blur"]:
        white[:] = gf(white, cfg["data_params"]["blur_kernel"])[:]

    data[:] = normalize(data, white, dark, padval=0)[:]

    if (
        cfg["recon_config"]["use_debug"]
        and cfg["recon_config"]["recon_type"] == "Trial Cent"
    ):
        save_debug(cfg["file_params"]["debug_top_dir"], "1-norm_data.tiff", data)

    if cfg["recon_config"]["is_wedge"]:
        if ref_bad_angs is None:
            if cfg["recon_config"]["use_wedge_ang_auto_det"]:
                print(
                    "wedge_ref_file: ", cfg["file_params"]["wedge_ang_auto_det_ref_fn"]
                )
                tem_cfg = deepcopy(cfg)
                tem_cfg["data_params"]["scan_id"] = get_wedge_ref_fn_scn_id(cfg)
                ref_data, _, _, ref_angs = read_data(tem_cfg, mean_axis=2)
                ref_angs = ref_angs * np.pi / 180.0
                ref_bad_angs = ref_data < cfg["data_params"]["wedge_ang_auto_det_thres"]
            else:
                ref_bad_angs = np.zeros([data.shape[0], data.shape[1]], dtype=bool)
                ref_bad_angs[
                    cfg["data_params"]["wedge_missing_s"] : cfg["data_params"][
                        "wedge_missing_e"
                    ],
                    :,
                ] = True
        if ref_angs is None:
            ref_angs = theta

        data[:] = sort_wedge(
            data, theta, ref_bad_angs, ref_angs, 0, data.shape[1], padval=1
        )[:]

        if (
            cfg["recon_config"]["use_debug"]
            and cfg["recon_config"]["recon_type"] == "Trial Cent"
        ):
            save_debug(cfg["file_params"]["debug_top_dir"], "2-wedge_data.tiff", data)

    if 0 != len(cfg["flt_params"].keys()):
        for idx in sorted(cfg["flt_params"].keys()):
            data[:] = run_filter(data, cfg["flt_params"][idx])[:]
            if (
                cfg["recon_config"]["use_debug"]
                and cfg["recon_config"]["recon_type"] == "Trial Cent"
            ):
                save_debug(
                    cfg["file_params"]["debug_top_dir"],
                    f'2-filter_name_{cfg["flt_params"][idx]["filter_name"]}_filtered_data.tiff',
                    data,
                )

    if if_log(cfg["flt_params"]):
        minus_log(data)
        if (
            cfg["recon_config"]["use_debug"]
            and cfg["recon_config"]["recon_type"] == "Trial Cent"
        ):
            save_debug(cfg["file_params"]["debug_top_dir"], "3-log_data.tiff", data)
        if "remove cupping" in cfg["flt_params"].keys():
            params = translate_params(cfg["flt_params"]["remove cupping"]["params"])
            data -= params["cc"]
            print("running remove cupping")

    if cfg["recon_config"]["is_wedge"]:
        data[:] = sort_wedge(
            data, theta, ref_bad_angs, ref_angs, 0, data.shape[1], padval=0
        )[:]
        if cfg["recon_config"]["recon_type"] == "Trial Cent":
            if cfg["recon_config"]["use_debug"]:
                save_debug(
                    cfg["file_params"]["debug_top_dir"], "4-wedge_data.tiff", data
                )
    print("preproc finished")
    return data


def prep_xns3d_auto_tomo_cfg(aut_cen_cfg):
    aut_cen_cfg["file_params"]["io_confg"]["customized_reader"]["user_tomo_reader"] = ""
    if not aut_cen_cfg["file_params"]["reader"]:
        aut_cen_cfg["file_params"]["reader"] = data_reader(tomo_h5_reader)
    if not aut_cen_cfg["file_params"]["info_reader"]:
        aut_cen_cfg["file_params"]["info_reader"] = data_info(tomo_h5_info)

    eng_lst = []
    fnt = str(
        Path(aut_cen_cfg["file_params"]["raw_data_top_dir"]).joinpath(
            aut_cen_cfg["file_params"]["io_confg"]["tomo_raw_fn_template"]
        )
    )
    for sid in aut_cen_cfg["aut_xns3d_pars"]["scn_id_lst"]:
        with h5py.File(fnt.format(sid)) as f:
            eng_lst.append(
                f[
                    aut_cen_cfg["file_params"]["io_confg"]["structured_h5_reader"][
                        "io_data_structure"
                    ]["eng_path"]
                ][()]
            )
    eng_lst = np.array(eng_lst)

    if eng_lst[0] > eng_lst[-1]:
        eng_lst[:] = eng_lst[::-1]
        aut_cen_cfg["aut_xns3d_pars"]["scn_id_lst"] = aut_cen_cfg["aut_xns3d_pars"][
            "scn_id_lst"
        ][::-1]

    data_half_z = int(
        aut_cen_cfg["aut_xns3d_pars"]["ref_sli_srch_half_wz"]
        + aut_cen_cfg["data_params"]["margin"]
    )
    aut_cen_cfg["aut_tomo_pars"] = {
        "scn_id_s": aut_cen_cfg["aut_xns3d_pars"]["scn_id_s"],
        "scn_id_e": aut_cen_cfg["aut_xns3d_pars"]["scn_id_e"],
        "scn_id_lst": aut_cen_cfg["aut_xns3d_pars"]["scn_id_lst"],
        "reg_mode": aut_cen_cfg["aut_xns3d_pars"]["reg_mode"],
        "mrtv_knl_sz": aut_cen_cfg["aut_xns3d_pars"]["mrtv_knl_sz"],
        "ds_fac": aut_cen_cfg["data_params"]["downsample"],
        "cen_srch_half_wz": aut_cen_cfg["aut_xns3d_pars"]["ref_cen_srch_half_wz"],
        "use_dflt_ref_reg_roi": aut_cen_cfg["aut_xns3d_pars"]["use_dflt_ref_reg_roi"],
        "ref_cen_sli": aut_cen_cfg["aut_xns3d_pars"]["ref_cen_sli"],
        "ref_cen_roi": aut_cen_cfg["aut_xns3d_pars"]["ref_cen_roi"],
        "auto_rec": True,
        "rec_all_sli": False,
        "trial_cen_h5_fn": aut_cen_cfg["aut_xns3d_pars"]["xanes3d_sav_trl_reg_fn"],
    }
    aut_cen_cfg["data_params"]["sli_s"] = min(
        0, aut_cen_cfg["aut_xns3d_pars"]["ref_cen_sli"] - int(1.5 * data_half_z)
    )
    file_raw_fn, file_recon_template = get_file(aut_cen_cfg)
    dim = aut_cen_cfg["file_params"]["info_reader"](
        file_raw_fn, dtype="data", cfg=aut_cen_cfg["file_params"]["io_confg"]
    )
    aut_cen_cfg["data_params"]["sli_e"] = max(
        dim[1], aut_cen_cfg["aut_xns3d_pars"]["ref_cen_sli"] + int(1.5 * data_half_z)
    )


def prep_xns3D_auto_reg_cfg(aut_xns3d_cfg):
    aut_xns3d_cfg["file_params"]["io_confg"]["customized_reader"][
        "user_tomo_reader"
    ] = ""
    if not aut_xns3d_cfg["file_params"]["reader"]:
        aut_xns3d_cfg["file_params"]["reader"] = data_reader(tomo_h5_reader)
    if not aut_xns3d_cfg["file_params"]["info_reader"]:
        aut_xns3d_cfg["file_params"]["info_reader"] = data_info(tomo_h5_info)

    eng_lst = []
    fnt = str(
        Path(aut_xns3d_cfg["file_params"]["raw_data_top_dir"]).joinpath(
            aut_xns3d_cfg["file_params"]["io_confg"]["tomo_raw_fn_template"]
        )
    )
    for sid in aut_xns3d_cfg["aut_xns3d_pars"]["scn_id_lst"]:
        with h5py.File(fnt.format(sid)) as f:
            eng_lst.append(
                f[
                    aut_xns3d_cfg["file_params"]["io_confg"]["structured_h5_reader"][
                        "io_data_structure"
                    ]["eng_path"]
                ][()]
            )
    eng_lst = np.array(eng_lst)

    if eng_lst[0] > eng_lst[-1]:
        eng_lst[:] = eng_lst[::-1]
        aut_xns3d_cfg["aut_xns3d_pars"]["scn_id_lst"] = aut_xns3d_cfg["aut_xns3d_pars"][
            "scn_id_lst"
        ][::-1]

    aut_xns3d_cfg["auto_reg_cfg"] = {
        "data_type": "3D_XANES",
        "reg": {
            "alg": (
                "rig-mrtv" if aut_xns3d_cfg["aut_xns3d_pars"]["ang_corr"] else "mrtv"
            ),
            "alg_pars": {
                "MRTV": {
                    "lvl": 2,
                    "wz": 10,
                    "sp_wz": 3,
                    "smth_knl": aut_xns3d_cfg["aut_xns3d_pars"]["mrtv_knl_sz"],
                    "pre_offset": None,
                    "gm": 1,
                    "use_flt": True,
                    "use_norm": False,
                },
                "RIG-MRTV": {
                    "lvl": 2,
                    "wz": 10,
                    "sp_wz": 3,
                    "smth_knl": aut_xns3d_cfg["aut_xns3d_pars"]["mrtv_knl_sz"],
                    "ang_rgn": aut_xns3d_cfg["aut_xns3d_pars"]["ang_corr_rgn"],
                    "pre_offset": None,
                    "gm": 1,
                    "use_flt": True,
                    "use_norm": False,
                },
            },
            "ref_mode": aut_xns3d_cfg["aut_xns3d_pars"]["reg_mode"],
            "use_chnk": True,
            "chnk_sz": aut_xns3d_cfg["aut_xns3d_pars"]["reg_chnk_sz"],
            "XANES3D_fixed_ref_sli": (
                aut_xns3d_cfg["aut_xns3d_pars"]["opt_reg_sli"]
                if aut_xns3d_cfg["aut_xns3d_pars"]["use_opt_reg_roi"]
                else aut_xns3d_cfg["aut_xns3d_pars"]["ref_cen_sli"]
            ),
            "XANES3D_sli_srch_half_range": aut_xns3d_cfg["aut_xns3d_pars"][
                "ref_sli_srch_half_wz"
            ],
            "ref_reg_roi": (
                aut_xns3d_cfg["aut_xns3d_pars"]["opt_reg_roi"]
                if aut_xns3d_cfg["aut_xns3d_pars"]["use_opt_reg_roi"]
                else aut_xns3d_cfg["aut_xns3d_pars"]["ref_cen_roi"]
            ),
        },
        "data": {
            "im_id_s": int(aut_xns3d_cfg["aut_xns3d_pars"]["scn_id_s"]),
            "im_id_e": int(aut_xns3d_cfg["aut_xns3d_pars"]["scn_id_e"]),
            "im_id_fixed": int(aut_xns3d_cfg["aut_xns3d_pars"]["ref_scn_id"]),
            "XANES3D_scn_ids": list(
                np.int_(aut_xns3d_cfg["aut_xns3d_pars"]["scn_id_lst"])
            ),
            "roi": (aut_xns3d_cfg["aut_xns3d_pars"]["rec_roi"]),
        },
        "file": {
            "XANES3D_rec_path_tplt": aut_xns3d_cfg["aut_xns3d_pars"]["rec_fn_tplt"],
            "XANES3D_raw_h5_top_dir": aut_xns3d_cfg["file_params"]["raw_data_top_dir"],
            "XANES2D_raw_fn": None,
            "XANES_tmp_fn": aut_xns3d_cfg["file_params"]["raw_data_top_dir"],
            "sav_fn": aut_xns3d_cfg["aut_xns3d_pars"]["xanes3d_sav_trl_reg_fn"],
        },
        "preproc": {
            "use_mask": False,
            "mask_thres": 0,
            "use_smth_im": False,
            "smth_im_sig": 0,
        },
        "meta": {"eng_list": eng_lst},
    }


def read_data(cfg, mean_axis=None):
    fn, _ = get_file(cfg)
    reader = cfg["file_params"]["reader"]
    io_cfg = cfg["file_params"]["io_confg"]
    sli_s = cfg["data_params"]["sli_s"]
    sli_e = cfg["data_params"]["sli_e"]
    col_s = cfg["data_params"]["col_s"]
    col_e = cfg["data_params"]["col_e"]
    flat_nm = cfg["file_params"]["alt_flat_file"]
    dark_nm = cfg["file_params"]["alt_dark_file"]
    use_fake_flat = cfg["recon_config"]["use_fake_flat"]
    use_fake_dark = cfg["recon_config"]["use_fake_dark"]
    fake_flat_val = cfg["data_params"]["fake_flat_val"]
    fake_dark_val = cfg["data_params"]["fake_dark_val"]
    fake_flat_roi = cfg["data_params"]["fake_flat_roi"]
    ds_use = cfg["recon_config"]["use_ds"]
    if "hardware_trig_type" in cfg["file_params"].keys():
        hdtrg = cfg["file_params"]["hardware_trig_type"]
    else:
        hdtrg = False

    if flat_nm is None:
        flat_nm = fn
    if dark_nm is None:
        dark_nm = fn

    data_dim = cfg["file_params"]["info_reader"](
        fn, dtype="data", cfg=cfg["file_params"]["io_confg"]
    )

    theta = reader(fn, dtype="theta", sli=[None], cfg=io_cfg).astype(np.float32)
    if hdtrg:
        idx = np.ones(data_dim[0], dtype=bool)
        theta = theta[: data_dim[0]]
    else:
        idx = rm_redundant(theta)
        theta = theta[idx]
        if data_dim[0] > theta.shape[0]:
            idx = np.concatenate(
                (idx, np.zeros(data_dim[0] - theta.shape[0], dtype=bool))
            )

    if mean_axis is None:
        if ds_use:
            if cfg["recon_config"]["recon_type"] == "Trial Cent":
                data = ds_data_reader(cfg, dtype="data")[idx, :, col_s:col_e]
                if use_fake_flat:
                    if fake_flat_roi is None:
                        white = fake_flat_val * np.ones(
                            [1, data.shape[1], data.shape[2]]
                        ).astype(np.float32)
                    else:
                        white = data[
                            :,
                            fake_flat_roi[0] : fake_flat_roi[1],
                            fake_flat_roi[2] : fake_flat_roi[3],
                        ].mean(axis=(1, 2), keepdims=True) * np.ones(
                            [1, data.shape[1], data.shape[2]]
                        ).astype(
                            np.float32
                        )
                else:
                    white = ds_data_reader(cfg, dtype="flat")[:, :, col_s:col_e]

                if use_fake_dark:
                    dark = fake_dark_val * np.ones(
                        [1, data.shape[1], data.shape[2]]
                    ).astype(np.float32)
                else:
                    dark = ds_data_reader(cfg, dtype="dark")[:, :, col_s:col_e]
            else:
                data = ds_data_reader(cfg, dtype="data")[idx, sli_s:sli_e, col_s:col_e]
                if use_fake_flat:
                    if fake_flat_roi is None:
                        white = fake_flat_val * np.ones(
                            [1, data.shape[1], data.shape[2]]
                        ).astype(np.float32)
                    else:
                        white = data[
                            :,
                            fake_flat_roi[0] : fake_flat_roi[1],
                            fake_flat_roi[2] : fake_flat_roi[3],
                        ].mean(axis=(1, 2), keepdims=True) * np.ones(
                            [1, data.shape[1], data.shape[2]]
                        ).astype(
                            np.float32
                        )
                else:
                    white = ds_data_reader(cfg, dtype="flat")[
                        :, sli_s:sli_e, col_s:col_e
                    ]
                if use_fake_dark:
                    dark = fake_dark_val * np.ones(
                        [1, data.shape[1], data.shape[2]]
                    ).astype(np.float32)
                else:
                    dark = ds_data_reader(cfg, dtype="dark")[
                        :, sli_s:sli_e, col_s:col_e
                    ]
        else:
            data = reader(
                fn, dtype="data", sli=[None, [sli_s, sli_e], [col_s, col_e]], cfg=io_cfg
            ).astype(np.float32)[idx]

            if use_fake_flat:
                if fake_flat_roi is None:
                    white = fake_flat_val * np.ones(
                        [1, data.shape[1], data.shape[2]], dtype=np.float32
                    )
                else:
                    white = data[
                        :,
                        fake_flat_roi[0] : fake_flat_roi[1],
                        fake_flat_roi[2] : fake_flat_roi[3],
                    ].mean(axis=(1, 2), keepdims=True) * np.ones(
                        [1, data.shape[1], data.shape[2]], dtype=np.float32
                    )
            else:
                white = reader(
                    flat_nm,
                    dtype="flat",
                    sli=[None, [sli_s, sli_e], [col_s, col_e]],
                    cfg=io_cfg,
                ).astype(np.float32)

            if use_fake_dark:
                dark = fake_dark_val * np.ones(
                    [1, data.shape[1], data.shape[2]], dtype=np.float32
                )
            else:
                dark = reader(
                    dark_nm,
                    dtype="dark",
                    sli=[None, [sli_s, sli_e], [col_s, col_e]],
                    cfg=io_cfg,
                ).astype(np.float32)
    else:
        col_s = cfg["data_params"]["wedge_col_s"]
        col_e = cfg["data_params"]["wedge_col_e"]
        if ds_use:
            if cfg["recon_config"]["recon_type"] == "Trial Cent":
                data = ds_data_reader(cfg, dtype="data")[idx, :, col_s:col_e]
                if use_fake_flat:
                    if fake_flat_roi is None:
                        white = fake_flat_val * np.ones(
                            [data.shape[1], data.shape[2]]
                        ).astype(np.float32)
                    else:
                        white = data[
                            :,
                            fake_flat_roi[0] : fake_flat_roi[1],
                            fake_flat_roi[2] : fake_flat_roi[3],
                        ].mean(axis=(1, 2), keepdims=True) * np.ones(
                            [data.shape[1], data.shape[2]]
                        ).astype(
                            np.float32
                        )
                else:
                    white = (
                        ds_data_reader(cfg, dtype="flat")[:, :, col_s:col_e]
                        .mean(axis=0)
                        .astype(np.float32)
                    )

                if use_fake_dark:
                    dark = fake_dark_val * np.ones(
                        [data.shape[1], data.shape[2]]
                    ).astype(np.float32)
                else:
                    dark = (
                        ds_data_reader(cfg, dtype="dark")[:, :, col_s:col_e]
                        .mean(axis=0)
                        .astype(np.float32)
                    )
                data[:] = (data - dark[np.newaxis, :]) / (
                    white[np.newaxis, :] - dark[np.newaxis, :]
                )[:]
                data[np.isinf(data)] = 0
                data[np.isnan(data)] = 0
                data = data.mean(axis=mean_axis).astype(np.float32)
            else:
                data = ds_data_reader(cfg, dtype="data")[idx, sli_s:sli_e, col_s:col_e]
                if use_fake_flat:
                    if fake_flat_roi is None:
                        white = fake_flat_val * np.ones(
                            [data.shape[1], data.shape[2]]
                        ).astype(np.float32)
                    else:
                        white = data[
                            :,
                            fake_flat_roi[0] : fake_flat_roi[1],
                            fake_flat_roi[2] : fake_flat_roi[3],
                        ].mean(axis=(1, 2), keepdims=True) * np.ones(
                            [data.shape[1], data.shape[2]]
                        ).astype(
                            np.float32
                        )
                else:
                    white = (
                        ds_data_reader(cfg, dtype="flat")[:, sli_s:sli_e, col_s:col_e]
                        .mean(axis=0)
                        .astype(np.float32)
                    )

                if use_fake_dark:
                    dark = fake_dark_val * np.ones(
                        [data.shape[1], data.shape[2]]
                    ).astype(np.float32)
                else:
                    dark = (
                        ds_data_reader(cfg, dtype="dark")[:, sli_s:sli_e, col_s:col_e]
                        .mean(axis=0)
                        .astype(np.float32)
                    )
                data[:] = (data - dark[np.newaxis, :]) / (
                    white[np.newaxis, :] - dark[np.newaxis, :]
                )[:]
                data[np.isinf(data)] = 0
                data[np.isnan(data)] = 0
                data = data.mean(axis=mean_axis).astype(np.float32)
        else:
            data = reader(
                fn, dtype="data", sli=[None, [sli_s, sli_e], [col_s, col_e]], cfg=io_cfg
            ).astype(np.float32)[idx]
            if use_fake_flat:
                white = fake_flat_val * np.ones(
                    [data.shape[1], data.shape[2]], dtype=np.float32
                )
            else:
                white = (
                    reader(
                        flat_nm,
                        dtype="flat",
                        sli=[None, [sli_s, sli_e], [col_s, col_e]],
                        cfg=io_cfg,
                    )
                    .mean(axis=0)
                    .astype(np.float32)
                )

            if use_fake_dark:
                dark = fake_dark_val * np.ones(
                    [data.shape[1], data.shape[2]], dtype=np.float32
                )
            else:
                dark = (
                    reader(
                        dark_nm,
                        dtype="dark",
                        sli=[None, [sli_s, sli_e], [col_s, col_e]],
                        cfg=io_cfg,
                    )
                    .mean(axis=0)
                    .astype(np.float32)
                )
            data[:] = (data - dark[np.newaxis, :]) / (
                white[np.newaxis, :] - dark[np.newaxis, :]
            )[:]
            data[np.isinf(data)] = 0
            data[np.isnan(data)] = 0
            data = data.mean(axis=mean_axis).astype(np.float32)
    gc.collect()
    return data, white, dark, theta


def read_normalized_proj(idx, cfg, roi="quad"):
    dim_info = cfg["file_params"]["info_reader"]
    reader = cfg["file_params"]["reader"]
    io_cfg = cfg["file_params"]["io_confg"]
    flat_name = cfg["file_params"]["alt_flat_file"]
    dark_name = cfg["file_params"]["alt_dark_file"]
    use_fake_flat = cfg["recon_config"]["use_fake_flat"]
    use_fake_dark = cfg["recon_config"]["use_fake_dark"]
    fake_flat_val = cfg["data_params"]["fake_flat_val"]
    fake_dark_val = cfg["data_params"]["fake_dark_val"]
    fake_flat_roi = cfg["data_params"]["fake_flat_roi"]
    ds_use = cfg["recon_config"]["use_ds"]
    ds = 1.0 / cfg["data_params"]["downsample"]

    fn, _ = get_file(cfg)
    img_shape = np.array(dim_info(fn, dtype="data", cfg=io_cfg))

    img_shape[1:] = binning(img_shape[1:], ds)
    if roi is None:
        roi = np.s_[:, :]
    elif roi == "quad":
        roi = np.s_[
            int(img_shape[1] / 4) : (img_shape[1] - int(img_shape[1] / 4)),
            int(img_shape[2] / 4) : (img_shape[2] - int(img_shape[2] / 4)),
        ]

    if flat_name is None:
        flat_name = fn
    if dark_name is None:
        dark_name = fn

    if ds_use:
        data = rescale(
            reader(fn, dtype="data", sli=[idx, None, None], cfg=io_cfg),
            [ds, ds],
            order=4,
            mode="edge",
            anti_aliasing=True,
        ).astype(np.float32)

        if use_fake_flat:
            if fake_flat_roi is None:
                white = fake_flat_val * np.ones(data.shape, dtype=np.float32)
            else:
                white = data[
                    idx,
                    fake_flat_roi[0] : fake_flat_roi[1],
                    fake_flat_roi[2] : fake_flat_roi[3],
                ].mean() * np.ones(data.shape, dtype=np.float32)
        else:
            white = (
                rescale(
                    reader(flat_name, dtype="flat", sli=[None, None, None], cfg=io_cfg),
                    [1, ds, ds],
                    order=4,
                    mode="edge",
                    anti_aliasing=True,
                )
                .mean(axis=0)
                .astype(np.float32)
            )

        if use_fake_dark:
            dark = fake_dark_val * np.ones(data.shape, dtype=np.float32)
        else:
            dark = (
                rescale(
                    reader(dark_name, dtype="dark", sli=[None, None, None], cfg=io_cfg),
                    [1, ds, ds],
                    order=4,
                    mode="edge",
                    anti_aliasing=True,
                )
                .mean(axis=0)
                .astype(np.float32)
            )
    else:
        data = reader(fn, dtype="data", sli=[idx, None, None], cfg=io_cfg).astype(
            np.float32
        )

        if use_fake_flat:
            if fake_flat_roi is None:
                white = fake_flat_val * np.ones(data.shape, dtype=np.float32)
            else:
                white = data[
                    idx,
                    fake_flat_roi[0] : fake_flat_roi[1],
                    fake_flat_roi[2] : fake_flat_roi[3],
                ].mean() * np.ones(data.shape, dtype=np.float32)
        else:
            white = (
                reader(flat_name, dtype="flat", sli=[None, None, None], cfg=io_cfg)
                .mean(axis=0)
                .astype(np.float32)
            )

        if use_fake_dark:
            dark = fake_dark_val * np.ones(data.shape, dtype=np.float32)
        else:
            dark = (
                reader(dark_name, dtype="dark", sli=[None, None, None], cfg=io_cfg)
                .mean(axis=0)
                .astype(np.float32)
            )

    proj = -np.log(np.squeeze((data - dark) / (white - dark)))
    proj[np.isnan(proj)] = 0
    proj[np.isinf(proj)] = 0
    gc.collect()
    return proj[roi]


def retrieve_phase(
    data, pixel_size=6.5e-5, dist=15, energy=35, alpha=1e-2, pad=True, filter="paganin"
):
    if filter == "paganin":
        data[:] = tomopy.prep.phase.retrieve_phase(
            data, pixel_size=pixel_size, dist=dist, energy=energy, alpha=alpha, pad=pad
        )[:]
    elif filter == "bronnikov":
        data[:] = (1 - data)[:]
        data[:] = tomopy.prep.phase.retrieve_phase(
            data, pixel_size=pixel_size, dist=dist, energy=energy, alpha=alpha, pad=pad
        )[:]
    return data


def rm_redundant(ang):
    dang = np.diff(ang, prepend=0)
    idx = dang > 0.01
    if np.argmax(idx) > 0:
        idx[np.argmax(idx) - 1] = True
    return idx


def run_engine(sav_rec=True, **kwargs):
    """
    kwargs: dictionary
        This is the reconstruction configuration dictionary tomo_recon_param_dict
        input from tomo_recon_gui
    """
    if kwargs["data_params"]["downsample"] == 1:
        kwargs["recon_config"]["use_ds"] = False
    else:
        kwargs["recon_config"]["use_ds"] = True

    if "use_ang_corr" in kwargs["recon_config"].keys():
        if not kwargs["recon_config"]["use_ang_corr"]:
            kwargs["data_params"]["theta_offset"] = 0
    else:
        kwargs["recon_config"]["use_ang_corr"] = False
        kwargs["data_params"]["theta_offset"] = 0

    if kwargs["recon_config"]["recon_type"] == "Trial Cent":
        file_raw_fn, file_recon_template = get_file(kwargs)
        data, white, dark, theta = read_data(kwargs)
        theta += kwargs["data_params"]["theta_offset"]
        theta = theta * np.pi / 180.0
        dim = data.shape
        data = preproc_data(
            data, white, dark, theta, kwargs, ref_bad_angs=None, ref_angs=None
        )

        if sav_rec:
            overwrite_dir(kwargs["file_params"]["data_center_dir"])
            write_center(
                data[:, int(dim[1] / 2) - 1 : int(dim[1] / 2) + 1, :],
                theta,
                dpath=kwargs["file_params"]["data_center_dir"],
                cen_range=(
                    kwargs["data_params"]["cen_win_s"],
                    (
                        kwargs["data_params"]["cen_win_s"]
                        + kwargs["data_params"]["cen_win_w"]
                    ),
                    0.5,
                ),
                mask=kwargs["recon_config"]["use_mask"],
                ratio=kwargs["data_params"]["mask_ratio"],
                algorithm=(
                    kwargs["alg_params"]["algorithm"]
                    if (kwargs["alg_params"]["algorithm"] != "astra")
                    else tomopy.astra
                ),
                **(translate_params(kwargs["alg_params"]["params"])),
            )
        else:
            data_recon = trial_center_stack(
                data[:, [int(dim[1] / 2)], :],
                theta,
                cen_range=(
                    kwargs["data_params"]["cen_win_s"],
                    (
                        kwargs["data_params"]["cen_win_s"]
                        + kwargs["data_params"]["cen_win_w"]
                    ),
                    0.5,
                ),
                mask=kwargs["recon_config"]["use_mask"],
                ratio=kwargs["data_params"]["mask_ratio"],
                algorithm=(
                    kwargs["alg_params"]["algorithm"]
                    if (kwargs["alg_params"]["algorithm"] != "astra")
                    else tomopy.astra
                ),
                **(translate_params(kwargs["alg_params"]["params"])),
            )
            return data_recon

        rec_use_logging = False
        if rec_use_logging:
            fout = os.path.join(
                os.path.dirname(file_raw_fn),
                "".join(os.path.basename(file_raw_fn).split(".")[:-1])
                + "_finding_cneter_log.txt",
            )
            with open(fout, "w") as fo:
                for k, v in kwargs.items():
                    fo.write(str(k) + ": " + str(v) + "\n\n")
        print("trial center recon is done!")
        return 0
    else:
        state = 1
        file_raw_fn, file_recon_template = get_file(kwargs)

        dim = list(
            kwargs["file_params"]["info_reader"](
                file_raw_fn, dtype="data", cfg=kwargs["file_params"]["io_confg"]
            )
        )
        if kwargs["data_params"]["sli_s"] < 0:
            kwargs["data_params"]["sli_s"] = 0
        if kwargs["data_params"]["sli_e"] > dim[1]:
            kwargs["data_params"]["sli_e"] = dim[1]

        if kwargs["data_params"]["chunk_sz"] >= int((
            kwargs["data_params"]["sli_e"] - kwargs["data_params"]["sli_s"]
        ) / kwargs["data_params"]["downsample"]):
            kwargs["data_params"]["chunk_sz"] = int((
                kwargs["data_params"]["sli_e"] - kwargs["data_params"]["sli_s"]
            ) / kwargs["data_params"]["downsample"])
            num_chunk = 1
        else:
            num_chunk = (
                int(
                    (kwargs["data_params"]["sli_e"] - kwargs["data_params"]["sli_s"])
                    / (
                        kwargs["data_params"]["chunk_sz"]
                        - 2 * kwargs["data_params"]["margin"]
                    ) 
                    / kwargs["data_params"]["downsample"]
                )
                + 1
            )
            kwargs["data_params"]["chunk_sz"] = int(
                kwargs["data_params"]["chunk_sz"] 
                * kwargs["data_params"]["downsample"])
            

        # do data downsampling on the entire dataset
        tem_cfg = deepcopy(kwargs)
        if tem_cfg["recon_config"]["use_ds"]:
            ds = 1.0 / tem_cfg["data_params"]["downsample"]
            dim[1:] = binning(dim[1:], ds)
            tem_cfg["data_params"]["sli_s"] = 0
            tem_cfg["data_params"]["sli_e"] = dim[1]
            data, white, dark, theta = read_data(tem_cfg)
            theta += kwargs["data_params"]["theta_offset"]
            theta = theta * np.pi / 180
            data[:] = preproc_data(
                data, white, dark, theta, tem_cfg, ref_bad_angs=None, ref_angs=None
            )[:]

        ds_ss = 0  # slice starting index in the dataset for the recon to be saved
        for ii in range(num_chunk):
            try:
                if ii == 0:
                    sli_start = kwargs["data_params"]["sli_s"]
                    sli_end = (
                        kwargs["data_params"]["sli_s"]
                        + kwargs["data_params"]["chunk_sz"]
                    )
                else:
                    sli_start = kwargs["data_params"]["sli_s"] + ii * (
                        kwargs["data_params"]["chunk_sz"]
                        - 2 * kwargs["data_params"]["margin"]
                    )
                    sli_end = sli_start + kwargs["data_params"]["chunk_sz"]
                    if sli_end > kwargs["data_params"]["sli_e"]:
                        sli_end = kwargs["data_params"]["sli_e"]
                    if sli_end > dim[1]:
                        sli_end = dim[1]
                tem_cfg["data_params"]["sli_s"] = sli_start
                tem_cfg["data_params"]["sli_e"] = sli_end
                if (sli_end - sli_start) <= tem_cfg["data_params"]["margin"]:
                    print("skip")
                    break
                else:
                    if tem_cfg["recon_config"]["use_ds"]:
                        data_recon = tomopy.recon(
                            data[:, sli_start:sli_end, :],
                            theta,
                            center=tem_cfg["data_params"]["rot_cen"],
                            algorithm=(
                                tem_cfg["alg_params"]["algorithm"]
                                if (tem_cfg["alg_params"]["algorithm"] != "astra")
                                else tomopy.astra
                            ),
                            **(translate_params(tem_cfg["alg_params"]["params"])),
                        )
                    else:
                        data, white, dark, theta = read_data(tem_cfg)
                        theta += kwargs["data_params"]["theta_offset"]
                        theta = theta * np.pi / 180

                        data[:] = preproc_data(
                            data,
                            white,
                            dark,
                            theta,
                            tem_cfg,
                            ref_bad_angs=None,
                            ref_angs=None,
                        )[:]

                        data_recon = tomopy.recon(
                            data,
                            theta,
                            center=tem_cfg["data_params"]["rot_cen"],
                            algorithm=(
                                tem_cfg["alg_params"]["algorithm"]
                                if (tem_cfg["alg_params"]["algorithm"] != "astra")
                                else tomopy.astra
                            ),
                            **(translate_params(tem_cfg["alg_params"]["params"])),
                        )

                    if tem_cfg["recon_config"]["use_mask"]:
                        data_recon = tomopy.circ_mask(
                            data_recon, 0, ratio=tem_cfg["data_params"]["mask_ratio"]
                        )

                    if sav_rec:
                        if tem_cfg["recon_config"]["recon_type"] == "Vol Recon":
                            tif_seq_writer(
                                file_recon_template,
                                data_recon[
                                    int(tem_cfg["data_params"]["margin"]) : (
                                        sli_end
                                        - sli_start
                                        - int(tem_cfg["data_params"]["margin"])
                                    )
                                ],
                                axis=0,
                                ids=sli_start + int(tem_cfg["data_params"]["margin"]),
                                overwrite=True,
                            )
                        elif tem_cfg["recon_config"]["recon_type"] == "XANES3D Tomo":
                            rec_roi = np.array(tem_cfg["aut_xns3d_pars"]["rec_roi"])

                            with h5py.File(
                                tem_cfg["aut_xns3d_pars"]["xanes3d_sav_trl_reg_fn"], "a"
                            ) as f:
                                g3 = f[tem_cfg["aut_xns3d_pars"]["xanes3d_h5_ds_path"]]
                                ds_se = (
                                    ds_ss
                                    + sli_end
                                    - sli_start
                                    - 2 * int(tem_cfg["data_params"]["margin"])
                                )
                                g3[
                                    tem_cfg["data_params"]["scan_id"]
                                    - tem_cfg["aut_xns3d_pars"]["scn_id_lst"][0],
                                    ds_ss:ds_se,
                                    ...,
                                ] = data_recon[
                                    int(tem_cfg["data_params"]["margin"]) : (
                                        sli_end
                                        - sli_start
                                        - int(tem_cfg["data_params"]["margin"])
                                    ),
                                    rec_roi[0] : rec_roi[1],
                                    rec_roi[2] : rec_roi[3],
                                ].astype(
                                    np.float32
                                )
                                ds_ss = ds_se
                        print(
                            f"chunk {ii} reconstruction is saved \n{sli_start} : {sli_end}"
                        )
                    else:
                        return data_recon
                    print(
                        f"reconstruction of scan #{kwargs['data_params']['scan_id']} finished at {time.asctime()}"
                    )
            except Exception as e:
                state = 0
                print(type(e))
                print(e.args)
        if state == 1:
            print("Reconstruction finished!")
            return 0
        else:
            print("Reconstruction is terminated due to error.")
            return -1


def run_filter(data, flt):
    flt_name = flt["filter_name"]
    params = translate_params(flt["params"])
    print("running", flt_name)
    if flt_name == "denoise: wiener":
        psfw = int(params["psf"])
        params["psf"] = np.ones([psfw, psfw]) / (psfw**2)
        for ii in range(data.shape[0]):
            data[ii] = skr.wiener(
                data[ii],
                params["psf"],
                params["balance"],
                reg=params["reg"],
                is_real=params["is_real"],
                clip=params["clip"],
            )[:]
    elif flt_name == "denoise: median":
        data[:] = median(int(params["size x"]), data)[:]
    elif flt_name == "denoise: unsupervised_wiener":
        psfw = int(params["psf"])
        params["psf"] = np.ones([psfw, psfw]) / (psfw**2)
        for ii in range(data.shape[0]):
            data[ii], _ = skr.unsupervised_wiener(
                data[ii],
                params["psf"],
                reg=params["reg"],
                user_params=params["user_params"],
                is_real=params["is_real"],
                clip=params["clip"],
            )[:]
    elif flt_name == "denoise: denoise_nl_means":
        for ii in range(data.shape[0]):
            data[ii] = skr.denoise_nl_means(data[ii], **params, preserve_range=None)[:]
    elif flt_name == "denoise: denoise_tv_bregman":
        for ii in range(data.shape[0]):
            data[ii] = skr.denoise_tv_bregman(
                data[ii],
                params["weight"],
                max_iter=params["max_iter"],
                eps=params["eps"],
                isotropic=params["isotropic"],
                multichannel=params["multichannel"],
            )[:]
    elif flt_name == "denoise: denoise_tv_chambolle":
        for ii in range(data.shape[0]):
            data[ii] = skr.denoise_tv_chambolle(
                data[ii],
                params["weight"],
                n_iter_max=params["n_iter_max"],
                eps=params["eps"],
                multichannel=params["multichannel"],
            )[:]
    elif flt_name == "denoise: denoise_bilateral":
        for ii in range(data.shape[0]):
            data[ii] = skr.denoise_bilateral(data[ii], **params)[:]
    elif flt_name == "denoise: denoise_wavelet":
        for ii in range(data.shape[0]):
            data[ii] = skr.denoise_wavelet(data[ii], **params)[:]
    elif flt_name == "flatting bkg":
        data[:] = tomopy.prep.normalize.normalize_bg(data, air=params["air"])[:]
    elif flt_name == "stripe_removal: vo":
        for key in params.keys():
            if key in ["la_size", "sm_size"]:
                params[key] = int(params[key])
        data[:] = tomopy.prep.stripe.remove_all_stripe(data, **params)[:]
    elif flt_name == "stripe_removal: ti":
        data[:] = tomopy.prep.stripe.remove_stripe_ti(data, **params)[:]
    elif flt_name == "stripe_removal: sf":
        params["size"] = int(params["size"])
        data[:] = tomopy.prep.stripe.remove_stripe_sf(data, **params)[:]
    elif flt_name == "stripe_removal: fw":
        params["level"] = int(params["level"])
        data[:] = tomopy.prep.stripe.remove_stripe_fw(data, **params)[:]
    elif flt_name == "phase retrieval":
        data[:] = retrieve_phase(data, **params)[:]
    print(f"{flt_name} finished!")
    return data


def save_debug(debug_dir, debug_fn, data):
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    tifffile.imsave(os.path.join(debug_dir, debug_fn), data.astype(np.float32))


def sort_wedge(data, angs, ref_bad_angs, ref_angs, sli_start, sli_end, padval=0):
    f = sci.interp1d(
        ref_angs,
        ref_bad_angs[:, sli_start:sli_end],
        axis=0,
        bounds_error=False,
        fill_value=1,
    )
    bad_angs = f(angs) > 0.1
    data[bad_angs, :] = padval
    return data


def translate_params(params):
    for key, param in params.items():
        if param == "None":
            params[key] = None
        elif param == "True":
            params[key] = True
        elif param == "False":
            params[key] = False
    return params


def overwrite_dir(path):
    if os.path.isdir(path):
        if os.path.exists(path):
            shutil.rmtree(path)
            os.makedirs(path)
        else:
            os.makedirs(path)
        return 0
    else:
        return -1


def write_center(
    tomo,
    theta,
    dpath=Path("tmp/center"),
    cen_range=None,
    ind=None,
    mask=False,
    ratio=1.0,
    sinogram_order=False,
    algorithm="gridrec",
    filter_name="parzen",
    **kwargs,
):
    """
    Save images reconstructed with a range of rotation centers.

    Helps finding the rotation center manually by visual inspection of
    images reconstructed with a set of different centers.The output
    images are put into a specified folder and are named by the
    center position corresponding to the image.

    Parameters
    ----------
    tomo : ndarray
        3D tomographic data.
    theta : array
        Projection angles in radian.
    dpath : str, optional
        Folder name to save output images.
    cen_range : list, optional
        [start, end, step] Range of center values.
    ind : int, optional
        Index of the slice to be used for reconstruction.
    mask : bool, optional
        If ``True``, apply a circular mask to the reconstructed image to
        limit the analysis into a circular region.
    ratio : float, optional
        The ratio of the radius of the circular mask to the edge of the
        reconstructed image.
    sinogram_order: bool, optional
        Determins whether data is a stack of sinograms (True, y-axis first axis)
        or a stack of radiographs (False, theta first axis).
    algorithm : {str, function}
        One of the following string values.

        'art'
            Algebraic reconstruction technique :cite:`Kak:98`.
        'bart'
            Block algebraic reconstruction technique.
        'fbp'
            Filtered back-projection algorithm.
        'gridrec'
            Fourier grid reconstruction algorithm :cite:`Dowd:99`,
            :cite:`Rivers:06`.
        'mlem'
            Maximum-likelihood expectation maximization algorithm
            :cite:`Dempster:77`.
        'osem'
            Ordered-subset expectation maximization algorithm
            :cite:`Hudson:94`.
        'ospml_hybrid'
            Ordered-subset penalized maximum likelihood algorithm with
            weighted linear and quadratic penalties.
        'ospml_quad'
            Ordered-subset penalized maximum likelihood algorithm with
            quadratic penalties.
        'pml_hybrid'
            Penalized maximum likelihood algorithm with weighted linear
            and quadratic penalties :cite:`Chang:04`.
        'pml_quad'
            Penalized maximum likelihood algorithm with quadratic penalty.
        'sirt'
            Simultaneous algebraic reconstruction technique.
        'tv'
            Total Variation reconstruction technique
            :cite:`Chambolle:11`.
        'grad'
            Gradient descent method with a constant step size
        'tikh'
            Tikhonov regularization with identity Tikhonov matrix.


    filter_name : str, optional
        Name of the filter for analytic reconstruction.

        'none'
            No filter.
        'shepp'
            Shepp-Logan filter (default).
        'cosine'
            Cosine filter.
        'hann'
            Cosine filter.
        'hamming'
            Hamming filter.
        'ramlak'
            Ram-Lak filter.
        'parzen'
            Parzen filter.
        'butterworth'
            Butterworth filter.
        'custom'
            A numpy array of size `next_power_of_2(num_detector_columns)/2`
            specifying a custom filter in Fourier domain. The first element
            of the filter should be the zero-frequency component.
        'custom2d'
            A numpy array of size `num_projections*next_power_of_2(num_detector_columns)/2`
            specifying a custom angle-dependent filter in Fourier domain. The first element
            of each filter should be the zero-frequency component.
    """
    tomo = tomopy.util.dtype.as_float32(tomo)
    theta = tomopy.util.dtype.as_float32(theta)

    if sinogram_order:
        dy, dt, dx = tomo.shape
    else:
        dt, dy, dx = tomo.shape
    if ind is None:
        ind = dy // 2
    if cen_range is None:
        center = np.arange(dx / 2 - 5, dx / 2 + 5, 0.5)
    else:
        center = np.arange(*cen_range)

    stack = tomopy.util.dtype.empty_shared_array((len(center), dt, dx))

    for m in range(center.size):
        if sinogram_order:
            stack[m] = tomo[ind]
        else:
            stack[m] = tomo[:, ind, :]

    # Reconstruct the same slice with a range of centers.
    rec = tomopy.recon(
        stack,
        theta,
        center=center,
        sinogram_order=True,
        algorithm=algorithm,
        nchunk=1,
        **kwargs,
    )

    # Apply circular mask.
    if mask is True:
        rec = tomopy.circ_mask(rec, axis=0, ratio=ratio)

    # Save images to a temporary folder.
    dpath = os.path.abspath(dpath)
    if not os.path.exists(dpath):
        os.makedirs(dpath)

    for m in range(len(center)):
        tomopy.util.misc.write_tiff(
            data=rec[m], fname=dpath, digit="{0:.2f}".format(center[m])
        )


def tv_l1_img(cfg, img):
    if cfg["use_norm"]:
        if not isinstance(cfg["gm"], np.ndarray):
            cfg["gm"] = img != 0
            cfg["gm"][:] = binary_erosion(cfg["gm"], iterations=3)[:]
        pnts = cfg["gm"].sum()
    else:
        pnts = 1

    if cfg["use_flt"]:
        return (
            (
                np.abs(np.diff(gf(img, cfg["smth_krnl"]), axis=0, prepend=1))
                + np.abs(np.diff(gf(img, cfg["smth_krnl"]), axis=1, prepend=1))
            )
            * cfg["gm"]
        ).sum() / pnts
    else:
        return (
            (
                np.abs(np.diff(img, axis=0, prepend=1))
                + np.abs(np.diff(img, axis=1, prepend=1))
            )
            * cfg["gm"]
        ).sum() / pnts


def tomo_auto_center_reg(rec, meth="TVL1", reg_cfg={}, cen_range=[]):
    print(f"using registration method: {meth}")
    print(f"registration config: {reg_cfg}")
    cen_lst = np.arange(*cen_range)

    if meth.upper() == "TVL1":
        with mp.Pool(N_CPU) as pool:
            rlt = pool.map(
                partial(tv_l1_img, reg_cfg[meth]),
                [rec[jj] for jj in range(rec.shape[0])],
            )
        pool.close()
        pool.join()

        tvl = []
        for jj in range(len(rlt)):
            tvl.append(rlt[jj])
        idx = np.array(tvl).argmin() + 1
        try:
            best_cen = cen_lst[idx]
        except:
            print(
                "Cannot find rotation center. Please try to adjust the ROI set in 'Ref Slice and ROI for Auto Cent' and try again"
            )
            return None, None, None, None
        del rlt
        gc.collect()
    return tvl, idx, best_cen, rec[idx]


def tomo_auto_center(aut_cen_cfg, xns3d_trl_sav=False):
    # kwargs['aut_tomo_pars']['cen_opt']
    # kwargs['aut_tomo_pars']['scn_id_lst']
    # kwargs['aut_tomo_pars']['scn_id_s']
    # kwargs['aut_tomo_pars']['scn_id_e']
    # kwargs['aut_tomo_pars']['reg_mode']
    # kwargs['aut_tomo_pars']['mrtv_knl_sz']
    # kwargs['aut_tomo_pars']['ds_fac']
    # kwargs['aut_tomo_pars']['cen_srch_half_wz']
    # kwargs['aut_tomo_pars']['auto_rec']
    # kwargs['aut_tomo_pars']['rec_all_sli']
    # kwargs['aut_tomo_pars']['use_dflt_ref_reg_roi']
    # kwargs['aut_tomo_pars']['ref_cen_sli']
    # kwargs['aut_tomo_pars']['trial_cen_h5_fn']

    # kwargs['aut_xns3d_pars']['cen_opt']
    # kwargs['aut_xns3d_pars']['rec_dir_tplt']
    # kwargs['aut_xns3d_pars']['rec_fn_tplt']
    # kwargs['aut_xns3d_pars']['ref_scn_cen']
    # kwargs['aut_xns3d_pars']['ref_cen_sli']
    # kwargs['aut_xns3d_pars']['ref_cen_roi']
    # kwargs['aut_xns3d_pars']['rec_roi']
    # kwargs['aut_xns3d_pars']['ref_sli_srch_half_wz']
    # kwargs['aut_xns3d_pars']['ref_cen_srch_half_wz']
    # kwargs['aut_xns3d_pars']['scn_id_lst']
    # kwargs['aut_xns3d_pars']['ref_scn_id']
    # kwargs['aut_xns3d_pars']['scn_id_s']
    # kwargs['aut_xns3d_pars']['scn_id_e']
    # kwargs['aut_xns3d_pars']['reg_mode']
    # kwargs['aut_xns3d_pars']['reg_chnk_sz']
    # kwargs['aut_xns3d_pars']['mrtv_knl_sz']
    # kwargs['aut_xns3d_pars']['reg&rec']
    # kwargs['aut_xns3d_pars']['xanes3d_sav_trl_reg_fn']

    # kwargs['recon_config']['recon_type']
    # kwargs['file_params']['raw_data_top_dir']
    # kwargs['file_params']['data_center_dir']
    # kwargs['file_params']['recon_top_dir']
    # kwargs['file_params']['debug_top_dir']
    # kwargs['file_params']['alt_flat_file']
    # kwargs['file_params']['alt_dark_file']
    # kwargs['file_params']['wedge_ang_auto_det_ref_fn']
    # kwargs['file_params']['io_confg']
    # kwargs['file_params']['reader']
    # kwargs['file_params']['info_reader']
    # kwargs['file_params']['use_struc_h5_reader']
    # kwargs['file_params']['hardware_trig_type']

    # kwargs['data_params']['scan_id']
    # kwargs['data_params']['downsample']
    # kwargs['data_params']['rot_cen']
    # kwargs['data_params']['cen_win_s']
    # kwargs['data_params']['cen_win_w']
    # kwargs['data_params']['sli_s']
    # kwargs['data_params']['sli_e']
    # kwargs['data_params']['col_s']
    # kwargs['data_params']['col_e']
    # kwargs['data_params']['fake_flat_val']
    # kwargs['data_params']['fake_dark_val']
    # kwargs['data_params']["fake_flat_roi"]
    # kwargs['data_params']['chunk_sz']
    # kwargs['data_params']['margin']
    # kwargs['data_params']["blur_kernel"]
    # kwargs['data_params']['zinger_val']
    # kwargs['data_params']['mask_ratio']
    # kwargs['data_params']['wedge_missing_s']
    # kwargs['data_params']['wedge_missing_e']
    # kwargs['data_params']["wedge_col_s"]
    # kwargs['data_params']["wedge_col_e"]
    # kwargs['data_params']['wedge_ang_auto_det_thres']
    # kwargs['data_params']["theta_offset"]

    # kwargs['recon_config']['recon_type']
    # kwargs['recon_config']['use_debug']
    # kwargs['recon_config']['use_alt_flat']
    # kwargs['recon_config']['use_alt_dark']
    # kwargs['recon_config']['use_fake_flat']
    # kwargs['recon_config']['use_fake_dark']
    # kwargs["recon_config"]["use_flat_blur"]
    # kwargs['recon_config']['use_rm_zinger']
    # kwargs['recon_config']['use_mask']
    # kwargs['recon_config']['use_wedge_ang_auto_det']
    # kwargs['recon_config']['is_wedge']
    # kwargs['recon_config']['use_ang_corr']

    # kwargs["flt_params"]
    # kwargs["alg_params"]

    if aut_cen_cfg["data_params"]["downsample"] == 1:
        aut_cen_cfg["recon_config"]["use_ds"] = False
    else:
        aut_cen_cfg["recon_config"]["use_ds"] = True

    if "meth" not in aut_cen_cfg["aut_tomo_pars"]:
        aut_cen_cfg["aut_tomo_pars"]["meth"] = "TVL1"

    reg_cfg = {}
    if aut_cen_cfg["aut_tomo_pars"]["meth"] == "TVL1":
        reg_cfg["TVL1"] = {}
        reg_cfg["TVL1"]["smth_krnl"] = aut_cen_cfg["aut_tomo_pars"]["mrtv_knl_sz"]
        reg_cfg["TVL1"]["gm"] = 1
        reg_cfg["TVL1"]["use_flt"] = True
        reg_cfg["TVL1"]["use_norm"] = False

    scn_lst = get_algn_pair_lst(
        aut_cen_cfg["aut_tomo_pars"]["scn_id_lst"], aut_cen_cfg, ref_id=None
    )
    cen_cfg = deepcopy(aut_cen_cfg)
    # cen_cfg["flt_params"] = {}
    cen_cfg["aut_tomo_pars"]["ref_cen"] = cen_cfg["data_params"]["rot_cen"]

    b = "{date:%Y-%m-%d-%H-%M-%S}".format(date=datetime.now())
    trial_cen_dict_fn = str(
        Path(cen_cfg["file_params"]["raw_data_top_dir"]).joinpath(
            "trial_auto_cen_dict_{}.json".format(b)
        )
    )
    vol_rec_cfg = {}
    tem_rec_cfg = {}

    trl_fn = aut_cen_cfg["aut_tomo_pars"]["trial_cen_h5_fn"]
    if aut_cen_cfg["recon_config"]["is_wedge"]:
        ref_bad_angs, ref_angs = get_dark_angs_all_sli(aut_cen_cfg, data=None)
        ref_angs *= np.pi / 180.0
    else:
        ref_bad_angs, ref_angs = None, None

    if Path(trl_fn).exists():
        os.remove(trl_fn)
    with h5py.File(trl_fn, "w") as f:
        f.create_group("auto_centering")

    for ii in scn_lst:
        with h5py.File(trl_fn, "a") as f:
            g = f["auto_centering"]
            g.create_group(str(ii))

        print(f" finding center for scan {ii} ... ".center(80, "#"))
        cen_cfg["data_params"]["scan_id"] = ii

        sli = cen_cfg["aut_tomo_pars"]["ref_cen_sli"]
        if cen_cfg["aut_tomo_pars"]["use_dflt_ref_reg_roi"]:
            roi = np.s_[:]
        else:
            roi = np.s_[
                :,
                cen_cfg["aut_tomo_pars"]["ref_cen_roi"][0] : cen_cfg["aut_tomo_pars"][
                    "ref_cen_roi"
                ][1],
                cen_cfg["aut_tomo_pars"]["ref_cen_roi"][2] : cen_cfg["aut_tomo_pars"][
                    "ref_cen_roi"
                ][3],
            ]
        print(f"auto centering for scan {ii} uses slice {sli}")

        cen_cfg["data_params"]["sli_s"] = sli - cen_cfg["data_params"]["margin"]
        cen_cfg["data_params"]["sli_e"] = sli + cen_cfg["data_params"]["margin"]

        data, white, dark, theta = read_data(cen_cfg)
        theta = theta * np.pi / 180

        data[:] = preproc_data(
            data,
            white,
            dark,
            theta,
            cen_cfg,
            ref_bad_angs=ref_bad_angs,
            ref_angs=ref_angs,
        )[:]

        fn, _ = get_file(cen_cfg)
        dim = list(
            cen_cfg["file_params"]["info_reader"](
                fn, dtype="data", cfg=cen_cfg["file_params"]["io_confg"]
            )
        )
        if cen_cfg["recon_config"]["use_ds"]:
            ds = 1.0 / cen_cfg["data_params"]["downsample"]
            dim[1:] = binning(dim[1:], ds)

        cen = cen_cfg["aut_tomo_pars"]["ref_cen"]
        print(f"initial guessed center of scan {ii}: {cen}")
        print(f"search half range: {cen_cfg['aut_tomo_pars']['cen_srch_half_wz']}")

        for itr in range(2):
            if itr == 0:
                cen_range = [
                    cen - cen_cfg["aut_tomo_pars"]["cen_srch_half_wz"],
                    cen + cen_cfg["aut_tomo_pars"]["cen_srch_half_wz"],
                    0.5,
                ]
            elif itr == 1:
                cen_range = [
                    cen - 2,
                    cen + 2,
                    0.1,
                ]

            rec = trial_center_stack(
                data[:, [cen_cfg["data_params"]["margin"]], :],
                theta,
                cen_range=cen_range,
                mask=True,
                ratio=0.9 if cen_cfg["aut_tomo_pars"]["use_dflt_ref_reg_roi"] else 1,
                sinogram_order=False,
                algorithm=(
                    cen_cfg["alg_params"]["algorithm"]
                    if (cen_cfg["alg_params"]["algorithm"] != "astra")
                    else tomopy.astra
                ),
                **(translate_params(cen_cfg["alg_params"]["params"])),
            )

            print(f"scan_id: {ii}, itr: {itr}, {cen_range=}")
            tvl, idx, best_cen, rec = tomo_auto_center_reg(
                rec[roi],
                meth=aut_cen_cfg["aut_tomo_pars"]["meth"],
                reg_cfg=reg_cfg,
                cen_range=cen_range,
            )

            if best_cen is None:
                return -1
            else:
                cen = best_cen
                with h5py.File(trl_fn, "a") as f:
                    g = f[f"auto_centering/{str(ii)}"]
                    g0 = g.create_group(f"optimization itr {itr}")
                    g0.create_dataset("tvl", data=tvl)
                    g0.create_dataset("tvl_min_idx", data=idx)
                    g0.create_dataset("best_cen", data=best_cen)
                    g0.create_dataset("trial_rec", data=rec)
                print(f"round #{itr} optimized center of scan {ii}: {cen}")

        cen_cfg["aut_tomo_pars"]["ref_cen"] = cen
        print(f"best center for scan {ii} is {cen}")

        # both vol_rec_cfg and tem_rec_cfg keep original configurations from
        # aut_cen_cfg except of the items below being reset.
        vol_rec_cfg[str(ii)] = deepcopy(aut_cen_cfg)

        vol_rec_cfg[str(ii)]["data_params"]["scan_id"] = ii
        vol_rec_cfg[str(ii)]["data_params"]["rot_cen"] = cen
        vol_rec_cfg[str(ii)]["recon_config"]["recon_type"] = "Vol Recon"
        if aut_cen_cfg["aut_tomo_pars"]["rec_all_sli"]:
            vol_rec_cfg[str(ii)]["data_params"]["sli_s"] = 0
            vol_rec_cfg[str(ii)]["data_params"]["sli_e"] = dim[1]
        else:
            if "aut_xns3d_pars" in aut_cen_cfg.keys():
                vol_rec_cfg[str(ii)]["data_params"]["sli_s"] = max(
                    0,
                    aut_cen_cfg["aut_xns3d_pars"]["rec_roi"][4]
                    - aut_cen_cfg["data_params"]["margin"]
                    - aut_cen_cfg["aut_xns3d_pars"]["ref_sli_srch_half_wz"],
                )
                vol_rec_cfg[str(ii)]["data_params"]["sli_e"] = min(
                    dim[1],
                    aut_cen_cfg["aut_xns3d_pars"]["rec_roi"][5]
                    + aut_cen_cfg["data_params"]["margin"]
                    + aut_cen_cfg["aut_xns3d_pars"]["ref_sli_srch_half_wz"],
                )
            else:
                vol_rec_cfg[str(ii)]["data_params"]["sli_s"] = max(
                    0,
                    aut_cen_cfg["data_params"]["sli_s"]
                    - aut_cen_cfg["data_params"]["margin"],
                )
                vol_rec_cfg[str(ii)]["data_params"]["sli_e"] = min(
                    dim[1],
                    aut_cen_cfg["data_params"]["sli_e"]
                    + aut_cen_cfg["data_params"]["margin"],
                )
        vol_rec_cfg[str(ii)]["file_params"]["trial_cen_dict_fn"] = trial_cen_dict_fn

        tem_rec_cfg[str(ii)] = deepcopy(vol_rec_cfg[str(ii)])
        tem_rec_cfg[str(ii)]["file_params"]["io_confg"]["customized_reader"][
            "user_tomo_reader"
        ] = ""
        tem_rec_cfg[str(ii)]["file_params"]["reader"] = ""
        tem_rec_cfg[str(ii)]["file_params"]["info_reader"] = ""
        tem_rec_cfg[str(ii)]["file_params"]["trial_cen_dict_fn"] = trial_cen_dict_fn
    aut_cen_cfg["file_params"]["trial_cen_dict_fn"] = trial_cen_dict_fn
    with open(trial_cen_dict_fn, "w") as f:
        json.dump(tem_rec_cfg, f, indent=4, separators=(",", ": "))

    if aut_cen_cfg["aut_tomo_pars"]["auto_rec"]:
        # if use_ang_corr, don't do full rec for now
        if "aut_xns3d_pars" in aut_cen_cfg.keys():
            if aut_cen_cfg["aut_xns3d_pars"]["ang_corr"]:
                for ii in vol_rec_cfg.keys():
                    vol_rec_cfg[str(ii)]["data_params"]["sli_s"] = max(
                        0,
                        aut_cen_cfg["aut_tomo_pars"]["ref_cen_sli"]
                        - aut_cen_cfg["data_params"]["margin"]
                        - 2 * aut_cen_cfg["aut_xns3d_pars"]["ref_sli_srch_half_wz"],
                    )
                    vol_rec_cfg[str(ii)]["data_params"]["sli_e"] = min(
                        dim[1],
                        aut_cen_cfg["aut_tomo_pars"]["ref_cen_sli"]
                        + aut_cen_cfg["data_params"]["margin"]
                        + 2 * aut_cen_cfg["aut_xns3d_pars"]["ref_sli_srch_half_wz"],
                    )
        for ii in vol_rec_cfg.keys():
            print(f" reconstructing scan {ii=} ... ".center(80, "#"))
            run_engine(sav_rec=True, **vol_rec_cfg[ii])
        return 0
    else:
        return vol_rec_cfg


def trial_center_stack(
    tomo,
    theta,
    cen_range=None,
    mask=False,
    ratio=1.0,
    sinogram_order=False,
    algorithm="gridrec",
    **alg_pars,
):
    tomo = tomopy.util.dtype.as_float32(tomo)
    theta = tomopy.util.dtype.as_float32(theta)

    if sinogram_order:
        dy, dt, dx = tomo.shape
    else:
        dt, dy, dx = tomo.shape
    if cen_range is None:
        center = np.arange(dx / 2 - 5, dx / 2 + 5, 0.5)
    else:
        center = np.arange(*cen_range)

    nc = len(center)
    stack = tomopy.util.dtype.empty_shared_array((nc, dt, dx))
    rec = tomopy.util.dtype.empty_shared_array((int(dy * nc), dx, dx))

    for ii in range(dy):
        for m in range(center.size):
            if sinogram_order:
                stack[m] = tomo[ii]
            else:
                stack[m] = tomo[:, ii, :]

        # Reconstruct the same slice with a range of centers.
        rec[ii * nc : (ii + 1) * nc] = tomopy.recon(
            stack,
            theta,
            center=center,
            sinogram_order=True,
            algorithm=algorithm,
            nchunk=1,
            **alg_pars,
        )
        # Apply circular mask.
        if mask is True:
            rec[ii * nc : (ii + 1) * nc] = tomopy.circ_mask(
                rec[ii * nc : (ii + 1) * nc], axis=0, ratio=ratio
            )
    return rec


def xanes3d_auto_tomo_rec(kwargs):
    """
    kwargs: dictionary
        This is the reconstruction configuration dictionary
        input from tomo_recon_gui
    """

    if not kwargs["recon_config"]["use_alt_flat"]:
        kwargs["file_params"]["alt_flat_file"] = None
    if not kwargs["recon_config"]["use_alt_dark"]:
        kwargs["file_params"]["alt_dark_file"] = None
    if kwargs["data_params"]["downsample"] == 1:
        kwargs["recon_config"]["use_ds"] = False
    else:
        kwargs["recon_config"]["use_ds"] = True

    aut_cen_cfg = deepcopy(kwargs)
    aut_cen_cfg["aut_xns3d_pars"][
        "xanes3d_h5_ds_path"
    ] = "/registration_results/reg_results/registered_xanes3D"
    reg_rec_cfg = deepcopy(kwargs)
    reg_rec_cfg["aut_xns3d_pars"][
        "xanes3d_h5_ds_path"
    ] = "/registration_results/reg_results/registered_xanes3D"

    rec_roi = np.array(kwargs["aut_xns3d_pars"]["rec_roi"])

    if kwargs["aut_xns3d_pars"]["reg&rec"]:
        with h5py.File(kwargs["aut_xns3d_pars"]["xanes3d_sav_trl_reg_fn"], "a") as f:
            if "/registration_results" in f.keys():
                del f["/registration_results"]
            g1 = f.create_group("registration_results")
            g2 = g1.create_group("reg_results")
            g3 = g2.create_dataset(
                "registered_xanes3D",
                shape=(
                    int(kwargs["aut_xns3d_pars"]["scn_id_e"])
                    - int(kwargs["aut_xns3d_pars"]["scn_id_s"])
                    + 1,
                    rec_roi[5] - rec_roi[4] + 1,
                    rec_roi[1] - rec_roi[0],
                    rec_roi[3] - rec_roi[2],
                ),
                dtype=np.float32,
            )

    # auto centering
    if aut_cen_cfg["aut_xns3d_pars"]["cen_opt"] is None:
        print("tomography reconstructions have been done manually.")
    elif aut_cen_cfg["aut_xns3d_pars"]["cen_opt"].upper() == "ABSOLUTE":
        print(f" auto centering started at {time.asctime()} ".center(120, "$"))
        prep_xns3d_auto_tomo_cfg(aut_cen_cfg)
        success = tomo_auto_center(aut_cen_cfg)
        if success == -1:
            return -1
        print(f" auto centering finished at {time.asctime()} ".center(120, "$"))

    print(f" xanes registration started at {time.asctime()} ".center(120, "$"))
    prep_xns3D_auto_reg_cfg(aut_cen_cfg)
    xr = reg(aut_cen_cfg["auto_reg_cfg"])
    xr.compose_dicts()
    xr.reg_xanes3D_chunk()
    shft_dict = reg.default_3DXANES_best_shift(xr.sav_fn)
    abs_shift_dict, _ = reg.sort_absolute_shift(
        shft_dict["algn_pair_lst"].tolist(),
        shft_dict=shft_dict["shft_by_pair_id"],
        data_type="3D_XANES",
        reg_alg="RIG-MRTV",
    )
    print(f" xanes registration finished at {time.asctime()} ".center(120, "$"))

    print(f" shift correction started at {time.asctime()} ".center(120, "$"))

    slioff = []
    for key in sorted(abs_shift_dict.keys()):
        slioff.append(abs_shift_dict[key]["out_sli_shift"])
    slioff = np.array(slioff)

    if aut_cen_cfg["aut_xns3d_pars"]["cen_opt"] is None:
        pass
    elif aut_cen_cfg["aut_xns3d_pars"]["cen_opt"].upper() == "ABSOLUTE":
        print(f'aut_cen_cfg["file_params"]["trial_cen_dict_fn"]: {aut_cen_cfg["file_params"]["trial_cen_dict_fn"]}')
        with open(aut_cen_cfg["file_params"]["trial_cen_dict_fn"], "r") as f:
            rec_dicts = json.load(f)

        ori_sli_s = rec_dicts[list(rec_dicts.keys())[0]]["data_params"]["sli_s"]
        ori_sli_e = rec_dicts[list(rec_dicts.keys())[0]]["data_params"]["sli_e"]
        
        file_raw_fn, _ = get_file(rec_dicts[list(rec_dicts.keys())[0]])

        dim = list(
            kwargs["file_params"]["info_reader"](
                file_raw_fn, dtype="data", cfg=rec_dicts[list(rec_dicts.keys())[0]]["file_params"]["io_confg"]
            )
        )

        sli_s = max(
            0,
            ori_sli_s
            + slioff.min()
            - rec_dicts[list(rec_dicts.keys())[0]]["data_params"]["margin"],
                    )
        sli_e = min(
            dim[1] - 1,
            ori_sli_e
            + slioff.max() 
            + rec_dicts[list(rec_dicts.keys())[0]]["data_params"]["margin"]
                    )
    
        for key in rec_dicts.keys():
            rec_dicts[key]["auto_reg_cfg"] = aut_cen_cfg["auto_reg_cfg"]
            rec_dicts[key]["file_params"]["reader"] = data_reader(tomo_h5_reader)
            rec_dicts[key]["file_params"]["info_reader"] = data_info(tomo_h5_info)
            rec_dicts[key]["recon_config"]["use_ang_corr"] = (
                True
                if rec_dicts[key]["auto_reg_cfg"]["reg"]["alg"].upper() == "RIG-MRTV"
                else False
            )
            print(
                f" vol recon of scan {key} started at {time.asctime()} ".center(80, "#")
            )
            if rec_dicts[key]["recon_config"]["use_ang_corr"]:
                rec_dicts[key]["data_params"]["theta_offset"] = abs_shift_dict[
                    str(xr.xanes3D_scn_ids.index(int(key))).zfill(3)
                ]["in_sli_rot"]
            rec_dicts[key]["data_params"]["sli_s"] = sli_s
            rec_dicts[key]["data_params"]["sli_e"] = sli_e
            run_engine(sav_rec=True, **rec_dicts[key])

    xr.im_roi = aut_cen_cfg["aut_xns3d_pars"]["rec_roi"]
    xr.apply_xanes3D_chunk_shift(shft_dict["shft_by_pair_id"])
    print(f" shift correction finished at {time.asctime()} ".center(120, "$"))

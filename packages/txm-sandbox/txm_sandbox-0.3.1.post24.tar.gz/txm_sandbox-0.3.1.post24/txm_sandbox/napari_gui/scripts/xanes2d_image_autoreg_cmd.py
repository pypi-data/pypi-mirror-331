import json
from pathlib import Path
import numpy as np
from multiprocess import freeze_support

import h5py
import dask.array as da

from txm_sandbox.utils import xanes_regtools as xr


cfg_fn = Path(__file__).parents[1] / "configs/txm_simple_gui_script_cfg.json"

if __name__ == "__main__":
    with open(cfg_fn, "r") as f:
        with open(json.load(f)["xanes2d_reg"]["cfg_file"], "r") as ft:
            reg_cfg = json.load(ft)

    freeze_support()
    reg = xr.regtools(reg_cfg)
    with h5py.File(reg_cfg["file"]["XANES2D_raw_fn"], "r") as f:
        reg.eng_lst = f["X_eng"][
            reg_cfg["data"]["im_id_s"] : reg_cfg["data"]["im_id_e"]
        ]
        dark = da.from_array(f["img_dark"][:]).squeeze()
        flat = da.from_array(f["img_bkg"][:]).squeeze()
        tem = -np.log((da.from_array(f["img_xanes"]) - dark) / (flat - dark))
        tem[np.isinf(tem)] = 0
        tem[np.isnan(tem)] = 0

        reg.im = tem[
            reg_cfg["data"]["im_id_s"] : reg_cfg["data"]["im_id_e"],
            reg_cfg["data"]["roi"][0] : reg_cfg["data"]["roi"][1],
            reg_cfg["data"]["roi"][2] : reg_cfg["data"]["roi"][3],
        ].compute()
    reg.msk = None

    if reg_cfg["reg_type"] == "auto_reg":
        reg.compose_dicts()
        reg.reg_xanes2D_chunk()

    shift_dict = {}
    with h5py.File(reg_cfg["file"]["sav_fn"], "r") as f:
        _alignment_pairs = f[
            "/trial_registration/trial_reg_parameters/alignment_pairs"
        ][:]
        for ii in range(_alignment_pairs.shape[0]):
            shift_dict["{}".format(ii)] = f[
                "/trial_registration/trial_reg_results/{0}/shift{0}".format(
                    str(ii).zfill(3)
                )
            ][:]

    tmp_dict = {}
    for key in shift_dict.keys():
        tmp_dict[key] = tuple(shift_dict[key])

    with h5py.File(reg_cfg["file"]["XANES2D_raw_fn"], "r") as f:
        reg.eng_lst = f["X_eng"][
            reg_cfg["data"]["im_id_s"] : reg_cfg["data"]["im_id_e"]
        ]
        dark = da.from_array(f["img_dark"][:]).squeeze()
        flat = da.from_array(f["img_bkg"][:]).squeeze()
        tem = -np.log((da.from_array(f["img_xanes"]) - dark) / (flat - dark))
        tem[np.isinf(tem)] = 0
        tem[np.isnan(tem)] = 0

        reg.im = tem[
            reg_cfg["data"]["im_id_s"] : reg_cfg["data"]["im_id_e"],
            :,
            :,
        ].compute()

    reg.apply_xanes2D_chunk_shift(tmp_dict)

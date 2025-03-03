import json
from pathlib import Path
import numpy as np
from multiprocess import freeze_support
from copy import deepcopy

import h5py
import dask.array as da

from txm_sandbox.utils import xanes_regtools as xr
from txm_sandbox.gui.gui_components import (
    check_file_availability,
)
from txm_sandbox.napari_gui.utils.ext_io_lib import mk_aps_cfg
from txm_sandbox.napari_gui.dicts.data_struct_dict import APS_TXM_CFG


cfg_fn = Path(__file__).parents[1] / "configs/txm_simple_gui_script_cfg.json"


def mk_xanes_dataset(reg_cfg):
    top_dir = Path(reg_cfg["file"]["XANES2D_raw_fn"]).parent
    fn_tplt = Path(reg_cfg["file"]["XANES2D_raw_fn"]).stem.rsplit("_", maxsplit=1)[0]
    _cfg = deepcopy(APS_TXM_CFG)
    _2dxanes_cfg = mk_aps_cfg(
        fn_tplt,
        _cfg,
        dtype="APS 2D XANES",
    )["io_data_structure_xanes2D"]
    ids = check_file_availability(
        Path(reg_cfg["file"]["XANES2D_raw_fn"]).parent,
        scan_id=None,
        signature=_2dxanes_cfg["xanes2D_raw_fn_template"],
        return_idx=True,
    )

    if ids:
        ids = sorted(ids)
        eng_lst = []
        data = []
        for ii in ids[
            int(reg_cfg["data"]["im_id_s"]) : int(reg_cfg["data"]["im_id_e"])
        ]:
            with h5py.File(
                top_dir / _2dxanes_cfg["xanes2D_raw_fn_template"].format(ii),
                "r",
            ) as f:
                if f[
                    _2dxanes_cfg["structured_h5_reader"]["io_data_structure"][
                        "eng_path"
                    ]
                ].shape:
                    eng = f[
                        _2dxanes_cfg["structured_h5_reader"]["io_data_structure"][
                            "eng_path"
                        ]
                    ][()][0]
                else:
                    eng = f[
                        _2dxanes_cfg["structured_h5_reader"]["io_data_structure"][
                            "eng_path"
                        ]
                    ][()]
                eng_lst.append(eng)
                dark = f[
                    _2dxanes_cfg["structured_h5_reader"]["io_data_structure"][
                        "dark_path"
                    ]
                ][0].squeeze()
                flat = f[
                    _2dxanes_cfg["structured_h5_reader"]["io_data_structure"][
                        "flat_path"
                    ]
                ][0].squeeze()
                tem = -np.log(
                    (
                        f[
                            _2dxanes_cfg["structured_h5_reader"]["io_data_structure"][
                                "data_path"
                            ]
                        ][0]
                        - dark
                    )
                    / (flat - dark)
                )
                tem[np.isinf(tem)] = 0
                tem[np.isnan(tem)] = 0
                data.append(tem)
            _2dxanes_eng_lst = np.array(eng_lst)
            _2dxanes_data = np.array(data)
    return _2dxanes_eng_lst, _2dxanes_data


if __name__ == "__main__":
    with open(cfg_fn, "r") as f:
        with open(json.load(f)["xanes2d_reg"]["cfg_file"], "r") as ft:
            reg_cfg = json.load(ft)

    freeze_support()
    reg = xr.regtools(reg_cfg)

    _2dxanes_eng_lst, _2dxanes_data = mk_xanes_dataset(reg_cfg)
    reg.eng_lst = _2dxanes_eng_lst
    reg.im = _2dxanes_data

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

    _2dxanes_eng_lst, _2dxanes_data = mk_xanes_dataset(reg_cfg)
    reg.eng_lst = _2dxanes_eng_lst
    reg.im = _2dxanes_data

    reg.apply_xanes2D_chunk_shift(tmp_dict)

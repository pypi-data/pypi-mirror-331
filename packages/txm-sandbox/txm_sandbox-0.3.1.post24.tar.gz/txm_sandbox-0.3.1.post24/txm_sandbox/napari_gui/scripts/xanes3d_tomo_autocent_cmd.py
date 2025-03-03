import json
from pathlib import Path

from txm_sandbox.utils.tomo_recon_tools import (
    xanes3d_auto_tomo_rec,
    prep_xns3d_auto_tomo_cfg,
    tomo_auto_center,
)
from txm_sandbox.utils.io import data_reader, tomo_h5_reader, data_info, tomo_h5_info

cfg_fn = Path(__file__).parents[1] / "configs/txm_simple_gui_script_cfg.json"

with open(cfg_fn, "r") as f:
    with open(json.load(f)["xanes3d_auto_cen"]["cfg_file"], "r") as ft:
        tem = json.load(ft)

if __name__ == "__main__":
    with open(tem["template_file"], "r") as f:
        tem2 = json.load(f)
        params = tem2[list(tem2.keys())[0]]
        params["aut_xns3d_pars"] = tem["aut_xns3d_pars"]
    print(json.dumps(params, indent=4))

    params["file_params"]["reader"] = data_reader(tomo_h5_reader)
    params["file_params"]["info_reader"] = data_info(tomo_h5_info)

    if tem["run_type"] == "autocen":
        params["aut_xns3d_pars"][
            "xanes3d_h5_ds_path"
        ] = "/registration_results/reg_results/registered_xanes3D"
        prep_xns3d_auto_tomo_cfg(params)
        params["aut_tomo_pars"]["auto_rec"] = False
        success = tomo_auto_center(params)
    elif tem["run_type"] == "autocen&rec&reg":
        success = xanes3d_auto_tomo_rec(params)

    if success == -1:
        exit(-1)

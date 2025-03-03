import json
from pathlib import Path

from txm_sandbox.utils.tomo_recon_tools import run_engine
from txm_sandbox.utils.io import data_reader, tomo_h5_reader, data_info, tomo_h5_info

cfg_fn = Path(__file__).parents[1] / "configs/txm_simple_gui_script_cfg.json"


with open(cfg_fn, "r") as f:
    with open(json.load(f)["tomo_batch_recon"]["cfg_file"], "r") as ft:
        tem = json.load(ft)

if __name__ == "__main__":
    for scn_id in list(tem.keys()):
        params = tem[scn_id]
        params["file_params"]["reader"] = data_reader(tomo_h5_reader)
        params["file_params"]["info_reader"] = data_info(tomo_h5_info)
        run_engine(**params)

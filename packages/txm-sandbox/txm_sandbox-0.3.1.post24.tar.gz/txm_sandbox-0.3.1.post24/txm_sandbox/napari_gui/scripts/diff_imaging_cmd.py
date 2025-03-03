import numpy as np
from scipy.ndimage import zoom

from pathlib import Path
import json
import h5py

cfg_fn = Path(__file__).parents[1] / "configs/txm_simple_gui_script_cfg.json"


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()

    with open(cfg_fn, "r") as f:
        diff_data_fn = json.load(f)["diff_imaging"]["cfg_file"]

    proc_diff_imaging_path = "/processed_diff_imaging"
    with h5py.File(diff_data_fn, "a") as f:
        reg_img_path = f[f"/{proc_diff_imaging_path}/proc_parameters/reg_img_path"][()].decode(
            "utf-8"
        )
        diff_img_idx = f[f"/{proc_diff_imaging_path}/proc_parameters/diff_img_idx"][:]
        bin_fact = f[f"/{proc_diff_imaging_path}/proc_parameters/bin_fact"][()]
        diff_img_shape = np.int32(
                np.round(f[f"/{proc_diff_imaging_path}/proc_parameters/img_shape"][:] / bin_fact)
            )
        if f"/{proc_diff_imaging_path}/proc_rlt" in f:
            del f[f"/{proc_diff_imaging_path}/proc_rlt"]
            g0 = f.create_group(f"/{proc_diff_imaging_path}/proc_rlt")
        else:
            g0 = f.create_group(f"/{proc_diff_imaging_path}/proc_rlt")
        g0.create_dataset(
                        "diff_img", shape=(diff_img_shape), dtype=np.float32
                    )

    if len(diff_img_shape) == 2:
        with h5py.File(diff_data_fn, "r+") as f:
            img1 = zoom(f[reg_img_path][diff_img_idx[0], :, :], (1 / bin_fact, 1 / bin_fact))
            img2 = zoom(f[reg_img_path][diff_img_idx[1], :, :], (1 / bin_fact, 1 / bin_fact))
            diff_img = img1 - img2
            _g0 = f[f"/{proc_diff_imaging_path}/proc_rlt/diff_img"]
            _g0[:] = np.float32(diff_img)[:]
    elif len(diff_img_shape) == 3:
        img1 = np.ndarray(([i for i in diff_img_shape[1:]]))
        img2 = np.ndarray(([i for i in diff_img_shape[1:]]))
        sli_img = np.ndarray(([i for i in diff_img_shape[1:]]))
        with h5py.File(diff_data_fn, "r+") as f:
            _g0 = f[f"/{proc_diff_imaging_path}/proc_rlt/diff_img"]
            if bin_fact == 1:
                for ii in range(diff_img_shape[0]):    
                    _g0[ii] = np.float32((f[reg_img_path][diff_img_idx[0], ii, :, :] - f[reg_img_path][diff_img_idx[1], ii, :, :]))[:]            
            else:
                for ii in range(diff_img_shape[0]):
                    img1[:] = zoom(f[reg_img_path][diff_img_idx[0], ii * bin_fact : (ii + 1) * bin_fact, :, :], (1 / bin_fact, 1 / bin_fact))[:]  
                    img2[:] = zoom(f[reg_img_path][diff_img_idx[1], ii * bin_fact : (ii + 1) * bin_fact, :, :], (1 / bin_fact, 1 / bin_fact))[:]
                    sli_img[:] = np.squeeze(img1 - img2).astype(np.float32)[:]
                    _g0[ii] = sli_img[:]
    print("differential imaging analysis is done!")

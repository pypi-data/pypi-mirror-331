#!/usr/bin/env python3
# -*- coding: utf-8 -*-

ZFLY_CFG = {
    "io_data_structure_tomo": {
        "use_h5_reader": True,
        "structured_h5_reader": {
            "io_data_structure": {
                "data_path": "/Exchange/data",
                "flat_path": "/Exchange/flat",
                "dark_path": "/Exchange/dark",
                "theta_path": "/Exchange/angle",
            },
            "io_data_info": {
                "item00_path": "/Exchange/data",
                "item01_path": "/Exchange/angle",
                "item02_path": "/Experiment/Magnification",
                "item03_path": "/Experiment/Pixel Size",
                "item04_path": "/Experiment/X_eng (keV)",
                "item05_path": "/Experiment/note",
                "item06_path": "/Experiment/scan_time",
                "item07_path": "",
            },
        },
        "tomo_raw_fn_template": "tomo_zfly_id_{0}.h5",
        "customized_reader": {"user_tomo_reader": ""},
    },
    "io_data_structure_xanes2D": {
        "use_h5_reader": True,
        "structured_h5_reader": {
            "io_data_structure": {
                "data_path": "/img_xanes",
                "flat_path": "/img_bkg",
                "dark_path": "/img_dark",
                "eng_path": "/X_eng",
            },
            "io_data_info": {
                "item00_path": "/img_xanes",
                "item01_path": "/X_eng",
                "item02_path": "/Magnification",
                "item03_path": "/Pixel Size",
                "item04_path": "/note",
                "item05_path": "/scan_time",
                "item06_path": "",
                "item07_path": "",
            },
        },
        "xanes2D_raw_fn_template": "xanes_scan2_id_{0}.h5",
        "customized_reader": {"user_xanes2D_reader": ""},
    },
    "io_data_structure_xanes3D": {
        "use_h5_reader": True,
        "structured_h5_reader": {
            "io_data_structure": {
                "data_path": "/Exchange/data",
                "flat_path": "/Exchange/flat",
                "dark_path": "/Exchange/dark",
                "eng_path": "/Experiment/X_eng (keV)",
            },
            "io_data_info": {
                "item00_path": "/Exchange/data",
                "item01_path": "/Exchange/angle",
                "item02_path": "/Experiment/Magnification",
                "item03_path": "/Experiment/Pixel Size",
                "item04_path": "/Experiment/X_eng (keV)",
                "item05_path": "/Experiment/note",
                "item06_path": "/Experiment/scan_time",
                "item07_path": "",
            },
        },
        "tomo_raw_fn_template": "tomo_zfly_id_{0}.h5",
        "xanes3D_recon_dir_template": "recon_tomo_zfly_id_{0}",
        "xanes3D_recon_fn_template": "recon_tomo_zfly_id_{0}_{1}.tiff",
        "customized_reader": {"user_xanes3D_reader": ""},
    },
}

FLY_CFG = {
    "io_data_structure_tomo": {
        "use_h5_reader": True,
        "structured_h5_reader": {
            "io_data_structure": {
                "data_path": "/img_tomo",
                "flat_path": "/img_bkg",
                "dark_path": "/img_dark",
                "theta_path": "/angle",
            },
            "io_data_info": {
                "item00_path": "/img_tomo",
                "item01_path": "/angle",
                "item02_path": "/Magnification",
                "item03_path": "/Pixel Size",
                "item04_path": "/X_eng",
                "item05_path": "/note",
                "item06_path": "/scan_time",
                "item07_path": "",
            },
        },
        "tomo_raw_fn_template": "fly_scan_id_{0}.h5",
        "customized_reader": {"user_tomo_reader": ""},
    },
    "io_data_structure_xanes2D": {
        "use_h5_reader": True,
        "structured_h5_reader": {
            "io_data_structure": {
                "data_path": "/img_xanes",
                "flat_path": "/img_bkg",
                "dark_path": "/img_dark",
                "eng_path": "/X_eng",
            },
            "io_data_info": {
                "item00_path": "/img_xanes",
                "item01_path": "/X_eng",
                "item02_path": "/Magnification",
                "item03_path": "/Pixel Size",
                "item04_path": "/note",
                "item05_path": "/scan_time",
                "item06_path": "",
                "item07_path": "",
            },
        },
        "xanes2D_raw_fn_template": "xanes_scan2_id_{0}.h5",
        "customized_reader": {"user_xanes2D_reader": ""},
    },
    "io_data_structure_xanes3D": {
        "use_h5_reader": True,
        "structured_h5_reader": {
            "io_data_structure": {
                "data_path": "/img_tomo",
                "flat_path": "/img_bkg",
                "dark_path": "/img_dark",
                "eng_path": "/X_eng",
            },
            "io_data_info": {
                "item00_path": "/img_tomo",
                "item01_path": "/angle",
                "item02_path": "/Magnification",
                "item03_path": "/Pixel Size",
                "item04_path": "/X_eng",
                "item05_path": "/note",
                "item06_path": "/scan_time",
                "item07_path": "",
            },
        },
        "tomo_raw_fn_template": "fly_scan_id_{0}.h5",
        "xanes3D_recon_dir_template": "recon_fly_scan_id_{0}",
        "xanes3D_recon_fn_template": "recon_fly_scan_id_{0}_{1}.tiff",
        "customized_reader": {"user_xanes3D_reader": ""},
    },
}

APS_TXM_CFG = {
    "io_data_structure_tomo": {
        "use_h5_reader": True,
        "structured_h5_reader": {
            "io_data_structure": {
                "data_path": "/exchange/data",
                "flat_path": "/exchange/data_white",
                "dark_path": "/exchange/data_dark",
                "theta_path": "/exchange/theta",
            },
            "io_data_info": {
                "item00_path": "/exchange/data",
                "item01_path": "/exchange/theta",
                "item02_path": "/measurement/instrument/detection_system/objective/magnification",
                "item03_path": "/measurement/instrument/detector/pixel_size",
                "item04_path": "/measurement/instrument/monochromator/energy",
                "item05_path": "measurement/sample/description_1",
                "item06_path": "/process/acquisition/start_date",
                "item07_path": "/measurement/sample/file/name",
            },
        },
        "tomo_raw_fn_template": "{0}_{1}.h5",
        "customized_reader": {"user_tomo_reader": ""},
    },
    "io_data_structure_xanes2D": {
        "use_h5_reader": True,
        "structured_h5_reader": {
            "io_data_structure": {
                "data_path": "/exchange/data",
                "flat_path": "/exchange/data_white",
                "dark_path": "/exchange/data_dark",
                "eng_path": "/measurement/instrument/monochromator/energy",
            },
            "io_data_info": {
                "item00_path": "/exchange/data",
                "item01_path": "/measurement/instrument/monochromator/energy",
                "item02_path": "/measurement/instrument/detection_system/objective/magnification",
                "item03_path": "/measurement/instrument/detector/pixel_size",
                "item04_path": "measurement/sample/description_1",
                "item05_path": "/process/acquisition/start_date",
                "item06_path": "",
                "item07_path": "",
            },
        },
        "xanes2D_raw_fn_template": "{0}_{1}.h5",
        "customized_reader": {"user_xanes2D_reader": ""},
    },
    "io_data_structure_xanes3D": {
        "use_h5_reader": True,
        "structured_h5_reader": {
            "io_data_structure": {
                "data_path": "/exchange/data",
                "flat_path": "/exchange/data_white",
                "dark_path": "/exchange/data_dark",
                "eng_path": "/measurement/instrument/monochromator/energy",
            },
            "io_data_info": {
                "item00_path": "/exchange/data",
                "item01_path": "/exchange/theta",
                "item02_path": "/measurement/instrument/detection_system/objective/magnification",
                "item03_path": "/measurement/instrument/detector/pixel_size",
                "item04_path": "/measurement/instrument/monochromator/energy",
                "item05_path": "measurement/sample/description_1",
                "item06_path": "/process/acquisition/start_date",
                "item07_path": "",
            },
        },
        "tomo_raw_fn_template": "{0}_{1}.h5",
        "xanes3D_recon_dir_template": "recon_{0}_{1}",
        "xanes3D_recon_fn_template": "recon_{0}_{1}_{2}.tiff",
        "customized_reader": {"user_xanes3D_reader": ""},
    },
}

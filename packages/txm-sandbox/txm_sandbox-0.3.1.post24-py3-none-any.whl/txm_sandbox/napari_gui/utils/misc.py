import h5py
from pathlib import Path
from qtpy.QtWidgets import QApplication

from ...dicts import customized_struct_dict as dat_dict


def check_avail_items(fn, file_type):
    choices = []
    if file_type == "TOMO Recon":
        choices = ["recon tiff"]
    else:
        if Path(fn).exists() & Path(fn).is_file():
            with h5py.File(fn, "r") as f:
                keys = list(f.keys())
                if file_type == "TOMO Raw":
                    if "img_tomo" in keys:
                        choices = [
                            "img_tomo",
                            "img_bkg",
                            "img_dark",
                            "angle",
                        ]
                    elif "Exchange" in keys:
                        choices = ["data", "flat", "dark", "angle"]
                elif file_type == "2D XANES":
                    if "processed_XANES2D" in keys:
                        choices = list(f["/processed_XANES2D/proc_spectrum"].keys())
                        if "gen_masks" in f["/processed_XANES2D"].keys():
                            choices += list(f["/processed_XANES2D/gen_masks"].keys())
                    elif "processed_XANES" in keys:
                        choices = list(f["/processed_XANES/proc_spectrum"].keys())
                        if "gen_masks" in f["/processed_XANES"].keys():
                            choices += list(f["/processed_XANES/gen_masks"].keys())
                    if "registration_results" in keys:
                        try:
                            if (
                                "registered_xanes2D"
                                in f["/registration_results/reg_results"].keys()
                            ):
                                choices += [
                                    "eng_list",
                                    "registered_xanes2D",
                                ]
                        except:
                            pass
                    if "processed_diff_imaging" in keys:
                        choices += [
                            "diff_img",
                        ]
                elif file_type == "3D XANES":
                    if "processed_XANES3D" in keys:
                        choices = list(f["/processed_XANES3D/proc_spectrum"].keys())
                        if "gen_masks" in f["/processed_XANES3D"].keys():
                            choices += list(f["/processed_XANES3D/gen_masks"].keys())
                    elif "processed_XANES" in keys:
                        choices = list(f["/processed_XANES/proc_spectrum"].keys())
                        if "gen_masks" in f["/processed_XANES"].keys():
                            choices += list(f["/processed_XANES/gen_masks"].keys())
                    if "registration_results" in keys:
                        try:
                            if (
                                "registered_xanes3D"
                                in f["/registration_results/reg_results"].keys()
                            ):
                                choices += [
                                    "eng_list",
                                    "registered_xanes3D",
                                ]
                        except:
                            pass
                    if "processed_diff_imaging" in keys:
                        choices += [
                            "diff_img",
                        ]
    return choices


def disp_progress_info(info):
    def decorated_func(func):
        def inner_func(self):
            self.op_status.value = "doing " + info + " ..."
            QApplication.processEvents()
            print("doing " + info + " ...")
            func(self)
            self.op_status.value = info + " finished"
            print(info + " finished")
            return

        return inner_func

    return decorated_func


def get_slcd_ds_path(fn, file_type, _slcd_item):
    if not isinstance(fn, str):
        fn = str(fn)
    if (file_type == "TOMO Raw") and _slcd_item:
        with h5py.File(fn, "r") as f:
            if "tomo_zfly" in fn:
                _in_dat_path_in_h5 = dat_dict.TOMO_ZFLY_ITEM_DICT[_slcd_item]["path"]
                _in_dat_desc = dat_dict.TOMO_ZFLY_ITEM_DICT[_slcd_item]["description"]
                _in_dat_dtype = dat_dict.TOMO_ZFLY_ITEM_DICT[_slcd_item]["dtype"]
            elif "fly_scan" in fn:
                _in_dat_path_in_h5 = dat_dict.TOMO_FLY_ITEM_DICT[_slcd_item]["path"]
                _in_dat_desc = dat_dict.TOMO_FLY_ITEM_DICT[_slcd_item]["description"]
                _in_dat_dtype = dat_dict.TOMO_FLY_ITEM_DICT[_slcd_item]["dtype"]
    elif (file_type == "2D XANES") and _slcd_item:
        if "mk" in _slcd_item:
            with h5py.File(fn, "r") as f:
                if "processed_XANES3D" in f.keys():
                    _in_dat_path_in_h5 = dat_dict.XANES2D_ANA_ITEM_DICT["mask"][
                        "path"
                    ].format(_slcd_item)
                else:
                    _in_dat_path_in_h5 = (
                        dat_dict.XANES2D_ANA_ITEM_DICT["mask"]["path"]
                        .replace("processed_XANES2D", "processed_XANES")
                        .format(_slcd_item)
                    )
            _in_dat_desc = dat_dict.XANES3D_ANA_ITEM_DICT["mask"]["description"]
            _in_dat_dtype = dat_dict.XANES3D_ANA_ITEM_DICT["mask"]["dtype"]
        else:
            with h5py.File(fn, "r") as f:
                if "processed_XANES2D" in f.keys():
                    _in_dat_path_in_h5 = dat_dict.XANES2D_ANA_ITEM_DICT[_slcd_item][
                        "path"
                    ]
                else:
                    _in_dat_path_in_h5 = dat_dict.XANES2D_ANA_ITEM_DICT[_slcd_item][
                        "path"
                    ].replace("processed_XANES2D", "processed_XANES")
            _in_dat_desc = dat_dict.XANES2D_ANA_ITEM_DICT[_slcd_item]["description"]
            _in_dat_dtype = dat_dict.XANES2D_ANA_ITEM_DICT[_slcd_item]["dtype"]
    elif (file_type == "3D XANES") and _slcd_item:
        if "mk" in _slcd_item:
            with h5py.File(fn, "r") as f:
                if "processed_XANES3D" in f.keys():
                    _in_dat_path_in_h5 = dat_dict.XANES3D_ANA_ITEM_DICT["mask"][
                        "path"
                    ].format(_slcd_item)
                else:
                    _in_dat_path_in_h5 = (
                        dat_dict.XANES3D_ANA_ITEM_DICT["mask"]["path"]
                        .replace("processed_XANES3D", "processed_XANES")
                        .format(_slcd_item)
                    )
            _in_dat_desc = dat_dict.XANES3D_ANA_ITEM_DICT["mask"]["description"]
            _in_dat_dtype = dat_dict.XANES3D_ANA_ITEM_DICT["mask"]["dtype"]
        else:
            with h5py.File(fn, "r") as f:
                if "processed_XANES3D" in f.keys():
                    _in_dat_path_in_h5 = dat_dict.XANES3D_ANA_ITEM_DICT[_slcd_item][
                        "path"
                    ]
                else:
                    _in_dat_path_in_h5 = dat_dict.XANES3D_ANA_ITEM_DICT[_slcd_item][
                        "path"
                    ].replace("processed_XANES3D", "processed_XANES")
            _in_dat_desc = dat_dict.XANES3D_ANA_ITEM_DICT[_slcd_item]["description"]
            _in_dat_dtype = dat_dict.XANES3D_ANA_ITEM_DICT[_slcd_item]["dtype"]
    return _in_dat_path_in_h5, _in_dat_desc, _in_dat_dtype


def info_reader(scn_fn, dtype="data", cfg=None):
    with h5py.File(scn_fn, "r") as f:
        return f[
            cfg["structured_h5_reader"]["io_data_structure"][f"{dtype}_path"]
        ].shape


def overlap_roi(viewer, gui, mode="auto_cen"):
    if mode == "auto_cen":
        if "recon_roi" in viewer.layers:
            viewer.layers["recon_roi"].visible = False
        if "xanes_roi" in viewer.layers:
            viewer.layers["xanes_roi"].visible = False
        if "ext_reg_roi" in viewer.layers:
            viewer.layers["ext_reg_roi"].visible = False
        rm_gui_viewers(viewer, ["auto_cen_roi"])
        if gui.auto_cen_dft_roi.value:
            dim = viewer.layers["xanes_raw_viewer"].data.shape
            ellipse_data = [
                [int(dim[0] * 0.5), int(dim[1] * 0.5)],
                [int(dim[0] * 0.45), int(dim[1] * 0.45)],
            ]
            viewer.add_shapes(
                ellipse_data,
                shape_type="ellipse",
                edge_color="green",
                edge_width=3,
                face_color="transparent",
                name="auto_cen_roi",
            )
        else:
            [xs, xe] = gui.auto_cen_roix.value
            [ys, ye] = gui.auto_cen_roiy.value
            roi_coor = [[ys, xs], [ys, xe], [ye, xe], [ye, xs]]
            viewer.add_shapes(
                roi_coor,
                shape_type="rectangle",
                edge_color="green",
                edge_width=3,
                face_color="transparent",
                name="auto_cen_roi",
            )
        viewer.layers["xanes_raw_viewer"].refresh()
    elif mode == "ext_reg_roi":
        if "recon_roi" in viewer.layers:
            viewer.layers["recon_roi"].visible = False
        if "xanes_roi" in viewer.layers:
            viewer.layers["xanes_roi"].visible = False
        if "auto_cen_roi" in viewer.layers:
            viewer.layers["auto_cen_roi"].visible = False
        rm_gui_viewers(viewer, ["ext_reg_roi"])
        [xs, xe] = gui.opt_reg_roix.value
        [ys, ye] = gui.opt_reg_roiy.value
        roi_coor = [[ys, xs], [ys, xe], [ye, xe], [ye, xs]]
        viewer.add_shapes(
            roi_coor,
            shape_type="rectangle",
            edge_color="red",
            edge_width=3,
            face_color="transparent",
            name="ext_reg_roi",
        )
        viewer.layers["xanes_raw_viewer"].refresh()
    elif mode == "recon_roi":
        [xs, xe] = gui.rec_roix.value
        [ys, ye] = gui.rec_roiy.value
        roi_coor = [[ys, xs], [ys, xe], [ye, xe], [ye, xs]]
        rm_gui_viewers(viewer, ["recon_roi"])
        if "auto_cen_roi" in viewer.layers:
            viewer.layers["auto_cen_roi"].visible = False
        if "xanes_roi" in viewer.layers:
            viewer.layers["xanes_roi"].visible = False
        if "ext_reg_roi" in viewer.layers:
            viewer.layers["ext_reg_roi"].visible = False
        viewer.add_shapes(
            roi_coor,
            shape_type="rectangle",
            edge_color="green",
            edge_width=3,
            face_color="transparent",
            name="recon_roi",
        )
        viewer.layers["xanes_raw_viewer"].refresh()
    elif mode == "xanes_spec_roi":
        cx = gui.roi_cen_x.value
        cy = gui.roi_cen_y.value
        roi_coor = [
            [cy - 5, cx - 5],
            [cy - 5, cx + 5],
            [cy + 5, cx + 5],
            [cy + 5, cx - 5],
        ]
        if "recon_roi" in viewer.layers:
            viewer.layers["recon_roi"].visible = False
        if "auto_cen_roi" in viewer.layers:
            viewer.layers["auto_cen_roi"].visible = False
        if "ext_reg_roi" in viewer.layers:
            viewer.layers["ext_reg_roi"].visible = False
        rm_gui_viewers(viewer, ["xanes_spec_roi"])
        viewer.add_shapes(
            roi_coor,
            shape_type="rectangle",
            edge_color="blue",
            edge_width=3,
            face_color="transparent",
            name="xanes_spec_roi",
        )
        viewer.layers["xanes_data"].refresh()


def rm_gui_viewers(viewer, viewers: list):
    for v in viewers:
        if v in viewer.layers:
            viewer.layers.remove(v)


def set_data_widget(widget, new_min, new_val, new_max):
    widget.min = min(new_min, widget.min)
    widget.max = max(new_max, widget.max)
    widget.value = new_val
    widget.min = new_min
    widget.max = new_max


def show_layers_in_viewer(viewer, layers: list):
    for layer in viewer.layers:
        layer.visible = False
    for layer in layers:
        if layer in viewer.layers:
            viewer.layers[layer].visible = True
    viewer.reset_view()


def update_layer_in_viewer(viewer, data, layer: str, data_type="image"):
    rm_gui_viewers(viewer, [layer])
    if data_type == "image":
        viewer.add_image(data, name=layer)
    elif data_type == "folder":
        viewer.open(data, name=layer)
    viewer.reset_view()

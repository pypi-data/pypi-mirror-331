#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 08:56:30 2020

@author: xiao
"""

import os, functools, inspect, psutil
from numbers import Number

from pathlib import Path
import glob
import h5py
import tifffile
from PIL import Image
import numpy as np
from dask import delayed
import dask.array as da
import linecache
import pandas as pd

from ..dicts.config_dict import (IO_TOMO_CFG_DEFAULT, IO_XANES2D_CFG_DEFAULT,
                                 IO_XANES3D_CFG_DEFAULT)

CHUNK_SIZE = 640E6

N_CPU = os.cpu_count()
if N_CPU > 1:
    N_CPU -= 1


def cal_mem_lim(img_sz, mem_lim=None):
    if mem_lim is None:
        mem = psutil.virtual_memory()
        mem_lim = mem.available / N_CPU
    mem_lim = (mem_lim // img_sz) * img_sz
    return mem_lim


def shape_from_slice(sli, shp):
    """ Calculate shape based on np.s_ 
    Parameters:
        sli: np.s_ 
        shape: tuple; having same dimensions as sli
    
    Return:
        tuple; shape based on sli and shape
    """
    s = []
    if sli == slice(None, None, None):
        s = shp
        return s
    elif isinstance(sli, tuple) and (len(sli) > len(shp)):
        print(
            "The dimensions fo the pinput sli should be either smaller than or equal to the input shape"
        )
        return None
    elif isinstance(sli, tuple) and (len(sli) < len(shp)):
        sli = list(sli)
        for _ in range(len(shp) - len(sli)):
            sli.append(slice(None, None, None))
        for ii in range(len(sli)):
            if isinstance(sli[ii], int) and (sli[ii] < shp[ii]):
                s.append(1)
            elif isinstance(sli[ii], slice):
                if sli[ii].start is None:
                    d0 = 0
                elif isinstance(sli[ii].start, int) and (
                        sli[ii].start >= 0) and (sli[ii].start <= shp[ii] - 1):
                    d0 = sli[ii].start
                else:
                    raise (
                        TypeError,
                        'Slicing index has to be either None or positive integers smaller than shape.'
                    )
                if sli[ii].stop is None:
                    d1 = shp[ii]
                elif isinstance(sli[ii].stop, int) and (
                        sli[ii].stop >= 0) and (sli[ii].stop <= shp[ii]):
                    d1 = sli[ii].stop
                else:
                    raise (
                        TypeError,
                        'Slicing index has to be either None or positive integers smaller than shape.'
                    )
                if sli[ii].step is None:
                    dt = 1
                elif isinstance(sli[ii].step, int) and (sli[ii].step >= 0):
                    dt = sli[ii].step
                else:
                    raise (
                        TypeError,
                        'Slicing index has to be either None or positive integer.'
                    )
                s.append(int(d1 - d0) / dt)
            else:
                raise (
                    TypeError,
                    'Slicing index has to be either None or positive integers smaller than shape.'
                )
        return s


def sli_interpreter(sli_tuple):
    sli = []
    for s in sli_tuple:
        if isinstance(s, list):
            sli.append(np.s_[s[0]:s[1]])
        elif s == ':':
            sli.append(np.s_[:])
        elif isinstance(s, int):
            sli.append(np.s_[s])
        elif s is None:
            sli.append(slice(None))
    return tuple(sli)


def tomo_h5_reader(fn,
                   dtype='data',
                   sli=[[None, None]],
                   cfg=IO_TOMO_CFG_DEFAULT):
    """
    Inputs:
        fnt: string
             file name template to raw h5 data files
        cfg: dictionary; optional
             dictionary with 4 items 'data_path', 'flat_path', 'dark_path', and
             'eng_path' under item 'io_data_structure'; paths point to the
             datasets locations in h5 files
        dtype: string; optional
             specifying which one of the above four items will be read
        sli: list; optional
             a 4-element list; each element is again a list indicating the
             start and end of the slicing on that dimension. The four dimensions
             are [eng, angle, y, x] for dtype='data', or three dimensions of
             [eng, y, x] for dtype='flat' and 'dark', or one dimension of [eng]
             for dtype='eng'
    Returns:
        ndarray
    """
    sli = sli_interpreter(sli)
    with h5py.File(fn, 'r') as f:
        if dtype == 'data':
            # print(sli)
            return np.squeeze(f[cfg['structured_h5_reader']
                                ['io_data_structure']['data_path']])[sli]
        elif dtype == 'flat':
            return np.squeeze(f[cfg['structured_h5_reader']
                                ['io_data_structure']['flat_path']])[sli]
        elif dtype == 'dark':
            return np.squeeze(f[cfg['structured_h5_reader']
                                ['io_data_structure']['dark_path']])[sli]
        elif dtype == 'theta':
            return np.squeeze(f[cfg['structured_h5_reader']
                                ['io_data_structure']['theta_path']])[sli[0]]


def tomo_h5_info(fn, dtype='data', cfg=IO_XANES2D_CFG_DEFAULT):
    with h5py.File(fn, "r") as f:
        if dtype == 'data':
            try:
                arr = np.squeeze(f[cfg['structured_h5_reader']
                                   ['io_data_structure']['data_path']])
                dim = arr.shape
                return dim
            except:
                return 0
        elif dtype == 'flat':
            try:
                arr = np.squeeze(f[cfg['structured_h5_reader']
                                   ['io_data_structure']['flat_path']])
                dim = arr.shape
                return dim
            except:
                return 0
        elif dtype == 'dark':
            try:
                arr = np.squeeze(f[cfg['structured_h5_reader']
                                   ['io_data_structure']['dark_path']])
                dim = arr.shape
                return dim
            except:
                return 0
        elif dtype == 'theta':
            try:
                arr = np.squeeze(f[cfg['structured_h5_reader']
                                   ['io_data_structure']['theta_path']])
                dim = arr.shape
                return dim
            except:
                return 0


def xanes2D_h5_reader(fn,
                      dtype='data',
                      sli=[[None, None]],
                      cfg=IO_XANES2D_CFG_DEFAULT):
    sli = sli_interpreter(sli)
    with h5py.File(fn, 'r') as f:
        if dtype == 'data':
            return np.squeeze(f[cfg['structured_h5_reader']
                                ['io_data_structure']['data_path']])[sli]
        elif dtype == 'flat':
            return np.squeeze(f[cfg['structured_h5_reader']
                                ['io_data_structure']['flat_path']])[sli]
        elif dtype == 'dark':
            return np.squeeze(f[cfg['structured_h5_reader']
                                ['io_data_structure']['dark_path']])[sli]
        elif dtype == 'eng':
            return np.squeeze(f[cfg['structured_h5_reader']
                                ['io_data_structure']['eng_path']])[sli]


def xanes3D_h5_reader(fn,
                      ids,
                      dtype='data',
                      sli=[[None, None]],
                      cfg=IO_XANES3D_CFG_DEFAULT):
    """
    Inputs:
        fn:  string
             file name template to raw h5 data files
        cfg: dictionary; optional
             dictionary with 4 items 'data_path', 'flat_path', 'dark_path', and
             'eng_path' under item 'io_data_structure'; paths point to the
             datasets locations in h5 files
        dtype: string; optional
             specifying which one of the above four items will be read
        sli: list; optional
             a 4-element list; each element is again a list indicating the
             start and end of the slicing on that dimension. The four dimensions
             are [eng, angle, y, x] for dtype='data', or three dimensions of
             [eng, y, x] for dtype='flat' and 'dark', or one dimension of [eng]
             for dtype='eng'
    Returns:
        ndarray
    """
    sli = sli_interpreter(sli)
    if dtype == 'data':
        data = []
        for ii in ids:
            fn0 = fn.format(ii)
            with h5py.File(fn0, 'r') as f:
                data.append(
                    np.squeeze(f[cfg['structured_h5_reader']
                                 ['io_data_structure']['data_path']])[sli])
        return np.array(data)
    elif dtype == 'flat':
        data = []
        for ii in ids:
            fn0 = fn.format(ii)
            with h5py.File(fn0, 'r') as f:
                data.append(
                    np.squeeze(f[cfg['structured_h5_reader']
                                 ['io_data_structure']['flat_path']])[sli])
        return np.array(data)
    elif dtype == 'dark':
        data = []
        for ii in ids:
            fn0 = fn.format(ii)
            with h5py.File(fn0, 'r') as f:
                data.append(
                    np.squeeze(f[cfg['structured_h5_reader']
                                 ['io_data_structure']['dark_path']])[sli])
        return np.array(data)
    elif dtype == 'eng':
        eng = []
        for ii in ids:
            fn0 = fn.format(ii)
            with h5py.File(fn0, 'r') as f:
                eng.append(
                    np.squeeze(f[cfg['structured_h5_reader']
                                 ['io_data_structure']['eng_path']])[()])
        return np.array(eng)


def data_reader(func):

    @functools.wraps(func)
    def wrapper_data_reader(fn, *args, **kwargs):
        return func(fn, *args, **kwargs)

    return wrapper_data_reader


def data_info(func):

    @functools.wraps(func)
    def wrapper_data_info(fn, dtype='data', *args, **kwargs):
        if not (set(
            ('fn', 'dtype')) <= set(inspect.getfullargspec(func).args)):
            raise TypeError(
                f'{func.__name__} missing one or more arguments in ("fn", "dtype")'
            )
            return None
        return func(fn, dtype=dtype, *args, **kwargs)

    return wrapper_data_info


def read_xanes2D_wl_fit(fn):
    with h5py.File(fn, 'r') as f:
        return f['/processed_XANES2D/proc_spectrum/whiteline_pos_fit'][:]


def tiff_vol_reader(fn_temp, scan_id, roi):
    vol = []
    for ii in range(roi[0], roi[1]):
        vol.append(
            tifffile.imread(fn_temp.format(scan_id,
                                           str(ii).zfill(5)))[roi[2]:roi[3],
                                                              roi[4]:roi[5]])
    return np.array(vol)


def h5_lazy_reader(fn, path, sli):

    @delayed
    def dlyd_rdr(fn, path, sli):
        try:
            with h5py.File(fn, 'r') as f:
                return f[path][sli]
        except:
            print(
                "Cannot read data with the given filename, dataset path, and slice range."
            )
            return None

    try:
        with h5py.File(fn, 'r') as f:
            dtp = f[path].dtype
            shp = f[path].shape
    except:
        print(
            "Cannot read data with the given filename, dataset path, and slice range."
        )
        shp, dtp = None, None

    if shp is None:
        print("Cannot get the dataset shape.")
        return None
    s = shape_from_slice(sli, shp)

    delayed_arr = dlyd_rdr(fn, path, sli)
    if delayed_arr is None:
        print("Cannot read the dataset.")
        return None
    else:
        if len(shp) == 3:
            s0 = int(CHUNK_SIZE / (s[1] * s[2]) / 4)
            if s0 > s[0]:
                s0 = s[0]
            chunk = {0: s0, 1: -1, 2: -1}
            return da.from_delayed(delayed_arr, shape=s,
                                   dtype=dtp).rechunk(chunk)
        else:
            return da.from_delayed(delayed_arr, shape=s, dtype=dtp)


def tif_lazy_reader(fnt, ids=None, ide=None, digit=5):

    @delayed
    def dlyd_seq_rdr(fnt, ids=ids, ide=ide, digit=5, dtype=np.float32):
        try:
            imgs = [
                tifffile.imread(fnt.format(str(ii).zfill(digit))).astype(dtype)
                for ii in range(ids, ide)
            ]
            return np.array(imgs)
        except:
            print(
                "Cannot read data with the given filename and the index range."
            )
            return None

    @delayed
    def dlyd_sgl_rdr(fn, dtype=np.float32):
        pass

    if ids is None:
        im = Image.open(fnt)
        s = im.size
        if im.mode == 'F':
            dtp = np.float32
        elif im.mode == 'I':
            dtp = np.int32
        elif im.mode in ['1', 'L', 'P']:
            dtp = np.int8
        im.close()

        delayed_arr = dlyd_sgl_rdr(fnt, dtype=dtp)
        if delayed_arr is None:
            print("Cannot read the dataset.")
            return None
        else:
            if len(s) == 3:
                s0 = int(CHUNK_SIZE / (s[1] * s[2]) / 4)
                if s0 > s[0]:
                    s0 = s[0]
                chunk = {0: s0, 1: -1, 2: -1}
                return da.from_delayed(delayed_arr, shape=s,
                                       dtype=dtp).rechunk(chunk)
            else:
                return da.from_delayed(delayed_arr, shape=s, dtype=dtp)
    else:
        im = Image.open(fnt.format(str(ids).zfill(digit)))
        s = im.size
        if im.mode == 'F':
            dtp = np.float32
        elif im.mode == 'I':
            dtp = np.int32
        elif im.mode in ['1', 'L', 'P']:
            dtp = np.int8
        im.close()

        fns = sorted(glob.glob(fnt.format('*')))
        id_min = int(os.path.basename(fns[0]).split('_')[-1])
        id_max = int(os.path.basename(fns[-1]).split('_')[-1])
        if ide == -1:
            ide = id_max
        if ids > ide:
            ids = ide
        if ids > id_max:
            ids = id_max
        if ide > id_max:
            ide = id_max
        if ids < id_min:
            ids = id_min
        if ide < id_min:
            ide = id_min
        s.insert(0, ide - ids + 1)

        delayed_arr = dlyd_seq_rdr(fnt,
                                   ids=ids,
                                   ide=ide,
                                   digit=digit,
                                   dtype=dtp)
        if delayed_arr is None:
            print("Cannot read the dataset.")
            return None
        else:
            if len(s) == 3:
                s0 = int(CHUNK_SIZE / (s[1] * s[2]) / 4)
                if s0 > s[0]:
                    s0 = s[0]
                chunk = {0: s0, 1: -1, 2: -1}
                return da.from_delayed(delayed_arr, shape=s,
                                       dtype=dtp).rechunk(chunk)
            else:
                return da.from_delayed(delayed_arr, shape=s, dtype=dtp)


def tif_reader(fn):
    pass


def tif_seq_reader(fn):
    pass


def h5_reader(fn):
    pass


def tif_writer(fn, img):
    tifffile.imsave(fn, img)


def tif_seq_writer(fnt, img, axis=0, ids=0, digit=5, overwrite=True):
    if len(img.shape) < 3:
        raise (TypeError, "Cannot save the image as an image sequence")
    else:
        if axis == 0:
            for ii in range(ids, ids + img.shape[0]):
                fn = fnt.format(str(ii).zfill(digit))
                tifffile.imsave(fn, img[ii - ids].astype(np.float32))
        elif axis == 1:
            for ii in range(ids, ids + img.shape[1]):
                fn = fnt.format(str(ii).zfill(digit))
                tifffile.imsave(fn, img[:, ii - ids, :].astype(np.float32))
        elif axis == 2:
            for ii in range(ids, ids + img.shape[1]):
                fn = fnt.format(str(ii).zfill(digit))
                tifffile.imsave(fn, img[:, :, ii - ids].astype(np.float32))


def raw_writer(fn, img):
    with open(fn, 'wb') as f:
        np.save(f, img, allow_pickle=False, fix_imports=False)


def raw_seq_writer(fnt, img, ids=0, digit=5):
    if len(img.shape) < 3:
        raise (TypeError, "Cannot save the image as an image sequence")
    else:
        for ii in range(ids, ids + img.shape[0]):
            fn = fnt.format(str(ii).zfill(digit))
            with open(fn, 'wb') as f:
                np.save(f,
                        img[ii - ids],
                        allow_pickle=False,
                        fix_imports=False)


def asc_writer(fn, img):
    np.savetxt(fn,
                  img,
                  fmt='%10.5f',
                  delimiter='\t',
                  newline='\n',
                  header='X-ray energy in eV',
                  footer='',
                  comments='# ',
                  encoding=None)


def h5_writer(fn, ds_path, img):
    try:
        with h5py.File(fn, 'a') as f:
            if ds_path in f:
                del f[ds_path]
                f.create_dataset(ds_path, data=img, dtype=img.dtype)
            else:
                f.create_dataset(ds_path, data=img, dtype=img.dtype)
    except Exception as e:
        raise (e)


def data_writer(func):

    @functools.wraps(func)
    def wrapper_data_reader(fn, *args, **kwargs):
        return func(fn, *args, **kwargs)

    return wrapper_data_reader


def read_xas_ascii(filename):
    try:
        # First use numpy to detect where data starts
        with open(filename, "r") as f:
            first_data_line = 0
            for i, line in enumerate(f):
                try:
                    # Try to convert line to floats
                    [float(x) for x in line.strip().split()]
                    first_data_line = i
                    break
                except ValueError:
                    continue

        # Now read with pandas starting from the data line
        s = linecache.getline(str(filename), first_data_line)

        parts = s.lstrip("#").split("*")
        cleaned_parts = [part.strip() for part in parts]
        headings = [*cleaned_parts[:-1], *cleaned_parts[-1].split()]
        print(f"input data has columns: {headings}")
        xas = pd.read_csv(filename, sep="\s+", skiprows=first_data_line, names=headings)
        return xas
    except Exception as e:
        print(e)
        print(f"Unrecognizable file: {filename}")
        return None


def create_hdf5_from_json(structure, file_path):
    with h5py.File(file_path, "r+") as f:
        create_group(f, None, structure)


def create_group(parent_group, group_name, structure):
    if group_name is None:
        group = parent_group
    else:
        if group_name in parent_group:
            del parent_group[group_name]
        group = parent_group.create_group(group_name)
    for key, value in structure.items():
        if isinstance(value, dict):
            create_group(group, key, value)
        elif isinstance(value, pd.DataFrame):
            create_dataset(group, key, value)
            create_dataset(group, f"{key}_columns", list(value.columns))
            create_dataset(group, f"{key}_index", np.array(value.index, dtype='int64'))
        else:
            if value is None:
                value = "None"
            create_dataset(group, key, value)


def create_dataset(group, key, value):
    group.create_dataset(key, data=value)


def read_hdf5_group_to_dict(fp, group, is_file=False):
    if is_file:
        with h5py.File(fp, "r") as f:
            return recursively_load_dict(f[group])
    else:
        return recursively_load_dict(fp[group])


def recursively_load_dict(group):
    output = {}
    for key, val in group.items():
        if isinstance(val, h5py.Dataset):
            output[key] = val[...]
            if isinstance(output[key], np.ndarray):
                if output[key].ndim == 0:
                    if isinstance(output[key].item(), bytes):
                        output[key] = output[key].item().decode("utf-8")
                    else:
                        output[key] = output[key].item()
        elif isinstance(val, h5py.Group):
            output[key] = recursively_load_dict(val)
    return output

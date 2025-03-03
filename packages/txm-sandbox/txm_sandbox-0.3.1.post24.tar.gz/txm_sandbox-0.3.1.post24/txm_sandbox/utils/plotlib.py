#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 00:12:06 2021

@author: xiao
"""
import matplotlib.pyplot as plt
from .xanes_math import index_of


def disp(ij, ijui, img, bc=None, cm=None):
    ijui.show(ij.py.to_java(img))
    if bc is None:
        ij.py.run_macro("""run("Enhance Contrast", "saturated=0.35")""")
    else:
        ij.py.run_macro(f"""setMinAndMax({bc[0]}, {bc[1]})""")

    if cm is None:
        ij.py.run_macro("""run("16 colors")""")
    else:
        ij.py.run_macro(f"""run({cm})""")


def plot_kde(eng,
             pdf,
             val,
             imgv,
             label=None,
             fig=None,
             ax=None,
             figsize=[10, 10],
             shade=True,
             plot_hist=False,
             cl='r',
             xlim=None,
             ylim=None):
    if (fig is None) or (ax is None):
        fig, ax = plt.subplots(figsize=figsize)
    # elif xlim is None:
    #     xlim = ax.get_xlim()

    # if xlim is None:
    #     ll = 0
    #     ul = eng.shape[0]
    #     ax.set_xlim(val.min() - 0.001, val.max() + 0.001)
    # else:
    #     ll = index_of(eng, xlim[0])
    #     ul = index_of(eng, xlim[1])
    #     ax.set_xlim(max(val.min() - 0.001, eng[ll]),
    #                 min(val.max() + 0.001, eng[ul]))

    if xlim is None:
        xll = 0
        xul = eng.shape[0] - 1
        ax.set_xlim(eng[xll], eng[xul])
    else:
        xll = index_of(eng, xlim[0])
        xul = index_of(eng, xlim[1])
        ax.set_xlim(xlim[0], xlim[1])

    if ylim is None:
        ax.set_ylim(pdf[0], pdf[-1])
    else:
        ax.set_ylim(ylim[0], ylim[1])

    if label is None:
        ax.plot(eng[xll:xul+1], pdf[xll:xul+1], linewidth=3, alpha=0.5, color=cl)
    else:
        ax.plot(eng[xll:xul+1],
                pdf[xll:xul+1],
                linewidth=3,
                alpha=0.5,
                label=label,
                color=cl)
        ax.legend(loc='upper left')

    if plot_hist:
        ax.hist(imgv,
                val.shape[0],
                fc=cl,
                histtype='stepfilled' if shade else 'step',
                alpha=0.3,
                density=True)
    return fig, ax


def plot():
    pass

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from magicgui import widgets
from qtpy.QtCore import Qt
from ...utils.io import read_xas_ascii
from ...utils.misc import cal_xas_mu
from ..utils.misc import set_data_widget

_XANES_RE_SPECTRA = []


def get_ref_spectra_choices(ComboBox):
    global _XANES_RE_SPECTRA
    return _XANES_RE_SPECTRA


class lcf_cfg_gui:
    def __init__(self, parent=None):
        self._parent_obj = parent
        self._ref_spectra = {}

        self.ref_fn = widgets.FileEdit(
            mode="r",
            name="ref spec",
        )
        self.spec_table = widgets.Select(
            choices=get_ref_spectra_choices, name="ref spectra"
        )
        self.rem_ref = widgets.PushButton(text="remove spec", enabled=False)
        self.plot_spec = widgets.PushButton(text="plot", enabled=False)
        self.is_chi = widgets.CheckBox(value=False, text="normalize", enabled=False)
        self.pre_edge_fit_eng_e = widgets.LineEdit(
            value=-50, 
            label="pre edge eng e (eV)", 
            enabled=False,
            tooltip="upper limit of energy range relative to absorption edge for pre-edge background fitting",
            )
        self.post_edge_fit_eng_s = widgets.LineEdit(
            value=100, 
            label="post edge eng s (eV)", 
            enabled=False,
            tooltip="lower limit of energy range relative to absorption edge for post-edge fitting",
            )
        self.norm_ref_spec = widgets.PushButton(
            text="normalize \& plot", 
            enabled=False,
            tooltip="subtract pre-edge background and normalize the raw spectrum, then plot the normalized spectrum",
            )
        self.update_ref_spec = widgets.PushButton(
            text="update spec", 
            enabled=False,
            tooltip="update reference spectrum with the normalized version",
            )
        self.label0 = widgets.Label(
            value="-------------------     Fitting Energy Range    --------------------",
        )
        self.lcf_fit_eng_rng_s = widgets.LineEdit(
            value="", 
            label="lcf fitting eng s (eV)", 
            enabled=False,
            tooltip="lower bound of energy range for lcf fitting",
            )
        self.lcf_fit_eng_rng_e = widgets.LineEdit(
            value="", 
            label="lcf fitting eng e (eV)", 
            enabled=False,
            tooltip="upper bound of energy range for lcf fitting",
            )
        self.lcf_fit_eng_rng = widgets.RangeSlider(
            min=0, 
            max=1, 
            name="lcf fitting energy range", 
            value=[0, 1], 
            enabled=False,
            tooltip="define fitting energy range for LCF",
        )
        
        ref_table_op_layout = widgets.VBox(
            widgets=[
                self.rem_ref,
                self.plot_spec,
            ]
        )
        ref_table_layout = widgets.HBox(
            widgets=[                
                self.spec_table, 
                ref_table_op_layout,
            ]
        )
        
        edge_fit_eng_layout = widgets.HBox(
            widgets=[
                self.pre_edge_fit_eng_e,
                self.post_edge_fit_eng_s
            ]
        )
        spec_norm_layout = widgets.VBox(
            widgets=[
                self.is_chi,
                edge_fit_eng_layout,
                self.norm_ref_spec,
                self.update_ref_spec,
            ]
        )

        lcf_fit_eng_rgn_disp = widgets.HBox(
            widgets=[
                self.lcf_fit_eng_rng_s,
                self.lcf_fit_eng_rng_e
            ]
        )
        self.label0.native.setAlignment(Qt.AlignCenter)
        lcf_fit_eng_rgn_disp.native.layout().setAlignment(Qt.AlignCenter)
        self.lcf_fit_eng_rng.native.layout().setAlignment(Qt.AlignCenter)

        self.ref_fn.changed.connect(self._load_ref_spec)
        self.spec_table.changed.connect(self._sel_spec)
        self.rem_ref.changed.connect(self.__rem_ref)
        self.plot_spec.changed.connect(self._plot_spec)
        self.is_chi.changed.connect(self._is_chi)
        self.pre_edge_fit_eng_e.changed.connect(self._set_pre_edge_fit_e)
        self.post_edge_fit_eng_s.changed.connect(self._set_post_edge_fit_s)
        self.norm_ref_spec.changed.connect(self._norm_spec_plot)
        self.update_ref_spec.changed.connect(self._update_ref_spec)
        self.lcf_fit_eng_rng.changed.connect(self._lcf_fit_eng_rng)
        
        layout = widgets.VBox(
            widgets=[
                self.ref_fn, 
                ref_table_layout,
                spec_norm_layout,
                self.label0,
                lcf_fit_eng_rgn_disp,
                self.lcf_fit_eng_rng
            ]
        )
        self.gui = widgets.Dialog(
            widgets=[
                layout,
            ]
        )
        print("this is the correct version")
        self.rtn = self.gui.exec()

    def __init_widgets(self):
        global _XANES_RE_SPECTRA
        _XANES_RE_SPECTRA = []
        self.spec_table.reset_choices()

        self.is_chi.value = False
        self.pre_edge_fit_eng_e.value = -50.0
        self.post_edge_fit_eng_s.value = 100.0
        self.spec_table.enabled = False
        self.rem_ref.enabled = False
        self.plot_spec.enabled = False
        self.is_chi.enabled = False
        self.pre_edge_fit_eng_e.enabled = False
        self.post_edge_fit_eng_s.enabled = False
        self.norm_ref_spec.enabled = False
        self.update_ref_spec.enabled = False
        self.lcf_fit_eng_rng_s.enabled = False
        self.lcf_fit_eng_rng_e.enabled = False
        self.lcf_fit_eng_rng.enabled = False

    def __lcf_cfg_gui_widgets_logic(self):
        if self.spec_table.value:
            self.rem_ref.enabled = True
            self.plot_spec.enabled = True
            self.is_chi.enabled = True
        else:
            self.rem_ref.enabled = False
            self.plot_spec.enabled = False
            self.is_chi.value = False
            self.is_chi.enabled = False

        if self.is_chi.value:
            self.pre_edge_fit_eng_e.enabled = True
            self.post_edge_fit_eng_s.enabled = True
            self.norm_ref_spec.enabled = True
            self.update_ref_spec.enabled = True
        else:
            self.pre_edge_fit_eng_e.enabled = False
            self.post_edge_fit_eng_s.enabled = False
            self.norm_ref_spec.enabled = False
            self.update_ref_spec.enabled = False

        if len(self.spec_table.value) != 0:
            ready = 1
            for ii in self.spec_table.value:
                if "chi_ref" in self._ref_spectra[ii]["data"].columns:
                    ready *= 1
                else:
                    ready *= 0
            if ready == 1:
                self.lcf_fit_eng_rng.enabled = True
                low = []
                high = []
                for ii in self.spec_table.value:
                    low.append(self._ref_spectra[ii]["data"]["Mono Energy"].iloc[0])
                    high.append(self._ref_spectra[ii]["data"]["Mono Energy"].iloc[-1])
                lower = max(low)
                upper = min(high)
                set_data_widget(
                    self.lcf_fit_eng_rng, 
                    lower, 
                    [lower, upper], 
                    upper
                )                
            else:
                self.lcf_fit_eng_rng.enabled = False
        else:
            self.lcf_fit_eng_rng.enabled = False

    def _load_ref_spec(self):
        xas = read_xas_ascii(self.ref_fn.value)
        if xas is None:
            keys = list(self._ref_spectra.keys())
            if len(keys):
                self.spec_table.value = [
                    keys[-1],
                    ]
            else:
                self.__init_widgets()
        else:
            data = cal_xas_mu(xas)
            if data is not None:
                xas["mu_ref"] = data[0]
                xas["mu_standard"] = data[1]
                self._ref_spectra[Path(self.ref_fn.value).name] = {}
                self._ref_spectra[Path(self.ref_fn.value).name]["data"] = xas
                self._ref_spectra[Path(self.ref_fn.value).name]["mu_plot"] = None
                self._ref_spectra[Path(self.ref_fn.value).name]["chi_plot"] =None
                self._ref_spectra[Path(self.ref_fn.value).name]["chi_plot_ax"] = None
                self._ref_spectra[Path(self.ref_fn.value).name]["file_path"] = self.ref_fn.value
                keys = [key for key in self._ref_spectra.keys()]
                global _XANES_RE_SPECTRA
                _XANES_RE_SPECTRA = keys
                self.spec_table.reset_choices()
                self.spec_table.value = [
                    keys[-1],
                    ] 
        self.__lcf_cfg_gui_widgets_logic()          

    def _sel_spec(self):
        self.__lcf_cfg_gui_widgets_logic() 
    
    def __rem_ref(self):
        global _XANES_RE_SPECTRA
        for ii in self.spec_table.value:
            _XANES_RE_SPECTRA.remove(ii)
            if self._ref_spectra[ii]["mu_plot"] is not None:
                plt.close(self._ref_spectra[ii]["mu_plot"])
            if self._ref_spectra[ii]["chi_plot"] is not None:
                plt.close(self._ref_spectra[ii]["chi_plot"])
            if self._ref_spectra[Path(self.ref_fn.value).name]["file_path"] == self.ref_fn.value:
                self.ref_fn.value = ""
            self._ref_spectra.pop(ii)
            
        self.spec_table.reset_choices()
        if len(_XANES_RE_SPECTRA):
            self.spec_table.value = [
                _XANES_RE_SPECTRA[-1],
                ]        
        self.__lcf_cfg_gui_widgets_logic()
    
    def _plot_spec(self):
        if plt.fignum_exists(0):
            plt.close(0)
        fig = plt.figure(0)
        legend = []
        for ii in self.spec_table.value:
            plt.plot(self._ref_spectra[ii]["data"]["Mono Energy"],
                        self._ref_spectra[ii]["data"]["mu_ref"])
            legend.append(ii)
            self._ref_spectra[ii]["mu_plot"] = fig
        fig.legend(legend)
        fig.gca().set_xlabel("energy (eV)")
        fig.gca().set_ylabel(r"$\mu$ (ab.u.)")
        fig.gca().set_title(r"$\mu$ plot")
        fig.show()

    def _is_chi(self):
        self.__lcf_cfg_gui_widgets_logic()

    def _set_pre_edge_fit_e(self):
        if float(self.pre_edge_fit_eng_e.value) > -50.0:
            self.pre_edge_fit_eng_e.value = -50.0

    def _set_post_edge_fit_s(self):
        if float(self.post_edge_fit_eng_s.value) < 100.0:
            self.post_edge_fit_eng_s.value = 100.

    def _norm_spec_plot(self):
        if plt.fignum_exists(1):
            plt.close(1)
        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, sharex=True, sharey=False)
        plt.ion()
        legend = []
        for ii in self.spec_table.value:
            cfg = {}
            spec2_e0_idx = lcf_cfg_gui.find_e0_idx(
                self._ref_spectra[ii]["data"]["mu_ref"]
                )
            cfg["pre_es_idx"] = 0
            cfg["pre_ee_idx"] = lcf_cfg_gui.index_of(
                self._ref_spectra[ii]["data"]["Mono Energy"], 
                self._ref_spectra[ii]["data"]["Mono Energy"][spec2_e0_idx] + float(self.pre_edge_fit_eng_e.value)
                )
            cfg["post_es_idx"] = lcf_cfg_gui.index_of(
                self._ref_spectra[ii]["data"]["Mono Energy"], 
                self._ref_spectra[ii]["data"]["Mono Energy"][spec2_e0_idx] + float(self.post_edge_fit_eng_s.value)
                )
            cfg["post_ee_idx"] = -1
            cfg["e0_idx"] = spec2_e0_idx
            pre_edge_fit_rlt, post_edge_fit_rlt, chi = lcf_cfg_gui.cal_ref_chi(
                self._ref_spectra[ii]["data"]["Mono Energy"], 
                self._ref_spectra[ii]["data"]["mu_ref"], 
                cfg,
                in_place=False
                )
            ax1.plot(
                self._ref_spectra[ii]["data"]["Mono Energy"],
                self._ref_spectra[ii]["data"]["mu_ref"],
            )
            ax1.plot(
                self._ref_spectra[ii]["data"]["Mono Energy"],
                np.polyval(
                    pre_edge_fit_rlt[0], 
                    self._ref_spectra[ii]["data"]["Mono Energy"]
                ),
            )
            ax1.plot(
                self._ref_spectra[ii]["data"]["Mono Energy"],
                np.polyval(
                    post_edge_fit_rlt[0], 
                    self._ref_spectra[ii]["data"]["Mono Energy"]
                ),
            )
            ax2.plot(
                self._ref_spectra[ii]["data"]["Mono Energy"],
                chi
            )
            legend.append(ii)
            self._ref_spectra[ii]["chi_plot"] = fig
            self._ref_spectra[ii]["chi_plot_ax"] = ax2
        fig.legend(legend)
        ax1.set_xlabel("energy (eV)")
        ax1.set_ylabel(r"$\mu$")
        ax1.set_title(r"$\mu$ plot")
        ax2.set_xlabel("energy (eV)")
        ax2.set_ylabel(r"$\chi$")
        ax2.set_title(r"$\chi$ plot")
        fig.show()
        self.__lcf_cfg_gui_widgets_logic()

    def _update_ref_spec(self):
        for ii in self.spec_table.value:
            cfg = {}
            spec2_e0_idx = lcf_cfg_gui.find_e0_idx(
                self._ref_spectra[ii]["data"]["mu_ref"]
                )
            cfg["pre_es_idx"] = 0
            cfg["pre_ee_idx"] = lcf_cfg_gui.index_of(
                self._ref_spectra[ii]["data"]["Mono Energy"], 
                self._ref_spectra[ii]["data"]["Mono Energy"][spec2_e0_idx] + float(self.pre_edge_fit_eng_e.value)
                )
            cfg["post_es_idx"] = lcf_cfg_gui.index_of(
                self._ref_spectra[ii]["data"]["Mono Energy"], 
                self._ref_spectra[ii]["data"]["Mono Energy"][spec2_e0_idx] + float(self.post_edge_fit_eng_s.value)
                )
            cfg["post_ee_idx"] = -1
            cfg["e0_idx"] = spec2_e0_idx
            _, _, self._ref_spectra[ii]["data"]["chi_ref"] = lcf_cfg_gui.cal_ref_chi(
                self._ref_spectra[ii]["data"]["Mono Energy"], 
                self._ref_spectra[ii]["data"]["mu_ref"], 
                cfg,
                in_place=False
                )
        self.__lcf_cfg_gui_widgets_logic()

    def _lcf_fit_eng_rng(self):
        key = self.spec_table.value[0]
        self._ref_spectra[key]["chi_plot_ax"].set_xlim(
            self.lcf_fit_eng_rng.value[0], 
            self.lcf_fit_eng_rng.value[1]
        )
        self.lcf_fit_eng_rng_s.value = self.lcf_fit_eng_rng.value[0]
        self.lcf_fit_eng_rng_e.value = self.lcf_fit_eng_rng.value[1]

    @staticmethod
    def find_e0_idx(spec):
        return np.argmax(np.diff(spec))

    @staticmethod
    def index_of(arr, val):
        return np.argmin(np.abs(arr - val))

    @staticmethod
    def cal_ref_chi(eng, spec, cfg, in_place=False):
        pre_edge_fit_rlt = np.polyfit(
            eng[cfg["pre_es_idx"] : cfg["pre_ee_idx"]],
            spec[cfg["pre_es_idx"] : cfg["pre_ee_idx"]],
            1, rcond=None, full=True
            )
        pre = np.polyval(pre_edge_fit_rlt[0], eng)
        
        post_edge_fit_rlt = np.polyfit(
            eng[cfg["post_es_idx"] : cfg["post_ee_idx"]],
            spec[cfg["post_es_idx"] : cfg["post_ee_idx"]],
            2, rcond=None, full=True
        )
        post = np.polyval(post_edge_fit_rlt[0], eng)
        
        if in_place:
            spec[:] = ((spec - pre) / (post[cfg["e0_idx"]] - pre[cfg["e0_idx"]]))[:]
            spec[np.isnan(spec)] = 0
            spec[np.isinf(spec)] = 0
            return pre_edge_fit_rlt, post_edge_fit_rlt, spec
        else:
            mu = np.asarray(spec)
            mu = ((spec - pre) / (post[cfg["e0_idx"]] - pre[cfg["e0_idx"]]))
            mu[np.isnan(mu)] = 0
            mu[np.isinf(mu)] = 0
            return pre_edge_fit_rlt, post_edge_fit_rlt, mu


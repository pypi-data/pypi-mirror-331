from collections import OrderedDict
import numpy as np

TOMO_RECON_PARAM_DICT = {
    "file_params": {
        "raw_data_top_dir": None,
        "data_center_dir": None,
        "recon_top_dir": None,
        "debug_top_dir": None,
        "cen_list_file": None,
        "alt_flat_file": None,
        "alt_dark_file": None,
        "wedge_ang_auto_det_ref_fn": None
    },
    "recon_config": {
        "recon_type": 'Trial Cent',
        "use_debug": False,
        "use_alt_flat": False,
        "use_alt_dark": False,
        "use_fake_flat": False,
        "use_fake_dark": False,
        "use_rm_zinger": False,
        "use_mask": True,
        "use_wedge_ang_auto_det": False,
        "is_wedge": False
    },
    "flt_params": {
        "filters": {}
    },
    "data_params": {
        "scan_id": 0,
        "downsample": 1,
        "rot_cen": 1280,
        "cen_win_s": 1240,
        "cen_win_w": 8,
        "fake_flat_val": 1e4,
        "fake_dark_val": 1e2,
        "sli_s": 1280,
        "sli_e": 1300,
        "chunk_sz": 200,
        "margin": 15,
        "zinger_val": 500,
        "mask_ratio": 1,
        # "wedge_blankat":90,
        "wedge_missing_s": 500,
        "wedge_missing_e": 600,
        "wedge_ang_auto_det_thres": 0.1
    },
    "alg_params": {}
}

TOMO_FILTERLIST = [
    "phase retrieval", "flatting bkg", "remove cupping", "stripe_removal: vo",
    "stripe_removal: ti", "stripe_removal: sf", "stripe_removal: fw",
    "denoise: median", "denoise: wiener", "denoise: unsupervised_wiener",
    "denoise: denoise_nl_means", "denoise: denoise_tv_bregman",
    "denoise: denoise_tv_chambolle", "denoise: denoise_bilateral",
    "denoise: denoise_wavelet"
]

TOMO_FILTER_PARAM_DICT = dict(
    OrderedDict({
        "phase retrieval": {
            0: [
                "filter",
                ["paganin", "bronnikov"],
                "filter: filter type used in phase retrieval",
            ],
            1: [
                "pad",
                ["True", "False"],
                "pad: boolean, if pad the data before phase retrieval filtering",
            ],
            6: ["pixel_size", 6.5e-5, "pixel_size: in cm unit"],
            7: ["dist", 15.0, "dist: sample-detector distance in cm"],
            8: ["energy", 35.0, "energy: x-ray energy in keV"],
            9: [
                "alpha",
                1e-2,
                "alpha: beta/delta, wherr n = (1-delta + i*beta) is x-ray rafractive index in the sample",
            ],
        },
        "flatting bkg": {
            6: [
                "air",
                30,
                "air: number of pixels on the both sides of projection images where is sample free region. This region will be used to correct background nonunifromness",
            ]
        },
        "remove cupping": {
            6: [
                "cc",
                0.5,
                "cc: constant that is subtracted from the logrithm of the normalized images. This is for correcting the cup-like background in the case when the sample size is much larger than the image view",
            ]
        },
        "stripe_removal: vo": {
            6: ["snr", 4, "snr: signal-to-noise ratio"],
            7: ["la_size", 81, "la_size: large ring's width in pixel"],
            8: ["sm_size", 21, "sm_size: small ring's width in pixel"],
        },
        "stripe_removal: ti": {
            6: ["nblock", 1, "nblock: "],
            7: ["alpha", 5, "alpha: "],
        },
        "stripe_removal: sf": {
            6: ["size", 31, "size: "]
        },
        "stripe_removal: fw": {
            0: [
                "pad",
                ["True", "False"],
                "pad: boolean, if padding data before filtering",
            ],
            1: [
                "wname",
                [
                    "db5",
                    "db1",
                    "db2",
                    "db3",
                    "sym2",
                    "sym6",
                    "haar",
                    "gaus1",
                    "gaus2",
                    "gaus3",
                    "gaus4",
                ],
                "wname: wavelet name",
            ],
            6: ["level", 6, "level: how many of level of wavelet transforms"],
            7: [
                "sigma",
                2,
                "sigma: sigam of gaussian filter in image Fourier space",
            ],
        },
        "denoise: median": {
            6:
            ["size angle", 1, "median kernel size along rotation angle axis"],
            7: [
                "size y",
                5,
                "median kernel size along projection image vertical axis",
            ],
            8: [
                "size x",
                5,
                "median kernel size along projection image horizontal axis",
            ],
        },
        "denoise: wiener": {
            0: [
                "reg",
                ["None"],
                "reg: The regularisation operator. The Laplacian by default. It can be an impulse response or a transfer function, as for the psf",
            ],
            1: ["is_real", ["True", "False"], "is_real: "],
            2: [
                "clip",
                ["True", "False"],
                "clip: True by default. If true, pixel values of the result above 1 or under -1 are thresholded for skimage pipeline compatibility",
            ],
            6: [
                "psf",
                2,
                "psf: The impulse response (input image’s space) or the transfer function (Fourier space). Both are accepted. The transfer function is automatically recognized as being complex (np.iscomplexobj(psf))",
            ],
            7: ["balance", 0.3, "balance: "],
        },
        "denoise: unsupervised_wiener": {
            0: [
                "reg",
                ["None"],
                "reg: The regularisation operator. The Laplacian by default. It can be an impulse response or a transfer function, as for the psf. Shape constraint is the same as for the psf parameter",
            ],
            1: [
                "is_real",
                ["True", "False"],
                "is_real: True by default. Specify if psf and reg are provided with hermitian hypothesis, that is only half of the frequency plane is provided (due to the redundancy of Fourier transform of real signal). It’s apply only if psf and/or reg are provided as transfer function. For the hermitian property see uft module or np.fft.rfftn",
            ],
            2: [
                "clip",
                ["True", "False"],
                "clip: True by default. If True, pixel values of the result above 1 or under -1 are thresholded for skimage pipeline compatibility",
            ],
            3: [
                "user_params",
                ["None"],
                "user_params: Dictionary of parameters for the Gibbs sampler. See below",
            ],
            6: [
                "psf",
                2,
                "psf: Point Spread Function. This is assumed to be the impulse response (input image space) if the data-type is real, or the transfer function (Fourier space) if the data-type is complex. There is no constraints on the shape of the impulse response. The transfer function must be of shape (M, N) if is_real is True, (M, N // 2 + 1) otherwise (see np.fft.rfftn)",
            ],
        },
        "denoise: denoise_nl_means": {
            0: [
                "multichannel",
                ["False", "True"],
                "multichannel: Whether the last axis of the image is to be interpreted as multiple channels or another spatial dimension",
            ],
            1: [
                "fast_mode",
                ["True", "False"],
                "fast_mode: If True (default value), a fast version of the non-local means algorithm is used. If False, the original version of non-local means is used. See the Notes section for more details about the algorithms",
            ],
            6: [
                "patch_size", 5,
                "patch_size: Size of patches used for denoising"
            ],
            7: [
                "patch_distance",
                7,
                "patch_distance: Maximal distance in pixels where to search patches used for denoising",
            ],
            8: [
                "h",
                0.1,
                "h: Cut-off distance (in gray levels). The higher h, the more permissive one is in accepting patches. A higher h results in a smoother image, at the expense of blurring features. For a Gaussian noise of standard deviation sigma, a rule of thumb is to choose the value of h to be sigma of slightly less",
            ],
            9: [
                "sigma",
                0.05,
                "sigma: The standard deviation of the (Gaussian) noise. If provided, a more robust computation of patch weights is computed that takes the expected noise variance into account (see Notes below)",
            ],
        },
        "denoise: denoise_tv_bregman": {
            0: [
                "multichannel",
                ["False", "True"],
                "multichannel: Apply total-variation denoising separately for each channel. This option should be true for color images, otherwise the denoising is also applied in the channels dimension",
            ],
            1: [
                "isotrophic",
                ["True", "False"],
                "isotrophic: Switch between isotropic and anisotropic TV denoisin",
            ],
            6: [
                "weight",
                1.0,
                "weight: Denoising weight. The smaller the weight, the more denoising (at the expense of less similarity to the input). The regularization parameter lambda is chosen as 2 * weight",
            ],
            7: [
                "max_iter",
                100,
                "max_iter: Maximal number of iterations used for the optimization",
            ],
            8: [
                "eps",
                0.001,
                "eps: Relative difference of the value of the cost function that determines the stop criterion.",
            ],
        },
        "denoise: denoise_tv_chambolle": {
            0: [
                "multichannel",
                ["False", "True"],
                "multichannel: Apply total-variation denoising separately for each channel. This option should be true for color images, otherwise the denoising is also applied in the channels dimension",
            ],
            6: [
                "weight",
                0.1,
                "weight: Denoising weight. The greater weight, the more denoising (at the expense of fidelity to input).",
            ],
            7: [
                "n_iter_max",
                100,
                "n_iter_max: Maximal number of iterations used for the optimization",
            ],
            8: [
                "eps",
                0.002,
                "eps: Relative difference of the value of the cost function that determines the stop criterion",
            ],
        },
        "denoise: denoise_bilateral": {
            0: [
                "win_size",
                ["None"],
                "win_size: Window size for filtering. If win_size is not specified, it is calculated as max(5, 2 * ceil(3 * sigma_spatial) + 1)",
            ],
            1: [
                "sigma_color",
                ["None"],
                "sigma_color: Standard deviation for grayvalue/color distance (radiometric similarity). A larger value results in averaging of pixels with larger radiometric differences. Note, that the image will be converted using the img_as_float function and thus the standard deviation is in respect to the range [0, 1]. If the value is None the standard deviation of the image will be used",
            ],
            2: [
                "multichannel",
                ["False", "True"],
                "multichannel: Whether the last axis of the image is to be interpreted as multiple channels or another spatial dimension",
            ],
            3: [
                "mode",
                ["constant", "edge", "symmetric", "reflect", "wrap"],
                "mode: How to handle values outside the image borders. See numpy.pad for detail",
            ],
            6: [
                "sigma_spatial",
                1,
                "sigma_spatial: Standard deviation for range distance. A larger value results in averaging of pixels with larger spatial difference",
            ],
            7: [
                "bins",
                10000,
                "bins: Number of discrete values for Gaussian weights of color filtering. A larger value results in improved accuracy",
            ],
            8: [
                "cval",
                0,
                "cval: Used in conjunction with mode ‘constant’, the value outside the image boundaries",
            ],
        },
        "denoise: denoise_wavelet": {
            0: [
                "wavelet",
                [
                    "db1",
                    "db2",
                    "db3",
                    "db5",
                    "sym2",
                    "sym6",
                    "haar",
                    "gaus1",
                    "gaus2",
                    "gaus3",
                    "gaus4",
                ],
                "wavelet: The type of wavelet to perform and can be any of the options pywt.wavelist outputs",
            ],
            1: [
                "mode",
                ["soft"],
                "mode: An optional argument to choose the type of denoising performed. It noted that choosing soft thresholding given additive noise finds the best approximation of the original image",
            ],
            2: [
                "multichannel",
                ["False", "True"],
                "multichannel: Apply wavelet denoising separately for each channel (where channels correspond to the final axis of the array)",
            ],
            3: [
                "convert2ycbcr",
                ["False", "True"],
                "convert2ycbcr: If True and multichannel True, do the wavelet denoising in the YCbCr colorspace instead of the RGB color space. This typically results in better performance for RGB images",
            ],
            4: [
                "method",
                ["BayesShrink"],
                "method: Thresholding method to be used. The currently supported methods are 'BayesShrink' [1] and 'VisuShrink' [2]. Defaults to 'BayesShrink'",
            ],
            6: [
                "sigma",
                1,
                "sigma: The noise standard deviation used when computing the wavelet detail coefficient threshold(s). When None (default), the noise standard deviation is estimated via the method in [2]",
            ],
            7: [
                "wavelet_levels",
                3,
                "wavelet_levels: The number of wavelet decomposition levels to use. The default is three less than the maximum number of possible decomposition levels",
            ],
        },
    }))

TOMO_ALG_PARAM_DICT = dict(
    OrderedDict({
        "gridrec": {
            0: [
                "filter_name",
                [
                    "parzen",
                    "shepp",
                    "cosine",
                    "hann",
                    "hamming",
                    "ramlak",
                    "butterworth",
                    "none",
                ],
                "filter_name: filter that is used in frequency space",
                str,
            ]
        },
        "sirt": {
            3: [
                "num_gridx",
                1280,
                "num_gridx: number of the reconstructed slice image along x direction",
                int,
            ],
            4: [
                "num_gridy",
                1280,
                "num_gridy: number of the reconstructed slice image along y direction",
                int,
            ],
            5: [
                "num_iter",
                10,
                "num_iter: number of reconstruction iterations",
                int,
            ],
        },
        "tv": {
            3: [
                "num_gridx",
                1280,
                "num_gridx: number of the reconstructed slice image along x direction",
                int,
            ],
            4: [
                "num_gridy",
                1280,
                "num_gridy: number of the reconstructed slice image along y direction",
                int,
            ],
            5: [
                "num_iter",
                10,
                "num_iter: number of reconstruction iterations",
                int,
            ],
            6: [
                "reg_par", 0.1, "reg_par: relaxation factor in tv regulation",
                int
            ],
        },
        "mlem": {
            3: [
                "num_gridx",
                1280,
                "num_gridx: number of the reconstructed slice image along x direction",
                int,
            ],
            4: [
                "num_gridy",
                1280,
                "num_gridy: number of the reconstructed slice image along y direction",
                int,
            ],
            5: [
                "num_iter",
                10,
                "num_iter: number of reconstruction iterations",
                int,
            ],
        },
        "astra": {
            0: [
                "method", ["EM_CUDA"], "method: astra reconstruction methods",
                str
            ],
            1: [
                "proj_type",
                ["cuda"],
                "proj_type: projection calculation options used in astra",
                str,
            ],
            2: [
                "extra_options",
                ["MinConstraint"],
                "extra_options: extra constraints used in the reconstructions. you need to set p03 for a MinConstraint level",
                str,
            ],
            3: [
                "extra_options_param",
                -0.1,
                "extra_options_param: parameter used together with extra_options",
                np.float32,
            ],
            4: [
                "num_iter",
                50,
                "num_iter: number of reconstruction iterations",
                int,
            ],
        },
    }))

XANES_PEAK_LINE_SHAPES = [
    'lorentzian', 'gaussian', 'voigt', 'pvoigt', 'moffat', 'pearson7',
    'breit_wigner', 'damped_oscillator', 'dho', 'lognormal', 'students_t',
    'expgaussian', 'donaich', 'skewed_gaussian', 'skewed_voigt', 'step',
    'rectangle', 'parabolic', 'sine', 'expsine', 'split_lorentzian'
]

XANES_STEP_LINE_SHAPES = ['logistic', 'exponential', 'powerlaw', 'linear']

XANES_PEAK_FIT_PARAM_DICT = {
    "parabolic": {
        0: ["a", 1, "a: ampflitude in parabolic function"],
        1: ["b", 0, "b: center of parabolic function"],
        2: ["c", 1, "c: standard deviation of parabolic function"]
    },
    "gaussian": {
        0: ["amp", 1, "amp: ampflitude in gaussian function"],
        1: ["cen", 0, "cen: center of gaussian function"],
        2: ["sig", 1, "sig: standard deviation of gaussian function"]
    },
    "lorentzian": {
        0: ["amp", 1, "amp: ampflitude in lorentzian function"],
        1: ["cen", 0, "cen: center of lorentzian function"],
        2: ["sig", 1, "sig: standard deviation of lorentzian function"]
    },
    "damped_oscillator": {
        0: ["amp", 1, "amp: ampflitude in damped_oscillator function"],
        1: ["cen", 0, "cen: center of damped_oscillator function"],
        2: ["sig", 1, "sig: standard deviation of damped_oscillator function"]
    },
    "lognormal": {
        0: ["amp", 1, "amp: ampflitude in lognormal function"],
        1: ["cen", 0, "cen: center of lognormal function"],
        2: ["sig", 1, "sig: standard deviation of lognormal function"]
    },
    "students_t": {
        0: ["amp", 1, "amp: ampflitude in students_t function"],
        1: ["cen", 0, "cen: center of students_t function"],
        2: ["sig", 1, "sig: standard deviation of students_t function"]
    },
    "sine": {
        0: ["amp", 1, "amp: ampflitude in sine function"],
        1: ["frq", 1, "frq: freqency in sine function"],
        2: ["shft", 0, "shft: shift in sine function"]
    },
    "voigt": {
        0: ["amp", 1, "amp: ampflitude in voigt function"],
        1: ["cen", 0, "cen: center of voigt function"],
        2: ["sig", 1, "sig: standard voigt of gaussian function"],
        3: ["gamma", 0, "gamma: "]
    },
    "split_lorentzian": {
        0: ["amp", 1, "amp: ampflitude in split_lorentzian function"],
        1: ["cen", 0, "cen: center of split_lorentzian function"],
        2: ["sig", 1, "sig: standard deviation of split_lorentzian function"],
        3: [
            "sigr", 1,
            "sigr: standard deviation of the right-hand side half in split_lorentzian function"
        ]
    },
    "pvoigt": {
        0: ["amp", 1, "amp: ampflitude in pvoigt function"],
        1: ["cen", 0, "cen: center of pvoigt function"],
        2: ["sig", 1, "sig: standard pvoigt of gaussian function"],
        3: ["frac", 0, "frac: "]
    },
    "moffat": {
        0: ["amp", 1, "amp: ampflitude in moffat function"],
        1: ["cen", 0, "cen: center of moffat function"],
        2: ["sig", 1, "sig: standard moffat of gaussian function"],
        3: ["beta", 0, "beta: "]
    },
    "pearson7": {
        0: ["amp", 1, "amp: ampflitude in pearson7 function"],
        1: ["cen", 0, "cen: center of pearson7 function"],
        2: ["sig", 1, "sig: standard pearson7 of gaussian function"],
        3: ["expo", 0, "expo: "]
    },
    "breit_wigner": {
        0: ["amp", 1, "amp: ampflitude in breit_wigner function"],
        1: ["cen", 0, "cen: center of breit_wigner function"],
        2: ["sig", 1, "sig: standard breit_wigner of gaussian function"],
        3: ["q", 0, "q: "]
    },
    "dho": {
        0: ["amp", 1, "amp: ampflitude in dho function"],
        1: ["cen", 0, "cen: center of dho function"],
        2: ["sig", 1, "sig: standard dho of gaussian function"],
        3: ["gama", 1, "gama: "]
    },
    "expgaussian": {
        0: ["amp", 1, "amp: ampflitude in expgaussian function"],
        1: ["cen", 0, "cen: center of expgaussian function"],
        2: ["sig", 1, "sig: standard expgaussian of gaussian function"],
        3: ["gama", 1, "gama: "]
    },
    "donaich": {
        0: ["amp", 1, "amp: ampflitude in donaich function"],
        1: ["cen", 0, "cen: center of donaich function"],
        2: ["sig", 1, "sig: standard donaich of gaussian function"],
        3: ["gama", 0, "gama: "]
    },
    "skewed_gaussian": {
        0: ["amp", 1, "amp: ampflitude in skewed_gaussian function"],
        1: ["cen", 0, "cen: center of skewed_gaussian function"],
        2: ["sig", 1, "sig: standard skewed_gaussian of gaussian function"],
        3: ["gama", 0, "gama: "]
    },
    "expsine": {
        0: ["amp", 1, "amp: ampflitude in expsine function"],
        1: ["frq", 1, "frq:  width of expsine function"],
        2: ["shft", 0, "shft: center of gaussian function"],
        3: ["dec", 0, "dec: exponential decay factor"]
    },
    "step": {
        0: ["amp", 1, "amp: ampflitude in step function"],
        1: ["cen", 0, "cen: center of step function"],
        2: ["sig", 1, "sig: standard step of gaussian function"],
        5: ["form", "linear", "form: "]
    },
    "skewed_voigt": {
        0: ["amp", 1, "amp: ampflitude in skewed_voigt function"],
        1: ["cen", 0, "cen: center of skewed_voigt function"],
        2: ["sig", 1, "sig: standard skewed_voigt of gaussian function"],
        3: ["gamma", 0, "gamma: "],
        4: ["skew", 0, "skew: "]
    },
    "rectangle": {
        0: ["amp", 1, "amp: ampflitude in rectangle function"],
        1: ["cen1", 0, "cen1: center of rectangle function"],
        2: ["sig1", 1, "sig1: standard deviation of rectangle function"],
        3: ["cen2", 0, "cen2: center of rectangle function"],
        4: ["sig2", 1, "sig2: standard deviation of rectangle function"],
        5: ["form", "linear", "form: "]
    },
}

XANES_PEAK_FIT_PARAM_BND_DICT = {
    "parabolic": {
        0: ["a", [-1e3, 1e3], "a: ampflitude in parabolic function"],
        1: ["b", [-1e3, 1e3], "b: center of parabolic function"],
        2: ["c", [-1e5, 1e5], "c: standard deviation of parabolic function"]
    },
    "gaussian": {
        0: ["amp", [-10, 10], "amp: ampflitude in gaussian function"],
        1: ["cen", [-2, 2], "cen: center of gaussian function"],
        2: ["sig", [0, 1e3], "sig: standard deviation of gaussian function"]
    },
    "lorentzian": {
        0: ["amp", [-10, 10], "amp: ampflitude in lorentzian function"],
        1: ["cen", [-2, 2], "cen: center of lorentzian function"],
        2: ["sig", [0, 1e3], "sig: standard deviation of lorentzian function"]
    },
    "damped_oscillator": {
        0: ["amp", [-10, 10], "amp: ampflitude in damped_oscillator function"],
        1: ["cen", [-2, 2], "cen: center of damped_oscillator function"],
        2: [
            "sig", [0, 1e3],
            "sig: standard deviation of damped_oscillator function"
        ]
    },
    "lognormal": {
        0: ["amp", [-10, 10], "amp: ampflitude in lognormal function"],
        1: ["cen", [-2, 2], "cen: center of lognormal function"],
        2: ["sig", [0, 1e3], "sig: standard deviation of lognormal function"]
    },
    "students_t": {
        0: ["amp", [-10, 10], "amp: ampflitude in students_t function"],
        1: ["cen", [-2, 2], "cen: center of students_t function"],
        2: ["sig", [0, 1e3], "sig: standard deviation of students_t function"]
    },
    "sine": {
        0: ["amp", [-10, 10], "amp: ampflitude in sine function"],
        1: ["frq", [0, 1], "frq: freqency in sine function"],
        2: ["shft", [0, 1], "shft: shift in sine function"]
    },
    "voigt": {
        0: ["amp", [-10, 10], "amp: ampflitude in voigt function"],
        1: ["cen", [-2, 2], "cen: center of voigt function"],
        2: ["sig", [0, 1e3], "sig: standard voigt of gaussian function"],
        3: ["gamma", [0, 1e3], "gamma: "]
    },
    "split_lorentzian": {
        0: ["amp", [-10, 10], "amp: ampflitude in split_lorentzian function"],
        1: ["cen", [-2, 2], "cen: center of split_lorentzian function"],
        2: [
            "sig", [0, 1e3],
            "sig: standard deviation of split_lorentzian function"
        ],
        3: [
            "sigr", [0, 1e3],
            "sigr: standard deviation of the right-hand side half in split_lorentzian function"
        ]
    },
    "pvoigt": {
        0: ["amp", [-10, 10], "amp: ampflitude in pvoigt function"],
        1: ["cen", [-2, 2], "cen: center of pvoigt function"],
        2: ["sig", [0, 1e3], "sig: standard pvoigt of gaussian function"],
        3: ["frac", [0, 1], "frac: "]
    },
    "moffat": {
        0: ["amp", [-10, 10], "amp: ampflitude in moffat function"],
        1: ["cen", [-2, 2], "cen: center of moffat function"],
        2: ["sig", [0, 1e3], "sig: standard moffat of gaussian function"],
        3: ["beta", [-1e3, 1e3], "beta: "]
    },
    "pearson7": {
        0: ["amp", [-10, 10], "amp: ampflitude in pearson7 function"],
        1: ["cen", [-2, 2], "cen: center of pearson7 function"],
        2: ["sig", [0, 1e3], "sig: standard pearson7 of gaussian function"],
        3: ["expo", [-1e2, 1e2], "expo: "]
    },
    "breit_wigner": {
        0: ["amp", [-10, 10], "amp: ampflitude in breit_wigner function"],
        1: ["cen", [-2, 2], "cen: center of breit_wigner function"],
        2:
        ["sig", [0, 1e3], "sig: standard breit_wigner of gaussian function"],
        3: ["q", [-10, 10], "q: "]
    },
    "dho": {
        0: ["amp", [-10, 10], "amp: ampflitude in dho function"],
        1: ["cen", [-2, 2], "cen: center of dho function"],
        2: ["sig", [0, 1e3], "sig: standard dho of gaussian function"],
        3: ["gama", [-10, 10], "gama: "]
    },
    "expgaussian": {
        0: ["amp", [-10, 10], "amp: ampflitude in expgaussian function"],
        1: ["cen", [-2, 2], "cen: center of expgaussian function"],
        2: ["sig", [0, 1e3], "sig: standard expgaussian of gaussian function"],
        3: ["gama", [-10, 10], "gama: "]
    },
    "donaich": {
        0: ["amp", [-10, 10], "amp: ampflitude in donaich function"],
        1: ["cen", [-2, 2], "cen: center of donaich function"],
        2: ["sig", [0, 1e3], "sig: standard donaich of gaussian function"],
        3: ["gama", [-10, 10], "gama: "]
    },
    "skewed_gaussian": {
        0: ["amp", [-10, 10], "amp: ampflitude in skewed_gaussian function"],
        1: ["cen", [-2, 2], "cen: center of skewed_gaussian function"],
        2: [
            "sig", [0, 1e3],
            "sig: standard skewed_gaussian of gaussian function"
        ],
        3: ["gama", 0, "gama: "]
    },
    "expsine": {
        0: ["amp", [-10, 10], "amp: ampflitude in expsine function"],
        1: ["frq", [0, 1], "frq: center of expsine function"],
        2: ["shft", [0, 1], "shft: standard expsine of gaussian function"],
        3: ["dec", [-10, 10], "dec: "]
    },
    "step": {
        0: ["amp", [-10, 10], "amp: ampflitude in step function"],
        1: ["cen", [-2, 2], "cen: center of step function"],
        2: ["sig", [0, 1e3], "sig: standard step of gaussian function"]
    },
    "skewed_voigt": {
        0: ["amp", [-10, 10], "amp: ampflitude in skewed_voigt function"],
        1: ["cen", [-2, 2], "cen: center of skewed_voigt function"],
        2:
        ["sig", [0, 1e3], "sig: standard skewed_voigt of gaussian function"],
        3: ["gamma", [0, 1e-3], "gamma: "],
        4: ["skew", [-10, 10], "skew: "]
    },
    "rectangle": {
        0: ["amp", [-10, 10], "amp: ampflitude in rectangle function"],
        1: ["cen1", [-2, 2], "cen1: center of rectangle function"],
        2:
        ["sig1", [0, 1e3], "sig1: standard deviation of rectangle function"],
        3: ["cen2", [-2, 2], "cen2: center of rectangle function"],
        4:
        ["sig2", [0, 1e3], "sig2: standard deviation of rectangle function"]
    }
}

XANES_EDGE_LINE_SHAPES = [
    'lorentzian', 'split_lorentzian', 'voigt', 'pvoigt', 'skewed_voigt',
    'gaussian', 'skewed_gaussian', 'expgaussian', 'sine', 'expsine'
]

XANES_EDGE_FIT_PARAM_DICT = {
    "gaussian": {
        0: ["amp", 1, "amp: ampflitude in gaussian function"],
        1: ["cen", 0, "cen: center of gaussian function"],
        2: ["sig", 1, "sig: standard deviation of gaussian function"]
    },
    "lorentzian": {
        0: ["amp", 1, "amp: ampflitude in lorentzian function"],
        1: ["cen", 0, "cen: center of lorentzian function"],
        2: ["sig", 1, "sig: standard deviation of lorentzian function"]
    },
    "sine": {
        0: ["amp", 1, "amp: ampflitude in sine function"],
        1: ["frq", 1, "frq: freqency in sine function"],
        2: ["shft", 0, "shft: shift in sine function"]
    },
    "voigt": {
        0: ["amp", 1, "amp: ampflitude in voigt function"],
        1: ["cen", 0, "cen: center of voigt function"],
        2: ["sig", 1, "sig: standard voigt of gaussian function"],
        3: ["gamma", 0, "gamma: "]
    },
    "split_lorentzian": {
        0: ["amp", 1, "amp: ampflitude in split_lorentzian function"],
        1: ["cen", 0, "cen: center of split_lorentzian function"],
        2: ["sig", 1, "sig: standard deviation of split_lorentzian function"],
        3: [
            "sigr", 1,
            "sigr: standard deviation of the right-hand side half in split_lorentzian function"
        ]
    },
    "pvoigt": {
        0: ["amp", 1, "amp: ampflitude in pvoigt function"],
        1: ["cen", 0, "cen: center of pvoigt function"],
        2: ["sig", 1, "sig: standard pvoigt of gaussian function"],
        3: ["frac", 0, "frac: "]
    },
    "expgaussian": {
        0: ["amp", 1, "amp: ampflitude in expgaussian function"],
        1: ["cen", 0, "cen: center of expgaussian function"],
        2: ["sig", 1, "sig: standard expgaussian of gaussian function"],
        3: ["gama", 1, "gama: "]
    },
    "skewed_gaussian": {
        0: ["amp", 1, "amp: ampflitude in skewed_gaussian function"],
        1: ["cen", 0, "cen: center of skewed_gaussian function"],
        2: ["sig", 1, "sig: standard skewed_gaussian of gaussian function"],
        3: ["gama", 0, "gama: "]
    },
    "expsine": {
        0: ["amp", 1, "amp: ampflitude in expsine function"],
        1: ["frq", 1, "frq:  width of expsine function"],
        2: ["shft", 0, "shft: center of gaussian function"],
        3: ["dec", 0, "dec: exponential decay factor"]
    },
    "skewed_voigt": {
        0: ["amp", 1, "amp: ampflitude in skewed_voigt function"],
        1: ["cen", 0, "cen: center of skewed_voigt function"],
        2: ["sig", 1, "sig: standard skewed_voigt of gaussian function"],
        3: ["gamma", 0, "gamma: "],
        4: ["skew", 0, "skew: "]
    }
}

XANES_EDGE_FIT_PARAM_BND_DICT = {
    "gaussian": {
        0: ["amp", [-10, 10], "amp: ampflitude in gaussian function"],
        1: ["cen", [0, 1], "cen: center of gaussian function"],
        2: ["sig", [0, 1e3], "sig: standard deviation of gaussian function"]
    },
    "lorentzian": {
        0: ["amp", [-10, 10], "amp: ampflitude in lorentzian function"],
        1: ["cen", [0, 1], "cen: center of lorentzian function"],
        2: ["sig", [0, 1e3], "sig: standard deviation of lorentzian function"]
    },
    "sine": {
        0: ["amp", [-10, 10], "amp: ampflitude in sine function"],
        1: ["frq", [0, 1], "frq: freqency in sine function"],
        2: ["shft", [0, 1], "shft: shift in sine function"]
    },
    "voigt": {
        0: ["amp", [-10, 10], "amp: ampflitude in voigt function"],
        1: ["cen", [0, 1], "cen: center of voigt function"],
        2: ["sig", [0, 1e3], "sig: standard voigt of gaussian function"],
        3: ["gamma", [0, 1e3], "gamma: "]
    },
    "split_lorentzian": {
        0: ["amp", [-10, 10], "amp: ampflitude in split_lorentzian function"],
        1: ["cen", [0, 1], "cen: center of split_lorentzian function"],
        2: [
            "sig", [0, 1e3],
            "sig: standard deviation of split_lorentzian function"
        ],
        3: [
            "sigr", [0, 1e3],
            "sigr: standard deviation of the right-hand side half in split_lorentzian function"
        ]
    },
    "pvoigt": {
        0: ["amp", [-10, 10], "amp: ampflitude in pvoigt function"],
        1: ["cen", [0, 1], "cen: center of pvoigt function"],
        2: ["sig", [0, 1e3], "sig: standard pvoigt of gaussian function"],
        3: ["frac", [0, 1], "frac: "]
    },
    "expgaussian": {
        0: ["amp", [-10, 10], "amp: ampflitude in expgaussian function"],
        1: ["cen", [0, 1], "cen: center of expgaussian function"],
        2: ["sig", [0, 1e3], "sig: standard expgaussian of gaussian function"],
        3: ["gama", [-10, 10], "gama: "]
    },
    "skewed_gaussian": {
        0: ["amp", [-10, 10], "amp: ampflitude in skewed_gaussian function"],
        1: ["cen", [0, 1], "cen: center of skewed_gaussian function"],
        2: [
            "sig", [0, 1e3],
            "sig: standard skewed_gaussian of gaussian function"
        ],
        3: ["gama", 0, "gama: "]
    },
    "expsine": {
        0: ["amp", [-10, 10], "amp: ampflitude in expsine function"],
        1: ["frq", [0, 1], "frq: center of expsine function"],
        2: ["shft", [0, 1], "shft: standard expsine of gaussian function"],
        3: ["dec", [-10, 10], "dec: "]
    },
    "skewed_voigt": {
        0: ["amp", [-10, 10], "amp: ampflitude in skewed_voigt function"],
        1: ["cen", [0, 1], "cen: center of skewed_voigt function"],
        2:
        ["sig", [0, 1e3], "sig: standard skewed_voigt of gaussian function"],
        3: ["gamma", [0, 1e-3], "gamma: "],
        4: ["skew", [-10, 10], "skew: "]
    }
}

XANES_FULL_SAVE_ITEM_OPTIONS = [
    'norm_spec', 'wl_pos_fit', 'wl_fit_err', 'wl_pos_dir',
    'wl_peak_height_dir', 'centroid_of_eng', 'centroid_of_eng_relative_to_wl',
    'weighted_attenuation', 'weighted_eng', 'edge50_pos_fit', 'edge50_pos_dir',
    'edge_pos_fit', 'edge_fit_err', 'edge_pos_dir', 'pre_edge_sd',
    'pre_edge_mean', 'post_edge_sd', 'post_edge_mean', 'pre_edge_fit_coef',
    'post_edge_fit_coef', 'wl_fit_coef', 'edge_fit_coef', 'lcf_fit',
    'lcf_fit_err'
]

XANES_FULL_SAVE_DEFAULT = [
    '', 'norm_spec', 'wl_pos_fit', 'wl_fit_err', 'centroid_of_eng',
    'centroid_of_eng_relative_to_wl', 'weighted_attenuation', 'weighted_eng',
    'edge50_pos_fit', 'edge_pos_fit', 'edge_fit_err', 'pre_edge_sd',
    'pre_edge_mean', 'post_edge_sd', 'post_edge_mean'
]

XANES_WL_SAVE_ITEM_OPTIONS = [
    'wl_fit_coef',
    'wl_fit_err',
    'wl_pos_dir',
    'wl_pos_fit',
    'centroid_of_eng',
    'centroid_of_eng_relative_to_wl',
    'weighted_attenuation',
    'weighted_eng',
]

XANES_WL_SAVE_DEFAULT = [
    '',
    'wl_fit_err',
    'wl_pos_fit',
    'weighted_attenuation',
]

TOMO_FLY_ITEM_DICT = {
    'img_bkg': {
        'description':
        'illumination beam reference images for normalizing sample images',
        'dtype': 'np.uint16'
    },
    'img_dark': {
        'description':
        'no-beam reference images for removing background noises in sample images',
        'dtype': 'np.uint16'
    },
    'img_tomo': {
        'description': 'sample images taken at different rotation angles',
        'dtype': 'np.uint16'
    },
    'angle': {
        'description': 'angles at which sample images are taken',
        'dtype': 'np.float64'
    }
}

TOMO_ZFLY_ITEM_DICT = {
    "data": {
        "description": "illumination beam reference images for normalizing sample images",
        "path": "/Exchange/data",
        "dtype": "np.uint16",
    },
    "flat": {
        "description": "no-beam reference images for removing background noises in sample images",
        "path": "/Exchange/flat",
        "dtype": "np.uint16",
    },
    "dark": {
        "description": "sample images taken at different rotation angles",
        "path": "/Exchange/dark",
        "dtype": "np.uint16",
    },
    "angle": {
        "description": "angles at which sample images are taken",
        "path": "/Exchange/angle",
        "dtype": "np.float64",
    },
}

XANES2D_ANA_ITEM_DICT = {
    'mask': {
        'description': 'a mask for isolating sample area from the background',
        'path': '/processed_XANES2D/gen_masks/{0}/{0}',
        'dtype': 'np.int8'
    },
    'registered_xanes2D': {
        'description': 'aligned 2D spectra image; it is a 3D data array',
        'path': '/registration_results/reg_results/registered_xanes2D',
        'dtype': 'np.float32'
    },
    'eng_list': {
        'description':
        'X-ray energy points at which 2D XANES images are taken',
        'path': '/registration_results/reg_results/eng_list',
        'dtype': 'np.float32'
    },
    'centroid_of_eng': {
        'description':
        'centroid of energy; can be used for making image masks to select just sample regions',
        'path': '/processed_XANES2D/proc_spectrum/centroid_of_eng',
        'dtype': 'np.float32'
    },
    'centroid_of_eng_relative_to_wl': {
        'description':
        'centroid of energy in a different way; can be used for making image masks to select just sample regions',
        'path':
        '/processed_XANES2D/proc_spectrum/centroid_of_eng_relative_to_wl',
        'dtype': 'np.float32'
    },
    'weighted_attenuation': {
        'description':
        'average attenuation over all energy points; it is the best for making image masks to select just sample regions by setting a global threshold',
        'path': '/processed_XANES2D/proc_spectrum/weighted_attenuation',
        'dtype': 'np.float32'
    },
    'weighted_eng': {
        'description':
        'averaged energy over all energy points; can be used for making image masks to select just sample regions',
        'path': '/processed_XANES2D/proc_spectrum/weighted_eng',
        'dtype': 'np.float32'
    },
    'whiteline_fit_err': {
        'description': 'whiteline fitting error',
        'path': '/processed_XANES2D/proc_spectrum/whiteline_fit_err',
        'dtype': 'np.float32'
    },
    'wl_fit_err': {
        'description': 'whiteline fitting error',
        'path': '/processed_XANES2D/proc_spectrum/wl_fit_err',
        'dtype': 'np.float32'
    },
    'whiteline_pos_fit': {
        'description': 'fitted whiteline positions',
        'path': '/processed_XANES2D/proc_spectrum/whiteline_pos_fit',
        'dtype': 'np.float32'
    },
    'wl_pos_fit': {
        'description': 'fitted whiteline positions',
        'path': '/processed_XANES2D/proc_spectrum/wl_pos_fit',
        'dtype': 'np.float32'
    },
    'wl_fit_coef': {
        'description': 'coefficients obtained from whiteline fitting',
        'path': '/processed_XANES2D/proc_spectrum/wl_fit_coef',
        'dtype': 'np.float32'
    },
    'wl_pos_dir': {
        'description':
        'whiteline positions measured directly from the experimental data; its precision may be strongly affected by the measurement quality and sampling rate of the energy points',
        'path': '/processed_XANES2D/proc_spectrum/wl_pos_dir',
        'dtype': 'np.float32'
    },
    'whiteline_pos_direct': {
        'description':
        'whiteline positions measured directly from the experimental data; its precision may be strongly affected by the measurement quality and sampling rate of the energy points',
        'path': '/processed_XANES2D/proc_spectrum/whiteline_pos_direct',
        'dtype': 'np.float32'
    },
    'norm_spec': {
        'description':
        'normalized spectra; it takes standard XANES spectrum normalization procedure, subtracting the background before the pre-edge then normalized by the fitted straight line in the post-edge range',
        'path': '/processed_XANES2D/proc_spectrum/norm_spec',
        'dtype': 'np.float32'
    },
    'normalized_spectrum': {
        'description':
        'normalized spectra; it takes standard XANES spectrum normalization procedure, subtracting the background before the pre-edge then normalized by the fitted straight line in the post-edge range',
        'path': '/processed_XANES2D/proc_spectrum/normalized_spectrum',
        'dtype': 'np.float32'
    },
    'wl_peak_height_dir': {
        'description':
        'the whiteline peak height measured directly at the energy sampling point where the x-ray attenuation is strongest; the result may be strongly affected by the measurement quality so prone to the noises',
        'path': '/processed_XANES2D/proc_spectrum/wl_peak_height_dir',
        'dtype': 'np.float32'
    },
    'whiteline_peak_height_direct': {
        'description':
        'the whiteline peak height measured directly at the energy sampling point where the x-ray attenuation is strongest; the result may be strongly affected by the measurement quality so prone to the noises',
        'path':
        '/processed_XANES2D/proc_spectrum/whiteline_peak_height_direct',
        'dtype': 'np.float32'
    },
    'edge50_pos_fit': {
        'description':
        'the energy position where the X-ray attenuation is 50% of that at the whiteline peak position; the calculation is based on the fitted whiteline peak and fitted X-ray absorption edge',
        'path': '/processed_XANES2D/proc_spectrum/edge50_pos_fit',
        'dtype': 'np.float32'
    },
    'edge0.5_pos_fit': {
        'description':
        'the energy position where the X-ray attenuation is 50% of that at the whiteline peak position; the calculation is based on the fitted whiteline peak and fitted X-ray absorption edge',
        'path': '/processed_XANES2D/proc_spectrum/edge0.5_pos_fit',
        'dtype': 'np.float32'
    },
    'edge50_pos_dir': {
        'description':
        'the energy position where the X-ray attenuation is 50% of that at the whiteline peak position; the calculation is based on the direct measurements of the whiteline and X-ray absorption edge; it may be strongly affected the noises',
        'path': '/processed_XANES2D/proc_spectrum/edge50_pos_dir',
        'dtype': 'np.float32'
    },
    'edge0.5_pos_dir': {
        'description':
        'the energy position where the X-ray attenuation is 50% of that at the whiteline peak position; the calculation is based on the direct measurements of the whiteline and X-ray absorption edge; it may be strongly affected the noises',
        'path': '/processed_XANES2D/proc_spectrum/edge0.5_pos_dir',
        'dtype': 'np.float32'
    },
    'edge0.5_pos_direct': {
        'description':
        'the energy position where the X-ray attenuation is 50% of that at the whiteline peak position; the calculation is based on the direct measurements of the whiteline and X-ray absorption edge; it may be strongly affected the noises',
        'path': '/processed_XANES2D/proc_spectrum/edge0.5_pos_direct',
        'dtype': 'np.float32'
    },
    'edge_pos_fit': {
        'description':
        'the x-ray absorption edge position defined as the maximum in the derivative of x-ray absorption edge; the calculation is based on the fitted X-ray absorption edge',
        'path': '/processed_XANES2D/proc_spectrum/edge_pos_fit',
        'dtype': 'np.float32'
    },
    'edge_fit_err': {
        'description': 'the fitting error in fitted x-ray absorption edge map',
        'path': '/processed_XANES2D/proc_spectrum/edge_fit_err',
        'dtype': 'np.float32'
    },
    'edge_fit_coef': {
        'description':
        'the fitting coefficients of the fitted x-ray absorption edge map',
        'path': '/processed_XANES2D/proc_spectrum/edge_fit_coef',
        'dtype': 'np.float32'
    },
    'edge_pos_dir': {
        'description':
        'the edge postions at each pixel calculated directly based on measured x-ray absorption spectra',
        'path': '/processed_XANES2D/proc_spectrum/edge_pos_dir',
        'dtype': 'np.float32'
    },
    'edge_pos_direct': {
        'description':
        'the edge postions at each pixel calculated directly based on measured x-ray absorption spectra',
        'path': '/processed_XANES2D/proc_spectrum/edge_pos_dir',
        'dtype': 'np.float32'
    },
    'edge_jump_filter': {
        'description':
        'a map over all pixels that measures the jump from the background section to the post-edge and normalized to the standard deviation between the measured values in the background section; it can be used as mask filter to select only sample regions',
        'path': '/processed_XANES2D/proc_spectrum/edge_jump_filter',
        'dtype': 'np.float32'
    },
    'edge_offset_filter': {
        'description':
        'it measures how parallel between the background section and the post-edge section in a spectrum; if they cross each other in the measurement energy range, it may indicate the measurement quality is bad; this filter provides such measurement at each pixel; it can be used as mask filter to select only sample regions',
        'path': '/processed_XANES2D/proc_spectrum/edge_offset_filter',
        'dtype': 'np.float32'
    },
    'pre_edge_sd': {
        'description':
        'standard deviation map over all pixels in the background region',
        'path': '/processed_XANES2D/proc_spectrum/pre_edge_sd',
        'dtype': 'np.float32'
    },
    'pre_edge_mean': {
        'description': 'the mean map over all pixels in the background region',
        'path': '/processed_XANES2D/proc_spectrum/pre_edge_mean',
        'dtype': 'np.float32'
    },
    'post_edge_sd': {
        'description':
        'standard deviation map over all pixels in the post-edge region',
        'path': '/processed_XANES2D/proc_spectrum/post_edge_sd',
        'dtype': 'np.float32'
    },
    'post_edge_mean': {
        'description': 'the mean map over all pixels in the post-edge region',
        'path': '/processed_XANES2D/proc_spectrum/post_edge_mean',
        'dtype': 'np.float32'
    },
    'pre_edge_fit_coef': {
        'description':
        'the fitting coefficients of the fitted background section',
        'path': '/processed_XANES2D/proc_spectrum/pre_edge_fit_coef',
        'dtype': 'np.float32'
    },
    'post_edge_fit_coef': {
        'description':
        'the fitting coefficients of the fitted post-edge section',
        'path': '/processed_XANES2D/proc_spectrum/post_edge_fit_coef',
        'dtype': 'np.float32'
    },
    'lcf_fit': {
        'description':
        'the fitting coefficients of the linear combination fitting of the spectra at all pixels',
        'path': '/processed_XANES2D/proc_spectrum/lcf_fit',
        'dtype': 'np.float32'
    },
    'lcf_fit_err': {
        'description':
        'the fitting errors of the linear combination fitting of the spectra at all pixels',
        'path': '/processed_XANES2D/proc_spectrum/lcf_fit_err',
        'dtype': 'np.float32'
    },
    'diff_img': {
        'description':
        'the differential image between two registered images at two different X-ray energies; it is used for discriminating the existence of certain elements in the sample',
        'path': '/processed_diff_imaging/proc_rlt/diff_img',
        'dtype': 'np.float32'
    },
}

XANES3D_ANA_ITEM_DICT = {
    'mask': {
        'description': 'a mask for isolating sample area from the background',
        'path': '/processed_XANES3D/gen_masks/{0}/{0}',
        'dtype': 'np.int8'
    },
    'registered_xanes3D': {
        'description': 'aligned 3D spectra image; it is a 4D data array',
        'path': '/registration_results/reg_results/registered_xanes3D',
        'dtype': 'np.float32'
    },
    'eng_list': {
        'description':
        'X-ray energy points at which tomography scans are taken',
        'path': '/registration_results/reg_results/eng_list',
        'dtype': 'np.float32'
    },
    'centroid_of_eng': {
        'description':
        'centroid of energy; can be used for making image masks to select just sample regions',
        'path': '/processed_XANES3D/proc_spectrum/centroid_of_eng',
        'dtype': 'np.float32'
    },
    'centroid_of_eng_relative_to_wl': {
        'description':
        'centroid of energy in a different way; can be used for making image masks to select just sample regions',
        'path':
        '/processed_XANES3D/proc_spectrum/centroid_of_eng_relative_to_wl',
        'dtype': 'np.float32'
    },
    'weighted_attenuation': {
        'description':
        'average attenuation over all energy points; it is the best for making image masks to select just sample regions by setting a global threshold',
        'path': '/processed_XANES3D/proc_spectrum/weighted_attenuation',
        'dtype': 'np.float32'
    },
    'weighted_eng': {
        'description':
        'averaged energy over all energy points; can be used for making image masks to select just sample regions',
        'path': '/processed_XANES3D/proc_spectrum/weighted_eng',
        'dtype': 'np.float32'
    },
    'whiteline_fit_err': {
        'description': 'whiteline fitting error',
        'path': '/processed_XANES3D/proc_spectrum/whiteline_fit_err',
        'dtype': 'np.float32'
    },
    'wl_fit_err': {
        'description': 'whiteline fitting error',
        'path': '/processed_XANES3D/proc_spectrum/wl_fit_err',
        'dtype': 'np.float32'
    },
    'whiteline_pos_fit': {
        'description': 'fitted whiteline positions',
        'path': '/processed_XANES3D/proc_spectrum/whiteline_pos_fit',
        'dtype': 'np.float32'
    },
    'wl_pos_fit': {
        'description': 'fitted whiteline positions',
        'path': '/processed_XANES3D/proc_spectrum/wl_pos_fit',
        'dtype': 'np.float32'
    },
    'wl_fit_coef': {
        'description': 'coefficients obtained from whiteline fitting',
        'path': '/processed_XANES3D/proc_spectrum/wl_fit_coef',
        'dtype': 'np.float32'
    },
    'wl_pos_dir': {
        'description':
        'whiteline positions measured directly from the experimental data; its precision may be strongly affected by the measurement quality and sampling rate of the energy points',
        'path': '/processed_XANES3D/proc_spectrum/wl_pos_dir',
        'dtype': 'np.float32'
    },
    'whiteline_pos_direct': {
        'description':
        'whiteline positions measured directly from the experimental data; its precision may be strongly affected by the measurement quality and sampling rate of the energy points',
        'path': '/processed_XANES3D/proc_spectrum/whiteline_pos_direct',
        'dtype': 'np.float32'
    },
    'norm_spec': {
        'description':
        'normalized spectra; it takes standard XANES spectrum normalization procedure, subtracting the background before the pre-edge then normalized by the fitted straight line in the post-edge range',
        'path': '/processed_XANES3D/proc_spectrum/norm_spec',
        'dtype': 'np.float32'
    },
    'normalized_spectrum': {
        'description':
        'normalized spectra; it takes standard XANES spectrum normalization procedure, subtracting the background before the pre-edge then normalized by the fitted straight line in the post-edge range',
        'path': '/processed_XANES3D/proc_spectrum/normalized_spectrum',
        'dtype': 'np.float32'
    },
    'wl_peak_height_dir': {
        'description':
        'the whiteline peak height measured directly at the energy sampling point where the x-ray attenuation is strongest; the result may be strongly affected by the measurement quality so prone to the noises',
        'path': '/processed_XANES3D/proc_spectrum/wl_peak_height_dir',
        'dtype': 'np.float32'
    },
    'whiteline_peak_height_direct': {
        'description':
        'the whiteline peak height measured directly at the energy sampling point where the x-ray attenuation is strongest; the result may be strongly affected by the measurement quality so prone to the noises',
        'path':
        '/processed_XANES3D/proc_spectrum/whiteline_peak_height_direct',
        'dtype': 'np.float32'
    },
    'edge50_pos_fit': {
        'description':
        'the energy position where the X-ray attenuation is 50% of that at the whiteline peak position; the calculation is based on the fitted whiteline peak and fitted X-ray absorption edge',
        'path': '/processed_XANES3D/proc_spectrum/edge50_pos_fit',
        'dtype': 'np.float32'
    },
    'edge0.5_pos_fit': {
        'description':
        'the energy position where the X-ray attenuation is 50% of that at the whiteline peak position; the calculation is based on the fitted whiteline peak and fitted X-ray absorption edge',
        'path': '/processed_XANES3D/proc_spectrum/edge0.5_pos_fit',
        'dtype': 'np.float32'
    },
    'edge50_pos_dir': {
        'description':
        'the energy position where the X-ray attenuation is 50% of that at the whiteline peak position; the calculation is based on the direct measurements of the whiteline and X-ray absorption edge; it may be strongly affected the noises',
        'path': '/processed_XANES3D/proc_spectrum/edge50_pos_dir',
        'dtype': 'np.float32'
    },
    'edge0.5_pos_dir': {
        'description':
        'the energy position where the X-ray attenuation is 50% of that at the whiteline peak position; the calculation is based on the direct measurements of the whiteline and X-ray absorption edge; it may be strongly affected the noises',
        'path': '/processed_XANES3D/proc_spectrum/edge0.5_pos_dir',
        'dtype': 'np.float32'
    },
    'edge0.5_pos_direct': {
        'description':
        'the energy position where the X-ray attenuation is 50% of that at the whiteline peak position; the calculation is based on the direct measurements of the whiteline and X-ray absorption edge; it may be strongly affected the noises',
        'path': '/processed_XANES3D/proc_spectrum/edge0.5_pos_direct',
        'dtype': 'np.float32'
    },
    'edge_pos_fit': {
        'description':
        'the x-ray absorption edge position defined as the maximum in the derivative of x-ray absorption edge; the calculation is based on the fitted X-ray absorption edge',
        'path': '/processed_XANES3D/proc_spectrum/edge_pos_fit',
        'dtype': 'np.float32'
    },
    'edge_fit_err': {
        'description': 'the fitting error in fitted x-ray absorption edge map',
        'path': '/processed_XANES3D/proc_spectrum/edge_fit_err',
        'dtype': 'np.float32'
    },
    'edge_fit_coef': {
        'description':
        'the fitting coefficients of the fitted x-ray absorption edge map',
        'path': '/processed_XANES3D/proc_spectrum/edge_fit_coef',
        'dtype': 'np.float32'
    },
    'edge_pos_dir': {
        'description':
        'the edge postions at each pixel calculated directly based on measured x-ray absorption spectra',
        'path': '/processed_XANES3D/proc_spectrum/edge_pos_dir',
        'dtype': 'np.float32'
    },
    'edge_pos_direct': {
        'description':
        'the edge postions at each pixel calculated directly based on measured x-ray absorption spectra',
        'path': '/processed_XANES3D/proc_spectrum/edge_pos_direct',
        'dtype': 'np.float32'
    },
    'edge_jump_filter': {
        'description':
        'a map over all pixels that measures the jump from the background section to the post-edge and normalized to the standard deviation between the measured values in the background section; it can be used as mask filter to select only sample regions',
        'path': '/processed_XANES3D/proc_spectrum/edge_jump_filter',
        'dtype': 'np.float32'
    },
    'edge_offset_filter': {
        'description':
        'it measures how parallel between the background section and the post-edge section in a spectrum; if they cross each other in the measurement energy range, it may indicate the measurement quality is bad; this filter provides such measurement at each pixel; it can be used as mask filter to select only sample regions',
        'path': '/processed_XANES3D/proc_spectrum/edge_offset_filter',
        'dtype': 'np.float32'
    },
    'pre_edge_sd': {
        'description':
        'standard deviation map over all pixels in the background region',
        'path': '/processed_XANES3D/proc_spectrum/pre_edge_sd',
        'dtype': 'np.float32'
    },
    'pre_edge_mean': {
        'description': 'the mean map over all pixels in the background region',
        'path': '/processed_XANES3D/proc_spectrum/pre_edge_mean',
        'dtype': 'np.float32'
    },
    'post_edge_sd': {
        'description':
        'standard deviation map over all pixels in the post-edge region',
        'path': '/processed_XANES3D/proc_spectrum/post_edge_sd',
        'dtype': 'np.float32'
    },
    'post_edge_mean': {
        'description': 'the mean map over all pixels in the post-edge region',
        'path': '/processed_XANES3D/proc_spectrum/post_edge_mean',
        'dtype': 'np.float32'
    },
    'pre_edge_fit_coef': {
        'description':
        'the fitting coefficients of the fitted background section',
        'path': '/processed_XANES3D/proc_spectrum/pre_edge_fit_coef',
        'dtype': 'np.float32'
    },
    'post_edge_fit_coef': {
        'description':
        'the fitting coefficients of the fitted post-edge section',
        'path': '/processed_XANES3D/proc_spectrum/post_edge_fit_coef',
        'dtype': 'np.float32'
    },
    'lcf_fit': {
        'description':
        'the fitting coefficients of the linear combination fitting of the spectra at all pixels',
        'path': '/processed_XANES3D/proc_spectrum/lcf_fit',
        'dtype': 'np.float32'
    },
    'lcf_fit_err': {
        'description':
        'the fitting errors of the linear combination fitting of the spectra at all pixels',
        'path': '/processed_XANES3D/proc_spectrum/lcf_fit_err',
        'dtype': 'np.float32'
    },
    'diff_img': {
        'description':
        'the differential image between two registered images at two different X-ray energies; it is used for discriminating the existence of certain elements in the sample',
        'path': '/processed_diff_imaging/proc_rlt/diff_img',
        'dtype': 'np.float32'
    },
}

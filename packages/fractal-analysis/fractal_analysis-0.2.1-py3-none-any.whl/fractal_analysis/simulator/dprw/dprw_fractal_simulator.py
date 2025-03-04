from typing import Callable

import numpy as np
import scipy
from fractal_analysis.simulator.wood_chan.wood_chan_fractal_simulator import WoodChanFgnSimulator


class DprwSelfSimilarFractalSimulator(WoodChanFgnSimulator):
    """
        Source paper: Y. Ding, Q. Peng, G. Ren, W. Wu "Simulation of Self-similar Processes using Lamperti Transformation
                      with An Application to Generate Multifractional Brownian Motion" todo: add source paper link
        Main idea: we use Lamperti transform to transfer a self-similar process to a stationary process, and
                   simulate the stationary process using circulant embedding approach (Wood, A.T.A., Chan, G., 1994.
                   Simulation of stationary Gaussian processes in [0, 1]^d. Journal of computational and graphical
                   statistics 3, 409–432). Then a subsequence of the simulated stationary process is convert back to
                   the series. Because we need to use its subsequence, the stationary process needs to have a longer
                   length (lamperti_series_len_multiplier*series_len) than the series.
    """

    def __init__(self, sample_size: int, hurst_parameter: float, covariance_func: Callable,
                 lamperti_multiplier: int = 5,
                 tmax: float = 1, std_const: float = 1):
        """
            sample_size: is the length of samples generated; it is a positive integer.
            hurst_parameter: is a real value in (0:1) that governs both the pointwise regularity and the shape around 0 of the power spectrum.
            covariance_func: covariance function of the self similar process
            lamperti_multiplier: an integer used for Lamperti transform; bigger value (usually <=10) provides more accuracy; default value is 5
            tmax: generates a self similar process using a specific size of time support, i.e. the time runs in [0,tmax]; if tmax is not specified, the default value is tmax = 1.
            std_const: generates a self similar process using a specific standard deviation at instant t = 1; if std_const is not specified, the default value is std_const = 1.
        """

        super().__init__(sample_size=sample_size, hurst_parameter=hurst_parameter, tmax=tmax, std_const=std_const)
        self.covariance_func = covariance_func
        if not isinstance(lamperti_multiplier, int) and lamperti_multiplier <= 0:
            raise ValueError(f'lamperti_multiplier must be a positive integer.')
        self.lamperti_multiplier = lamperti_multiplier
        self.lamperti_series_len = self.lamperti_multiplier * self.sample_size

    @property
    def _lamperti_subseq_index(self):
        seires_step = self.tmax / self.sample_size
        series_t = np.arange(start=seires_step, stop=self.tmax + seires_step, step=seires_step)
        # shifting negative time index to positive time index
        log_series_t = np.log(series_t) + np.abs(np.log(series_t[0]))
        max_log_series_exp_t = np.max(log_series_t)
        lamperti_subseq_index = np.rint(log_series_t * self.lamperti_series_len / max_log_series_exp_t) - 1
        lamperti_subseq_index[0] = 0
        return series_t, lamperti_subseq_index.astype(int)

    def get_self_similar_process(self, is_plot=False, method_name=None, series_name=None, seed=None,
                                 plot_path: str = None):
        series_t, lamperti_subseq_index = self._lamperti_subseq_index
        lamp_fgn = self.get_fgn(seed=seed, N=self.lamperti_series_len, cov=self.covariance_func)
        lamp_fgn = lamp_fgn - lamp_fgn[0]
        self_similar = series_t ** self.hurst_parameter * lamp_fgn[lamperti_subseq_index]
        if is_plot:
            self.plot(series=self_similar, method_name=method_name, series_name=series_name, save_path=plot_path)
        return self_similar


class DprwSubFbmSimulator(DprwSelfSimilarFractalSimulator):
    """
        Source paper: Y. Ding, Q. Peng, G. Ren, W. Wu "Simulation of Self-similar Processes using Lamperti Transformation
                      with An Application to Generate Multifractional Brownian Motion" todo: add source paper link
        Main idea: we use Lamperti transform to transfer sub-FBM (self-similar process) to a stationary process, and
                   simulate the stationary process using circulant embedding approach (Wood, A.T.A., Chan, G., 1994.
                   Simulation of stationary Gaussian processes in [0, 1]^d. Journal of computational and graphical
                   statistics 3, 409–432). Then a subsequence of the simulated stationary process is convert back to
                   the sub-FBM series. Because we need to use its subsequence, the stationary process needs to have a longer
                   length (lamperti_series_len_multiplier*series_len) than the sub-FBM series.
    """

    def __init__(self, sample_size: int, hurst_parameter: float,
                 lamperti_multiplier: int = 5, tmax: float = 1, std_const: float = 1):
        """
            sample_size: is the length of samples generated; it is a positive integer.
            hurst_parameter: is a real value in (0:1) that governs both the pointwise regularity and the shape around 0 of the power spectrum.
            lamperti_multiplier: used for Lamperti transform; bigger value (usually <=10) provides more accuracy; default value is 5
            tmax: generates sub-FBM using a specific size of time support, i.e. the time runs in [0,tmax]; if tmax is not specified, the default value is tmax = 1.
            std_const: generates sub-FBM using a specific standard deviation at instant t = 1; if std_const is not specified, the default value is std_const = 1.
        """

        super().__init__(sample_size=sample_size, hurst_parameter=hurst_parameter,
                         covariance_func=self.sub_fbm_covariance_func,
                         lamperti_multiplier=lamperti_multiplier, tmax=tmax, std_const=std_const)

    def sub_fbm_covariance_func(self, k):
        h2 = 2 * self.hurst_parameter
        n = self.sample_size
        k_h_n = k * self.hurst_parameter / n
        k_n_2 = k / n / 2
        v = n ** k_h_n + n ** (-k_h_n) - 0.5 * (
                (n ** k_n_2 + n ** (-k_n_2)) ** h2 + np.abs(n ** k_n_2 - n ** (-k_n_2)) ** h2)
        return v

    def get_sub_fbm(self, is_plot=False, seed=None, plot_path: str = None):
        sub_fbm = self.get_self_similar_process(is_plot=is_plot, seed=seed, method_name='DPRW', series_name='Sub-FBM',
                                                plot_path=plot_path)
        return sub_fbm


class DprwBiFbmSimulator(DprwSelfSimilarFractalSimulator):
    """
        Source paper: Y. Ding, Q. Peng, G. Ren, W. Wu "Simulation of Self-similar Processes using Lamperti Transformation
                      with An Application to Generate Multifractional Brownian Motion" todo: add source paper link
        Main idea: we use Lamperti transform to transfer Bi-FBM (self-similar process) to a stationary process, and
                   simulate the stationary process using circulant embedding approach (Wood, A.T.A., Chan, G., 1994.
                   Simulation of stationary Gaussian processes in [0, 1]^d. Journal of computational and graphical
                   statistics 3, 409–432). Then a subsequence of the simulated stationary process is convert back to
                   the Bi-FBM series. Because we need to use its subsequence, the stationary process needs to have a longer
                   length (lamperti_series_len_multiplier*series_len) than the Bi-FBM series.
    """

    def __init__(self, sample_size: int, hurst_parameter: float, bi_factor: float,
                 lamperti_multiplier: int = 5, tmax: float = 1, std_const: float = 1):
        """
            sample_size: is the length of samples generated; it is a positive integer.
            hurst_parameter: is a real value in (0:1) that governs both the pointwise regularity and the shape around 0 of the power spectrum.
            lamperti_multiplier: used for Lamperti transform; bigger value (usually <=10) provides more accuracy; default value is 5
            bi_factor: (0,1]; when it is 1, the series becomes FBM.
            tmax: generates bi-FBM using a specific size of time support, i.e. the time runs in [0,tmax]; if tmax is not specified, the default value is tmax = 1.
            std_const: generates bi-FBM using a specific standard deviation at instant t = 1; if std_const is not specified, the default value is std_const = 1.
        """

        super().__init__(sample_size=sample_size, hurst_parameter=hurst_parameter,
                         covariance_func=self.bi_fbm_covariance_func,
                         lamperti_multiplier=lamperti_multiplier, tmax=tmax, std_const=std_const)
        self.bi_factor = bi_factor

    def bi_fbm_covariance_func(self, k):
        n = self.sample_size
        k_h_n = k * self.hurst_parameter / n
        k_n_2 = k / n / 2
        h2 = 2 * self.hurst_parameter
        v = ((n ** k_h_n + n ** (-k_h_n)) ** self.bi_factor - np.abs(n ** k_n_2 - n ** (-k_n_2)) ** (
                h2 * self.bi_factor)) / (2 ** self.bi_factor)
        return v

    def get_bi_fbm(self, is_plot=False, seed=None, plot_path: str = None):
        bi_fbm = self.get_self_similar_process(is_plot=is_plot, seed=seed, method_name='DPRW',
                                               series_name=f'{self.bi_factor} Bi-FBM', plot_path=plot_path)
        return bi_fbm


class DprwTriFbmSimulator(DprwSelfSimilarFractalSimulator):
    """
        Source paper: Y. Ding, Q. Peng, G. Ren, W. Wu "Simulation of Self-similar Processes using Lamperti Transformation
                      with An Application to Generate Multifractional Brownian Motion" todo: add source paper link
        Main idea: we use Lamperti transform to transfer tri-FBM (self-similar process) to a stationary process, and
                   simulate the stationary process using circulant embedding approach (Wood, A.T.A., Chan, G., 1994.
                   Simulation of stationary Gaussian processes in [0, 1]^d. Journal of computational and graphical
                   statistics 3, 409–432). Then a subsequence of the simulated stationary process is convert back to
                   the tri-FBM series. Because we need to use its subsequence, the stationary process needs to have a longer
                   length (lamperti_series_len_multiplier*series_len) than the tri-FBM series.
    """

    def __init__(self, sample_size: int, hurst_parameter: float, tri_factor: float,
                 lamperti_multiplier: int = 5, tmax: float = 1, std_const: float = 1):
        """
            sample_size: is the length of samples generated; it is a positive integer.
            hurst_parameter: is a real value in (0:1) that governs both the pointwise regularity and the shape around 0 of the power spectrum.
            lamperti_multiplier: used for Lamperti transform; bigger value (usually <=10) provides more accuracy; default value is 5
            tri_factor: (0,1]; when it is 1, the series becomes FBM with a constant multiplier 2.
            tmax: generates tri-FBM using a specific size of time support, i.e. the time runs in [0,tmax]; if tmax is not specified, the default value is tmax = 1.
            std_const: generates tri-FBM using a specific standard deviation at instant t = 1; if std_const is not specified, the default value is std_const = 1.
        """

        super().__init__(sample_size=sample_size, hurst_parameter=hurst_parameter,
                         covariance_func=self.tri_fbm_covariance_func,
                         lamperti_multiplier=lamperti_multiplier, tmax=tmax, std_const=std_const)
        self.tri_factor = tri_factor

    def tri_fbm_covariance_func(self, k):
        n = self.sample_size
        k_h_f_n = k * self.hurst_parameter * self.tri_factor / n
        k_n_2 = k / n / 2
        h2 = 2 * self.hurst_parameter
        v = n ** k_h_f_n + n ** (-k_h_f_n) - np.abs(n ** k_n_2 - n ** (-k_n_2)) ** (
                h2 * self.tri_factor)
        return v

    def get_tri_fbm(self, is_plot=False, seed=None, plot_path: str = None):
        tri_fbm = self.get_self_similar_process(is_plot=is_plot, seed=seed, method_name='DPRW',
                                                series_name=f'{self.tri_factor} Tri-FBM', plot_path=plot_path)
        return tri_fbm


class DprwFbmSimulator(DprwBiFbmSimulator):
    """
        Source paper: Y. Ding, Q. Peng, G. Ren, W. Wu "Simulation of Self-similar Processes using Lamperti Transformation
                      with An Application to Generate Multifractional Brownian Motion" todo: add source paper link
        Main idea: we use Lamperti transform to transfer FBM (self-similar process) to a stationary process, and
                   simulate the stationary process using circulant embedding approach (Wood, A.T.A., Chan, G., 1994.
                   Simulation of stationary Gaussian processes in [0, 1]^d. Journal of computational and graphical
                   statistics 3, 409–432). Then a subsequence of the simulated stationary process is convert back to
                   the FBM series. Because we need to use its subsequence, the stationary process needs to have a longer
                   length (lamperti_series_len_multiplier*series_len) than the FBM series.
    """

    def __init__(self, sample_size: int, hurst_parameter: float,
                 lamperti_multiplier: int = 5, tmax: float = 1, std_const: float = 1):
        """
            sample_size: is the length of samples generated; it is a positive integer.
            hurst_parameter: is a real value in (0:1) that governs both the pointwise regularity and the shape around 0 of the power spectrum.
            lamperti_multiplier: used for Lamperti transform; bigger value (usually <=10) provides more accuracy; default value is 5
            tmax: generates FBM using a specific size of time support, i.e. the time runs in [0,tmax]; if tmax is not specified, the default value is tmax = 1.
            std_const: generates FBM using a specific standard deviation at instant t = 1; if std_const is not specified, the default value is std_const = 1.
        """

        super().__init__(sample_size=sample_size, hurst_parameter=hurst_parameter, bi_factor=1,
                         lamperti_multiplier=lamperti_multiplier, tmax=tmax, std_const=std_const)

    def get_fbm(self, is_plot=False, seed=None, plot_path: str = None):
        fbm = self.get_self_similar_process(is_plot=is_plot, seed=seed, method_name='DPRW', series_name='FBM',
                                            plot_path=plot_path)
        return fbm


class DprwNegFbmSimulator(DprwSelfSimilarFractalSimulator):
    """
        Source paper: Y. Ding, Q. Peng, G. Ren "Simulation of Self-similar Processes using Lamperti Transformation
                      with An Application to Generate Multifractional Brownian Motion" todo: add source paper link
        Main idea: we use Lamperti transform to transfer Neg-FBM (self-similar process) to a stationary process, and
                   simulate the stationary process using circulant embedding approach (Wood, A.T.A., Chan, G., 1994.
                   Simulation of stationary Gaussian processes in [0, 1]^d. Journal of computational and graphical
                   statistics 3, 409–432). Then a subsequence of the simulated stationary process is convert back to
                   the Neg-FBM series. Because we need to use its subsequence, the stationary process needs to have a longer
                   length (lamperti_series_len_multiplier*series_len) than the Neg-FBM series.
    """

    def __init__(self, sample_size: int, hurst_parameter: float,
                 lamperti_multiplier: int = 5, tmax: float = 1, std_const: float = 1):
        """
            sample_size: is the length of samples generated; it is a positive integer.
            hurst_parameter: is a real value in (0:1) that governs both the pointwise regularity and the shape around 0 of the power spectrum.
            lamperti_multiplier: used for Lamperti transform; bigger value (usually <=10) provides more accuracy; default value is 5
            tmax: generates Neg-FBM using a specific size of time support, i.e. the time runs in [0,tmax]; if tmax is not specified, the default value is tmax = 1.
            std_const: generates Neg-FBM using a specific standard deviation at instant t = 1; if std_const is not specified, the default value is std_const = 1.
        """

        super().__init__(sample_size=sample_size, hurst_parameter=hurst_parameter,
                         covariance_func=self.neg_fbm_covariance_func,
                         lamperti_multiplier=lamperti_multiplier, tmax=tmax, std_const=std_const)

    def neg_fbm_covariance_func(self, k):
        n = self.sample_size
        h = self.hurst_parameter
        h2 = 2 * h
        numerator = (scipy.special.gamma(h + 0.5)) ** 2 * (n ** (h * (k / n)) + n ** (h * (-k / n)) - (
                (np.abs(1 - n ** (-k / n))) ** h) * (np.abs(1 - n ** (k / n))) ** h)
        denominator = 2 * scipy.special.gamma(h2 + 1) * np.sin(h * np.pi)
        term = -n ** (-np.abs(k / n) / 2) / (h + 0.5)
        summ = scipy.special.hyp2f1(0.5 - h, 1, h + 3 / 2, n ** (-np.abs(k / n)))
        v = numerator / denominator + term * summ
        v[0] = (scipy.special.gamma(h + 0.5) ** 2) / (scipy.special.gamma(h2 + 1) * np.sin(h * np.pi)) - 1 / h2
        return v

    def get_neg_fbm(self, is_plot=False, seed=None, plot_path: str = None):
        neg_fbm = self.get_self_similar_process(is_plot=is_plot, seed=seed, method_name='DPRW', series_name='Neg-FBM',
                                                plot_path=plot_path)
        return neg_fbm

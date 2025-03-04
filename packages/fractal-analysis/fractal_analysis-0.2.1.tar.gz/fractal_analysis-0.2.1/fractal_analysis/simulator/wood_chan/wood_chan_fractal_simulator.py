import math
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft


class WoodChanFgnSimulator:
    def __init__(self, sample_size: int, hurst_parameter: float, tmax: float = 1, std_const: float = 1):
        """
            sample_size: is the length of samples generated; it is a positive integer.
            hurst_parameter: is a real value in (0:1) that governs both the pointwise regularity and the shape around 0 of the power spectrum.
            tmax: generates FGN using a specific size of time support, i.e. the time runs in [0,tmax]; if tmax is not specified, the default value is tmax = 1.
            std_const: generates FGN using a specific standard deviation at instant t = 1; if std_const is not specified, the default value is std_const = 1.
        """
        self.sample_size = sample_size
        if self.sample_size <= 0:
            raise ValueError(f'sample_size must be a positive integer.')
        self.hurst_parameter = hurst_parameter
        if not (0 < self.hurst_parameter < 1):
            raise ValueError(f'hurst_parameter must be in range (0, 1).')
        self.tmax = tmax
        if not self.tmax > 0:
            raise ValueError(f'tmax must be positive.')
        self.std_const = std_const
        if not self.std_const > 0:
            raise ValueError(f'std_const must be positive.')

    def _first_line_circulant_matrix(self, m, cov: Callable):
        """
            First line of the circulant matrix C built with covariances of the stationary process.
            References : 1 - Wood and Chan (1994) 2 - Phd Thesis Coeurjolly (2000), Appendix A p.132
            m : power of two larger than 2*(n-1).
        """
        k = self.tmax * np.arange(0, m)
        v = cov(k=k)
        ind = np.concatenate((np.arange(0, m / 2, dtype=int), np.arange(m / 2, 0, -1, dtype=int)))
        line = v[ind]
        return line

    @staticmethod
    def _simulate_w(m, seed: int = None):
        # simulation of w=(Q)^t Z, where Z leads N(0,I_m) and (Q)_{jk} = m^(-1/2) exp(-2i pi jk/m)
        np.random.seed(seed)
        ar = np.random.normal(0, 1, int(m / 2 + 1))
        ai = np.random.normal(0, 1, int(m / 2 + 1))
        ar[0] = 2 ** 0.5 * ar[0]
        ar[-1] = 2 ** 0.5 * ar[-1]
        ai[0] = 0
        ai[-1] = 0
        ar = np.concatenate((ar, ar[int(m / 2 - 1): 0:-1]))
        aic = -ai
        ai = np.concatenate((ai, aic[int(m / 2 - 1): 0:-1]))
        w = [complex(one_ar, one_ai) for one_ar, one_ai in zip(ar, ai)]
        return w

    def get_fgn(self, cov: Callable, N: int, seed: int = None) -> np.ndarray:
        """
            seed: generates with a specific random seed.
        """
        # Construction of the first line of the circulant matrix C
        m = 2 ** (int(math.log(N - 1) / math.log(2) + 1))
        eigc = self._first_line_circulant_matrix(m=m, cov=cov)
        eigc = fft(eigc)
        # search of the power of two (<2**18) such that eigc is definite positive
        while any(v <= 0 for v in eigc) and m < 2 ** 17:
            m = 2 * m
            eigc = self._first_line_circulant_matrix(m=m, cov=cov)
            eigc = fft(eigc).real
        # simulation of w=(Q)^t Z, where Z leads N(0,I_m) and (Q)_{jk} = m^(-1/2) exp(-2i pi jk/m)
        w = self._simulate_w(m=m, seed=seed)
        # reconstruction of the fgn
        w = np.sqrt(eigc.astype(np.cdouble)) * w
        fgn = fft(w)
        fgn = fgn / (2 * m) ** 0.5
        fgn = fgn.real
        return fgn

    def plot(self, series: np.ndarray, method_name: str, series_name: str, save_path: str = None):
        plt.plot(np.arange(0, self.tmax, self.tmax / self.sample_size), series)
        plt.title(
            f'{method_name} {series_name} simulation with {self.sample_size} samples and {self.hurst_parameter} hurst')
        plt.xlabel('Time')
        if save_path is not None:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


class WoodChanFbmSimulator(WoodChanFgnSimulator):
    """
        Main idea: WoodChanFbmSimulator generates a Fractional Brownian Motion (fBm) using Wood and Chan circulant matrix.
        Source paper: A.T.A. Wood, G. Chan, "Simulation of stationary Gaussian process in [0,1]d",
%                     Journal of Computational and Graphical Statistics, Vol. 3 (1994) 409-432.
        Corresponding Matlab code: FracLab (https://project.inria.fr/fraclab/)
                                   fbmwoodchan.m
    """

    def __init__(self, sample_size: int, hurst_parameter: float, tmax: float = 1, std_const: float = 1):
        """
            sample_size: is the length of samples generated; it is a positive integer.
            hurst_parameter: is a real value in (0:1) that governs both the pointwise regularity and the shape around 0 of the power spectrum.
            tmax: generates FBM using a specific size of time support, i.e. the time runs in [0,tmax]; if tmax is not specified, the default value is tmax = 1.
            std_const: generates FBM using a specific standard deviation at instant t = 1; if std_const is not specified, the default value is std_const = 1.
        """

        super().__init__(sample_size=sample_size, hurst_parameter=hurst_parameter, tmax=tmax, std_const=std_const)

    def fbm_cov(self, k):
        h2 = 2 * self.hurst_parameter
        v = 0.5 * self.std_const ** 2 * (abs(k - self.tmax) ** h2 - 2 * k ** h2 + (k + self.tmax) ** h2)
        v = v / self.sample_size ** h2
        return v

    def get_fbm(self, is_plot=False, seed=None):
        fgn = self.get_fgn(seed=seed, N=self.sample_size, cov=self.fbm_cov)
        fgn = fgn[:self.sample_size]
        fbm = np.cumsum(fgn)
        if is_plot:
            self.plot(series=fbm, method_name='Wood Chan', series_name='FBM')
        return fbm

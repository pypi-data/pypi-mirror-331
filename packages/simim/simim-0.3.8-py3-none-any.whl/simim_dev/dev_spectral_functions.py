# Functions for various types of spectra, for use with Grid.add_from_spec_func
import numpy as np
from numpy.typing import NDArray

from scipy.special import erf, gammaincc, gamma, zeta

from simim.constants import c, kB, h
# To do:
# - tests - can start from spec_gridder debug
# - Black body
# - Modified black body
# - others (long term/roll your own): busy function, double gaussian, etc.

def delta_cumulative(f: NDArray, pars: NDArray) -> NDArray:
    """Returns the integral of a delta function from 0 to f for each value of f

    Parameters
    ----------
    f : NDArray
        A one dimensional array containing the values along a spectral axis at
        which to evaluate the cumulative spectrum
    pars : NDArray
        An N x 2 array. The first axis should correspond to each object. The
        second axis should contain the location along the spectral axis of the
        delta function (position 0) and the amplitude of the delta function
        (position 1) for each object.

    Returns
    -------
    cumulative_spectrum : NDArray
        An N x len(f) array containing the cumulative spectrum of each object
        (along the first axis) at each frequency (along the second axis)
    """

    x = np.array(pars[:,0]).reshape(-1,1)
    a = np.array(pars[:,1]).reshape(-1,1)

    f=np.array(f,ndmin=1)
    if f.ndim != 1:
        raise ValueError("frequencies must be a 1d array")
    
    spec = np.where(f.reshape(1,-1)>=x.reshape(-1,1),a.reshape(-1,1),0)

    return spec

def gaus_cumulative(f: NDArray, pars: NDArray) -> NDArray:
    """Returns the integral of a Gaussian from 0 to f for each value of f

    Parameters
    ----------
    f : NDArray
        A one dimensional array containing the values along a spectral axis at
        which to evaluate the cumulative spectrum
    pars : NDArray
        An N x 3 array. The first axis should correspond to each object. The
        second axis should contain the location along the spectral axis of the
        Gaussian function (position 0), its full width at half maximum (position
        2), and its amplitude (position 3) for each object.

    Returns
    -------
    cumulative_spectrum : NDArray
        An N x len(f) array containing the cumulative spectrum of each object
        (along the first axis) at each frequency (along the second axis)
    """

    x = np.array(pars[:,0]).reshape(-1,1)
    w = np.array(pars[:,1]).reshape(-1,1) / (2*np.sqrt(2*np.log(2)))
    a = np.array(pars[:,2]).reshape(-1,1)

    f=np.array(f,ndmin=1)
    if f.ndim != 1:
        raise ValueError("frequencies must be a 1d array")
    
    spec = a * 0.5 * (1 + erf((f.reshape(1,-1)-x)/(np.sqrt(2)*w)))

    return spec

def mbb_cumulative(f: NDArray, pars: NDArray) -> NDArray:
    """Returns the integral of a modified blackbody from 0 to f for frequency

    Assumes f is frequency in Hz

    Parameters
    ----------
    f : NDArray
        A one dimensional array containing the values along a frequency (in Hz)
        axis at which to evaluate the cumulative spectrum
    pars : NDArray
        An N x 2 array. The first axis should correspond to each object. The
        second axis should contain the temperature (position 0) and modified
        black body index (beta; position 1) for each object

    Returns
    -------
    cumulative_spectrum : NDArray
        An N x len(f) array containing the cumulative spectrum of each object
        (along the first axis) at each frequency (along the second axis)
    """

    parT = np.array(pars[:,0]).reshape(-1,1)
    parbeta = np.array(pars[:,1]).reshape(-1,1)

    f=np.array(f,ndmin=1)
    if f.ndim != 1:
        raise ValueError("frequencies must be a 1d array")
    
    prefactor = 2 * (kB*parT)**(parbeta+3) / h**(parbeta+2) / c**2
    spec = prefactor * gamma(parbeta+4) * gammaincc(parbeta+4, h*f.reshape(1,-1)/kB/parT) * zeta(parbeta+4)

    return spec

# Check that evaluating at f=infinity, beta=0, T=1 gives steffan-boltzmann constant (or whatever it's supposed to be...)

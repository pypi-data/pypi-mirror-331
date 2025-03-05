# Functions for various statistical calculations relevant to Line Intensity Mapping
import numpy as np
from numpy.typing import NDArray

from simim.constants import c

# To do:
# - box to power spectrum - different unit options
# - box to LF - different unit options

def stat_lf(luminosities: NDArray, volume: NDArray, bins: NDArray = None, dexunits: bool = True) -> float:

    if np.array(volume,ndmin=1).shape == (1,):
        volume = np.ones(len(luminosities)) * volume
    elif len(volume) != len(luminosities):
        raise ValueError("volume must be a single number or one number per object")

    if bins is None:
        min = np.nanmin(luminosities[np.isfinite(luminosities)])
        max = np.nanmax(luminosities[np.isfinite(luminosities)])
        bins = np.logspace(np.log10(min),np.log10(max),10)

    lf, bins = np.histogram(luminosities,bins=bins,weights=1/volume)

    if dexunits:
        lf = lf / np.diff(np.log10(bins))
    else:
        lf = lf / np.diff(bins)

    return lf

def stat_moment1(luminosities: NDArray, volume: NDArray, redshift: NDArray = None, resultunit: str = 'Jy str-1', cosmo = None, restfreq = None) -> float:

    if resultunit not in ['Lsun Mpc-3','W sr-1 m-2 Hz-1','Jy str-1']:
        raise ValueError("resultunit not recognized")

    if np.array(volume,ndmin=1).shape == (1,):
        volume = np.ones(len(luminosities)) * volume
    elif len(volume) != len(luminosities):
        raise ValueError("volume must be a single number or one number per object")

    if np.array(redshift,ndmin=1).shape == (1,):
        redshift = np.ones(len(luminosities)) * redshift
    elif len(redshift) != len(luminosities):
        raise ValueError("redshift must be a single number or one number per object")

    # Luminosit density:
    result = np.nansum(luminosities / volume)
    if resultunit == 'Lsun Mpc-3':
        return result
    
    if redshift is None:
        raise ValueError("redshift must be specified for {} units".format(resultunit))
    if cosmo is None:
        raise ValueError("cosmo must be specified for {} units".format(resultunit))
    if restfreq is None:
        raise ValueError("restfreq must be specified for {} units".format(resultunit))

    y = c/restfreq * (1+redshift)**2 / (1000*cosmo.H(redshift).value) # derivative of distance with respect to frequency in Mpc / Hz
    d = cosmo.comoving_distance(redshift).value
    dl = (1+redshift) * d

    # Convert to flux density
    result = result / (4*np.pi*dl**2) * d**2 * y      # in Lsun / Mpc^2 * Mpc^2/Sr * Mpc/Hz
    result = result * 3.828e26                        # in W / Sr / Mpc^2 / Hz
    result = result / (3.0857e22)**2                  # in W / Sr / m^2 / Hz

    if resultunit == 'W sr-1 m-2 Hz-1':
        return result
    if resultunit == 'Jy sr-1':
        return 1e26 * result

def stat_moment2(luminosities: NDArray, volume: NDArray, redshift: NDArray = None, resultunit: str = 'Jy2 str-2 Mpc3', cosmo = None, restfreq = None) -> float:

    if resultunit not in ['Lsun2 Mpc-3','W2 sr-2 m-4 Hz-2 Mpc3','Jy2 str-2 Mpc3']:
        raise ValueError("resultunit not recognized")

    if np.array(volume,ndmin=1).shape == (1,):
        volume = np.ones(len(luminosities)) * volume
    elif len(volume) != len(luminosities):
        raise ValueError("volume must be a single number or one number per object")

    if np.array(redshift,ndmin=1).shape == (1,):
        redshift = np.ones(len(luminosities)) * redshift
    elif len(redshift) != len(luminosities):
        raise ValueError("redshift must be a single number or one number per object")

    # Luminosity2 density:
    result = np.nansum(luminosities**2 / volume)
    if resultunit == 'Lsun2 Mpc-3':
        return result
    
    
    if redshift is None:
        raise ValueError("redshift must be specified for {} units".format(resultunit))
    if cosmo is None:
        raise ValueError("cosmo must be specified for {} units".format(resultunit))
    if restfreq is None:
        raise ValueError("restfreq must be specified for {} units".format(resultunit))

    y = c/restfreq * (1+redshift)**2 / (1000*cosmo.H(redshift).value) # derivative of distance with respect to frequency in Mpc / Hz
    d = cosmo.comoving_distance(redshift).value
    dl = (1+redshift) * d

    # Convert to flux density
    result = result / (4*np.pi*dl**2)**2 * d**4 * y**2   # in Lsun^2/Mpc^3 / Mpc^4 * Mpc^4/Sr^2 * Mpc^2/Hz^2 = Lsun^2/Sr^2/Hz^2 / Mpc 
    result = result * 3.828e26**2                        # in W^2/Sr^2/Hz^2 / Mpc = W^2/Sr^2/Hz^2 / Mpc^4 * Mpc^3
    result = result / (3.0857e22)**4                     # in W^2/Sr^2/Hz^2/m^4 * Mpc^3

    if resultunit == 'W2 sr-2 m-4 Hz-2 Mpc3':
        return result
    if resultunit == 'Jy2 str-2 Mpc3':
        return 1e26**2 * result
    if resultunit == 'h-3 Jy2 str-2 Mpc3':
        return 1e26**2 * result * cosmo.h**3





# Function to compute the CII-SFR correlation
def cii_sfr_corr(sfr, lcii, logsfrbins=np.linspace(-5,5,51)):

    inds = np.nonzero(lcii>0)
    n_bin, _ = np.histogram(np.log10(sfr[inds]), logsfrbins, density=False)
    totlogl_bin, _ = np.histogram(np.log10(sfr[inds]), logsfrbins, weights=np.log10(lcii[inds]), density=False)
    meanlogl_bin = totlogl_bin / n_bin

    return meanlogl_bin

# Function to compute the real space power spectrum
def powspec_func(pos_x,pos_y,pos_z,lline,redshift,cosmo,box_edge,wavelength=157.74093e-6,kbins=np.logspace(-3,1,41)):
    
    if len(pos_x) == 0:
        return None

    h = cosmo.h
    d = cosmo.comoving_distance(redshift).value       # comoing distance at z in Mpc
    dl = (1+redshift)*d                               # luminosity distance to z in Mpc
    y = wavelength * (1+redshift)**2 / (1000*cosmo.H(redshift).value)  # derivative of distance with respect to frequency in Mpc / Hz

    pixel_size = 1
    side_length = ((box_edge/h)//pixel_size)*pixel_size   # Cut off the edge of the box if it doesn't match pixel size
    center_point = np.array([side_length/2,side_length/2,side_length/2])

    positions = np.array([pos_x,pos_y,pos_z]).T

    intensities = lline / pixel_size**3 / (4*np.pi*dl**2) * d**2 * y  # in Lsun/Mpc^3 / Mpc^2 * Mpc^2/Sr * Mpc/Hz
    intensities = intensities * 3.828e26 / 3.0857e22**2 *1e26               # in Jy/Sr
    intensities[np.isnan(intensities)] = 0

    grid = gridder(positions,intensities,center_point=center_point,side_length=side_length,pixel_size=pixel_size,axunits='Mpc',gridunits='Jy/Sr')
    ps = grid.power_spectrum(in_place=False,normalize=True)

    ax1d, ps1d = ps.spherical_average(ax=[0,1,2],bins=kbins/(2*np.pi))
    ps1d = ps1d[:,0] / side_length**3

    return ps1d

def crossspec_func(pos_x,pos_y,pos_z,lline,galcat,redshift,cosmo,box_edge,wavelength=157.74093e-6,kbins=np.logspace(-3,1,41)):
    
    if len(pos_x) == 0:
        return None

    h = cosmo.h
    d = cosmo.comoving_distance(redshift).value       # comoing distance at z in Mpc
    dl = (1+redshift)*d                               # luminosity distance to z in Mpc
    y = wavelength * (1+redshift)**2 / (1000*cosmo.H(redshift).value)  # derivative of distance with respect to frequency in Mpc / Hz

    pixel_size = 1
    side_length = ((box_edge/h)//pixel_size)*pixel_size   # Cut off the edge of the box if it doesn't match pixel size
    center_point = np.array([side_length/2,side_length/2,side_length/2])

    positions = np.array([pos_x,pos_y,pos_z]).T

    intensities = lline / pixel_size**3 / (4*np.pi*dl**2) * d**2 * y  # in Lsun/Mpc^3 / Mpc^2 * Mpc^2/Sr * Mpc/Hz
    intensities = intensities * 3.828e26 / 3.0857e22**2 *1e26               # in Jy/Sr
    intensities[np.isnan(intensities)] = 0

    grid = gridder(positions,intensities,center_point=center_point,side_length=side_length,pixel_size=pixel_size,axunits='Mpc',gridunits='Jy/Sr')
    grid2 = gridder(positions,galcat,center_point=center_point,side_length=side_length,pixel_size=pixel_size,axunits='Mpc',gridunits='')
    grid2.grid = grid2.grid / np.mean(grid2.grid) - 1
    
    ps = grid.power_spectrum(cross_grid=grid2,in_place=False,normalize=True)

    ax1d, ps1d = ps.spherical_average(ax=[0,1,2],bins=kbins/(2*np.pi))
    ps1d = ps1d[:,0] / side_length**3

    return ps1d

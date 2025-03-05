#  MeepMeep: fast orbit calculations for exoplanet modelling
#  Copyright (C) 2022 Hannu Parviainen
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.


from numba import njit
from numpy import pi, arctan2, sqrt, sin, cos, arccos, mod, copysign, sign, array, arcsin
from scipy.constants import G

HALF_PI = 0.5*pi
TWO_PI = 2.0*pi


@njit
def eccentricity_vector(i, e, w):
    if e > 1e-5:
        ci = cos(i)
        si = sin(i)
        ex = -e*cos(w)
        ey = -e*sin(w)*ci
        ez =  e*sin(w)*si
        return array([ex, ey, ez])
    else:
        return array([-1.0, 0.0, 0.0])


@njit
def eclipse_phase(p, i, e, w):
    """ Phase for the secondary eclipse center.

    Exact secondary eclipse center phase, good for all eccentricities.
    """
    etr = arctan2(sqrt(1. - e**2) * sin(HALF_PI - w), e + cos(HALF_PI - w))
    eec = arctan2(sqrt(1. - e**2) * sin(HALF_PI + pi - w), e + cos(HALF_PI + pi - w))
    mtr = etr - e * sin(etr)
    mec = eec - e * sin(eec)
    phase = (mec - mtr) * p / TWO_PI
    return phase if phase > 0. else p + phase


@njit
def af_transit(e, w):
    """Calculates the -- factor during the transit"""
    return (1.0-e**2)/(1.0 + e*sin(w))


@njit
def i_from_baew(b, a, e, w):
    """Orbital inclination from the impact parameter, scaled semi-major axis, eccentricity and argument of periastron

    Parameters
    ----------

      b  : impact parameter       [-]
      a  : scaled semi-major axis [R_Star]
      e  : eccentricity           [-]
      w  : argument of periastron [rad]

    Returns
    -------

      i  : inclination            [rad]
    """
    return arccos(b / (a*af_transit(e, w)))


@njit
def as_from_rhop(rho, period):
    """Scaled semi-major axis from the stellar density and planet's orbital period.

    Parameters
    ----------

      rho    : stellar density [g/cm^3]
      period : orbital period  [d]

    Returns
    -------

      as : scaled semi-major axis [R_star]
    """
    return (G/(3*pi))**(1/3) * ((period * 86400.0)**2 * 1e3 * rho)**(1 / 3)


@njit
def ta_from_ea_v(Ea, e):
    sta = sqrt(1.0-e**2) * sin(Ea)/(1.0-e*cos(Ea))
    cta = (cos(Ea)-e)/(1.0-e*cos(Ea))
    Ta  = arctan2(sta, cta)
    return Ta


@njit
def ta_from_ea_s(Ea, e):
    sta = sqrt(1.0-e**2) * sin(Ea)/(1.0-e*cos(Ea))
    cta = (cos(Ea)-e)/(1.0-e*cos(Ea))
    Ta  = arctan2(sta, cta)
    return Ta


@njit
def mean_anomaly_offset(e, w):
    mean_anomaly_offset = arctan2(sqrt(1.0-e**2) * sin(HALF_PI - w), e + cos(HALF_PI - w))
    mean_anomaly_offset -= e*sin(mean_anomaly_offset)
    return mean_anomaly_offset


@njit
def mean_anomaly(t, t0, p, e, w):
    offset = mean_anomaly_offset(e, w)
    Ma = mod(TWO_PI * (t - (t0 - offset * p / TWO_PI)) / p, TWO_PI)
    return Ma


@njit
def z_from_ta_s(Ta, a, i, e, w):
    z  = a*(1.0-e**2)/(1.0+e*cos(Ta)) * sqrt(1.0 - sin(w+Ta)**2 * sin(i)**2)
    z *= copysign(1.0, sin(w+Ta))
    return z


@njit(parallel=True)
def z_from_ta_v(Ta, a, i, e, w):
    z  = a*(1.0-e**2)/(1.0+e*cos(Ta)) * sqrt(1.0 - sin(w+Ta)**2 * sin(i)**2)
    z *= sign(1.0, sin(w+Ta))
    return z


@njit
def impact_parameter(a, i):
    return a * cos(i)


@njit
def impact_parameter_ec(a, i, e, w, tr_sign):
    return a * cos(i) * ((1.-e**2) / (1.+tr_sign*e*sin(w)))

@njit
def d_from_pkaiews(p, k, a, i, e, w, tr_sign, kind=14):
    """Transit duration (T14 or T23) from p, k, a, i, e, w, and the transit sign.

    Calculates the transit duration (T14) from the orbital period, planet-star radius ratio, scaled semi-major axis,
    orbital inclination, eccentricity, argument of periastron, and the sign of the transit (transit:1, eclipse: -1).

     Parameters
     ----------

       p  : orbital period         [d]
       k  : radius ratio           [R_Star]
       a  : scaled semi-major axis [R_star]
       i  : orbital inclination    [rad]
       e  : eccentricity           [-]
       w  : argument of periastron [rad]
       tr_sign : transit sign, 1 for a transit, -1 for an eclipse
       kind: either 14 for full transit duration or 23 for total transit duration

     Returns
     -------

       d  : transit duration T14  [d]
     """
    b  = impact_parameter_ec(a, i, e, w, tr_sign)
    ae = sqrt(1.-e**2)/(1.+tr_sign*e*sin(w))
    ds = 1. if kind == 14 else -1.
    return p/pi  * arcsin(sqrt((1.+ds*k)**2-b**2)/(a*sin(i))) * ae
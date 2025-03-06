# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2013-2023 GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.

"""
Module exports :class:`Lasocki2013`.
"""
import numpy as np
from scipy.constants import g

from openquake.hazardlib.gsim.base import GMPE, CoeffsTable
from openquake.hazardlib import const
from openquake.hazardlib.imt import PGA, PGV, SA

def get_magnitude_energy(mag):
    """
    Converts magnitude to energy-based magnitude term.
    """
    return 1.15 + 1.96 * mag

def get_distance_term(coeffs, repi):
    """
    Computes the distance term using the given GMPE coefficients.
    """
    R_h = np.sqrt(repi ** 2 + coeffs["c7"] ** 2)
    return np.log10(R_h)

def get_standard_deviation(coeffs, coeffs_cov, magE, repi):
    """
    Computes the standard deviation term.
    """
    Cb = np.array(list(coeffs_cov)).reshape(3,3)
    R_h = np.sqrt(repi ** 2 + coeffs["c7"] ** 2)
    X0 = np.array([1, magE[0], np.log10(R_h[0]**2)])
    variance_term = np.sqrt(X0 @ Cb @ X0 + coeffs["sigma"]**2)
    return variance_term

class Lasocki2013(GMPE):
    """
    Implement equation developed by Lasocki in "REPORT ON THE ATTENUATION 
    RELATIONS OF PEAK GROUND ACCELERATION AND SPECTRAL ORDINATES OF GROUND 
    MOTION FOR MINING-INDUCED SEISMIC EVENTS IN THE REGION OF THE ŻELAZNY 
    MOST REPOSITORY", 2009.
    Equation coefficients provided for the random horizontal component
    """
    #: Supported tectonic region type is induced, given
    #: that the equations have been derived for the LGCD mining area
    DEFINED_FOR_TECTONIC_REGION_TYPE = const.TRT.INDUCED

    #: Supported intensity measure types are spectral acceleration,
    #: and peak ground acceleration
    DEFINED_FOR_INTENSITY_MEASURE_TYPES = {PGA, SA}

    #: Supported intensity measure component is random horizontal
    #: :attr:`~openquake.hazardlib.const.IMC.RANDOM_HORIZONTAL`,
    DEFINED_FOR_INTENSITY_MEASURE_COMPONENT = const.IMC.RANDOM_HORIZONTAL
    # DEFINED_FOR_INTENSITY_MEASURE_COMPONENT = const.IMC.VERTICAL

    #: Supported standard deviation type is total
    DEFINED_FOR_STANDARD_DEVIATION_TYPES = {const.StdDev.TOTAL}

    #: site params are not required
    REQUIRES_SITES_PARAMETERS = set()

    #: Required rupture parameter is magnitude
    REQUIRES_RUPTURE_PARAMETERS = {'mag'}

    #: Required distance measure is epicentral distance
    #: see paragraph 'Predictor Variables', page 6.
    REQUIRES_DISTANCES = {'repi'}

    def compute(self, ctx: np.recarray, imts, mean, sig, tau, phi):
        """
        Computes mean ground motion values and standard deviations for Lasocki (2013) GMPE.
        
        Parameters:
            repi (float): Epicentral distance (m)
            mag (float): Earthquake magnitude
            imts (list of str): List of intensity measure types (e.g., 'PHA', 'PVA')
            mean (np.array): Array to store computed mean values
            sig (np.array): Array to store computed standard deviations
        """
        # Loop through each IMT and compute values
        for i, imt in enumerate(imts):            
            C = self.COEFFS[imt]
            C_cov = self.COEFFS_COV[imt]
            mag = ctx.mag
            repi = ctx.repi
            # Compute magnitude energy term
            magE = get_magnitude_energy(mag)

            # Compute GMPE terms
            mag_term = C['c1'] + C['c2'] * magE
            dist_term = C['c5'] * get_distance_term(C, repi)
            
            # Compute mean ground motion
            imean = mag_term + dist_term
            mean_value = np.log((10 ** imean) / g)  # Convert to natural log scale and divide by g
            mean[i] = mean_value

            # Compute standard deviation
            sigma = get_standard_deviation(C, C_cov, magE, repi)
            sig[i] = sigma

    #: coefficient table provided by report
    COEFFS = CoeffsTable(sa_damping=5, table="""\
    IMT  c1     c2      c5      c7    sigma     N        
    pga  1.25   0.31    -1.34   558   0.196     1196
    0.6  -3.86  0.55    -0.65   183   0.242     1194
    1.0  -3.94  0.62    -0.66   308   0.262     1197
    2.0  -1.14  0.47    -1.02   741   0.235     1195
    5.0  0.99   0.31    -1.15   690   0.234     1206
    10.0 3.06   0.27    -1.65   906   0.203     1192
    20.0 2.62   0.27    -1.60   435   0.196     1191
    50.0 2.09   0.27    -1.48   375   0.204     1191
    """)
    
    COEFFS_COV = CoeffsTable(sa_damping=5, table="""\
    IMT  Cb00      Cb01      Cb02      Cb10      Cb11      Cb12      Cb20      Cb21      Cb22        
    pga  0.005586  -0.000376 -0.000752 -0.000376 0.000103  -0.000111 -0.000752 -0.000111 0.000440
    0.6  0.007509  -0.000662 -0.000688 -0.000662 0.000161  -0.000154 -0.000688 -0.000154 0.000516
    1.0  0.009119  -0.00075  -0.000948 -0.00075  0.000189  -0.000187 -0.000948 -0.000187 0.000657                 
    2.0  0.008563  -0.000514 -0.001282 -0.000514 0.000147  -0.000164 -0.001282 -0.000164 0.000696         
    5.0  0.008283  -0.000516 -0.001202 -0.000516 0.000145  -0.000161 -0.001202 -0.000161 0.000668
   10.0  0.006904  -0.00036  -0.001145 -0.00036  0.000108  -0.000126 -0.001145 -0.000126 0.000578
   20.0  0.005389  -0.000396 -0.000658 -0.000396 0.000104  -0.000107 -0.000658 -0.000107 0.000408
   50.0  0.005874  -0.000449 -0.000678 -0.000449 0.000114  -0.000114 -0.000678 -0.000114 0.000428
    """)
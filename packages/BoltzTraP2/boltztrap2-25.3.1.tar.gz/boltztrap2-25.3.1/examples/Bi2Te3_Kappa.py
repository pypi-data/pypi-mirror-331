# -*- coding: utf-8 -*-
#    BoltzTraP2, a program for interpolating band structures and calculating
#                semi-classical transport coefficients.
#    Copyright (C) 2017-2025 Georg K. H. Madsen <georg.madsen@tuwien.ac.at>
#    Copyright (C) 2017-2025 Jesús Carrete <jesus.carrete.montana@tuwien.ac.at>
#    Copyright (C) 2017-2025 Matthieu J. Verstraete <matthieu.verstraete@ulg.ac.be>
#    Copyright (C) 2018-2019 Genadi Naydenov <gan503@york.ac.uk>
#    Copyright (C) 2020 Gavin Woolman <gwoolma2@staffmail.ed.ac.uk>
#    Copyright (C) 2020 Roman Kempt <roman.kempt@tu-dresden.de>
#    Copyright (C) 2022 Robert Stanton <stantor@clarkson.edu>
#    Copyright (C) 2024 Haoyu (Daniel) Yang <yanghaoyu97@outlook.com>
#
#    This file is part of BoltzTraP2.
#
#    BoltzTraP2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BoltzTraP2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BoltzTraP2.  If not, see <http://www.gnu.org/licenses/>.

###############################################################################
# Load Wien2k results for Bi2Te3, perform the interpolation and calculate
# kappa_e. Reproduce Fig. 3 from Comp. Phys. Comm. 175 (2006) 67–71
###############################################################################

import logging
import os
import os.path

import matplotlib.pylab as pl
import numpy as np
from environment import data_dir

from BoltzTraP2 import bandlib, dft, fite, serialization, sphere, units

logging.basicConfig(
    level=logging.DEBUG, format="{levelname:8s}│ {message:s}", style="{"
)

dirname = os.path.join(data_dir, "Bi2Te3")
bt2file = "Bi2Te3.bt2"

if __name__ == "__main__":
    # Load the interpolation results from a file
    data, equivalences, coeffs, metadata = serialization.load_calculation(
        bt2file
    )

    # Rebuild the bands from the interpolation coefficients
    lattvec = data.get_lattvec()

    # Plot the results

    eband, vvband, cband = fite.getBTPbands(
        equivalences, coeffs, lattvec, curvature=False
    )

    epsilon, dos, vvdos, cdos = bandlib.BTPDOS(eband, vvband, npts=4000)
    fermi = bandlib.solve_for_mu(
        epsilon, dos, data.nelect, 300, data.dosweight
    )

    mur = epsilon[100:-100]
    TEMP = np.array([300.0])
    N, L0, L1, L2, Lm11 = bandlib.fermiintegrals(
        epsilon, dos, vvdos, mur=mur, Tr=TEMP, dosweight=data.dosweight
    )

    # Use the Fermi integrals to obtain the Onsager coefficients
    UCvol = data.get_volume()
    sigma, seebeck, kappa, Hall = bandlib.calc_Onsager_coefficients(
        L0, L1, L2, mur, TEMP, UCvol
    )

    # Plot the results
    fig1, ax1 = pl.subplots(1, figsize=(6, 4))
    kappa = (kappa[0, :, 0, 0] + kappa[0, :, 1, 1] + kappa[0, :, 2, 2]) / 3.0
    kappaWF = (
        (sigma[0, :, 0, 0] + sigma[0, :, 1, 1] + sigma[0, :, 2, 2])
        / 3.0
        * 2.44e-8
        * TEMP[0]
    )
    kappaD = (
        (
            seebeck[0, :, 0, 0] ** 2 * sigma[0, :, 0, 0]
            + seebeck[0, :, 1, 1] ** 2 * sigma[0, :, 1, 1]
            + seebeck[0, :, 2, 2] ** 2 * sigma[0, :, 2, 2]
        )
        / 3.0
        * TEMP[0]
    )

    ax1.plot(
        (mur - fermi) / bandlib.eV, kappa * 1e-14, "k-", label=r"$\kappa_e$"
    )
    ax1.plot(
        (mur - fermi) / bandlib.eV, kappaWF * 1e-14, "k:", label=r"$L\sigma T$"
    )
    ax1.set_ylim([0, 60])
    ax1.set_xlim([-1, 1])
    ax1.set_xlabel(r"$\mu$ [eV]")
    ax1.set_ylabel(
        r"$\kappa/\tau \;\left(10^{14}\; \mathrm{W m}^{-1} \mathrm{K}^{-1}\right)$"
    )
    ax1.legend()

    pl.show()

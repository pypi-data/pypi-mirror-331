###############################################################################
# (c) Copyright 2025 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

from typing import List
from statistics import NormalDist

import numpy as np


def wilson(
    passed, total, confidence: float = 0.68, passed_error=None, total_error=None
):
    """Calculate the efficiency and lower/upper uncertainties based on a generalised Wilson interval.

    Args:
        passed: int or array of int
            Number of events passing a critera (numerator of the efficiency)
        total: int or array of int
            Total number of events (denominator of the efficiency)
        confidence: float, optional
            Confidence level for the interval; defaults to 0.68 (1 sigma), per the recommendation of the LHCb Statistics guidelines
        passed_error: int or array of int, optional
            Uncertainty on the number of events that pass some criteria if not strictly Poissonian; defaults to Poissonian uncertainty, `sqrt(passed)`, if not specified
        total_error: int or array of int, optional
            Uncertainty on the total number of events if not strictly Poissonian; defaults to Poissonian uncertainty, `sqrt(total)`, if not specified

    Returns:
        efficiency: float or array of float
            The raw efficiency (passed / total)
        lower_error: float or array of float
            The lower error on the efficiency from the Wilson interval
        upper_error: float or array of float
            The upper error on the efficiency from the Wilson interval

    Notes:
        This function implements the generalised Wilson interval of H. Dembinski and M. Schmelling, 2022 (https://arxiv.org/pdf/2110.00294).
    """
    if passed_error is None:
        passed_error = np.sqrt(passed)
    if total_error is None:
        total_error = np.sqrt(total)

    passed_np_variance = np.nan_to_num(
        passed_error**2 - passed
    )  # non-Poisson term in variance on n(passed)
    if isinstance(passed_np_variance, (List, np.ndarray)):
        passed_np_variance[passed_np_variance < 1e-12] = 0
    elif passed_np_variance < 1e-12:
        passed_np_variance = 0

    failed_np_variance = np.nan_to_num(
        total_error**2 - passed_error**2 - total + passed
    )
    if isinstance(failed_np_variance, (List, np.ndarray)):
        failed_np_variance[failed_np_variance < 1e-12] = 0
    elif failed_np_variance < 1e-12:
        failed_np_variance = 0

    # Define terms in line with the notation of the paper where possible
    n = total
    p = passed / total if total > 0 else 0
    z = NormalDist().inv_cdf((1 + confidence) / 2)

    # Calculate the lower and upper limits of the interval
    prefactor = (
        1 / (1 + (z**2 / n) * (1 - (passed_np_variance + failed_np_variance) / n))
        if n > 0
        else 0
    )
    positive_term = (
        p + (z**2 / (2 * n)) * (1 - 2 * passed_np_variance / n) if n > 0 else 0
    )
    plusminus_term = (
        (
            z
            / n
            * np.sqrt(
                p**2 * (passed_np_variance + failed_np_variance - n)
                + p * (n - 2 * passed_np_variance)
                + passed_np_variance
                + z**2 / 4 * (1 - 4 * passed_np_variance * failed_np_variance / n**2)
            )
        )
        if n > 0
        else 0
    )

    lower_limit = np.maximum(
        np.nan_to_num(prefactor * (positive_term - plusminus_term)), 0
    )
    upper_limit = np.minimum(
        np.nan_to_num(prefactor * (positive_term + plusminus_term)), 1
    )

    return p, p - lower_limit, upper_limit - p

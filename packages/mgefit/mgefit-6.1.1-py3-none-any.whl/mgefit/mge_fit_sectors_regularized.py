"""
Copyright (C) 1999-2025, Michele Cappellari

E-mail: michele.cappellari_at_physics.ox.ac.uk

Updated versions of the software are available from my web page
https://purl.org/cappellari/software

If you have found this software useful for your research, 
I would appreciate an acknowledgement to the use of
"the MGE fitting method and software by Cappellari (2002)".

https://ui.adsabs.harvard.edu/abs/2002MNRAS.333..400C

This software is provided as is without any warranty whatsoever.
Permission to use, for non-commercial purposes is granted.
Permission to modify for personal or internal use is granted,
provided this copyright and disclaimer are included unchanged
at the beginning of the file. All other rights are reserved.
In particular, redistribution of the code is not allowed.

################################################################################

Version History
---------------
- V1.0.0 : First implementation, MC, Oxford, 22 January 2013
- V1.0.1 : Fixed program stop when (qmin == qmax), thanks to Silvia Posacki
           (Bologna) for reporting the issue. MC, Oxford, 9 May 2013
- V2.0.0 : Converted from IDL into Python. MC, Oxford, 27 March 2015
- V2.0.1 : Removed truncation of input eps in `mge_fit_sectors`.
           MC, Atlantic Ocean, 28 March 2015
- V2.0.2 : Cleaned up loop. MC, Oxford, 30 May 2015
- V2.0.3 : Single plot created when `plot=True` and displayed post-completion.
           Printed best solution after the function finishes. MC, Oxford,
           14 February 2017
- V2.0.4 : Modified imports for the `mgefit` package. MC, Oxford, 17 April 2018
- Vx.x.xx: Additional changes are now documented in the global CHANGELOG.rst 
           file of the MgeFit package

"""
import numpy as np

from mgefit.mge_fit_sectors import mge_fit_sectors

#----------------------------------------------------------------------------

class mge_fit_sectors_regularized:
    """
    mge.fit_sectors_regularized
    ===========================

    Purpose
    -------
    Regularizes an MGE fit by restricting the range of `qObs` values.

    This class is a wrapper for the `mge_fit_sectors` procedure and supports all
    keywords of that program. Consult the documentation for `mge_fit_sectors`
    for detailed usage information.

    The wrapper implements the method described in Section 2.2.2 of
    Cappellari (2002, MNRAS, 333, 400), which "regularizes" an MGE model by
    restricting the range of `qObs` for Gaussians until the fit becomes
    unacceptable. This ensures that the allowable range of galaxy inclinations
    isn't artificially constrained by the data.

    The method detailed here was employed for MGE fits of galaxies in the Atlas3D
    project, as described in Section 3.2 of Scott et al. (2013, MNRAS, 432, 1894).

    Parameters
    ----------
    radius : array-like
        Radii of the data points to be fitted.
    angle : array-like
        Angles corresponding to the radii in the same order.
    counts : array-like
        Measured counts at the given radii and angles.
    eps : float
        Ellipticity of the data to be fitted.
    frac : float, optional
        The maximum allowed fractional increase in the absolute deviation
        of the fit. Default is 1.1.
    qbounds : tuple of float, optional
        The lower and upper bounds for `qObs` values. If None, defaults
        to (0.05, 1).
    plot : bool, optional
        If True, produces a plot of the final solution after fitting.
    **kwargs : dict, optional
        Additional keyword arguments passed to `mge_fit_sectors`.

    Attributes
    ----------
    sol : ndarray
        The final regularized MGE solution, consisting of Gaussian parameters.
    plot : callable
        A callable function for plotting the solution.

    Notes
    -----
    This wrapper calls `mge_fit_sectors` multiple times, so it is computationally
    intensive. Use it only after validating the input parameters (e.g., position
    angle, ellipticity, center, sky subtraction) with a standard MGE fit.

    The intended usage sequence is:
      1. Perform a standard MGE fit using `mge_fit_sectors`.
      2. When satisfied with the preliminary fit, replace `mge_fit_sectors`
         with `mge_fit_sectors_regularized` in your script to clean up the
         final solution.

    Examples
    --------
    >>> from mge_fit_sectors_regularized import mge_fit_sectors_regularized
    >>> mge = mge_fit_sectors_regularized(radius, angle, counts, eps)

    References
    ----------
    Cappellari, M. (2002). MNRAS, 333, 400.
    Scott, N., et al. (2013). MNRAS, 432, 1894.
    """

    def __init__(self, radius, angle, counts, eps, frac=1.1, qbounds=None, plot=False, **kwargs):

        if qbounds is None:
            qmin, qmax = 0.05, 1
        else:
            qmin, qmax = qbounds

        nq = int(np.ceil((qmax - qmin)/0.05) + 1)  # Adopt step <= 0.05 in qObs
        qrange = np.linspace(qmin, qmax, nq)
        bestnorm = np.inf

        for j in range(nq - 1):
            qmin = qrange[j]
            m = mge_fit_sectors(radius, angle, counts, eps,
                                qbounds=[qmin, qmax], plot=False, **kwargs)
            print(f'(minloop) qbounds ={qmin:6.3f}{qmax:6.3f}')
            print('############################################')
            if m.absdev > bestnorm*frac:    # frac is the allowed fractional increase in ABSDEV
                jbest = j - 1
                qmin = qrange[jbest]
                break  # stops if the error increases more than frac
            else:
                jbest = j
                bestnorm = min(bestnorm, m.absdev)
                self.sol = m.sol
                self.plot = m.plot

        for k in range(nq - 2, jbest, -1):
            qmax = qrange[k]
            m = mge_fit_sectors(radius, angle, counts, eps,
                                qbounds=[qmin, qmax], plot=False, **kwargs)
            print(f'(maxloop) qbounds ={qmin:6.3f}{qmax:6.3f}')
            print('############################################')
            if m.absdev > bestnorm*frac:    # frac is the allowed fractional increase in ABSDEV
                qmax = qrange[k + 1]
                break  # stops if the error increases more than frac
            else:
                bestnorm = min(bestnorm, m.absdev)
                self.sol = m.sol
                self.plot = m.plot

        if plot:
            self.plot()

        print('############################################')
        print('Final Regularized MGE Solution:')
        print('  Total_Counts  sigma_Pixels      q_obs')
        print('############################################')
        for sol in self.sol.T:
            print((' {:13.4e}{:#13.4g}{:13.4f}').format(*sol))
        print('++++++++++++++++++++++++++++++++++++++++++++')
        print(f'Final qbounds ={qmin:6.3f}{qmax:6.3f}')
        print('############################################')

#----------------------------------------------------------------------------

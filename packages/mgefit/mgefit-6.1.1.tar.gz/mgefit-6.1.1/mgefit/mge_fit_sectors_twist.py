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

#####################################################################

Changelog
---------

V1.0.0 First implementation, Padova, February 1999, Michele Cappellari
V2.0.0 Major revisions, Leiden, January 2000, MC
V3.0.0 Significant changes, Padova, July 2000, MC
V3.1.0 More robust definition of err in FITFUNC_MGE_SECTORS,
    Leiden, 27 April 2001, MC
V3.2.0 Graphical changes: always show about 7 sectors on the screen,
    and print plots with shared axes. Leiden, 8 July 2001, MC
V3.3.0 Added MGE PSF convolution, central pixel integration and changed
    program input parameters to make it independent from SECTORS_PHOTOMETRY
    Leiden, 26 July 2001, MC
V3.4.0 Added varying position angles fit, August 2001, MC
V3.5.0 Added /FASTNORM keyword, Leiden, 20 September 2001, MC
V3.6.0 Updated documentation, Leiden, 8 October 2001, MC
V3.7.0 Modified implementation with /NEGATIVE keyword
    Leiden, 23 October 2001, MC
V3.8.0 Added explicit stepsize (STEP) of numerical derivative in
    parinfo structure, after suggestion by Craig B. Markwardt.
    Leiden, 23 February 2002, MC
V3.8.1 Added compilation options, Leiden 20 May 2002, MC
V3.8.2 Corrected checking of input parameters when SIGMAPSF is a vector.
    Added ERRMSG keyword to MPFIT call. Leiden, 13 October 2002, MC
V3.8.3 Force the input parameters to the given bounds if they
    fall outside the required range before starting the fit.
    Leiden, 7 March 2003, MC
V3.8.4: Use N_ELEMENTS instead of KEYWORD_SET to test
    non-logical keywords. Leiden, 9 May 2003, MC
V3.8.5: Use updated calling sequence for BVLS. Leiden, 20 March 2004, MC
V3.9.0: Force the surface brightness of the MGE model to decrease at
    least as R^-2 at the largest measured radius. Leiden, 8 May 2004, MC
V3.9.1: Make sure this routine uses the Nov/2000 version of Craig Markwardt
    MPFIT which was renamed MGE_MPFIT to prevent potential conflicts with
    more recent versions of the same routine. Vicenza, 23 August 2004, MC.
V3.9.2: Allow forcing the outer slope of the surface brightness profile of
    the MGE model to decrease at least as R^-n at the largest measured
    radius (cfr. version 3.9). Leiden, 23 October 2004, MC
V3.9.3 Replaced LOGRANGE keyword in example with the new MAGRANGE.
    MC, Leiden, 1 May 2005
V3.9.4: Changed axes labels in plots. Leiden, 18 October 2005, MC
V3.9.5: Use more robust la_least_squares (IDL 5.6) instead of SVDC with
    /NEGATIVE keyword. MC, Oxford, 16 May 2008
V3.9.6: Force Gaussians smaller than the PSF, which have a degenerate
    axial ratio and PA, to have the same axial ratio and PA as the
    mean of the first two well determined Gaussians.
    MC, Oxford, 24 September 2008
V3.9.7: Changed definition of output PA to be positive in
    anti clockwise direction. Thanks to Remco van den Bosch
    for pointing out the inconsistency. MC, Oxford, 6 June 2009
V3.9.8: Small change to the treatment of the innermost unresolved
    Gaussians. MC, Oxford, 24 April 2012
V3.9.9: Explained optional usage of SOL in input.
    MC, Oxford, 10 January 2013
V3.9.10: Use ERF instead of obsolete ERRORF. MC, Oxford, 24 May 2017
V4.0.0: Converted mge_fit_sectors into into mge_fit_sectors_twist.
    MC, Oxford, 27 July 2017
V4.0.1: Changed imports for mgefit package. MC, Oxford, 17 April 2018
V4.0.2: Dropped legacy Python 2.7 support. MC, Oxford, 12 May 2018
V4.0.3: Fixed clock DeprecationWarning in Python 3.7.
    Use SciPy 1.1 `maxiter` keyword in `nnls`. MC, Oxford, 1 October 2018
V4.0.4: With ``negative=True`` use Numpy linalg.lstsq instead of Scipy
    for a better default in the criterion for rank deficiency.
    Fixed ignoring negative weights in output with ``negative=True``.
    MC, Oxford, 1 October 2020
Vx.x.xx: Additional changes are now documented in the global CHANGELOG.rst 
    file of the MgeFit package

"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import special
from time import perf_counter as clock

from capfit.capfit import lsq_box, capfit

#----------------------------------------------------------------------------

def linspace_open(a, b, num=50):

    dx = (b - a)/num
    x = a + (0.5 + np.arange(num))*dx

    return x

#-------------------------------------------------------------------------------

class mge_fit_sectors_twist:
    """
    mge.fit_sectors_twist
    =====================

    Purpose
    -------
    Approximates the surface brightness of a galaxy with a Multi-Gaussian
    Expansion (MGE) model, using the robust and automated fitting method of
    `Cappellari (2002) <https://ui.adsabs.harvard.edu/abs/2002MNRAS.333..400C>`_.

    The measurements are taken along sectors with a previous call to the
    procedure ``sectors_photometry_twist`` in the ``MgeFit`` package .
    All measurements within this program are in the instrumental units of
    ``pixels`` and ``counts``. This routine fits MGE models with varying
    position angle and common center.

    Calling Sequence
    ----------------
    .. code-block:: python

        import mgefit as mge

        m = mge.fit_sectors_twist(radius, angle, counts, eps,
                 ngauss=None, negative=False, sigmapsf=0., normpsf=1., scale=1.,
                 rbounds=None, qbounds=None, pabounds=None, quiet=False,
                 outer_slope=4, sol=0, plot=False, fignum=1

        total_counts, sigma, q_obs, ang = m.sol  # assign the solution to variables
        print(m.sol.T)  # Print a table of best-fitting MGE parameters

    Parameters
    ----------
    radius: array_like with shape (n,)
        Vector containing the radius of the surface brightness
        measurements, taken from the galaxy center. This is given
        in units of PIXELS (!) of the image. When fitting multiple images
        simultaneously this is in pixels units of the high-resolution image.
    angle: array_like with shape (n,)
        Vector containing the polar angle of the surface brightness
        measurements, measured from the galaxy major axis (in degrees).
    counts: array_like with shape (n,)
        Vector containing the surface brightness measurements in COUNTS/PIXEL (!) at
        the polar coordinates specified by the vectors ``radius`` and ``angle``.
        When fitting multiple images simultaneously this is in counts/pixels units
        of the high-resolution image.
    eps:
        Crude estimate for the galaxy characteristic ellipticity
        ``eps = 1 - b/a = 1 - q'``

    Other parameters
    ----------------
    fignum:
        Optional number to assign to the plotting window.
    negative:
        Set this keyword to allow for negative Gaussians in the fit.
        Use this only if everything else didn't work or if there is clear
        evidence that negative Gaussians are actually needed.
        Negative Gaussians are needed e.g. when fitting a boxy bulge.
    ngauss:
        Maximum number of Gaussians allowed in the MGE fit.
        Typical values are in the range 10-20 (default: ``ngauss=12``).
    normpsf: array_like with shape (p,)
        This is optional if only a scalar is given for ``sigmapsf``, otherwise it
        must contain the normalization of each MGE component of the PSF, whose
        sigma is given by ``sigmapsf``. The vector needs to have the same number of
        elements as ``sigmapsf`` and it must be normalized as ``normpsf.sum() = 1``
        (default: ``normpsf=1``).
    outer_slope:
        This scalar forces the surface brightness profile of
        the MGE model to decrease at least as fast as ``R**(-outer_slope)``
        at the largest measured radius (Default: ``outer_slope=2``).
    plot:
        Set ``plot=True`` to plot the best-fitting MGE profiles.
    qbounds:
        Two elements vector giving the minimum and maximum axial ratio ``q``
        allowed in the MGE fit.
    quiet:
        Set ``quiet = True`` to suppress printed output.
    rbounds:
        Two elements vector giving the minimum and maximum ``sigma`` allowed in
        the MGE fit. This is in the same ``pixels`` units as ``radius``.
    scale:
        The pixel scale in arcsec/pixels. This is *only* used for the scale on
        the plots. It has no influence on the output. (default: 1)
    sigmapsf: array_like with shape (p,)
        Scalar giving the ``sigma`` of the PSF, or vector with the ``sigma`` of
        an MGE model for the circular PSF. This is in the same ``pixels`` units
        as ``radius``. When fitting multiple images simultaneously this is the
        PSF of the high-resolution image [see pg. 406 of `Cappellari (2002)`_
        for details]. (Default: no convolution)
    sol:
        If this keyword has at least 8 elements in input, the ``sigma``,
        ``q_obs`` and ``pa`` will be used as starting point for the
        optimization. This is useful for testing but is never needed otherwise.
        The format is described in the ``Returns`` below.
    
    Returns
    -------
    Stored as attributes of the ``mge.fit_sectors_twist`` class:

    .sol: array_like with shape (4, ngauss)
        Array with the best-fitting MGE solution. If the PSF parameters are
        given in input, this model is deconvolved for the PSF and pixels
        effects:

            .sol[0]: array_like with shape (ngauss)
                ``total_counts`` of the Gaussian components;
            .sol[1]: array_like with shape (ngauss)
                ``sigma`` is the dispersion of the best-fitting Gaussians in pixels;
            .sol[2]: array_like with shape (ngauss)
                ``q_obs`` is the observed axial ratio of the best-fitting
                Gaussian components [q' in the notation of `Cappellari (2002)`_].
            .sol[3]: array_like with shape (ngauss)
                ``pa`` is the observed position angle of the best-fitting Gaussian
                components. It is measured with respect to the same (arbitrary)
                system of angular coordinates adopted for the input vector ``angle``.

        The relation below gives the Gaussians peak surface brightness ``surf``
        (e.g., for use with ``jam.axi.proj`` of the ``JamPy`` package)::

            total_counts, q_obs, sigma, pa = m.sol  # Assign MGE solution to variables
            surf = total_counts/(2*np.pi*q_obs*sigma**2)

    .absdev:
        Mean absolute deviation between the fitted MGE and the
        data expressed as a fraction. Good fits to high S/N images
        can reach values of ``absdev < 0.02 = 2%``.

    """

    def __init__(self, radius, angle, counts, eps,
                 ngauss=None, negative=False, sigmapsf=0., normpsf=1., scale=1.,
                 rbounds=None, qbounds=None, pabounds=None, quiet=False,
                 outer_slope=4, sol=0, plot=False, fignum=1):

        assert np.all(counts > 0), 'Input counts must be positive'
        assert radius.size == angle.size == counts.size, 'Input vectors must have the same length'
        outer_slope = np.clip(outer_slope, 1, 4)

        # load data vectors into class attributes
        #
        self.radius = radius
        self.counts = counts
        self.angle = angle
        self.scale = scale
        sol = np.asarray(sol)
        self.sigmaPSF = np.atleast_1d(sigmapsf)
        self.normPSF = np.atleast_1d(normpsf)
        self.negative = negative
        self.scale = scale
        self.quiet = quiet
        self.weights = None

        nPsf = self.sigmaPSF.size
        assert self.normPSF.size == nPsf, 'sigmaPSF and normPSF must have the same length'
        assert round(np.sum(normpsf), 2) == 1, 'Error: PSF not normalized'

        self.sectors = np.unique(angle) # Finds the different position angles

        # Open grid in the range [rminLog,rmaxLog]
        # The logarithmic slope of a Gaussian is slope(R) = -(R/sigma)**2
        # so to have a slope -n one needs to be at R = sqrt(n)*sigma.
        # Below we constrain the largest Gaussian to have sigma < rmax/sqrt(n)
        # to force the surface brightness of the MGE model to decrease
        # at least as fast as R**-n at the largest measured radius.
        #
        if rbounds is None:
            lrbounds = np.log10([np.min(radius), np.max(radius)/np.sqrt(outer_slope)])
        else:
            lrbounds = np.log10([rbounds[0], rbounds[1]/np.sqrt(outer_slope)])

        if qbounds is None:
            qbounds = np.array([0.05, 1.]) # no Gaussians flatter than q=0.05
        else:
            qbounds = np.asarray(qbounds)

        if pabounds is None:
            pabounds = np.array([-np.inf, np.inf])
        else:
            pabounds = np.asarray(pabounds)

        # If the smallest intrinsic Gaussian has sigma=0.75*sigmaPSF it will produce an
        # observed Gaussian with sigmaObs=SQRT(sigma**2+sigmaPSF**2)=1.25*sigmaPSF.
        # We require the sigma of the Gaussians to be larger than 0.75*sigmaPSF,
        # or the smallest measured radius, whichever is larger.
        #
        if np.sum(sigmapsf) > 0:
            lrbounds[0] = max(lrbounds[0], np.log10(0.75*np.min(sigmapsf)))

        # Here the actual calculation starts. The path is different depending on whether the
        # user has requested the nonlinear method or the linear one by setting the /LINEAR keyword
        #
        t = clock()
        if ngauss is None:
            ngauss = 12
        else:
            assert ngauss < 35, 'Too many Gaussians'
        if sol.size < 8:
            logsigma = linspace_open(*lrbounds, num=ngauss)  # open grid
            q = np.full_like(logsigma, 1 - eps)
            pa = np.zeros_like(logsigma)
        else:
            ngauss = sol.size // 4
            logsigma = np.log10(sol[1, :])      # Log(sigma)
            q = sol[2, :]                       # qObs
            pa = sol[3, :]                      # position angle

        logsigma = logsigma.clip(*lrbounds)
        q = q.clip(*qbounds)
        pa = pa.clip(*pabounds)

        bounds = np.tile(lrbounds, (3*ngauss, 1))
        abs_step = np.full(3*ngauss, 0.01)
        for j in range(ngauss, 2*ngauss):
            bounds[j] = qbounds
        for j in range(2*ngauss, 3*ngauss):
            bounds[j] = pabounds
            abs_step[j] = 1.0  # degrees: step for numerical derivative

        pars = np.concatenate([logsigma, q, pa])
        monitor = None if quiet else {"fun": self._monitor, "num": 10}        
        mp = capfit(self._fitfunc, pars, bounds=bounds.T, abs_step=abs_step, monitor=monitor)

        # Print the results for the nonzero Gaussians sorted by increasing sigma
        logSigma, q, pa = mp.x.reshape(3, -1)
        w = self.weights != 0
        m = w.sum()
        self.weights, self.gauss, logSigma, q, pa = \
            self.weights[w], self.gauss[:, w], logSigma[w], q[w], pa[w]

        j = np.argsort(logSigma)
        self.sol = np.vstack([self.weights[j], 10**logSigma[j], q[j], pa[j]])
        self.absdev = np.mean(np.abs(self.err))

        # Force Gaussians with minor axis smaller than the PSF, which have
        # a degenerate axial ratio, to have the same axial ratio as the mean
        # of the first two well determined Gaussians. Flux is conserved by
        # PSF convolution so no other changes are required
        #
        sigy = self.sol[1, :]*self.sol[2, :]
        w = sigy < np.min(sigmapsf)
        self.sol[2, w] = np.mean(self.sol[2, ~w][:2])

        if not self.quiet:
            print('############################################')
            print(f"CapFit {mp.message}, status: {mp.status}")                
            print('  Computation time: %.2f seconds' % (clock() - t))
            print('  Total Iterations: ', mp.njev)
            print(' Nonzero Gaussians: ', m)
            print('  Unused Gaussians: ', ngauss - m)
            print(' Sectors used in the fit: ', self.sectors.size)
            print(' Total number of points fitted: ', radius.size)
            print(' Chi2: %#.4g ' % mp.chi2)
            print(' STDEV: %#.4g ' % np.std(self.err))
            print(' MEANABSDEV: %#.4g ' % self.absdev)
            print('#####################################################')
            print('  Total_Counts   Sigma_Pixels     q_obs        PA')
            print('#####################################################')
            for sol in self.sol.T:
                print(('{:13.4e}{:#13.4g}{:13.4f}{:11.2f}').format(*sol))
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++')

        if plot:
            self.plot(fignum)

# -------------------------------------------------------------------------------

    def plot(self, fignum=1):
        """Produces final best-fitting plot"""

        # Select an x and y plot range that is the same for all plots
        #
        minrad = np.min(self.radius)*self.scale
        maxrad = np.max(self.radius)*self.scale
        mincnt = np.min(self.counts)
        maxcnt = np.max(self.counts)
        xran = minrad * (maxrad/minrad)**np.array([-0.02, +1.02])
        yran = mincnt * (maxcnt/mincnt)**np.array([-0.05, +1.05])

        n = self.sectors.size
        dn = int(round(n/6.))
        nrows = (n-1)//dn + 1 # integer division

        fig, ax = plt.subplots(nrows, 2, sharex=True, sharey='col', num=fignum)
        fig.subplots_adjust(hspace=0.01)

        fig.text(0.04, 0.5, 'counts', va='center', rotation='vertical')
        fig.text(0.96, 0.5, 'error (%)', va='center', rotation='vertical')

        ax[-1, 0].set_xlabel("arcsec")
        ax[-1, 1].set_xlabel("arcsec")

        row = 0
        for j in range(0, n, dn):
            w = np.nonzero(self.angle == self.sectors[j])[0]
            w = w[np.argsort(self.radius[w])]
            r = self.radius[w]*self.scale
            txt = "$%.f\\degree$" % self.sectors[j]

            ax[row, 0].set_xlim(xran)
            ax[row, 0].set_ylim(yran)
            ax[row, 0].loglog(r, self.counts[w], 'C0o')
            ax[row, 0].loglog(r, self.yfit[w], 'C1', linewidth=2)
            ax[row, 0].text(0.98, 0.95, txt, ha='right', va='top', transform=ax[row, 0].transAxes)
            ax[row, 0].loglog(r, self.gauss[w, :]*self.weights[None, :])

            ax[row, 1].semilogx(r, self.err[w]*100, 'C0o')
            ax[row, 1].axhline(linestyle='--', color='C1', linewidth=2)
            ax[row, 1].yaxis.tick_right()
            ax[row, 1].yaxis.set_label_position("right")
            ax[row, 1].set_ylim([-19.5, 20])

            row += 1

#----------------------------------------------------------------------------

    def _fitfunc(self, pars):

        logsigma, q, pa = pars.reshape(3, -1)

        r2 = (self.radius**2)[:, None, None]
        angle = self.angle[:, None, None]
        sigma2 = (10**(2*logsigma))[None, :, None]
        q2 = (q**2)[None, :, None]
        pa = pa[None, :, None]
        sigmaPSF2 = (self.sigmaPSF**2)[None, None, :]
        normPSF = self.normPSF[None, None, :]

        # Analytic convolution with an MGE circular PSF
        # Equations (4,5) in Cappellari (2002)
        sigmaX = np.sqrt(sigma2 + sigmaPSF2)
        sigmaY = np.sqrt(sigma2*q2 + sigmaPSF2)

        # Normalized (volume=1) 2-dim Gaussian in polar coordinates
        ang = np.radians(angle + pa)
        g = np.exp(-0.5*r2*((np.cos(ang)/sigmaX)**2 + (np.sin(ang)/sigmaY)**2))
        self.gauss = np.sum(normPSF/(2*np.pi*sigmaX*sigmaY)*g, 2)

        # Analytic integral of the MGE on the central pixel.
        # Below we assume the central pixel is aligned with the galaxy axes.
        # This is generally not the case, but the error due to this
        # approximation is negligible in realistic situations.
        w = self.radius < 0.5
        g = special.erf(2**-1.5/sigmaX) * special.erf(2**-1.5/sigmaY)
        self.gauss[w, :] = np.sum(normPSF*g, 2)

        A = self.gauss/self.counts[:, None] # gauss*SQRT(weights) = gauss/y
        b = np.ones_like(self.radius)  # y*SQRT(weights) = 1 <== weights = 1/sigma**2 = 1/y**2

        if self.negative:   # Solution by LAPACK linear least-squares
            self.weights = np.linalg.lstsq(A, b, rcond=None)[0]
        else:               # Solution by NNLS
            self.weights = lsq_box(A, b, bounds=(0, np.inf)).x

        self.yfit = self.gauss @ self.weights   # Evaluate predictions by matrix multiplications
        self.err = 1 - self.yfit / self.counts     # relative error: yfit, counts are positive quantities
        self.chi2 = np.sum(self.err**2)  # rnorm**2 = TOTAL(err**2) (this value is only used with the /LINEAR keyword)

        return self.err

#----------------------------------------------------------------------------

    def _monitor(self, pars, niter, chi2):
        """Called every 10 iterations of CapFit when quiet=False"""

        print(f'Iteration: {niter}  chi2: {chi2:#.4g}  '
              f'Nonzero: {np.sum(self.weights != 0)}/{self.weights.size}')

#----------------------------------------------------------------------------

"""
Bayesian Time Difference of Arrival (TDOA) Positioning System using PyMC.
Original author bmoseley: https://github.com/benmoseley/bayesian-time-difference-of-arrival-positioning
Updated to work with PyMC 5 and made into an installable package by CBeckwith
"""

import numpy as np
import pymc as pm
from scipy.stats import gaussian_kde

class BayesianTDOAPositioner:
    """Class implementing Bayesian TDOA positioning."""

    def __init__(
            self,
            stations,
            x_lim=1000,
            v_mu=346,
            v_sd=20,
            t_sd=0.05,
    ):
        """
        Constructor for BayesianTDOAPositioner.

        Args:
            stations (ndarray): Nx2 array containing locations of receiver stations.
            x_lim (float): Maximum bound for x and y dimensions.
            v_mu (float): Mean of the prior distribution for wave speed.
            v_sd (float): Standard deviation of the prior for wave speed.
            t_sd (float): Standard deviation of the noise in observed TDOAs.
        """
        if len(stations) < 4:
            raise ValueError("At least 4 stations are required for Bayesian TDOA positioning!")

        if not (np.all(0 <= stations) and np.all(stations <= x_lim)):
            raise ValueError("Receiver positions (stations) must lie within the bounding box [0, x_lim].")

        self.x_lim = x_lim
        self.v_mu = v_mu
        self.v_sd = v_sd
        self.t_sd = t_sd
        self.t_lim = np.sqrt(2) * x_lim / v_mu  # Maximum time difference bound
        self.stations = stations

    def sample(self, tdoa, draws=2000, tune=2000, chains=4, init="jitter+adapt_diag", verbose=False):
        """
        Perform Bayesian inference to sample posterior distribution of source position.

        Args:
            tdoa (array_like): Time differences of arrival (observed data).
            draws (int): Number of samples to draw.
            tune (int): Number of tuning steps.
            chains (int): Number of MCMC chains.
            init (str): Initialization method for PyMC.
            verbose (bool): Whether to display the progress bar.

        Returns:
            trace: PyMC inferred posterior distribution.
        """
        if len(tdoa) != len(self.stations):
            raise ValueError("Number of TDOA observations must match the number of stations.")

        if np.max(tdoa) > self.t_lim:
            raise ValueError("TDOA exceeds the maximum time difference limit.")

        with pm.Model() as model:
            # Priors on source position, wave speed, and time offset
            x = pm.Uniform("x", lower=0, upper=self.x_lim, shape=2)
            v = pm.Normal("v", mu=self.v_mu, sigma=self.v_sd)
            t1 = pm.Uniform("t1", lower=-0.5 * self.t_lim, upper=0.5 * self.t_lim)

            # Distance and TDOA Calculation
            d = pm.math.sqrt(pm.math.sum((self.stations - x) ** 2, axis=1))
            t0 = d / v
            t = t0 - t1

            # Likelihood
            pm.Normal("Y_obs", mu=t, sigma=self.t_sd, observed=tdoa)

            # Posterior Sampling
            trace = pm.sample(
                draws=draws, tune=tune, chains=chains, target_accept=0.95,
                init=init, return_inferencedata=True, progressbar=verbose
            )

        return trace

    def fit_xy_posterior(self, trace):
        """
        Fit posterior distribution to estimate mean and standard deviation of location.

        Args:
            trace: PyMC posterior samples.

        Returns:
            tuple: Posterior mean (mu) and standard deviations (sd) for position (x, y).
        """
        r = np.linspace(0, self.x_lim, 500)
        data = trace.posterior["x"].stack(samples=("chain", "draw")).values
        kde_result = [gaussian_kde(data[:, i])(r) for i in range(2)]

        mu = [r[np.argmax(kde)] for kde in kde_result]
        sd = [(np.max(r[kde > 0.6065 * np.max(kde)]) - np.min(r[kde > 0.6065 * np.max(kde)])) / 2 for kde in kde_result]

        return mu, sd

    def forward(self, x, v=None):
        """
        Predict time of flight (ToF) for a given source position.

        Args:
            x (ndarray): Source position [x, y].
            v (float): Wave speed (optional, defaults to prior mean).

        Returns:
            ndarray: Predicted ToFs for each station.
        """
        if v is None:
            v = self.v_mu
        distances = np.linalg.norm(self.stations - x, axis=1)
        return distances / v


================
bayes_positioner
================

Bayesian Time-Difference-of-Arrival Positioning
================================================

This code implements Bayesian time-difference-of-arrival (TDOA) positioning using PyMC, a modern probabilistic programming framework. It is an updated version repackaged for installation via pip and compatible with modern PyMC versions.

Original Version
----------------
The original implementation of this code was created by Ben Moseley. You can view the original repository here: `GitHub - Bayesian TDOA Positioning by Ben Moseley <https://github.com/benmoseley/bayesian-time-difference-of-arrival-positioning>`_.

Overview
--------
Bayesian TDOA positioning is utilized for estimating the position of a signal emitter based on the differences in signal arrival times at multiple sensor locations. This approach applies Bayesian inference methods to provide probabilistic estimations of the emitter's location.

Installation
------------
This package can be installed via pip. Ensure that you have Python 3.12.9 or higher installed.

.. code-block:: bash

    pip install bayes-positioner

Usage Example
-------------
The following is an example script demonstrating Bayesian TDOA positioning using this package:

.. code-block:: python

    """
    Bayesian Time Difference of Arrival (TDOA) Positioning System using PyMC.
    Original author bmoseley: https://github.com/benmoseley/bayesian-time-difference-of-arrival-positioning
    Updated to work with PyMC 5 and made into an installable package by CBeckwith
    """

    from bayes_positioner import BayesianTDOAPositioner
    import pymc as pm
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    if __name__ == "__main__":
        # Define problem parameters

        np.random.seed(1)  # Set random seed for reproducibility
        N_STATIONS = 4  # Number of receiver stations
        x_true = np.array([500, 500])  # True source position
        v_true = 346.0  # True wave speed
        t1_true = 0.5 * (np.sqrt(2) * 500 / 346)  # True time offset
        stations = np.random.randint(250, 750, size=(N_STATIONS, 2))  # Receiver positions

        # Generate noisy observations
        d_true = np.linalg.norm(stations - x_true, axis=1)
        t0_true = d_true / v_true
        t_obs = t0_true - t1_true + 0.05 * np.random.randn(*t0_true.shape)

        # Bayesian inference
        B = BayesianTDOAPositioner(stations)
        trace = B.sample(t_obs)

        # Posterior analysis
        mu, sd = B.fit_xy_posterior(trace)
        t0_pred = B.forward(mu)

        # Print results
        print(f"Posterior mean position: {mu}")
        print(f"Posterior std-dev: {sd}")
        print(f"True TOA: {t0_true}")
        print(f"Predicted TOA: {t0_pred}")
        print(f"True Time Offset (t1): {t1_true}")

        # Plot trace (optional)
        pm.plot_trace(trace)
        plt.show()

        # Plot results
        plt.figure(figsize=(6, 6))
        plt.scatter(stations[:, 0], stations[:, 1], marker="^", s=80, label="Receivers", c="blue")
        plt.scatter(x_true[0], x_true[1], s=50, label="True Source", c="red")
        plt.gca().add_patch(
            patches.Ellipse(
                xy=(mu[0], mu[1]), width=4 * sd[0], height=4 * sd[1], color="black",
                alpha=0.5, label="Posterior ($2\\sigma$)"
            )
        )
        plt.legend()
        plt.xlim(0, B.x_lim)
        plt.ylim(0, B.x_lim)
        plt.xlabel("x (m)")
        plt.ylabel("y (m)")
        plt.title("Bayesian TDOA Positioning Results")
        plt.grid()
        plt.show()

References
----------
- `PyMC Documentation <https://www.pymc.io/>`_
- `Bayesian Time-Difference-of-Arrival Positioning by Ben Moseley <https://github.com/benmoseley/bayesian-time-difference-of-arrival-positioning>`_
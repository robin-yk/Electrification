"""Isolated legacy open-step accounting, NOT a fixed-inlet-flow closure.

Adapted from run_cstr_case.step_temperature at 7515535e83284b7568e7481098bb9b7a90b29b62.
Keep separate from the production marcher until paired reacting tests exist.
Heating expels reactor gas; cooling draws additional feed. This extra feed
means this helper must not be presented as constant total 50 sccm operation.
"""
import numpy as np

def open_temperature_step(reactor, gas, temperature_K, pressure_Pa, feed_Y):
    """Return expelled species masses (kg) and extra feed mass (kg)."""
    if temperature_K<=0 or pressure_Pa<=0:
        raise ValueError("positive temperature and pressure required")
    feed_Y=np.asarray(feed_Y,dtype=float)
    if feed_Y.shape != gas.Y.shape or np.any(feed_Y<0) or not np.isclose(feed_Y.sum(),1):
        raise ValueError("normalized feed mass fractions required")
    m0=reactor.mass
    y0=gas.Y.copy()
    gas.TP=temperature_K,pressure_Pa
    reactor.syncState()
    m1=reactor.mass
    if m1<m0:
        return (m0-m1)*y0,0.
    if m1>m0:
        mw_feed=1/float(np.sum(feed_Y/gas.molecular_weights))
        drawn=(m1-m0)*mw_feed/gas.mean_molecular_weight
        gas.TPY=temperature_K,pressure_Pa,(m0*y0+drawn*feed_Y)/(m0+drawn)
        reactor.syncState()
        return np.zeros_like(y0),drawn
    return np.zeros_like(y0),0.

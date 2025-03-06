"""
Provides simple functions to calculate a rocket's acceleration, velocity, and distance over time.
This excludes external forces such as drag or gravity.
"""

from numpy import log, float64
from rocketry_py.universal.constants import g0


def acceleration(
        mass_flow: float64,
        specific_impulse: float64,
        dry_mass: float64,
        propellant_mass: float64,
        t: float64
) -> float64:
    """
    Calculates the acceleration of a rocket over time.
    :param propellant_mass: the mass of the propellant in the rocket in kg
    :param mass_flow: the mass flow rate of the rocket engine in kg/s
    :param specific_impulse: the specific impulse of the rocket engine in seconds
    :param dry_mass: the mass of the rocket without propellant
    :param t: time in seconds
    :return: the acceleration of the rocket at time t in m/s^2
    """

    a = (mass_flow * specific_impulse * g0) / (dry_mass + propellant_mass - mass_flow * t)

    return a


def velocity(
        mass_flow: float64,
        specific_impulse: float64,
        dry_mass: float64,
        propellant_mass: float64,
        t: float64
) -> float64:
    """
    Calculates the velocity of a rocket over time.
    :param propellant_mass: the mass of the propellant in the rocket in kg
    :param mass_flow: the mass flow rate of the rocket engine in kg/s
    :param specific_impulse: the specific impulse of the rocket engine in seconds
    :param dry_mass: the mass of the rocket without propellant
    :param t: time in seconds
    :return: the velocity of the rocket at time t in m/s
    """

    v = -specific_impulse * g0 * log(1 - (t * mass_flow) / (dry_mass + propellant_mass))

    return v


def distance(
        mass_flow: float64,
        specific_impulse: float64,
        dry_mass: float64,
        propellant_mass: float64,
        t: float64
) -> float64:
    """
    Calculates the distance of a rocket over time.
    :param propellant_mass: the mass of the propellant in the rocket in kg
    :param mass_flow: the mass flow rate of the rocket engine in kg/s
    :param specific_impulse: the specific impulse of the rocket engine in seconds
    :param dry_mass: the mass of the rocket without propellant
    :param t: time in seconds
    :return: the distance of the rocket at time t in meters
    """

    d = specific_impulse * g0 * (
        ((dry_mass + propellant_mass) / mass_flow - t) *
        log((dry_mass + propellant_mass - mass_flow * t) / (dry_mass + propellant_mass)) + t
    )

    return d
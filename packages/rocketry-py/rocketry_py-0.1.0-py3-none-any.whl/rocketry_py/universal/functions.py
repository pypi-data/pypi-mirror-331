from constants import G, mE, rE
from numpy import float64

def newtonian_gravity(m1: float64, m2: float64, r: float64) -> float64:
    """
    Calculates the force of gravity between two masses.
    :param m1: the first mass in kg
    :param m2: the second mass in kg
    :param r: the distance between the two masses in meters
    :return: the force of gravity between the two masses in Newtons
    """

    F = G * m1 * m2 / r ** 2

    return F
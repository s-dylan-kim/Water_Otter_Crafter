from constants import CRAFTSMANSHIP, CONTROL, RECIPE_LEVEL_PROG_DIV, RECIPE_LEVEL_PROG_MOD, RECIPE_LEVEL_QUAL_DIV, RECIPE_LEVEL_QUAL_MOD
import numpy as np

def calc_base_progress() -> np.float32:
    p1 = np.float32(CRAFTSMANSHIP)
    p1 *= 10
    p1 /= RECIPE_LEVEL_PROG_DIV
    p1 += 2

    p1 *= RECIPE_LEVEL_PROG_MOD
    p1 /= 100

    return np.floor(p1, dtype=np.float32)

def calc_base_quality() -> np.float32:
    q1 = np.float32(CONTROL)
    q1 *= 10
    q1 /= RECIPE_LEVEL_QUAL_DIV
    q1 += 35

    q1*= RECIPE_LEVEL_QUAL_MOD
    q1 /= 100

    return np.floor(q1, dtype=np.float32)
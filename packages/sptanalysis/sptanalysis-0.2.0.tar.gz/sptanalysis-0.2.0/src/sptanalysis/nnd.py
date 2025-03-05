import numpy as np


def pairwise_array(n):
    """
    Generates the pairwise array of consecutive integers from 0 to n-1.
    """
    if n <= 1:
        return np.array([])
    else:
        return np.array([[i, i + 1] for i in range(n - 1)])


# function for nearest neighbour distances for two time points
def nearest_neighbour_distances_2d(
    x0, y0, x1, y1, verbose_return=False, conversion_factor=0.13
):
    """
    Docstring for nearest_neighbour_distances_2d
    finds the nearest neighbour distances for two time points

    Parameters:
    -----------
    x0: array-like
        x coordinates for the first time point
    y0: array-like
        y coordinates for the first time point
    x1: array-like
        x coordinates for the second time point
    y1: array-like
        y coordinates for the second time point
    verbose_return: bool
        if True, returns a dictionary with the nearest neighbour distances for x and y
    conversion_factor: float
        conversion factor to convert to a certain unit. Default is 0.13, which is the conversion factor for the 100x objective pixel size to microns

    Returns:
    --------
    nearest_neighbour_distances: array-like
        nearest neighbour distances for the two time points
    nearest_neighbour_distances_x: array-like
        nearest neighbour distances for the two time points in the x direction
    nearest_neighbour_distances_y: array-like
        nearest neighbour distances for the two time points in the y direction

    Notes:
    ------
    1. If verbose_return is True, the function returns a dictionary with the nearest neighbour distances for x and y and r
    """
    # convert using the conversion factor
    x0 = x0 * conversion_factor
    y0 = y0 * conversion_factor
    x1 = x1 * conversion_factor
    y1 = y1 * conversion_factor

    # for each point in the first time point, find the nearest neighbour in the second time point
    NND_r = np.zeros(len(x0))
    NND_x = np.zeros(len(x0))
    NND_y = np.zeros(len(x0))
    for i in range(len(x0)):
        # find the distance between the point and all the points in the second time point
        r = np.sqrt((x1 - x0[i]) ** 2 + (y1 - y0[i]) ** 2)
        # find the index of the minimum distance
        idx = np.argmin(r)
        # find the minimum distance
        NND_r[i] = r[idx]
        # find the x and y distances
        NND_x[i] = x1[idx] - x0[i]
        NND_y[i] = y1[idx] - y0[i]

    # if verbose_return is True, return a dictionary with the nearest neighbour distances for x and y
    if verbose_return:
        return {"NND_r": NND_r, "NND_x": NND_x, "NND_y": NND_y}
    else:
        return NND_r, NND_x, NND_y

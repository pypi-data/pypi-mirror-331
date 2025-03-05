import numpy as np
import pytest

from sptanalysis.nnd import nearest_neighbour_distances_2d, pairwise_array


def test_nearest_neighbour_distances_2d():
    # create two sets of random x and y coordinates
    x0 = np.random.rand(10)
    y0 = np.random.rand(10)
    x1 = np.random.rand(10)
    y1 = np.random.rand(10)

    # calculate the nearest neighbour distances
    dict_NND = nearest_neighbour_distances_2d(
        x0, y0, x1, y1, verbose_return=True, conversion_factor=1
    )
    NND_r = dict_NND["NND_r"]
    NND_x = dict_NND["NND_x"]
    NND_y = dict_NND["NND_y"]

    # check that the output arrays have the correct shape
    assert NND_r.shape == (10,)
    assert NND_x.shape == (10,)
    assert NND_y.shape == (10,)

    # check that the nearest neighbour distances are positive
    assert np.all(NND_r >= 0)

    # check that the x and y distances are correct
    for i in range(10):
        idx = np.argmin(np.sqrt((x1 - x0[i]) ** 2 + (y1 - y0[i]) ** 2))
        assert NND_x[i] == pytest.approx(x1[idx] - x0[i])
        assert NND_y[i] == pytest.approx(y1[idx] - y0[i])


def test_pairwise_array():
    # Test for n = 0
    assert np.array_equal(pairwise_array(0), np.array([]))

    # Test for n = 1
    assert np.array_equal(pairwise_array(1), np.array([]))

    # Test for n = 2
    assert np.array_equal(pairwise_array(2), np.array([[0, 1]]))

    # Test for n = 3
    assert np.array_equal(pairwise_array(3), np.array([[0, 1], [1, 2]]))

    # Test for n = 4
    assert np.array_equal(pairwise_array(4), np.array([[0, 1], [1, 2], [2, 3]]))

    # Test for n = 5
    assert np.array_equal(pairwise_array(5), np.array([[0, 1], [1, 2], [2, 3], [3, 4]]))

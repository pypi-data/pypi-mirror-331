import numpy as np
import pytest

from sptanalysis.angles import (
    Angle_Storage,
    Angle_track,
    Track_Calculations_Individual_Dict,
    asymmetry_metric,
    trajectory_angles,
)


class TestAngleStorage:
    @pytest.fixture
    def sample_storage_data(self):
        return {
            "ensemble_angles": {0: [0.1, 0.2], 1: [0.3, 0.4]},
            "track_angles": {"track1": {0: [0.1], 1: [0.2]}},
            "track_storage": {"track1": [[0, 0], [1, 1], [2, 2]]},
        }

    def test_initialization(self, sample_storage_data):
        storage = Angle_Storage(
            name="test", track_class_type="ALL", storage_data=sample_storage_data
        )

        assert storage.name == "test"
        assert storage.track_class_type == "ALL"
        assert isinstance(storage.ensemble_angles, dict)
        assert isinstance(storage.track_angles, dict)

    def test_track_lengths_calculation(self, sample_storage_data):
        storage = Angle_Storage(
            name="test", track_class_type="ALL", storage_data=sample_storage_data
        )

        track_lengths = storage.track_lengths
        assert isinstance(track_lengths, dict)
        assert track_lengths["track1"] == 3


class TestTrackCalculationsIndividualDict:
    @pytest.fixture
    def sample_track_dict(self):
        return {
            "track1": np.array([[0, 0], [1, 1], [2, 2]]),
            "track2": np.array([[0, 0], [1, 1], [2, 2], [3, 3]]),
        }

    def test_initialization(self, sample_track_dict):
        calc = Track_Calculations_Individual_Dict(
            track_dict=sample_track_dict, pixel_to_um=0.13, frame_to_seconds=0.02
        )

        assert isinstance(calc.individual_store, Angle_Storage)

    def test_invalid_track_dict(self):
        with pytest.raises(ValueError):
            Track_Calculations_Individual_Dict(
                track_dict="invalid", pixel_to_um=0.13, frame_to_seconds=0.02
            )


class TestAngleTrack:
    @pytest.fixture
    def sample_tracks(self):
        return {
            "track1": np.array([[0, 0], [1, 1], [2, 2]]),
            "track2": np.array([[0, 0], [1, 1], [2, 2], [3, 3]]),
        }

    def test_angle_track_calculation(self, sample_tracks):
        result = Angle_track(
            tracks=sample_tracks, min_track_length=3, max_track_length=10
        )

        assert "ensemble_angles" in result
        assert "track_angles" in result
        assert "track_storage" in result
        assert isinstance(result["ensemble_angles"], dict)
        assert isinstance(result["track_angles"], dict)
        assert isinstance(result["track_storage"], dict)

    def test_min_track_length(self):
        tracks = {
            "short": np.array([[0, 0], [1, 1]]),  # Too short
            "valid": np.array([[0, 0], [1, 1], [2, 2]]),
        }

        result = Angle_track(tracks, min_track_length=3)
        assert "short" not in result["track_storage"]
        assert "valid" in result["track_storage"]

    def test_max_track_length(self):
        tracks = {
            "long": np.array([[i, i] for i in range(101)]),  # Too long
            "valid": np.array([[0, 0], [1, 1], [2, 2]]),
        }

        result = Angle_track(tracks, max_track_length=100)
        assert "long" not in result["track_storage"]
        assert "valid" in result["track_storage"]


class TestTrajectoryAngles:
    def test_basic_trajectory(self):
        trajectory = np.array([[0, 0], [1, 0], [1, 1], [2, 1]])

        angles = trajectory_angles(trajectory)
        assert len(angles) == len(trajectory) - 2
        assert np.all(np.isfinite(angles))

    def test_right_angle(self):
        trajectory = np.array([[0, 0], [1, 0], [1, 1]])

        angles = trajectory_angles(trajectory)
        assert len(angles) == 1
        assert np.isclose(angles[0], np.pi / 2, atol=1e-10)

    def test_straight_line(self):
        trajectory = np.array([[0, 0], [1, 1], [2, 2]])

        angles = trajectory_angles(trajectory)
        assert len(angles) == 1

    def test_nan_handling(self):
        trajectory = np.array([[0, 0], [np.nan, 1], [2, 2]])

        angles = trajectory_angles(trajectory)
        assert len(angles) == 1
        assert np.isnan(angles[0])


class TestAsymmetryMetric:
    def test_perfect_forward_asymmetry(self):
        angles = np.array([0, 0.1, 0.2])  # All in forward range
        forward_range = np.array([0, 0.5])
        backward_range = np.array([2.5, 3.0])

        asymmetry = asymmetry_metric(angles, forward_range, backward_range)
        assert np.isclose(asymmetry, 1.0)

    def test_perfect_backward_asymmetry(self):
        angles = np.array([2.6, 2.7, 2.8])  # All in backward range
        forward_range = np.array([0, 0.5])
        backward_range = np.array([2.5, 3.0])

        asymmetry = asymmetry_metric(angles, forward_range, backward_range)
        assert np.isclose(asymmetry, -1.0)

    def test_no_asymmetry(self):
        angles = np.array([0.1, 0.2, 2.6, 2.7])  # Equal in both ranges
        forward_range = np.array([0, 0.5])
        backward_range = np.array([2.5, 3.0])

        asymmetry = asymmetry_metric(angles, forward_range, backward_range)
        assert np.isclose(asymmetry, 0.0)

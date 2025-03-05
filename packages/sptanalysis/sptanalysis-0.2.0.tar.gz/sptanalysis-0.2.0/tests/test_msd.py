from unittest.mock import Mock

import numpy as np
import pytest

# Import the classes and functions to test
from sptanalysis.msd import (
    Calculation_abc,
    DatabaseOrderUtil,
    MSD_storage,
    MSD_tau,
    combine_track_dicts,
    linear_MSD_fit,
    msd_avgerage_utility,
    power_law,
    radius_of_confinement,
)


class TestCalculationABC:
    def test_initialization(self):
        class ConcreteCalculation(Calculation_abc):
            @property
            def combined_store(self):
                return {}

            @property
            def individual_store(self):
                return {}

        calc = ConcreteCalculation(
            pixel_size=0.13, frame_length=0.02, pixel_unit="um", frame_unit="s"
        )

        assert calc.pixel_size == 0.13
        assert calc.frame_length == 0.02
        assert calc.pixel_unit == "um"
        assert calc.frame_unit == "s"

    def test_abstract_methods(self):
        with pytest.raises(TypeError):
            Calculation_abc(0.13, 0.02, "um", "s")


class TestDatabaseOrderUtil:
    @pytest.fixture
    def sample_data(self):
        # Create mock run_analysis objects
        mock_ra1 = Mock()
        mock_ra1.my_name = "test1"
        mock_ra1.parameter_storage = {"param1": "value1"}

        mock_ra2 = Mock()
        mock_ra2.my_name = "test2"
        mock_ra2.parameter_storage = {"param2": "value2"}

        return [mock_ra1, mock_ra2]

    def test_initialization(self, sample_data):
        db_util = DatabaseOrderUtil(
            data_set_RA=sample_data, pixel_to_um=0.13, frame_to_seconds=0.02
        )

        assert db_util.pixel_to_um == 0.13
        assert db_util.frame_to_seconds == 0.02
        assert len(db_util.data_set_RA) == 2

    def test_data_set_properties(self, sample_data):
        db_util = DatabaseOrderUtil(data_set_RA=sample_data)

        assert db_util.data_set_number == 2
        assert db_util.data_set_names == ["test1", "test2"]
        assert db_util.data_set_parameters == [
            {"param1": "value1"},
            {"param2": "value2"},
        ]


class TestMSDStorage:
    @pytest.fixture
    def sample_storage_data(self):
        return {
            "ensemble_MSD": {1: 0.1, 2: 0.2},
            "ensemble_MSD_error": {1: 0.01, 2: 0.02},
            "ensemble_displacement": {
                1: np.array([[0.1, 0.1]]),
                2: np.array([[0.2, 0.2]]),
            },
            "track_MSD": {"track1": {1: 0.1}},
            "track_MSD_error": {"track1": {1: 0.01}},
            "track_displacement": {"track1": {1: np.array([[0.1, 0.1]])}},
        }

    def test_initialization(self, sample_storage_data):
        storage = MSD_storage(
            name="test", track_class_type="ALL", storage_data=sample_storage_data
        )

        assert storage.name == "test"
        assert storage.track_class_type == "ALL"
        assert isinstance(storage.ensemble_MSD, dict)
        assert isinstance(storage.track_MSD, dict)

    def test_displacement_r_calculation(self, sample_storage_data):
        storage = MSD_storage(
            name="test", track_class_type="ALL", storage_data=sample_storage_data
        )

        track_r = storage.track_displacement_r
        ensemble_r = storage.ensemble_displacement_r

        assert isinstance(track_r, dict)
        assert isinstance(ensemble_r, dict)


class TestUtilityFunctions:
    def test_msd_avgerage_utility(self):
        displacements = {1: np.array([[1, 1], [2, 2]]), 2: np.array([[2, 2], [3, 3]])}

        msd, error = msd_avgerage_utility(displacements)

        assert isinstance(msd, dict)
        assert isinstance(error, dict)

    def test_radius_of_confinement(self):
        t = np.array([1, 2, 3])
        result = radius_of_confinement(t, 1.0, 0.1, 0.01)
        assert isinstance(result, np.ndarray)

    def test_power_law(self):
        t = np.array([1, 2, 3])
        result = power_law(t, 1.0, 0.1, 0.01)
        assert isinstance(result, np.ndarray)

    def test_linear_msd_fit(self):
        t = np.array([1, 2, 3])
        result = linear_MSD_fit(t, 1.0, 0.1)
        assert isinstance(result, np.ndarray)


@pytest.mark.parametrize(
    "track_dict,expected_length",
    [
        ({"track1": np.array([[0, 0], [1, 1]])}, 1),
        ({"track1": np.array([[0, 0], [1, 1], [2, 2]])}, 2),
    ],
)
def test_msd_tau(track_dict, expected_length):
    track = track_dict["track1"]
    result = MSD_tau(track)
    assert len(result) == expected_length


def test_combine_track_dicts():
    dict1 = {
        "IN": {"1": np.array([[0, 0]])},
        "IO": {},
        "OUT": {},
        "ALL": {"1": np.array([[0, 0]])},
    }
    dict2 = {
        "IN": {"2": np.array([[1, 1]])},
        "IO": {},
        "OUT": {},
        "ALL": {"2": np.array([[1, 1]])},
    }

    result = combine_track_dicts([dict1, dict2])
    assert len(result["IN"]) == 2
    assert "1" in result["IN"]
    assert "2" in result["IN"]

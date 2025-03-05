import copy

import numpy as np

from .msd import (
    Calculation_abc,
)


class Angle_Storage:
    def __init__(self, name, track_class_type, storage_data) -> None:
        self.name = name
        self.track_class_type = track_class_type
        self.storage_data = storage_data
        self._store_data()

    def _store_data(self):
        for i in self.storage_data.keys():
            setattr(self, i, self.storage_data[i])

    @property
    def ensemble_angles(self):
        return self._ensemble_angles

    @ensemble_angles.setter
    def ensemble_angles(self, ensemble_angles):
        self._ensemble_angles = ensemble_angles

    @property
    def track_angles(self):
        return self._track_angles

    @track_angles.setter
    def track_angles(self, track_angles):
        self._track_angles = track_angles

    @property
    def track_lengths(self):
        if hasattr(self, "_track_lengths"):
            return self._track_lengths
        else:
            self._track_lengths = {}
            for i in self.track_storage.keys():
                self._track_lengths[i] = len(self.track_storage[i])
            return self._track_lengths

    @track_lengths.setter
    def track_lengths(self, track_lengths):
        self._track_lengths = track_lengths

    @property
    def track_storage(self):
        return self._track_storage

    @track_storage.setter
    def track_storage(self, track_storage):
        self._track_storage = track_storage


class Track_Calculations_Individual_Dict(Calculation_abc):
    # this is a similar class to the Track_Calculations class but it takes in a track_dict instead of a data_set_RA
    def __init__(self, track_dict, **kwargs) -> None:
        """
        Parameters:
        -----------
        track_dict: dict
            dict of tracks in the form:
            {
            track_ID: [[x,y],...,[x,y]],
            .
            .
            .
            }
        KWARGS:
        -------
        pixel_to_um: float
            pixel to um conversion
        frame_to_seconds: float
            frame to seconds conversion
        frame_units: str
            frame units
        pixel_units: str
            pixel units
        min_track_length: int, Default = 1
            minimum track length to be considered.
        max_track_length: int, Default = 1000
            maximum track length to be considered.
        """
        # initialize the MSD_Calculation_abc class
        super().__init__(
            pixel_size=kwargs.get("pixel_to_um", 0.13),
            frame_length=kwargs.get("frame_to_seconds", 0.02),
            pixel_unit=kwargs.get("pixel_units", "um"),
            frame_unit=kwargs.get("frame_units", "s"),
        )
        # make sure that the track_dict is a dict
        if isinstance(track_dict, dict):
            # set the track_dict
            self.track_dict = track_dict
        else:
            raise ValueError("track_dict must be a dict")
        self.pixel_to_um = kwargs.get("pixel_to_um", 0.13)
        self.frame_to_seconds = kwargs.get("frame_to_seconds", 0.02)
        # build the Angle_Tracks
        self._build_Angle_Tracks(**kwargs)

    def _build_Angle_Tracks(self, **kwargs):
        # build the Angle_Tracks
        Angle_Tracks_i = Angle_track(
            self.track_dict,
            conversion_factor=self.pixel_to_um,
            tau_conversion_factor=self.frame_to_seconds,
            **kwargs,
        )
        ensemble_angles = Angle_Tracks_i["ensemble_angles"]
        track_angles = Angle_Tracks_i["track_angles"]
        track_viable = Angle_Tracks_i["track_storage"]
        # create the storage object
        storage_data = {
            "ensemble_angles": ensemble_angles,
            "track_angles": track_angles,
            "track_storage": track_viable,
        }
        # create the storage object
        storage_object = Angle_Storage("Track_Dict", "ALL", storage_data)
        # store the storage object
        self._storage = storage_object

    @property
    def combined_store(self):
        Warning(
            "This is a track_dict and does not have a combined_store, returning the individual_store variable"
        )
        return self._storage

    @combined_store.setter
    def combined_store(self, combined_store):
        raise ValueError("combined_store cannot be set")

    @property
    def individual_store(self):
        return self._storage

    @individual_store.setter
    def individual_store(self, individual_store):
        raise ValueError("individual_store cannot be set")


def Angle_track(
    tracks: dict,
    conversion_factor=None,
    tau_conversion_factor=None,
    min_track_length=3,
    max_track_length=100,
    **kwargs,
) -> dict:
    """Documentation for Angle_track

    Parameters:
    -----------
    tracks : dict
        dictionary of tracks, key = track ID, value = [[x,y],...] of coordinates
    conversion_factor : float (default = None)
        if conversion_factor != None then the coordinates are converted to the desired units before the MSD is calculated
    tau_conversion_factor : float (default = None)
        if tau_conversion_factor != None then the time lags are converted to the desired units before the MSD is calculated
        units are for [0->n] (int) -> seconds (1 = 0.02 seconds)
    min_track_length : int (default = 2)
        the minimum length of a track to be included in the MSD calculation
    max_track_length : int (default = 100)
        the maximum length of a track to be included in the MSD calculation

    Returns:
    --------
    return_dict : dict
        dictionary of angles for each track, key = track ID, value = dictionary of angles of the trajectory at each time lag, key = time lag, value = angles
        This has two keys, "ensemble_angles" and "track_angles" which are the ensemble angles and the angles for each track respectively
        Final structure is:
        return_dict = {
            "ensemble_angles":{time_lag:angles,...},
            "track_angles":{track_ID:{time_lag:angles,...},...}
            "track_storage":{track_ID:[[x,y],...],...}
        }
    """
    # deep copy the tracks to avoid changing the original
    tracks_copy = copy.deepcopy(tracks)
    # initialize the return dictionary
    return_dict = {}
    # initialize the ensemble angles
    ensemble_angles = {}
    # initialize the track angles
    track_angles = {}
    # viable tracks
    viable_tracks = {}

    # loop over the tracks
    for track_ID in tracks_copy.keys():
        # get the track
        track = tracks_copy[track_ID]
        if len(track) >= min_track_length and len(track) <= max_track_length:
            # store the track
            viable_tracks[track_ID] = track
            max_tau = len(track) - 1
            tau_dict = {}
            # loop over the time lags
            for tau in range(max_tau):
                # find the set of points in the track that are tau apart
                tau_points = []
                for i in range(len(track) - tau):
                    tau_points.append(track[i + tau])
                # calculate the angles between the vectors of the trajectory
                angles = trajectory_angles(np.array(tau_points))
                # store the angles
                tau_dict[tau] = angles

                # for each tau store the ensemble angles
                if tau in ensemble_angles:
                    ensemble_angles[tau] += list(angles)
                else:
                    ensemble_angles[tau] = list(angles)
            # store the track angles
            track_angles[track_ID] = tau_dict
            # for each tau store the ensemble angles
            # ensemble_angles = dic_union_two(ensemble_angles, tau_dict)

    # store the ensemble angles
    return_dict["ensemble_angles"] = ensemble_angles
    # store the track angles
    return_dict["track_angles"] = track_angles
    # store the track storage
    return_dict["track_storage"] = viable_tracks
    return return_dict


def trajectory_angles(trajectory: np.ndarray) -> np.ndarray:
    """Calculates the angles between the vectors of a trajectory. (using the cosine rule)

    Parameters:
    -----------
    trajectory: 2D array
        Array of x and y coordinates of a trajectory (in the form [[x1, y1], [x2, y2], ...])

    Returns:
    --------
    angles: 1D array
        Array of angles between the vectors of the trajectory (in radians)
    """

    angles = np.zeros(len(trajectory) - 2)

    for i in range(len(trajectory) - 2):
        # if any of the points are nan then the angle is nan
        if (
            np.isnan(trajectory[i][0])
            or np.isnan(trajectory[i][1])
            or np.isnan(trajectory[i + 1][0])
            or np.isnan(trajectory[i + 1][1])
            or np.isnan(trajectory[i + 2][0])
            or np.isnan(trajectory[i + 2][1])
        ):
            angles[i] = np.nan
        else:
            a = np.sqrt(
                (trajectory[i + 1][0] - trajectory[i][0]) ** 2
                + (trajectory[i + 1][1] - trajectory[i][1]) ** 2
            )
            b = np.sqrt(
                (trajectory[i + 2][0] - trajectory[i + 1][0]) ** 2
                + (trajectory[i + 2][1] - trajectory[i + 1][1]) ** 2
            )
            c = np.sqrt(
                (trajectory[i + 2][0] - trajectory[i][0]) ** 2
                + (trajectory[i + 2][1] - trajectory[i][1]) ** 2
            )
            angles[i] = np.arccos((a**2 + b**2 - c**2) / (2 * a * b))

    return angles


def asymmetry_metric(
    angle_distribution: np.ndarray,
    forward_angle_range: np.ndarray,
    backward_angle_range: np.ndarray,
) -> float:
    """Calculates the asymmetry metric for the forward and backward angle distributions.
    Defined as the difference between the percentage of angles in the forward and backward angle ranges. This metric is bounded by
    -1 and 1, where -1 indicates that all angles are in the backward angle range and 1 indicates that all angles are in the forward angle range.

    Parameters:
    -----------
    angle_distribution: 1D array
        Array of angles between the vectors of the trajectory
    forward_angle_range: 1D array of length 2
        Range of angles to consider for the forward angle distribution (in radians)
    backward_angle_range: 1D array of length 2
        Range of angles to consider for the backward angle distribution (in radians)

    Returns:
    --------
    asymmetry: float
        Asymmetry metric for the forward and backward angle distributions
    """

    total_angles = len(angle_distribution)
    forward_angles = len(
        angle_distribution[
            (angle_distribution >= forward_angle_range[0])
            & (angle_distribution <= forward_angle_range[1])
        ]
    )
    backward_angles = len(
        angle_distribution[
            (angle_distribution >= backward_angle_range[0])
            & (angle_distribution <= backward_angle_range[1])
        ]
    )
    # now take the difference between the forward and backward angles percentages
    asymmetry = (forward_angles / total_angles) - (backward_angles / total_angles)
    # double check if this is bounded by -1 and 1
    assert (
        asymmetry >= -1 and asymmetry <= 1
    ), "Asymmetry metric is not bounded by -1 and 1"
    return asymmetry

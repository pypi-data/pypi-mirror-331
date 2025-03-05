def _convert_ams_tracks_to_SPTAnalysis(tracks: dict) -> dict:
    """
    Tracks dict is of the following format:
        - {0: {"xy": [[x,y,z],...[x,y,z]], "frames": [f1,...]}, 1: ... ,}
        - Format is {Track_ID: {xyz coordinates, frames}}

    Output format is:
        - {0: [[x,y,z], ...]], 1: ... }
        - Format is {Track_ID: [xyz coordinates]}
    """

    track_dict = {}
    for i in tracks.keys():
        track_dict[i] = tracks[i]["xy"]
    return track_dict

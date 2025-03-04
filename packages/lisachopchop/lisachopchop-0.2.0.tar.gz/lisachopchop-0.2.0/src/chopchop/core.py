"""
Core module
===========

This module provides functions to compute and visualize data delivery scenarios.

Delivery scenario
-----------------

Start by instantiating a :class:`DataDeliveryScenario` object with the desired
parameters. The object provides derived parameters and can print them.

.. autoclass:: DataDeliveryScenario
    :members:

Telemetry
---------

The following functions allow you to compute and visualize downloaded segments
during a telemetry session. You can also compute masks to mask data arrays with
the available data.

.. autofunction:: compute_downloaded_segments

.. autofunction:: plot_downloaded_segments

.. autofunction:: plot_available_data

.. autofunction:: compute_masks
"""

import math
from typing import TypeAlias

import attrs
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import ArrayLike


@attrs.frozen
class DataDeliveryScenario:
    """Configure a data delivery scenario.

    Default values are based on ESA-LISA-EST-MIS-TN-0003 - LISA Science Data
    Description and Budget (Iss1Rev0), denoted as [AD1].
    """

    segment_duration: float = 5 * 60
    """Duration of each segment [s].

    A segment is the smallest unit of data that can be delivered.
    """

    session_duration: float = 8 * 3600
    """Duration of a telemetry session [s].

    A telemetry session is a commmunication session between the LISA instrument
    and the ground station. During a telemetry session, commands are sent to the
    instrument and data segements are received.
    """

    session_interval: float = 24 * 3600
    """Interval between two telemetry sessions [s].

    The interval between two telemetry sessions is the time between the
    beginning of two consecutive telemetry sessions.
    """

    rate_per_spacecraft: float = 10.98e3
    """Data generation rate per spacecraft, without margin [bps]."""

    p1_rate_per_spacecraft: float = 3.58e3
    """Priority-1 data generation rate per spacecraft, without margin [bps]."""

    rate_margin: float = 0.5
    """Margin on the data generation rate."""

    packet_overhead: float = 0.1
    """Packet overhead."""

    downlink_overhead: float = 20e3
    """Overhead for high-rate data downlink [bps]."""

    transfer_time: float = (2.5e9 + 50e9) / 3e8
    """Total transfer time [s].

    This includes the time to transfer data between spacecraft and from the
    time to transfer data from the spacecraft to the ground station.
    """

    packet_loss_rate: float = 0.0
    """Data packet loss rate during transfer."""

    def _constellation_rate(self, rate: float) -> float:
        """Convert a rate per spacecraft to a constellation rate.

        This function also adds margins and overheads.

        Parameters
        ----------
        rate : float
            Rate per spacecraft, without margin [bps].

        Returns
        -------
        float
            Constellation rate, including margin [bps].
        """
        return 3 * rate * (1 + self.rate_margin) * (1 + self.packet_overhead)

    @property
    def data_volume_per_session(self) -> float:
        """Volume of data to download per day including marging [bits]."""
        constellation_rate = self._constellation_rate(self.rate_per_spacecraft)
        total_rate = constellation_rate + self.downlink_overhead  # + RgEng
        return total_rate * self.session_interval

    @property
    def download_rate(self) -> float:
        """Necessary download rate [bps]."""
        return self.data_volume_per_session / self.session_duration

    @property
    def p1_rate(self) -> float:
        """Priority data generate rate [bps]."""
        return self._constellation_rate(self.p1_rate_per_spacecraft)

    @property
    def data_volume_per_segment(self) -> float:
        """Volume of data to download per segment [bits]."""
        return self.segment_duration * self.p1_rate

    @property
    def segment_download_time(self) -> float:
        """Time to download a segment [s]."""
        return self.data_volume_per_segment / self.download_rate

    @property
    def available_download_time_between_live_segments(self) -> float:
        """Time available to download data between live segments [s]."""
        return self.segment_duration - self.segment_download_time

    @property
    def downloaded_segments_between_live_segments(self) -> int:
        """Number of segments that can be downloaded between live segments."""
        return math.floor(
            self.available_download_time_between_live_segments
            * self.download_rate
            / self.data_volume_per_segment
        )

    @property
    def archived_data_segments(self) -> int:
        """Number of archived data segments to be downloaded."""
        return math.ceil(
            (self.session_interval - self.session_duration)
            * self.p1_rate
            / self.data_volume_per_segment
        )

    @property
    def archived_data_download_time(self) -> float:
        """Time to download all archived data [s]."""
        return (
            self.archived_data_segments
            / self.downloaded_segments_between_live_segments
            * self.segment_duration
        )

    def print_derived_parameters(self) -> None:
        """Print derived parameters."""
        print(
            "Volume of data to download (including marging):"
            f" {self.data_volume_per_session / 1e6:.3f} Mbits per day\n"
            f"Downloading rate: {self.download_rate / 1e3:.1f} kbps\n"
            f"Data generation rate for priority 1 data: {self.p1_rate / 1e3} kbps\n"
            "Volume of data in a segement:"
            f" {self.data_volume_per_segment / 1e3} kbits\n"
            f"Download time for a segment: {self.segment_download_time:.1f} s\n"
            f"Number of archived data segments that can be downloaded between two"
            f" live data segments: {self.downloaded_segments_between_live_segments}\n"
            "Number of archived data segments to download:"
            f" {self.archived_data_segments}\n"
            f"Time to download all archived data:"
            f" {self.archived_data_download_time / 3600:.1f} h",
        )


SegmentIdentifer: TypeAlias = float
"""Segment identifier, here as segment start time [s].

The start time is represented as the number of seconds since the current
telemetry session start. Archived data segments are therefore identified by
negative numbers.
"""

DownloadedSegmentList: TypeAlias = list[tuple[float, SegmentIdentifer]]
"""List of downloaded segments.

The list contains tuples, each containing the segment reception time (when it
becomes available for data processing), and the segment identifer.
"""


def compute_downloaded_segments(
    scenario: DataDeliveryScenario, seed: int = 0
) -> tuple[DownloadedSegmentList, list[SegmentIdentifer]]:
    """Compute a list of downloaded segments.

    Parameters
    ----------
    scenario : DataDeliveryScenario
        Data delivery scenario.
    seed : int
        Random seed used for data packet loss simulation.

    Returns
    -------
    DownloadedSegmentList
        List of downloaded segments with their reception times.
    list[SegmentIdentifer]
        List of lost packets.
    """

    # First element is the first element to be downloaded
    download_queue = list(
        (-np.arange(1, scenario.archived_data_segments)) * scenario.segment_duration
    )

    # Time at the communicating spacecraft
    sc_current_time = 0.0
    # Time at which the next live segment will be available
    next_available_live_segment_time = 0.0

    # List of all downloaded segments
    downloaded_segments: DownloadedSegmentList = []
    lost_packets = []

    # Create random number generator from seed
    random_gen = np.random.default_rng(seed)

    while sc_current_time < scenario.session_duration:

        # Clean temp vars to avoid being polluted by the previous loop
        new_segment = None

        # Check if new kive segment is available
        if sc_current_time >= next_available_live_segment_time:
            # Live segments have priority
            download_queue.insert(0, next_available_live_segment_time)
            next_available_live_segment_time += scenario.segment_duration

        # Try to download a segment
        try:
            new_segment = download_queue.pop(0)
        except IndexError:
            # Need to wait for the next NRT segment
            sc_current_time = next_available_live_segment_time
            continue

        if random_gen.random() < scenario.packet_loss_rate:
            # Lost packet so add it at the end of the download queue
            lost_packets.append(new_segment)
            download_queue.append(new_segment)
        else:
            # Add the segment to the list of downloaded segment
            downloaded_segments.append(
                (sc_current_time + scenario.transfer_time, new_segment)
            )

        # Update the time
        sc_current_time += scenario.segment_download_time

    return (downloaded_segments, lost_packets)


def plot_downloaded_segments(
    scenario: DataDeliveryScenario, segments: DownloadedSegmentList
) -> None:
    """Plot downloaded segments.

    Parameters
    ----------
    scenario : DataDeliveryScenario
        Data delivery scenario.
    segments : DownloadedSegmentList
        List of downloaded segments, e.g., as computed by
        :func:`compute_downloaded_segments`.
    """

    plt.figure(figsize=(10, 7))
    for ti, istart in segments:
        plt.plot(
            np.array([istart, istart + scenario.segment_duration]) / 3600,
            np.ones(2) * ti / 3600,
            "-b",
        )
    plt.xlabel("Downloaded segment [h]")
    plt.xlim([-16, 8])
    plt.ylabel("Availability time on ground [h]")
    plt.grid()
    plt.title("Downloaded segments")


def plot_available_data(
    scenaria: DataDeliveryScenario, segments: DownloadedSegmentList
) -> None:
    """Plot available data (cumulated downlaaded segments).

    Parameters
    ----------
    scenario : DataDeliveryScenario
        Data delivery scenario.
    segments : DownloadedSegmentList
        List of downloaded segments, e.g., as computed by
        :func:`compute_downloaded_segments`.
    """
    plt.figure(figsize=(10, 7))
    accumulated_segments: list[SegmentIdentifer] = []

    for availability_time, seg_start in segments:
        accumulated_segments.append(seg_start)
        for seg in accumulated_segments:
            plt.plot(
                np.array([seg, seg + scenaria.segment_duration]) / 3600,
                np.ones(2) * availability_time / 3600,
                "-b",
            )

    plt.xlabel("Available data [h]")
    plt.ylabel("Availability time on ground [h]")
    plt.grid()
    plt.xlim([-16, 8])
    plt.title("Available data")


def compute_masks(
    scenario: DataDeliveryScenario,
    segments: DownloadedSegmentList,
    data_times: ArrayLike,
) -> tuple[np.ndarray, np.ndarray]:
    """Convert downloaded segments to mask arrays.

    You can use the mask arrays to mask data arrays with the available data.

    >>> availability_times, masks = compute_masks(segments, data_times)
    >>> my_mask, corresponding_availability_time = masks[234], availability_times[234]
    >>> masked_data = data[my_mask]

    Parameters
    ----------
    scenario : DataDeliveryScenario
        Data delivery scenario.
    segments : DownloadedSegmentList, of length N
        List of downloaded segments, e.g., as computed by
        :func:`compute_downloaded_segments`.
    data_times : array-like of shape (M,)
        Times attached to the data array to be masked [s]. The times should
        be represented as the number of seconds since the current telemetry
        session start.

    Returns
    -------
    Array, of shape (N,)
        Array of availability times on ground [s].
    Array, of shape (N, M)
        Array of masks. True values indicate that the data is available.
    """
    data_times = np.asarray(data_times)
    masks = np.full((len(segments), len(data_times)), False)

    for availability_index, (_, seg_start) in enumerate(segments):
        seg_end = seg_start + scenario.segment_duration
        condition = np.logical_and(seg_start <= data_times, data_times <= seg_end)
        masks[availability_index:, condition] = True

    availability_times = np.array([t for t, _ in segments])

    return availability_times, masks

# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from enum import StrEnum
from urllib.parse import urljoin

import requests
from requests.models import Response

from .exceptions import HTTPRequestError

__all__ = ["Client"]


class ClientRoute(StrEnum):
    # LOGIN
    LOGIN_VALIDATE = "login/validate"
    # CAMERAS
    CAMERAS_HEARTBEAT = "cameras/heartbeat"
    CAMERAS_IMAGE = "cameras/image"
    CAMERAS_FETCH = "cameras/"
    # POSES
    POSES_CREATE = "poses/"
    POSES_BY_ID = "poses/{pose_id}"
    POSES_MASKS_BY_ID = "poses/{pose_id}/occlusion_masks"
    # OCCLUSION MASKS
    OCCLUSION_MASKS_CREATE = "occlusion_masks"
    OCCLUSION_MASKS_BY_ID = "occlusion_masks/{mask_id}"
    # DETECTIONS
    DETECTIONS_CREATE = "detections/"
    DETECTIONS_FETCH = "detections"
    DETECTIONS_URL = "detections/{det_id}/url"
    # SEQUENCES
    SEQUENCES_LABEL = "sequences/{seq_id}/label"
    SEQUENCES_FETCH_DETECTIONS = "sequences/{seq_id}/detections"
    SEQUENCES_FETCH_LATEST = "sequences/unlabeled/latest"
    SEQUENCES_FETCH_FROMDATE = "sequences/all/fromdate"
    # ORGS
    ORGS_FETCH = "organizations"


def _to_str(coord: float) -> str:
    """Format string conditionally."""
    return f"{coord:.0f}" if coord == round(coord) else f"{coord:.3f}"


def _dump_bbox_to_json(
    bboxes: list[tuple[float, float, float, float, float]],
) -> str:
    """Performs a custom JSON dump for list of coordinates.

    Args:
        bboxes: list of tuples where each tuple is a relative coordinate in order xmin, ymin, xmax, ymax, conf
    Returns:
        the JSON string dump with 3 decimal precision
    """
    if any(coord > 1 or coord < 0 for bbox in bboxes for coord in bbox):
        raise ValueError("coordinates are expected to be relative")
    if any(len(bbox) != 5 for bbox in bboxes):
        raise ValueError("Each bbox is expected to be in format xmin, ymin, xmax, ymax, conf")
    box_strs = (
        f"({_to_str(xmin)},{_to_str(ymin)},{_to_str(xmax)},{_to_str(ymax)},{_to_str(conf)})"
        for xmin, ymin, xmax, ymax, conf in bboxes
    )
    return f"[{','.join(box_strs)}]"


class Client:
    """Isometric Python client for Pyronear wildfire detection API.

    Args:
        token: your personal API token
        endpoint: the host for your instance of pyronear API
        timeout (int): number of seconds before request timeout
        kwargs: optional parameters of `requests.post`
    """

    def __init__(
        self,
        token: str,
        host: str = "https://api.pyronear.org",
        timeout: int = 10,
        **kwargs,
    ) -> None:
        # Check host
        if requests.get(urljoin(host, "status"), timeout=timeout, **kwargs).status_code != 200:
            raise ValueError(f"unable to reach host {host}")
        # Prepend API url to each route
        self._route_prefix = urljoin(host, "api/v1/")
        # Check token
        response = requests.get(
            urljoin(self._route_prefix, ClientRoute.LOGIN_VALIDATE),
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout,
            **kwargs,
        )
        if response.status_code != 200:
            raise HTTPRequestError(response.status_code, response.text)
        self.token = token
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    # CAMERAS
    def fetch_cameras(self) -> Response:
        """List the cameras accessible to the authenticated user.

        >>> from pyroclient import client
        >>> api_client = Client("MY_USER_TOKEN")
        >>> response = api_client.fetch_cameras()

        Returns:
            HTTP response
        """
        return requests.get(
            urljoin(self._route_prefix, ClientRoute.CAMERAS_FETCH),
            headers=self.headers,
            timeout=self.timeout,
        )

    def heartbeat(self) -> Response:
        """Update the last ping of the camera.

        >>> from pyroclient import Client
        >>> api_client = Client("MY_CAM_TOKEN")
        >>> response = api_client.heartbeat()

        Returns:
            HTTP response containing the update device info
        """
        return requests.patch(
            urljoin(self._route_prefix, ClientRoute.CAMERAS_HEARTBEAT), headers=self.headers, timeout=self.timeout
        )

    def update_last_image(self, media: bytes) -> Response:
        """Update the last image of the camera.

        >>> from pyroclient import Client
        >>> api_client = Client("MY_CAM_TOKEN")
        >>> with open("path/to/my/file.ext", "rb") as f: data = f.read()
        >>> response = api_client.update_last_image(data)

        Returns:
            HTTP response containing the update device info
        """
        return requests.patch(
            urljoin(self._route_prefix, ClientRoute.CAMERAS_IMAGE),
            headers=self.headers,
            files={"file": ("logo.png", media, "image/png")},
            timeout=self.timeout,
        )

    # POSES
    def create_pose(
        self,
        camera_id: int,
        azimuth: float,
        patrol_id: int | None = None,
    ) -> Response:
        """Create a pose for a camera.

        >>> api_client.create_pose(camera_id=1, azimuth=120.5, patrol_id=3)
        """
        payload = {
            "camera_id": camera_id,
            "azimuth": azimuth,
        }
        if patrol_id is not None:
            payload["patrol_id"] = patrol_id

        return requests.post(
            urljoin(self._route_prefix, ClientRoute.POSES_CREATE),
            headers=self.headers,
            json=payload,
            timeout=self.timeout,
        )

    def patch_pose(
        self,
        pose_id: int,
        azimuth: float | None = None,
        patrol_id: int | None = None,
    ) -> Response:
        """Update a pose.

        >>> api_client.patch_pose(pose_id=1, azimuth=90.0)
        """
        payload = {}
        if azimuth is not None:
            payload["azimuth"] = azimuth
        if patrol_id is not None:
            payload["patrol_id"] = patrol_id

        return requests.patch(
            urljoin(self._route_prefix, ClientRoute.POSES_BY_ID.format(pose_id=pose_id)),
            headers=self.headers,
            json=payload,
            timeout=self.timeout,
        )

    def delete_pose(self, pose_id: int) -> Response:
        """Delete a pose.

        >>> api_client.delete_pose(pose_id=1)
        """
        return requests.delete(
            urljoin(self._route_prefix, ClientRoute.POSES_BY_ID.format(pose_id=pose_id)),
            headers=self.headers,
            timeout=self.timeout,
        )

    def list_pose_masks(self, pose_id: int) -> Response:
        """List occlusion masks for a pose (given its pose_id).

        >>> api_client.list_pose_masks(pose_id=1)
        """
        return requests.get(
            urljoin(self._route_prefix, ClientRoute.POSES_MASKS_BY_ID.format(pose_id=pose_id)),
            headers=self.headers,
            timeout=self.timeout,
        )

    # OCCLUSION MASKS

    def create_occlusion_mask(
        self,
        pose_id: int,
        mask: str,
    ) -> Response:
        """Create a create occlusion_mask for a pose.

        >>> api_client.create_occlusion_mask(pose_id=1, mask="(0.1,0.1,0.9,0.9)")
        """
        payload = {
            "pose_id": pose_id,
            "mask": mask,
        }

        return requests.post(
            urljoin(self._route_prefix, ClientRoute.OCCLUSION_MASKS_CREATE),
            headers=self.headers,
            json=payload,
            timeout=self.timeout,
        )

    def patch_occlusion_mask(
        self,
        mask_id: int,
        mask: str,
    ) -> Response:
        """Update an occlusion mask.

        >>> api_client.patch_occlusion_mask(mask_id=1, mask="(0.1,0.2,0.9,0.3)")
        """
        payload = {"mask": mask}

        return requests.patch(
            urljoin(self._route_prefix, ClientRoute.OCCLUSION_MASKS_BY_ID.format(mask_id=mask_id)),
            headers=self.headers,
            json=payload,
            timeout=self.timeout,
        )

    def get_occlusion_mask(
        self,
        mask_id: int,
    ) -> Response:
        """Get mask from occlusion mask.

        >>> api_client.get_occlusion_mask(mask_id=1")
        """
        return requests.get(
            urljoin(self._route_prefix, ClientRoute.OCCLUSION_MASKS_BY_ID.format(mask_id=mask_id)),
            headers=self.headers,
            timeout=self.timeout,
        )

    def delete_occlusion_mask(self, mask_id: int) -> Response:
        """Delete an occlusion mask.

        >>> api_client.delete_occlusion_mask(mask_id=1)
        """
        return requests.delete(
            urljoin(self._route_prefix, ClientRoute.OCCLUSION_MASKS_BY_ID.format(mask_id=mask_id)),
            headers=self.headers,
            timeout=self.timeout,
        )

    # DETECTIONS

    def create_detection(
        self,
        media: bytes,
        azimuth: float,
        bboxes: list[tuple[float, float, float, float, float]],
        pose_id: int | None = None,
    ) -> Response:
        """Notify the detection of a wildfire on the picture taken by a camera.

        >>> from pyroclient import Client
        >>> api_client = Client("MY_CAM_TOKEN")
        >>> with open("path/to/my/file.ext", "rb") as f: data = f.read()
        >>> response = api_client.create_detection(data, azimuth=124.2, bboxes=[(.1,.1,.5,.8,.5)], pose_id=12)

        Args:
            media: byte data of the picture
            azimuth: the azimuth of the camera when the picture was taken
            bboxes: list of tuples where each tuple is a relative coordinate in order xmin, ymin, xmax, ymax, conf
            pose_id: optional, pose_id of the detection

        Returns:
            HTTP response
        """
        if not isinstance(bboxes, (list, tuple)) or len(bboxes) == 0 or len(bboxes) > 5:
            raise ValueError("bboxes must be a non-empty list of tuples with a maximum of 5 boxes")
        data = {
            "azimuth": azimuth,
            "bboxes": _dump_bbox_to_json(bboxes),
        }
        if pose_id is not None:
            data["pose_id"] = pose_id
        return requests.post(
            urljoin(self._route_prefix, ClientRoute.DETECTIONS_CREATE),
            headers=self.headers,
            data=data,
            timeout=self.timeout,
            files={"file": ("logo.png", media, "image/png")},
        )

    def get_detection_url(self, detection_id: int) -> Response:
        """Retrieve the URL of the media linked to a detection.

        >>> from pyroclient import client
        >>> api_client = Client("MY_USER_TOKEN")
        >>> response = api_client.get_detection_url(1)

        Args:
            detection_id: ID of the associated detection entry

        Returns:
            HTTP response
        """
        return requests.get(
            urljoin(self._route_prefix, ClientRoute.DETECTIONS_URL.format(det_id=detection_id)),
            headers=self.headers,
            timeout=self.timeout,
        )

    def fetch_detections(self) -> Response:
        """List the detections accessible to the authenticated user.

        >>> from pyroclient import client
        >>> api_client = Client("MY_USER_TOKEN")
        >>> response = api_client.fetch_detections()

        Returns:
            HTTP response
        """
        return requests.get(
            urljoin(self._route_prefix, ClientRoute.DETECTIONS_FETCH),
            headers=self.headers,
            timeout=self.timeout,
        )

    def label_sequence(self, sequence_id: int, is_wildfire: str) -> Response:
        """Update the label of a sequence made by a camera.

        >>> from pyroclient import client
        >>> api_client = Client("MY_USER_TOKEN")
        >>> response = api_client.label_sequence(1, is_wildfire="wildfire_smoke")

        Args:
            sequence_id: ID of the associated sequence entry
            is_wildfire: whether this sequence is confirmed as a wildfire

        Returns:
            HTTP response
        """
        return requests.patch(
            urljoin(self._route_prefix, ClientRoute.SEQUENCES_LABEL.format(seq_id=sequence_id)),
            headers=self.headers,
            json={"is_wildfire": is_wildfire},
            timeout=self.timeout,
        )

    def fetch_sequences_from_date(self, from_date: str, limit: int = 15, offset: int = 0) -> Response:
        """List the sequences accessible to the authenticated user for a specific date.

        >>> from pyroclient import client
        >>> api_client = Client("MY_USER_TOKEN")
        >>> response = api_client.fetch_sequences_from_date("2023-07-04")

        Args:
            from_date: date of the sequences to fetch
            limit: maximum number of sequences to fetch
            offset: number of sequences to skip before starting to fetch

        Returns:
            HTTP response
        """
        params: dict[str, str | int] = {"from_date": from_date, "limit": limit, "offset": offset}
        return requests.get(
            urljoin(self._route_prefix, ClientRoute.SEQUENCES_FETCH_FROMDATE),
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )

    def fetch_latest_sequences(self) -> Response:
        """List the latest sequences accessible to the authenticated user.

        >>> from pyroclient import client
        >>> api_client = Client("MY_USER_TOKEN")
        >>> response = api_client.fetch_latest_sequences()

        Returns:
            HTTP response
        """
        return requests.get(
            urljoin(self._route_prefix, ClientRoute.SEQUENCES_FETCH_LATEST),
            headers=self.headers,
            timeout=self.timeout,
        )

    def fetch_sequences_detections(self, sequence_id: int, limit: int = 10, desc: bool = True) -> Response:
        """List the detections of a sequence.

        >>> from pyroclient import client
        >>> api_client = Client("MY_USER_TOKEN")
        >>> response = api_client.fetch_sequences_detections(1)

        Args:
            sequence_id: ID of the associated sequence entry
            limit: maximum number of detections to fetch
            desc: whether to order the detections by created_at in descending order

        Returns:
            HTTP response
        """
        return requests.get(
            urljoin(self._route_prefix, ClientRoute.SEQUENCES_FETCH_DETECTIONS.format(seq_id=sequence_id)),
            headers=self.headers,
            params={"limit": limit, "desc": desc},
            timeout=self.timeout,
        )

    # ORGANIZATIONS

    def fetch_organizations(self) -> Response:
        """List the organizations accessible to the authenticated user.

        >>> from pyroclient import client
        >>> api_client = Client("MY_USER_TOKEN")
        >>> response = api_client.fetch_organizations()

        Returns:
            HTTP response
        """
        return requests.get(
            urljoin(self._route_prefix, ClientRoute.ORGS_FETCH),
            headers=self.headers,
            timeout=self.timeout,
        )

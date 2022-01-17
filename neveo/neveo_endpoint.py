"""Handles call to Neveo endpoint."""
import requests as rq
from urllib.parse import urljoin
import time

import utils

logger = utils.get_logger(__name__)


class NeveoEndpoint(object):
    """Handles requests to Neveo Endpoint."""

    instance = None

    def __init__(self, url: str, login: str, password: str):
        """Define url of endpoint."""
        self.url = url
        self.login = login
        self.password = password

    @classmethod
    def get_instance(cls):
        """Create singleton instance."""
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

    def authenticate(self):
        """Generate_token."""
        path = "/api/sessions/user_auth"
        logger.debug("Logging in to Neveo endpoint {}".format(path))
        json = {"user": {"email": self.login, "password": self.password}}

        logger.debug("sending {}".format(json))
        result = self.call_endpoint(
            method="post",
            subpath=path,
            content_type="application/json",
            json=json,
            re_authenticate=False,
        )

        if result:
            logger.debug("Logged in.")
            self.token = result.get("access_token")
            return True

        return False

    def call_endpoint(
        self,
        method: str = "post",
        subpath: str = "",
        params=None,
        json=None,
        content_type=None,
        re_authenticate: bool = True,
    ):
        """Send a request to the Neveo endpoint.

        Args:
            - method: str
                get, put, post
            - subpath: str
                the route on the endpoint
            - params: Dict[str, Any]
                the GET parameters to add
            - json: Dict
                the json payload
            - content_type: str
                the content_type to add to the headers
            - re_authenticate: bool
                Whether to try to re_authenticate (used to not authenticate infinitely)
        """
        assert method in ["get", "post", "put"]
        headers = {}
        if content_type:
            headers["Content-Type"] = content_type
        try_number = 0
        path = urljoin(self.url, subpath)
        logger.debug("path : {}".format(urljoin(self.url, subpath)))
        logger.debug("headers : {}".format(headers))
        logger.debug("json : {}".format(json))
        while try_number < 3:
            try_number += 1
            try:
                r = getattr(rq, method)(
                    path,
                    headers=headers,
                    params=params,
                    json=json,
                )

                if r.status_code == 401 and re_authenticate:
                    self.authenticate()
                    return self.call_endpoint(
                        method=method,
                        subpath=subpath,
                        params=params,
                        json=json,
                        content_type=content_type,
                        relog=False,
                    )

                if r.status_code >= 400:
                    logger.warning(
                        "Neveo Endpoint returned ({}) {}".format(r.status_code, r.text)
                    )
                    return {}

                return r.json()
            except Exception as e:
                logger.warning("Exception while calling Neveo Endpoint: {}".format(e))
            time.sleep(1)
        logger.error(
            (
                "Error while calling Neveo Endpoint: "
                "method: {}, subpath: {}, params: {}, json: {}, "
                "content-type: {}, re_authenticate: {}".format(
                    method, subpath, params, json, content_type, re_authenticate
                )
            )
        )
        return {}

    def list_medias(self, page: int):
        """Load candidate id from a sender_id."""
        if not self.authenticate():
            return []
        medias = self.call_endpoint(
            "get",
            "/api/family/media_objects?limit=100&page={}&token={}".format(
                page, self.token
            ),
        )
        if medias:
            logger.debug("medias {}".format(medias))
            return medias.get("media_objects")
        return []

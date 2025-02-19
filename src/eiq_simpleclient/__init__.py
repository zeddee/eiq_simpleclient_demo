from furl import furl
import json
from pprint import pprint as pp
import requests
from typing import Any, Dict, List
import uuid


class APIClient:
    def __init__(self, baseurl: str, apikey: str):
        """Simple Python REST API client for EclecticIQ Intelligence Center (IC).

        :param baseurl: URL to access the REST API endpoint on your IC instance.
            For example: "https://ic-playground.eclecticiq.com/api/beta"
        :type baseurl: str
        :param apikey: API key
        :type apikey: str
        """
        self.baseurl = baseurl
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {apikey}",
            "Accept": "application/json",
        }

    def get(self, path: str, params: Dict[str, str] = {}) -> Dict[str, Any]:
        """Send a GET request to a given endpoint"""
        if path.startswith(self.baseurl):
            f = furl(path)
        else:
            if not path.startswith("/"):
                path = "/" + path
            f = furl(self.baseurl)
            f.path.add(path)
            f.args = params

        r = requests.get(f, headers=self.headers)
        return json.loads(r.text)

    def post(self, path: str, payload: str) -> Dict[str, Any]:
        """Send a POST request to a given endpoint"""
        if not path.startswith("/"):
            path = "/" + path

        f = furl(self.baseurl)
        f.path.add(path)

        r = requests.post(f, headers=self.headers, data=json.dumps(payload))
        return json.loads(r.text)

    def resolve(self, path: str) -> Dict[str, Any]:
        """Retrieves a resources at a given endpoint"""

        # Get only stem of path; omit query parameters
        f = furl(path)
        f.host = furl(self.baseurl).host
        f.scheme = furl(self.baseurl).scheme
        f.args = {}

        return self.get(f.url)

    @staticmethod
    def make_id(namespace: str, kind: str, value: str):
        """Creates a STIX-like ID, used to set the `data.id`
        field of the payload when making a POST /entities
        request.

        :param namespace: E.g., "tip.example.com"
        :type namespace: str
        :param kind: The type of object being identified.
            This is usually an entity type, e.g. "indicator"
        :type kind: str
        :param value: The value contained by the object to identify.
            For example, when identifying an IPv4 indicator,
            the 'value' should be the IPv4 value being indicated.
            E.g., "172.16.1.10"
        :type value: str
        """

        hashable_value = "{}:{}".format(kind.encode("utf-8"), value.encode("utf-8"))

        this_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, hashable_value)

        if kind in ["email", "uri", "ipv4", "ip", "domain"]:
            tlo_type = "indicator"
        else:
            tlo_type = kind

        return "{{{}}}{}-{}".format(namespace, tlo_type, this_uuid)

from uplink import (
    Consumer,
    get as http_get,
    post,
    patch,
    delete,
    returns,
    headers,
    retry,
    Body,
    json,
    Query,
)


from .module_imports import key
from uplink.retry.when import status_5xx


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class _Simple_Forms(Consumer):
    """Inteface to Simple Forms resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("simple-forms")
    def list(
        self,
        limit: Query = None,
        order: Query = None,
    ):
        """This call will return list of resourcess."""

    @returns.json
    @http_get("simple-forms/{uid}")
    def get(self, uid: str):
        """This call will get the resources for the specified uid."""

    @delete("simple-forms/{uid}")
    def delete(self, uid: str):
        """This call will delete the resources for the specified uid."""

    @returns.json
    @json
    @post("simple-forms")
    def insert(self, resource: Body):
        """This call will create the resources with the specified parameters."""

    @json
    @patch("simple-forms/{uid}")
    def update(self, uid: str, resource: Body):
        """This call will update the resources with the specified parameters."""

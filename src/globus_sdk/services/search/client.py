import logging
from typing import Any, Dict, Optional, Union

from globus_sdk import client, paging, response, utils
from globus_sdk.scopes import SearchScopes
from globus_sdk.types import UUIDLike

from .data import SearchQuery
from .errors import SearchAPIError

log = logging.getLogger(__name__)


class SearchClient(client.BaseClient):
    r"""
    Client for the Globus Search API

    This class provides helper methods for most common resources in the
    API, and basic ``get``, ``put``, ``post``, and ``delete`` methods
    from the base client that can be used to access any API resource.

    :param authorizer: An authorizer instance used for all calls to
                       Globus Search
    :type authorizer: :class:`GlobusAuthorizer \
                      <globus_sdk.authorizers.base.GlobusAuthorizer>`

    **Methods**

    .. automethodlist:: globus_sdk.SearchClient
    """
    error_class = SearchAPIError
    service_name = "search"
    scopes = SearchScopes

    #
    # Index Management
    #

    @utils.doc_api_method("Get Index Metadata", "search/reference/index_show/")
    def get_index(
        self, index_id: UUIDLike, *, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /v1/index/<index_id>``

        **Examples**

        >>> sc = globus_sdk.SearchClient(...)
        >>> index = sc.get_index(index_id)
        >>> assert index['index_id'] == index_id
        >>> print(index["display_name"],
        >>>       "(" + index_id + "):",
        >>>       index["description"])
        """
        index_id = utils.safe_stringify(index_id)
        log.info(f"SearchClient.get_index({index_id})")
        return self.get(f"/v1/index/{index_id}", query_params=query_params)

    #
    # Search queries
    #

    @utils.doc_api_method("GET Search Query", "search/reference/get_query/")
    @paging.has_paginator(
        paging.HasNextPaginator,
        items_key="gmeta",
        get_page_size=lambda x: x["count"],
        max_total_results=10000,
        page_size=100,
    )
    def search(
        self,
        index_id: UUIDLike,
        q: str,
        *,
        offset: int = 0,
        limit: int = 10,
        advanced: bool = False,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /v1/index/<index_id>/search``

        **Examples**

        >>> sc = globus_sdk.SearchClient(...)
        >>> result = sc.search(index_id, 'query string')
        >>> advanced_result = sc.search(index_id, 'author: "Ada Lovelace"',
        >>>                             advanced=True)
        """
        index_id = utils.safe_stringify(index_id)
        if query_params is None:
            query_params = {}
        query_params.update(
            {
                "q": q,
                "offset": offset,
                "limit": limit,
                "advanced": advanced,
            }
        )

        log.info(f"SearchClient.search({index_id}, ...)")
        return self.get(f"/v1/index/{index_id}/search", query_params=query_params)

    @utils.doc_api_method("POST Search Query", "search/reference/post_query")
    def post_search(
        self, index_id: UUIDLike, data: Union[Dict[str, Any], SearchQuery]
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /v1/index/<index_id>/search``

        **Examples**

        >>> sc = globus_sdk.SearchClient(...)
        >>> query_data = {
        >>>   "@datatype": "GSearchRequest",
        >>>   "q": "user query",
        >>>   "filters": [
        >>>     {
        >>>       "type": "range",
        >>>       "field_name": "path.to.date",
        >>>       "values": [
        >>>         {"from": "*",
        >>>          "to": "2014-11-07"}
        >>>       ]
        >>>     }
        >>>   ],
        >>>   "facets": [
        >>>     {"name": "Publication Date",
        >>>      "field_name": "path.to.date",
        >>>      "type": "date_histogram",
        >>>      "date_interval": "year"}
        >>>   ],
        >>>   "sort": [
        >>>     {"field_name": "path.to.date",
        >>>      "order": "asc"}
        >>>   ]
        >>> }
        >>> search_result = sc.post_search(index_id, query_data)
        """
        index_id = utils.safe_stringify(index_id)
        log.info(f"SearchClient.post_search({index_id}, ...)")
        return self.post(f"v1/index/{index_id}/search", data=data)

    #
    # Bulk data indexing
    #

    @utils.doc_api_method("Ingest", "search/reference/ingest")
    def ingest(
        self, index_id: UUIDLike, data: Dict[str, Any]
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /v1/index/<index_id>/ingest``

        **Examples**

        >>> sc = globus_sdk.SearchClient(...)
        >>> ingest_data = {
        >>>   "ingest_type": "GMetaEntry",
        >>>   "ingest_data": {
        >>>     "subject": "https://example.com/foo/bar",
        >>>     "visible_to": ["public"],
        >>>     "content": {
        >>>       "foo/bar": "some val"
        >>>     }
        >>>   }
        >>> }
        >>> sc.ingest(index_id, ingest_data)

        or with multiple entries at once via a GMetaList:

        >>> sc = globus_sdk.SearchClient(...)
        >>> ingest_data = {
        >>>   "ingest_type": "GMetaList",
        >>>   "ingest_data": {
        >>>     "gmeta": [
        >>>       {
        >>>         "subject": "https://example.com/foo/bar",
        >>>         "visible_to": ["public"],
        >>>         "content": {
        >>>           "foo/bar": "some val"
        >>>         }
        >>>       },
        >>>       {
        >>>         "subject": "https://example.com/foo/bar",
        >>>         "id": "otherentry",
        >>>         "visible_to": ["public"],
        >>>         "content": {
        >>>           "foo/bar": "some otherval"
        >>>         }
        >>>       }
        >>>     ]
        >>>   }
        >>> }
        >>> sc.ingest(index_id, ingest_data)
        """
        index_id = utils.safe_stringify(index_id)
        log.info(f"SearchClient.ingest({index_id}, ...)")
        return self.post(f"/v1/index/{index_id}/ingest", data=data)

    #
    # Bulk delete
    #

    @utils.doc_api_method("Delete By Query", "search/reference/delete_by_query")
    def delete_by_query(
        self, index_id: UUIDLike, data: Dict[str, Any]
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /v1/index/<index_id>/delete_by_query``

        **Examples**

        >>> sc = globus_sdk.SearchClient(...)
        >>> query_data = {
        >>>   "q": "user query",
        >>>   "filters": [
        >>>     {
        >>>       "type": "range",
        >>>       "field_name": "path.to.date",
        >>>       "values": [
        >>>         {"from": "*",
        >>>          "to": "2014-11-07"}
        >>>       ]
        >>>     }
        >>>   ]
        >>> }
        >>> sc.delete_by_query(index_id, query_data)
        """
        index_id = utils.safe_stringify(index_id)
        log.info(f"SearchClient.delete_by_query({index_id}, ...)")
        return self.post(f"/v1/index/{index_id}/delete_by_query", data=data)

    #
    # Subject Operations
    #

    @utils.doc_api_method("Get Subject", "search/reference/get_subject")
    def get_subject(
        self,
        index_id: UUIDLike,
        subject: str,
        *,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /v1/index/<index_id>/subject``

        **Examples**

        Fetch the data for subject ``http://example.com/abc`` from index
        ``index_id``:

        >>> sc = globus_sdk.SearchClient(...)
        >>> subject_data = sc.get_subject(index_id, 'http://example.com/abc')
        """
        index_id = utils.safe_stringify(index_id)
        if query_params is None:
            query_params = {}
        query_params["subject"] = subject
        log.info(f"SearchClient.get_subject({index_id}, {subject}, ...)")
        return self.get(f"/v1/index/{index_id}/subject", query_params=query_params)

    @utils.doc_api_method("Delete Subject", "search/reference/delete_subject")
    def delete_subject(
        self,
        index_id: UUIDLike,
        subject: str,
        *,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /v1/index/<index_id>/subject``

        **Examples**

        Delete all data for subject ``http://example.com/abc`` from index
        ``index_id``, even data which is not visible to the current user:

        >>> sc = globus_sdk.SearchClient(...)
        >>> subject_data = sc.get_subject(index_id, 'http://example.com/abc')
        """
        index_id = utils.safe_stringify(index_id)
        if query_params is None:
            query_params = {}
        query_params["subject"] = subject

        log.info(f"SearchClient.delete_subject({index_id}, {subject}, ...)")
        return self.delete(f"/v1/index/{index_id}/subject", query_params=query_params)

    #
    # Entry Operations
    #

    @utils.doc_api_method("Get Entry", "search/reference/get_entry")
    def get_entry(
        self,
        index_id: UUIDLike,
        subject: str,
        *,
        entry_id: Optional[str] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /v1/index/<index_id>/entry``

        **Examples**

        Lookup the entry with a subject of ``https://example.com/foo/bar`` and
        a null entry_id:

        >>> sc = globus_sdk.SearchClient(...)
        >>> entry_data = sc.get_entry(index_id, 'http://example.com/foo/bar')

        Lookup the entry with a subject of ``https://example.com/foo/bar`` and
        an entry_id of ``foo/bar``:

        >>> sc = globus_sdk.SearchClient(...)
        >>> entry_data = sc.get_entry(index_id, 'http://example.com/foo/bar',
        >>>                           entry_id='foo/bar')
        """
        index_id = utils.safe_stringify(index_id)
        if query_params is None:
            query_params = {}
        query_params["subject"] = subject
        if entry_id is not None:
            query_params["entry_id"] = entry_id

        log.info(
            "SearchClient.get_entry({}, {}, {}, ...)".format(
                index_id, subject, entry_id
            )
        )
        return self.get(f"/v1/index/{index_id}/entry", query_params=query_params)

    @utils.doc_api_method("Create Entry", "search/reference/create_or_update_entry")
    def create_entry(
        self, index_id: UUIDLike, data: Dict[str, Any]
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /v1/index/<index_id>/entry``

        **Examples**

        Create an entry with a subject of ``https://example.com/foo/bar`` and
        a null entry_id:

        >>> sc = globus_sdk.SearchClient(...)
        >>> sc.create_entry(index_id, {
        >>>     "subject": "https://example.com/foo/bar",
        >>>     "visible_to": ["public"],
        >>>     "content": {
        >>>         "foo/bar": "some val"
        >>>     }
        >>> })

        Create an entry with a subject of ``https://example.com/foo/bar`` and
        an entry_id of ``foo/bar``:

        >>> sc = globus_sdk.SearchClient(...)
        >>> sc.create_entry(index_id, {
        >>>     "subject": "https://example.com/foo/bar",
        >>>     "visible_to": ["public"],
        >>>     "id": "foo/bar",
        >>>     "content": {
        >>>         "foo/bar": "some val"
        >>>     }
        >>> })
        """
        index_id = utils.safe_stringify(index_id)
        log.info(f"SearchClient.create_entry({index_id}, ...)")
        return self.post(f"/v1/index/{index_id}/entry", data=data)

    @utils.doc_api_method("Update Entry", "search/reference/create_or_update_entry")
    def update_entry(
        self, index_id: UUIDLike, data: Dict[str, Any]
    ) -> response.GlobusHTTPResponse:
        """
        ``PUT /v1/index/<index_id>/entry``

        **Examples**

        Update an entry with a subject of ``https://example.com/foo/bar`` and
        a null entry_id:

        >>> sc = globus_sdk.SearchClient(...)
        >>> sc.update_entry(index_id, {
        >>>     "subject": "https://example.com/foo/bar",
        >>>     "visible_to": ["public"],
        >>>     "content": {
        >>>         "foo/bar": "some val"
        >>>     }
        >>> })
        """
        index_id = utils.safe_stringify(index_id)
        log.info(f"SearchClient.update_entry({index_id}, ...)")
        return self.put(f"/v1/index/{index_id}/entry", data=data)

    @utils.doc_api_method("Delete Entry", "search/reference/delete_entry")
    def delete_entry(
        self,
        index_id: UUIDLike,
        subject: str,
        *,
        entry_id: Optional[str] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE  /v1/index/<index_id>/entry``

        **Examples**

        Delete an entry with a subject of ``https://example.com/foo/bar`` and
        a null entry_id:

        >>> sc = globus_sdk.SearchClient(...)
        >>> sc.delete_entry(index_id, "https://example.com/foo/bar")

        Delete an entry with a subject of ``https://example.com/foo/bar`` and
        an entry_id of "foo/bar":

        >>> sc = globus_sdk.SearchClient(...)
        >>> sc.delete_entry(index_id, "https://example.com/foo/bar",
        >>>                 entry_id="foo/bar")
        """
        index_id = utils.safe_stringify(index_id)
        if query_params is None:
            query_params = {}
        query_params["subject"] = subject
        if entry_id is not None:
            query_params["entry_id"] = entry_id
        log.info(
            "SearchClient.delete_entry({}, {}, {}, ...)".format(
                index_id, subject, entry_id
            )
        )
        return self.delete(f"/v1/index/{index_id}/entry", query_params=query_params)

    #
    # Task Management
    #

    @utils.doc_api_method("Get Task", "search/reference/get_task")
    def get_task(
        self, task_id: UUIDLike, *, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /v1/task/<task_id>``

        **Examples**

        >>> sc = globus_sdk.SearchClient(...)
        >>> task = sc.get_task(task_id)
        >>> assert task['index_id'] == known_index_id
        >>> print(task["task_id"] + " | " + task['state'])
        """
        task_id = utils.safe_stringify(task_id)
        log.info(f"SearchClient.get_task({task_id})")
        return self.get(f"/v1/task/{task_id}", query_params=query_params)

    @utils.doc_api_method("Task List", "search/reference/task_list")
    def get_task_list(
        self, index_id: UUIDLike, *, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /v1/task_list/<index_id>``

        **Examples**

        >>> sc = globus_sdk.SearchClient(...)
        >>> task_list = sc.get_task_list(index_id)
        >>> for task in task_list['tasks']:
        >>>     print(task["task_id"] + " | " + task['state'])
        """
        index_id = utils.safe_stringify(index_id)
        log.info(f"SearchClient.get_task_list({index_id})")
        return self.get(f"/v1/task_list/{index_id}", query_params=query_params)

import abc
from typing import Any, Dict, Iterable, Optional, Tuple, Union

from globus_sdk import utils
from globus_sdk._types import UUIDLike

from ._common import ensure_datatype


class StorageGatewayDocument(utils.PayloadWrapper):
    """
    Convenience class for constructing a Storage Gateway document
    to use as the `data` parameter to ``create_storage_gateway`` or
    ``update_storage_gateway``

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param display_name: Name of the Storage Gateway
    :type display_name: str, optional
    :param connector_id: UUID of the connector type that this Storage Gateway interacts
        with.
    :type connector_id: str, optional
    :param identity_mappings: A list of IdentityMapping objects which are applied to
        user identities to attempt to determine what accounts are available for access.
    :type identity_mappings: iterable of dict, optional
    :param policies: Connector specific storage policies. It is recommended that
        you use one of the policy helper classes (e.g. `POSIXStoragePolicies`
        if you are using the POSIX connector) to create these.
    :type policies: dict or StorageGatewayPolicy, optional
    :param allowed_domains: List of allowed domains. Users creating credentials or
        collections on this Storage Gateway must have an identity in one of these
        domains.
    :type allowed_domains: iterable of string
    :param restrict_paths: Path restrictions within this Storage Gateway. Private.
    :type restrict_paths: dict, optional
    :param high_assurance: Flag indicating if the Storage Gateway requires high
        assurance features.
    :type high_assurance: bool, optional
    :param authentication_timeout_mins: Timeout (in minutes) during which a user is
        required to have authenticated in a session to access this storage gateway.
    :type authentication_timeout_mins: int, optional
    :param users_allow:  List of connector-specific usernames allowed to access this
        Storage Gateway. Private.
    :type users_allow: iterable of str, optional
    :param users_deny: List of connector-specific usernames denied access to this
        Storage Gateway. Private.
    :type users_deny: iterable of str, optional
    :param process_user: Local POSIX user the GridFTP server should run as when
        accessing this Storage Gateway.
    :type process_user: str, optional
    :param load_dsi_module: Name of the DSI module to load by the GridFTP server when
        accessing this Storage Gateway.
    :type load_dsi_module: str, optional
    :param require_mfa: Flag indicating that the Storage Gateway requires multi-factor
        authentication. Only usable on high assurance Storage Gateways.
    :type require_mfa: bool, optional

    :param additional_fields: Additional data for inclusion in the Storage Gateway
        document
    :type additional_fields: dict, optional
    """

    DATATYPE_BASE: str = "storage_gateway"
    DATATYPE_VERSION_IMPLICATIONS: Dict[str, Tuple[int, int, int]] = {
        "require_mfa": (1, 1, 0),
    }

    def __init__(
        self,
        DATA_TYPE: Optional[str] = None,
        display_name: Optional[str] = None,
        connector_id: Optional[UUIDLike] = None,
        root: Optional[str] = None,
        identity_mappings: Optional[Iterable[Dict[str, Any]]] = None,
        policies: Union["StorageGatewayPolicies", Dict[str, Any], None] = None,
        allowed_domains: Optional[Iterable[str]] = None,
        high_assurance: Optional[bool] = None,
        require_mfa: Optional[bool] = None,
        authentication_timeout_mins: Optional[int] = None,
        users_allow: Optional[Iterable[str]] = None,
        users_deny: Optional[Iterable[str]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(
            DATA_TYPE=DATA_TYPE,
            display_name=display_name,
            connector_id=connector_id,
            root=root,
        )
        self._set_optstrlists(
            allow_domains=allowed_domains,
            users_allow=users_allow,
            users_deny=users_deny,
        )
        self._set_optbools(high_assurance=high_assurance, require_mfa=require_mfa)
        self._set_optints(authentication_timeout_mins=authentication_timeout_mins)
        self._set_value("identity_mappings", identity_mappings, callback=list)
        self._set_value("policies", policies, callback=dict)
        if additional_fields is not None:
            self.update(additional_fields)
        ensure_datatype(self)


class StorageGatewayPolicies(utils.PayloadWrapper, abc.ABC):
    """
    This is the abstract base type for Storage Policies documents to use as the
    ``policies`` parameter when creating a StorageGatewayDocument.

    Several fields on policy documents are marked as ``Private``. This means that they
    are not visible except to admins and owners of the storage gateway.
    """


class POSIXStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a POSIX Storage Policy document
    to use as the ``policies`` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param groups_allow: List of POSIX group IDs allowed to access this Storage
        Gateway. Private.
    :type groups_allow: iterable of str, optional
    :param groups_deny: List of POSIX group IDs denied access this Storage
        Gateway. Private.
    :type groups_deny: iterable of str, optional
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "posix_storage_policies#1.0.0",
        groups_allow: Optional[Iterable[str]] = None,
        groups_deny: Optional[Iterable[str]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(DATA_TYPE=DATA_TYPE)
        self._set_optstrlists(groups_allow=groups_allow, groups_deny=groups_deny)
        if additional_fields is not None:
            self.update(additional_fields)


class POSIXStagingStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a POSIX Staging Storage Policy document
    to use as the ``policies`` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param groups_allow: List of POSIX group IDs allowed to access this Storage
        Gateway. Private.
    :type groups_allow: iterable of str, optional
    :param groups_deny: List of POSIX group IDs denied access this Storage
        Gateway. Private.
    :type groups_deny: iterable of str, optional
    :param stage_app: Path to the stage app. Private.
    :type stage_app: str, optional
    :param environment: A mapping of variable names to values to set in the environment
        when executing the ``stage_app``. Private.
    :type environment: iterable of dict, optional
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "posix_staging_storage_policies#1.0.0",
        groups_allow: Optional[Iterable[str]] = None,
        groups_deny: Optional[Iterable[str]] = None,
        stage_app: Optional[str] = None,
        environment: Optional[Iterable[Dict[str, str]]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(DATA_TYPE=DATA_TYPE, stage_app=stage_app)
        self._set_optstrlists(groups_allow=groups_allow, groups_deny=groups_deny)
        self._set_value(
            "environment",
            environment,
            callback=lambda env_iter: [{**e} for e in env_iter],
        )
        if additional_fields is not None:
            self.update(additional_fields)


class BlackPearlStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a BlackPearl Storage Policy document
    to use as the ``policies`` parameter when creating a StorageGatewayDocument.

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param s3_endpoint: The URL of the S3 endpoint of the BlackPearl appliance to use to
        access collections on this Storage Gateway.
    :type s3_endpoint: str
    :param bp_access_id_file: Path to the file which provides mappings from usernames
        within the configured identity domain to the ID and secret associated with the
        user's BlackPearl account
    :type bp_access_id_file: str
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "blackpearl_storage_policies#1.0.0",
        s3_endpoint: Optional[str] = None,
        bp_access_id_file: Optional[str] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(
            DATA_TYPE=DATA_TYPE,
            s3_endpoint=s3_endpoint,
            bp_access_id_file=bp_access_id_file,
        )
        if additional_fields is not None:
            self.update(additional_fields)


class BoxStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a Box Storage Policy document
    to use as the ``policies`` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param enterpriseID: Identifies which Box Enterprise this Storage Gateway is
        authorized to access. Private.
    :type enterpriseID: str
    :param boxAppSettings: Values that the Storage Gateway uses to identify and
        authenticate with the Box API. Private.
    :type boxAppSettings: dict
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "box_storage_policies#1.0.0",
        enterpriseID: Optional[str] = None,
        boxAppSettings: Optional[Dict[str, Any]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(DATA_TYPE=DATA_TYPE, enterpriseID=enterpriseID)
        self._set_value("boxAppSettings", boxAppSettings)
        if additional_fields is not None:
            self.update(additional_fields)


class CephStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a Ceph Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param s3_endpoint: URL of the S3 API endpoint
    :type s3_endpoint: str
    :param s3_buckets: List of buckets not owned by the collection owner that will be
        shown in the root of collections created at the base of this Storage Gateway.
    :type s3_buckets: iterable of str
    :param ceph_admin_key_id: Administrator key id used to authenticate with the ceph
        admin service to obtain user credentials. Private.
    :type ceph_admin_key_id: str
    :param ceph_admin_secret_key: Administrator secret key used to authenticate with the
        ceph admin service to obtain user credentials. Private.
    :type ceph_admin_secret_key: str
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "ceph_storage_policies#1.0.0",
        s3_endpoint: Optional[str] = None,
        s3_buckets: Optional[Iterable[str]] = None,
        ceph_admin_key_id: Optional[str] = None,
        ceph_admin_secret_key: Optional[str] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(
            DATA_TYPE=DATA_TYPE,
            s3_endpoint=s3_endpoint,
            ceph_admin_key_id=ceph_admin_key_id,
            ceph_admin_secret_key=ceph_admin_secret_key,
        )
        self._set_optstrlists(s3_buckets=s3_buckets)
        if additional_fields is not None:
            self.update(additional_fields)


class GoogleDriveStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a Google Drive Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param client_id: Client ID registered with the Google Application console to access
        Google Drive. Private.
    :type client_id: str
    :param secret: Secret created to access access Google Drive with the client_id in
        this policy. Private.
    :type secret: str
    :param user_api_rate_quota: User API Rate quota associated with this client ID.
    :type user_api_rate_quota: int
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "google_drive_storage_policies#1.0.0",
        client_id: Optional[str] = None,
        secret: Optional[str] = None,
        user_api_rate_quota: Optional[int] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(DATA_TYPE=DATA_TYPE, client_id=client_id, secret=secret)
        self._set_optints(user_api_rate_quota=user_api_rate_quota)
        if additional_fields is not None:
            self.update(additional_fields)


class GoogleCloudStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a Google Cloud Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param client_id: Client ID registered with the Google Application console to
        access Google Drive. Private.
    :type client_id: str
    :param secret: Secret created to access access Google Drive with the client_id in
        this policy. Private.
    :type secret: str
    :param service_account_key: Credentials for use with service account auth, read
        from a Google-provided json file. Private.
    :type service_account_key: dict
    :param buckets: The list of Google Cloud Storage buckets which the Storage
        Gateway is allowed to access, as well as the list of buckets that will be
        shown in root level directory listings. If this list is unset, bucket
        access is unrestricted and all non public credential accessible buckets
        will be shown in root level directory listings. The value is a list of
        bucket names.
    :type buckets: iterable of str
    :param projects: The list of Google Cloud Storage projects which the
        Storage Gateway is allowed to access. If this list is unset, project access
        is unrestricted.  The value is a list of project id strings.
    :type projects: iterable of str
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "google_cloud_storage_policies#1.0.0",
        client_id: Optional[str] = None,
        secret: Optional[str] = None,
        service_account_key: Optional[Dict[str, Any]] = None,
        buckets: Optional[Iterable[str]] = None,
        projects: Optional[Iterable[str]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(DATA_TYPE=DATA_TYPE, client_id=client_id, secret=secret)
        self._set_optstrlists(buckets=buckets, projects=projects)
        self._set_value("service_account_key", service_account_key)
        if additional_fields is not None:
            self.update(additional_fields)


class OneDriveStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a OneDrive Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param client_id: Client ID registered with the MS Application console to
        access OneDrive. Private.
    :type client_id: str
    :param secret: Secret created to access access MS with the client_id in
        this policy. Private.
    :type secret: str
    :param tenant: MS Tenant ID from which to allow user logins. Private.
    :type tenant: str or None
    :param user_api_rate_limit: User API Rate limit associated with this client ID.
    :type user_api_rate_limit: int
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "onedrive_storage_policies#1.0.0",
        client_id: Optional[str] = None,
        secret: Optional[str] = None,
        tenant: Optional[str] = None,
        user_api_rate_limit: Optional[int] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(
            DATA_TYPE=DATA_TYPE, client_id=client_id, secret=secret, tenant=tenant
        )
        self._set_optints(user_api_rate_limit=user_api_rate_limit)
        if additional_fields is not None:
            self.update(additional_fields)


class AzureBlobStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a Azure Blob Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param client_id: Client ID registered with the MS Application console to
        access Azure Blob Private.
    :type client_id: str
    :param secret: Secret created to access access MS with the client_id in
        this policy. Private.
    :type secret: str
    :param tenant: MS Tenant ID from which to allow user logins. Private.
    :type tenant: str
    :param account: Azure Storage account. Private.
    :type account: str
    :param auth_type: Auth type: user, service_principal or user_service_principal
    :type auth_type: str
    :param adls: ADLS support enabled or not. Private.
    :type adls: bool
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "azure_blob_storage_policies#1.0.0",
        client_id: Optional[str] = None,
        secret: Optional[str] = None,
        tenant: Optional[str] = None,
        account: Optional[str] = None,
        auth_type: Optional[str] = None,
        adls: Optional[bool] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(
            DATA_TYPE=DATA_TYPE,
            client_id=client_id,
            secret=secret,
            tenant=tenant,
            account=account,
            auth_type=auth_type,
        )
        self._set_optbools(adls=adls)
        if additional_fields is not None:
            self.update(additional_fields)


class S3StoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a Google Cloud Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param s3_endpoint: URL of the S3 API endpoint
    :type s3_endpoint: str
    :param s3_buckets: List of buckets not owned by the collection owner that
        will be shown in the root of collections created at the base of this
        Storage Gateway.
    :type s3_buckets: iterable of str
    :param s3_user_credential_required: Flag indicating if a Globus User must
        register a user credential in order to create a Guest Collection on this
        Storage Gateway.
    :type s3_user_credential_required: str
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "s3_storage_policies#1.0.0",
        s3_endpoint: Optional[str] = None,
        s3_buckets: Optional[Iterable[str]] = None,
        s3_user_credential_required: Optional[bool] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(DATA_TYPE=DATA_TYPE, s3_endpoint=s3_endpoint)
        self._set_optbools(s3_user_credential_required=s3_user_credential_required)
        self._set_optstrlists(s3_buckets=s3_buckets)
        if additional_fields is not None:
            self.update(additional_fields)


class ActiveScaleStoragePolicies(S3StoragePolicies):
    """
    The ActiveScale Storage Policy is an alias for the S3 Storage Policy.
    It even uses S3 policy DATA_TYPE.
    """


class IrodsStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing an iRODS Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param irods_environment_file: Path to iRODS environent file on the endpoint
    :type irods_environment_file: str
    :param irods_authentication_file: Path to iRODS authentication file on the endpoint
    :type irods_authentication_file: str
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "irods_storage_policies#1.0.0",
        irods_environment_file: Optional[str] = None,
        irods_authentication_file: Optional[str] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(
            DATA_TYPE=DATA_TYPE,
            irods_environment_file=irods_environment_file,
            irods_authentication_file=irods_authentication_file,
        )
        if additional_fields is not None:
            self.update(additional_fields)


class HPSSStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a HPSS Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param authentication_mech: Authentication mechanism to use with HPSS.
    :type authentication_mech: str
    :param authenticator: Authentication credentials to use with HPSS.
    :type authenticator: str
    :param uda_checksum_support: Flag indicating whether checksums should be
        stored in metadata.
    :type uda_checksum_support: bool
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "hpss_storage_policies#1.0.0",
        authentication_mech: Optional[str] = None,
        authenticator: Optional[str] = None,
        uda_checksum_support: Optional[bool] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(
            DATA_TYPE=DATA_TYPE,
            authentication_mech=authentication_mech,
            authenticator=authenticator,
        )
        self._set_optbools(uda_checksum_support=uda_checksum_support)
        if additional_fields is not None:
            self.update(additional_fields)
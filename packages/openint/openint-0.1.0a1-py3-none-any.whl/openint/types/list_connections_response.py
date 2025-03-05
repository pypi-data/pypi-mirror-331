# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "ListConnectionsResponse",
    "ConnectorsAircallConnectionSettings",
    "ConnectorsAircallConnectionSettingsSettings",
    "ConnectorsAirtableConnectionSettings",
    "ConnectorsAirtableConnectionSettingsSettings",
    "ConnectorsApolloConnectionSettings",
    "ConnectorsApolloConnectionSettingsSettings",
    "ConnectorsApolloConnectionSettingsSettingsOAuth",
    "ConnectorsApolloConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsApolloConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsApolloConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsApolloConnectionSettingsSettingsError",
    "ConnectorsBeancountConnectionSettings",
    "ConnectorsBrexConnectionSettings",
    "ConnectorsBrexConnectionSettingsSettings",
    "ConnectorsCodaConnectionSettings",
    "ConnectorsCodaConnectionSettingsSettings",
    "ConnectorsConfluenceConnectionSettings",
    "ConnectorsConfluenceConnectionSettingsSettings",
    "ConnectorsConfluenceConnectionSettingsSettingsOAuth",
    "ConnectorsConfluenceConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsConfluenceConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsConfluenceConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsConfluenceConnectionSettingsSettingsError",
    "ConnectorsDebugConnectionSettings",
    "ConnectorsDiscordConnectionSettings",
    "ConnectorsDiscordConnectionSettingsSettings",
    "ConnectorsDiscordConnectionSettingsSettingsOAuth",
    "ConnectorsDiscordConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsDiscordConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsDiscordConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsDiscordConnectionSettingsSettingsError",
    "ConnectorsFinchConnectionSettings",
    "ConnectorsFinchConnectionSettingsSettings",
    "ConnectorsFirebaseConnectionSettings",
    "ConnectorsFirebaseConnectionSettingsSettings",
    "ConnectorsFirebaseConnectionSettingsSettingsUnionMember0",
    "ConnectorsFirebaseConnectionSettingsSettingsUnionMember0ServiceAccount",
    "ConnectorsFirebaseConnectionSettingsSettingsUnionMember1",
    "ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthData",
    "ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember0",
    "ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson",
    "ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember1",
    "ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember2",
    "ConnectorsFirebaseConnectionSettingsSettingsUnionMember1FirebaseConfig",
    "ConnectorsForeceiptConnectionSettings",
    "ConnectorsForeceiptConnectionSettingsSettings",
    "ConnectorsFsConnectionSettings",
    "ConnectorsFsConnectionSettingsSettings",
    "ConnectorsGitHubConnectionSettings",
    "ConnectorsGitHubConnectionSettingsSettings",
    "ConnectorsGitHubConnectionSettingsSettingsOAuth",
    "ConnectorsGitHubConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsGitHubConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsGitHubConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsGitHubConnectionSettingsSettingsError",
    "ConnectorsGongConnectionSettings",
    "ConnectorsGongConnectionSettingsSettings",
    "ConnectorsGongConnectionSettingsSettingsOAuth",
    "ConnectorsGongConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsGongConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsGongConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsGongConnectionSettingsSettingsError",
    "ConnectorsGoogleConnectionSettings",
    "ConnectorsGoogleConnectionSettingsSettings",
    "ConnectorsGoogleConnectionSettingsSettingsOAuth",
    "ConnectorsGoogleConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsGoogleConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsGoogleConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsGoogleConnectionSettingsSettingsError",
    "ConnectorsGreenhouseConnectionSettings",
    "ConnectorsGreenhouseConnectionSettingsSettings",
    "ConnectorsHeronConnectionSettings",
    "ConnectorsHubspotConnectionSettings",
    "ConnectorsHubspotConnectionSettingsSettings",
    "ConnectorsHubspotConnectionSettingsSettingsOAuth",
    "ConnectorsHubspotConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsHubspotConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsHubspotConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsHubspotConnectionSettingsSettingsError",
    "ConnectorsIntercomConnectionSettings",
    "ConnectorsIntercomConnectionSettingsSettings",
    "ConnectorsIntercomConnectionSettingsSettingsOAuth",
    "ConnectorsIntercomConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsIntercomConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsIntercomConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsIntercomConnectionSettingsSettingsError",
    "ConnectorsJiraConnectionSettings",
    "ConnectorsJiraConnectionSettingsSettings",
    "ConnectorsJiraConnectionSettingsSettingsOAuth",
    "ConnectorsJiraConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsJiraConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsJiraConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsJiraConnectionSettingsSettingsError",
    "ConnectorsKustomerConnectionSettings",
    "ConnectorsKustomerConnectionSettingsSettings",
    "ConnectorsKustomerConnectionSettingsSettingsOAuth",
    "ConnectorsKustomerConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsKustomerConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsKustomerConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsKustomerConnectionSettingsSettingsError",
    "ConnectorsLeverConnectionSettings",
    "ConnectorsLeverConnectionSettingsSettings",
    "ConnectorsLeverConnectionSettingsSettingsOAuth",
    "ConnectorsLeverConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsLeverConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsLeverConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsLeverConnectionSettingsSettingsError",
    "ConnectorsLinearConnectionSettings",
    "ConnectorsLinearConnectionSettingsSettings",
    "ConnectorsLinearConnectionSettingsSettingsOAuth",
    "ConnectorsLinearConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsLinearConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsLinearConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsLinearConnectionSettingsSettingsError",
    "ConnectorsLunchmoneyConnectionSettings",
    "ConnectorsMercuryConnectionSettings",
    "ConnectorsMergeConnectionSettings",
    "ConnectorsMergeConnectionSettingsSettings",
    "ConnectorsMicrosoftConnectionSettings",
    "ConnectorsMicrosoftConnectionSettingsSettings",
    "ConnectorsMicrosoftConnectionSettingsSettingsOAuth",
    "ConnectorsMicrosoftConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsMicrosoftConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsMicrosoftConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsMicrosoftConnectionSettingsSettingsError",
    "ConnectorsMongoDBConnectionSettings",
    "ConnectorsMongoDBConnectionSettingsSettings",
    "ConnectorsMootaConnectionSettings",
    "ConnectorsOnebrickConnectionSettings",
    "ConnectorsOnebrickConnectionSettingsSettings",
    "ConnectorsOutreachConnectionSettings",
    "ConnectorsOutreachConnectionSettingsSettings",
    "ConnectorsOutreachConnectionSettingsSettingsOAuth",
    "ConnectorsOutreachConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsOutreachConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsOutreachConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsOutreachConnectionSettingsSettingsError",
    "ConnectorsPipedriveConnectionSettings",
    "ConnectorsPipedriveConnectionSettingsSettings",
    "ConnectorsPipedriveConnectionSettingsSettingsOAuth",
    "ConnectorsPipedriveConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsPipedriveConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsPipedriveConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsPipedriveConnectionSettingsSettingsError",
    "ConnectorsPlaidConnectionSettings",
    "ConnectorsPlaidConnectionSettingsSettings",
    "ConnectorsPostgresConnectionSettings",
    "ConnectorsPostgresConnectionSettingsSettings",
    "ConnectorsPostgresConnectionSettingsSettingsSourceQueries",
    "ConnectorsQboConnectionSettings",
    "ConnectorsQboConnectionSettingsSettings",
    "ConnectorsQboConnectionSettingsSettingsOAuth",
    "ConnectorsQboConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsQboConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsQboConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsQboConnectionSettingsSettingsError",
    "ConnectorsRampConnectionSettings",
    "ConnectorsRampConnectionSettingsSettings",
    "ConnectorsRevertConnectionSettings",
    "ConnectorsRevertConnectionSettingsSettings",
    "ConnectorsSalesforceConnectionSettings",
    "ConnectorsSalesforceConnectionSettingsSettings",
    "ConnectorsSalesforceConnectionSettingsSettingsOAuth",
    "ConnectorsSalesforceConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsSalesforceConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsSalesforceConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsSalesforceConnectionSettingsSettingsError",
    "ConnectorsSalesloftConnectionSettings",
    "ConnectorsSalesloftConnectionSettingsSettings",
    "ConnectorsSalesloftConnectionSettingsSettingsOAuth",
    "ConnectorsSalesloftConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsSalesloftConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsSalesloftConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsSalesloftConnectionSettingsSettingsError",
    "ConnectorsSaltedgeConnectionSettings",
    "ConnectorsSlackConnectionSettings",
    "ConnectorsSlackConnectionSettingsSettings",
    "ConnectorsSlackConnectionSettingsSettingsOAuth",
    "ConnectorsSlackConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsSlackConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsSlackConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsSlackConnectionSettingsSettingsError",
    "ConnectorsSplitwiseConnectionSettings",
    "ConnectorsSplitwiseConnectionSettingsSettings",
    "ConnectorsSplitwiseConnectionSettingsSettingsCurrentUser",
    "ConnectorsSplitwiseConnectionSettingsSettingsCurrentUserNotifications",
    "ConnectorsSplitwiseConnectionSettingsSettingsCurrentUserPicture",
    "ConnectorsSpreadsheetConnectionSettings",
    "ConnectorsSpreadsheetConnectionSettingsSettings",
    "ConnectorsStripeConnectionSettings",
    "ConnectorsStripeConnectionSettingsSettings",
    "ConnectorsTellerConnectionSettings",
    "ConnectorsTellerConnectionSettingsSettings",
    "ConnectorsTogglConnectionSettings",
    "ConnectorsTogglConnectionSettingsSettings",
    "ConnectorsTwentyConnectionSettings",
    "ConnectorsTwentyConnectionSettingsSettings",
    "ConnectorsVenmoConnectionSettings",
    "ConnectorsVenmoConnectionSettingsSettings",
    "ConnectorsWebhookConnectionSettings",
    "ConnectorsWebhookConnectionSettingsSettings",
    "ConnectorsWiseConnectionSettings",
    "ConnectorsWiseConnectionSettingsSettings",
    "ConnectorsXeroConnectionSettings",
    "ConnectorsXeroConnectionSettingsSettings",
    "ConnectorsXeroConnectionSettingsSettingsOAuth",
    "ConnectorsXeroConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsXeroConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsXeroConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsXeroConnectionSettingsSettingsError",
    "ConnectorsYodleeConnectionSettings",
    "ConnectorsYodleeConnectionSettingsSettings",
    "ConnectorsYodleeConnectionSettingsSettingsAccessToken",
    "ConnectorsYodleeConnectionSettingsSettingsProviderAccount",
    "ConnectorsZohodeskConnectionSettings",
    "ConnectorsZohodeskConnectionSettingsSettings",
    "ConnectorsZohodeskConnectionSettingsSettingsOAuth",
    "ConnectorsZohodeskConnectionSettingsSettingsOAuthCredentials",
    "ConnectorsZohodeskConnectionSettingsSettingsOAuthCredentialsRaw",
    "ConnectorsZohodeskConnectionSettingsSettingsOAuthConnectionConfig",
    "ConnectorsZohodeskConnectionSettingsSettingsError",
    "ConnectorsGoogledriveConnectionSettings",
]


class ConnectorsAircallConnectionSettingsSettings(BaseModel):
    api_id: str = FieldInfo(alias="apiId")

    api_token: str = FieldInfo(alias="apiToken")


class ConnectorsAircallConnectionSettings(BaseModel):
    connector_name: Literal["aircall"]

    settings: ConnectorsAircallConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsAirtableConnectionSettingsSettings(BaseModel):
    airtable_base: str = FieldInfo(alias="airtableBase")

    api_key: str = FieldInfo(alias="apiKey")


class ConnectorsAirtableConnectionSettings(BaseModel):
    connector_name: Literal["airtable"]

    settings: ConnectorsAirtableConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsApolloConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsApolloConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsApolloConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsApolloConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsApolloConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsApolloConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsApolloConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsApolloConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsApolloConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsApolloConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsApolloConnectionSettingsSettingsError] = None


class ConnectorsApolloConnectionSettings(BaseModel):
    connector_name: Literal["apollo"]

    settings: ConnectorsApolloConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsBeancountConnectionSettings(BaseModel):
    connector_name: Literal["beancount"]

    settings: None

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsBrexConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")


class ConnectorsBrexConnectionSettings(BaseModel):
    connector_name: Literal["brex"]

    settings: ConnectorsBrexConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsCodaConnectionSettingsSettings(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ConnectorsCodaConnectionSettings(BaseModel):
    connector_name: Literal["coda"]

    settings: ConnectorsCodaConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsConfluenceConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsConfluenceConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsConfluenceConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsConfluenceConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsConfluenceConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsConfluenceConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsConfluenceConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsConfluenceConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsConfluenceConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsConfluenceConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsConfluenceConnectionSettingsSettingsError] = None


class ConnectorsConfluenceConnectionSettings(BaseModel):
    connector_name: Literal["confluence"]

    settings: ConnectorsConfluenceConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsDebugConnectionSettings(BaseModel):
    connector_name: Literal["debug"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    settings: Optional[object] = None

    updated_at: Optional[datetime] = None


class ConnectorsDiscordConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsDiscordConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsDiscordConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsDiscordConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsDiscordConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsDiscordConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsDiscordConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsDiscordConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsDiscordConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsDiscordConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsDiscordConnectionSettingsSettingsError] = None


class ConnectorsDiscordConnectionSettings(BaseModel):
    connector_name: Literal["discord"]

    settings: ConnectorsDiscordConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsFinchConnectionSettingsSettings(BaseModel):
    access_token: str


class ConnectorsFinchConnectionSettings(BaseModel):
    connector_name: Literal["finch"]

    settings: ConnectorsFinchConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsFirebaseConnectionSettingsSettingsUnionMember0ServiceAccount(BaseModel):
    project_id: str

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsFirebaseConnectionSettingsSettingsUnionMember0(BaseModel):
    role: Literal["admin"]

    service_account: ConnectorsFirebaseConnectionSettingsSettingsUnionMember0ServiceAccount = FieldInfo(
        alias="serviceAccount"
    )


class ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson(BaseModel):
    app_name: str = FieldInfo(alias="appName")

    sts_token_manager: Dict[str, object] = FieldInfo(alias="stsTokenManager")

    uid: str

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember0(BaseModel):
    method: Literal["userJson"]

    user_json: ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson = FieldInfo(
        alias="userJson"
    )


class ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember1(BaseModel):
    custom_token: str = FieldInfo(alias="customToken")

    method: Literal["customToken"]


class ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember2(BaseModel):
    email: str

    method: Literal["emailPassword"]

    password: str


ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthData: TypeAlias = Union[
    ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember0,
    ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember1,
    ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember2,
]


class ConnectorsFirebaseConnectionSettingsSettingsUnionMember1FirebaseConfig(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")

    app_id: str = FieldInfo(alias="appId")

    auth_domain: str = FieldInfo(alias="authDomain")

    database_url: str = FieldInfo(alias="databaseURL")

    project_id: str = FieldInfo(alias="projectId")

    measurement_id: Optional[str] = FieldInfo(alias="measurementId", default=None)

    messaging_sender_id: Optional[str] = FieldInfo(alias="messagingSenderId", default=None)

    storage_bucket: Optional[str] = FieldInfo(alias="storageBucket", default=None)


class ConnectorsFirebaseConnectionSettingsSettingsUnionMember1(BaseModel):
    auth_data: ConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthData = FieldInfo(alias="authData")

    firebase_config: ConnectorsFirebaseConnectionSettingsSettingsUnionMember1FirebaseConfig = FieldInfo(
        alias="firebaseConfig"
    )

    role: Literal["user"]


ConnectorsFirebaseConnectionSettingsSettings: TypeAlias = Union[
    ConnectorsFirebaseConnectionSettingsSettingsUnionMember0, ConnectorsFirebaseConnectionSettingsSettingsUnionMember1
]


class ConnectorsFirebaseConnectionSettings(BaseModel):
    connector_name: Literal["firebase"]

    settings: ConnectorsFirebaseConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsForeceiptConnectionSettingsSettings(BaseModel):
    env_name: Literal["staging", "production"] = FieldInfo(alias="envName")

    api_id: Optional[object] = FieldInfo(alias="_id", default=None)

    credentials: Optional[object] = None

    options: Optional[object] = None


class ConnectorsForeceiptConnectionSettings(BaseModel):
    connector_name: Literal["foreceipt"]

    settings: ConnectorsForeceiptConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsFsConnectionSettingsSettings(BaseModel):
    base_path: str = FieldInfo(alias="basePath")


class ConnectorsFsConnectionSettings(BaseModel):
    connector_name: Literal["fs"]

    settings: ConnectorsFsConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsGitHubConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsGitHubConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsGitHubConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsGitHubConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsGitHubConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsGitHubConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsGitHubConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsGitHubConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsGitHubConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsGitHubConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsGitHubConnectionSettingsSettingsError] = None


class ConnectorsGitHubConnectionSettings(BaseModel):
    connector_name: Literal["github"]

    settings: ConnectorsGitHubConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsGongConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsGongConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsGongConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsGongConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsGongConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsGongConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsGongConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsGongConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsGongConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsGongConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsGongConnectionSettingsSettingsError] = None


class ConnectorsGongConnectionSettings(BaseModel):
    connector_name: Literal["gong"]

    settings: ConnectorsGongConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsGoogleConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsGoogleConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsGoogleConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsGoogleConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsGoogleConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsGoogleConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsGoogleConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsGoogleConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsGoogleConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsGoogleConnectionSettingsSettingsOAuth

    client_id: Optional[str] = None

    error: Optional[ConnectorsGoogleConnectionSettingsSettingsError] = None


class ConnectorsGoogleConnectionSettings(BaseModel):
    connector_name: Literal["google"]

    settings: ConnectorsGoogleConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsGreenhouseConnectionSettingsSettings(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ConnectorsGreenhouseConnectionSettings(BaseModel):
    connector_name: Literal["greenhouse"]

    settings: ConnectorsGreenhouseConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsHeronConnectionSettings(BaseModel):
    connector_name: Literal["heron"]

    settings: None

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsHubspotConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsHubspotConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsHubspotConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsHubspotConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsHubspotConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsHubspotConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsHubspotConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsHubspotConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsHubspotConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsHubspotConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsHubspotConnectionSettingsSettingsError] = None

    extra: Optional[object] = None


class ConnectorsHubspotConnectionSettings(BaseModel):
    connector_name: Literal["hubspot"]

    settings: ConnectorsHubspotConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsIntercomConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsIntercomConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsIntercomConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsIntercomConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsIntercomConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsIntercomConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsIntercomConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsIntercomConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsIntercomConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsIntercomConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsIntercomConnectionSettingsSettingsError] = None


class ConnectorsIntercomConnectionSettings(BaseModel):
    connector_name: Literal["intercom"]

    settings: ConnectorsIntercomConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsJiraConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsJiraConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsJiraConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsJiraConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsJiraConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsJiraConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsJiraConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsJiraConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsJiraConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsJiraConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsJiraConnectionSettingsSettingsError] = None


class ConnectorsJiraConnectionSettings(BaseModel):
    connector_name: Literal["jira"]

    settings: ConnectorsJiraConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsKustomerConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsKustomerConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsKustomerConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsKustomerConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsKustomerConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsKustomerConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsKustomerConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsKustomerConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsKustomerConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsKustomerConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsKustomerConnectionSettingsSettingsError] = None


class ConnectorsKustomerConnectionSettings(BaseModel):
    connector_name: Literal["kustomer"]

    settings: ConnectorsKustomerConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsLeverConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsLeverConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsLeverConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsLeverConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsLeverConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsLeverConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsLeverConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsLeverConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsLeverConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsLeverConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsLeverConnectionSettingsSettingsError] = None


class ConnectorsLeverConnectionSettings(BaseModel):
    connector_name: Literal["lever"]

    settings: ConnectorsLeverConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsLinearConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsLinearConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsLinearConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsLinearConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsLinearConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsLinearConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsLinearConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsLinearConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsLinearConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsLinearConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsLinearConnectionSettingsSettingsError] = None


class ConnectorsLinearConnectionSettings(BaseModel):
    connector_name: Literal["linear"]

    settings: ConnectorsLinearConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsLunchmoneyConnectionSettings(BaseModel):
    connector_name: Literal["lunchmoney"]

    settings: None

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsMercuryConnectionSettings(BaseModel):
    connector_name: Literal["mercury"]

    settings: None

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsMergeConnectionSettingsSettings(BaseModel):
    account_token: str = FieldInfo(alias="accountToken")

    account_details: Optional[object] = FieldInfo(alias="accountDetails", default=None)


class ConnectorsMergeConnectionSettings(BaseModel):
    connector_name: Literal["merge"]

    settings: ConnectorsMergeConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsMicrosoftConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsMicrosoftConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsMicrosoftConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsMicrosoftConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsMicrosoftConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsMicrosoftConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsMicrosoftConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsMicrosoftConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsMicrosoftConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsMicrosoftConnectionSettingsSettingsOAuth

    client_id: Optional[str] = None

    error: Optional[ConnectorsMicrosoftConnectionSettingsSettingsError] = None


class ConnectorsMicrosoftConnectionSettings(BaseModel):
    connector_name: Literal["microsoft"]

    settings: ConnectorsMicrosoftConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsMongoDBConnectionSettingsSettings(BaseModel):
    database_name: str = FieldInfo(alias="databaseName")

    database_url: str = FieldInfo(alias="databaseUrl")


class ConnectorsMongoDBConnectionSettings(BaseModel):
    connector_name: Literal["mongodb"]

    settings: ConnectorsMongoDBConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsMootaConnectionSettings(BaseModel):
    connector_name: Literal["moota"]

    settings: None

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsOnebrickConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")


class ConnectorsOnebrickConnectionSettings(BaseModel):
    connector_name: Literal["onebrick"]

    settings: ConnectorsOnebrickConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsOutreachConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsOutreachConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsOutreachConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsOutreachConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsOutreachConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsOutreachConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsOutreachConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsOutreachConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsOutreachConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsOutreachConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsOutreachConnectionSettingsSettingsError] = None


class ConnectorsOutreachConnectionSettings(BaseModel):
    connector_name: Literal["outreach"]

    settings: ConnectorsOutreachConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsPipedriveConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsPipedriveConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsPipedriveConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsPipedriveConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsPipedriveConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsPipedriveConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsPipedriveConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsPipedriveConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsPipedriveConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsPipedriveConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsPipedriveConnectionSettingsSettingsError] = None


class ConnectorsPipedriveConnectionSettings(BaseModel):
    connector_name: Literal["pipedrive"]

    settings: ConnectorsPipedriveConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsPlaidConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")

    institution: Optional[object] = None

    item: Optional[object] = None

    item_id: Optional[str] = FieldInfo(alias="itemId", default=None)

    status: Optional[object] = None

    webhook_item_error: None = FieldInfo(alias="webhookItemError", default=None)


class ConnectorsPlaidConnectionSettings(BaseModel):
    connector_name: Literal["plaid"]

    settings: ConnectorsPlaidConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsPostgresConnectionSettingsSettingsSourceQueries(BaseModel):
    invoice: Optional[str] = None


class ConnectorsPostgresConnectionSettingsSettings(BaseModel):
    database_url: str = FieldInfo(alias="databaseUrl")

    migrate_tables: Optional[bool] = FieldInfo(alias="migrateTables", default=None)

    source_queries: Optional[ConnectorsPostgresConnectionSettingsSettingsSourceQueries] = FieldInfo(
        alias="sourceQueries", default=None
    )


class ConnectorsPostgresConnectionSettings(BaseModel):
    connector_name: Literal["postgres"]

    settings: ConnectorsPostgresConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsQboConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    realm_id: str = FieldInfo(alias="realmId")


class ConnectorsQboConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsQboConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsQboConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsQboConnectionSettingsSettingsOAuth(BaseModel):
    connection_config: ConnectorsQboConnectionSettingsSettingsOAuthConnectionConfig

    credentials: ConnectorsQboConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None


class ConnectorsQboConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsQboConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsQboConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsQboConnectionSettingsSettingsError] = None


class ConnectorsQboConnectionSettings(BaseModel):
    connector_name: Literal["qbo"]

    settings: ConnectorsQboConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsRampConnectionSettingsSettings(BaseModel):
    access_token: Optional[str] = FieldInfo(alias="accessToken", default=None)

    start_after_transaction_id: Optional[str] = FieldInfo(alias="startAfterTransactionId", default=None)


class ConnectorsRampConnectionSettings(BaseModel):
    connector_name: Literal["ramp"]

    settings: ConnectorsRampConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsRevertConnectionSettingsSettings(BaseModel):
    tenant_id: str


class ConnectorsRevertConnectionSettings(BaseModel):
    connector_name: Literal["revert"]

    settings: ConnectorsRevertConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsSalesforceConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsSalesforceConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsSalesforceConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsSalesforceConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsSalesforceConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsSalesforceConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsSalesforceConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsSalesforceConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsSalesforceConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsSalesforceConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsSalesforceConnectionSettingsSettingsError] = None


class ConnectorsSalesforceConnectionSettings(BaseModel):
    connector_name: Literal["salesforce"]

    settings: ConnectorsSalesforceConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsSalesloftConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsSalesloftConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsSalesloftConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsSalesloftConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsSalesloftConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsSalesloftConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsSalesloftConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsSalesloftConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsSalesloftConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsSalesloftConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsSalesloftConnectionSettingsSettingsError] = None


class ConnectorsSalesloftConnectionSettings(BaseModel):
    connector_name: Literal["salesloft"]

    settings: ConnectorsSalesloftConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsSaltedgeConnectionSettings(BaseModel):
    connector_name: Literal["saltedge"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    settings: Optional[object] = None

    updated_at: Optional[datetime] = None


class ConnectorsSlackConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsSlackConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsSlackConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsSlackConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsSlackConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsSlackConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsSlackConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsSlackConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsSlackConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsSlackConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsSlackConnectionSettingsSettingsError] = None


class ConnectorsSlackConnectionSettings(BaseModel):
    connector_name: Literal["slack"]

    settings: ConnectorsSlackConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsSplitwiseConnectionSettingsSettingsCurrentUserNotifications(BaseModel):
    added_as_friend: bool

    added_to_group: bool

    announcements: bool

    bills: bool

    expense_added: bool

    expense_updated: bool

    monthly_summary: bool

    payments: bool


class ConnectorsSplitwiseConnectionSettingsSettingsCurrentUserPicture(BaseModel):
    large: Optional[str] = None

    medium: Optional[str] = None

    original: Optional[str] = None

    small: Optional[str] = None

    xlarge: Optional[str] = None

    xxlarge: Optional[str] = None


class ConnectorsSplitwiseConnectionSettingsSettingsCurrentUser(BaseModel):
    id: float

    country_code: str

    custom_picture: bool

    date_format: str

    default_currency: str

    default_group_id: float

    email: str

    first_name: str

    force_refresh_at: str

    last_name: str

    locale: str

    notifications: ConnectorsSplitwiseConnectionSettingsSettingsCurrentUserNotifications

    notifications_count: float

    notifications_read: str

    picture: ConnectorsSplitwiseConnectionSettingsSettingsCurrentUserPicture

    registration_status: str


class ConnectorsSplitwiseConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")

    current_user: Optional[ConnectorsSplitwiseConnectionSettingsSettingsCurrentUser] = FieldInfo(
        alias="currentUser", default=None
    )


class ConnectorsSplitwiseConnectionSettings(BaseModel):
    connector_name: Literal["splitwise"]

    settings: ConnectorsSplitwiseConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsSpreadsheetConnectionSettingsSettings(BaseModel):
    account_external_id: str = FieldInfo(alias="accountExternalId")

    preset: Literal[
        "ramp",
        "apple-card",
        "alliant-credit-union",
        "bbva-mexico",
        "brex-cash",
        "brex",
        "capitalone-bank",
        "capitalone",
        "coinbase",
        "coinkeeper",
        "etrade",
        "first-republic",
        "wise",
    ]


class ConnectorsSpreadsheetConnectionSettings(BaseModel):
    connector_name: Literal["spreadsheet"]

    settings: ConnectorsSpreadsheetConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsStripeConnectionSettingsSettings(BaseModel):
    secret_key: str = FieldInfo(alias="secretKey")


class ConnectorsStripeConnectionSettings(BaseModel):
    connector_name: Literal["stripe"]

    settings: ConnectorsStripeConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsTellerConnectionSettingsSettings(BaseModel):
    token: str


class ConnectorsTellerConnectionSettings(BaseModel):
    connector_name: Literal["teller"]

    settings: ConnectorsTellerConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsTogglConnectionSettingsSettings(BaseModel):
    api_token: str = FieldInfo(alias="apiToken")

    email: Optional[str] = None

    password: Optional[str] = None


class ConnectorsTogglConnectionSettings(BaseModel):
    connector_name: Literal["toggl"]

    settings: ConnectorsTogglConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsTwentyConnectionSettingsSettings(BaseModel):
    access_token: str


class ConnectorsTwentyConnectionSettings(BaseModel):
    connector_name: Literal["twenty"]

    settings: ConnectorsTwentyConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsVenmoConnectionSettingsSettings(BaseModel):
    credentials: Optional[object] = None

    me: Optional[object] = None


class ConnectorsVenmoConnectionSettings(BaseModel):
    connector_name: Literal["venmo"]

    settings: ConnectorsVenmoConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsWebhookConnectionSettingsSettings(BaseModel):
    destination_url: str = FieldInfo(alias="destinationUrl")


class ConnectorsWebhookConnectionSettings(BaseModel):
    connector_name: Literal["webhook"]

    settings: ConnectorsWebhookConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsWiseConnectionSettingsSettings(BaseModel):
    env_name: Literal["sandbox", "live"] = FieldInfo(alias="envName")

    api_token: Optional[str] = FieldInfo(alias="apiToken", default=None)


class ConnectorsWiseConnectionSettings(BaseModel):
    connector_name: Literal["wise"]

    settings: ConnectorsWiseConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsXeroConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsXeroConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsXeroConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsXeroConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsXeroConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsXeroConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsXeroConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsXeroConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsXeroConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsXeroConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsXeroConnectionSettingsSettingsError] = None


class ConnectorsXeroConnectionSettings(BaseModel):
    connector_name: Literal["xero"]

    settings: ConnectorsXeroConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsYodleeConnectionSettingsSettingsAccessToken(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")

    expires_in: float = FieldInfo(alias="expiresIn")

    issued_at: str = FieldInfo(alias="issuedAt")


class ConnectorsYodleeConnectionSettingsSettingsProviderAccount(BaseModel):
    id: float

    aggregation_source: str = FieldInfo(alias="aggregationSource")

    created_date: str = FieldInfo(alias="createdDate")

    dataset: List[object]

    is_manual: bool = FieldInfo(alias="isManual")

    provider_id: float = FieldInfo(alias="providerId")

    status: Literal["LOGIN_IN_PROGRESS", "USER_INPUT_REQUIRED", "IN_PROGRESS", "PARTIAL_SUCCESS", "SUCCESS", "FAILED"]

    is_deleted: Optional[bool] = FieldInfo(alias="isDeleted", default=None)


class ConnectorsYodleeConnectionSettingsSettings(BaseModel):
    login_name: str = FieldInfo(alias="loginName")

    provider_account_id: Union[float, str] = FieldInfo(alias="providerAccountId")

    access_token: Optional[ConnectorsYodleeConnectionSettingsSettingsAccessToken] = FieldInfo(
        alias="accessToken", default=None
    )

    provider: None = None

    provider_account: Optional[ConnectorsYodleeConnectionSettingsSettingsProviderAccount] = FieldInfo(
        alias="providerAccount", default=None
    )

    user: None = None


class ConnectorsYodleeConnectionSettings(BaseModel):
    connector_name: Literal["yodlee"]

    settings: ConnectorsYodleeConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsZohodeskConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ConnectorsZohodeskConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ConnectorsZohodeskConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ConnectorsZohodeskConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorsZohodeskConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ConnectorsZohodeskConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ConnectorsZohodeskConnectionSettingsSettingsOAuthConnectionConfig] = None


class ConnectorsZohodeskConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ConnectorsZohodeskConnectionSettingsSettings(BaseModel):
    oauth: ConnectorsZohodeskConnectionSettingsSettingsOAuth

    error: Optional[ConnectorsZohodeskConnectionSettingsSettingsError] = None


class ConnectorsZohodeskConnectionSettings(BaseModel):
    connector_name: Literal["zohodesk"]

    settings: ConnectorsZohodeskConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ConnectorsGoogledriveConnectionSettings(BaseModel):
    connector_name: Literal["googledrive"]

    settings: None

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


ListConnectionsResponse: TypeAlias = Union[
    ConnectorsAircallConnectionSettings,
    ConnectorsAirtableConnectionSettings,
    ConnectorsApolloConnectionSettings,
    ConnectorsBeancountConnectionSettings,
    ConnectorsBrexConnectionSettings,
    ConnectorsCodaConnectionSettings,
    ConnectorsConfluenceConnectionSettings,
    ConnectorsDebugConnectionSettings,
    ConnectorsDiscordConnectionSettings,
    ConnectorsFinchConnectionSettings,
    ConnectorsFirebaseConnectionSettings,
    ConnectorsForeceiptConnectionSettings,
    ConnectorsFsConnectionSettings,
    ConnectorsGitHubConnectionSettings,
    ConnectorsGongConnectionSettings,
    ConnectorsGoogleConnectionSettings,
    ConnectorsGreenhouseConnectionSettings,
    ConnectorsHeronConnectionSettings,
    ConnectorsHubspotConnectionSettings,
    ConnectorsIntercomConnectionSettings,
    ConnectorsJiraConnectionSettings,
    ConnectorsKustomerConnectionSettings,
    ConnectorsLeverConnectionSettings,
    ConnectorsLinearConnectionSettings,
    ConnectorsLunchmoneyConnectionSettings,
    ConnectorsMercuryConnectionSettings,
    ConnectorsMergeConnectionSettings,
    ConnectorsMicrosoftConnectionSettings,
    ConnectorsMongoDBConnectionSettings,
    ConnectorsMootaConnectionSettings,
    ConnectorsOnebrickConnectionSettings,
    ConnectorsOutreachConnectionSettings,
    ConnectorsPipedriveConnectionSettings,
    ConnectorsPlaidConnectionSettings,
    ConnectorsPostgresConnectionSettings,
    ConnectorsQboConnectionSettings,
    ConnectorsRampConnectionSettings,
    ConnectorsRevertConnectionSettings,
    ConnectorsSalesforceConnectionSettings,
    ConnectorsSalesloftConnectionSettings,
    ConnectorsSaltedgeConnectionSettings,
    ConnectorsSlackConnectionSettings,
    ConnectorsSplitwiseConnectionSettings,
    ConnectorsSpreadsheetConnectionSettings,
    ConnectorsStripeConnectionSettings,
    ConnectorsTellerConnectionSettings,
    ConnectorsTogglConnectionSettings,
    ConnectorsTwentyConnectionSettings,
    ConnectorsVenmoConnectionSettings,
    ConnectorsWebhookConnectionSettings,
    ConnectorsWiseConnectionSettings,
    ConnectorsXeroConnectionSettings,
    ConnectorsYodleeConnectionSettings,
    ConnectorsZohodeskConnectionSettings,
    ConnectorsGoogledriveConnectionSettings,
]

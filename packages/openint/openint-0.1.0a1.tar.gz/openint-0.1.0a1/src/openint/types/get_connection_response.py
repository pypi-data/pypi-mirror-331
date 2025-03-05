# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "GetConnectionResponse",
    "Item",
    "ItemConnectorsAircallConnectionSettings",
    "ItemConnectorsAircallConnectionSettingsSettings",
    "ItemConnectorsAirtableConnectionSettings",
    "ItemConnectorsAirtableConnectionSettingsSettings",
    "ItemConnectorsApolloConnectionSettings",
    "ItemConnectorsApolloConnectionSettingsSettings",
    "ItemConnectorsApolloConnectionSettingsSettingsOAuth",
    "ItemConnectorsApolloConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsApolloConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsApolloConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsApolloConnectionSettingsSettingsError",
    "ItemConnectorsBeancountConnectionSettings",
    "ItemConnectorsBrexConnectionSettings",
    "ItemConnectorsBrexConnectionSettingsSettings",
    "ItemConnectorsCodaConnectionSettings",
    "ItemConnectorsCodaConnectionSettingsSettings",
    "ItemConnectorsConfluenceConnectionSettings",
    "ItemConnectorsConfluenceConnectionSettingsSettings",
    "ItemConnectorsConfluenceConnectionSettingsSettingsOAuth",
    "ItemConnectorsConfluenceConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsConfluenceConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsConfluenceConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsConfluenceConnectionSettingsSettingsError",
    "ItemConnectorsDebugConnectionSettings",
    "ItemConnectorsDiscordConnectionSettings",
    "ItemConnectorsDiscordConnectionSettingsSettings",
    "ItemConnectorsDiscordConnectionSettingsSettingsOAuth",
    "ItemConnectorsDiscordConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsDiscordConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsDiscordConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsDiscordConnectionSettingsSettingsError",
    "ItemConnectorsFinchConnectionSettings",
    "ItemConnectorsFinchConnectionSettingsSettings",
    "ItemConnectorsFirebaseConnectionSettings",
    "ItemConnectorsFirebaseConnectionSettingsSettings",
    "ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember0",
    "ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember0ServiceAccount",
    "ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1",
    "ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthData",
    "ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember0",
    "ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson",
    "ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember1",
    "ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember2",
    "ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1FirebaseConfig",
    "ItemConnectorsForeceiptConnectionSettings",
    "ItemConnectorsForeceiptConnectionSettingsSettings",
    "ItemConnectorsFsConnectionSettings",
    "ItemConnectorsFsConnectionSettingsSettings",
    "ItemConnectorsGitHubConnectionSettings",
    "ItemConnectorsGitHubConnectionSettingsSettings",
    "ItemConnectorsGitHubConnectionSettingsSettingsOAuth",
    "ItemConnectorsGitHubConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsGitHubConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsGitHubConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsGitHubConnectionSettingsSettingsError",
    "ItemConnectorsGongConnectionSettings",
    "ItemConnectorsGongConnectionSettingsSettings",
    "ItemConnectorsGongConnectionSettingsSettingsOAuth",
    "ItemConnectorsGongConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsGongConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsGongConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsGongConnectionSettingsSettingsError",
    "ItemConnectorsGoogleConnectionSettings",
    "ItemConnectorsGoogleConnectionSettingsSettings",
    "ItemConnectorsGoogleConnectionSettingsSettingsOAuth",
    "ItemConnectorsGoogleConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsGoogleConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsGoogleConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsGoogleConnectionSettingsSettingsError",
    "ItemConnectorsGreenhouseConnectionSettings",
    "ItemConnectorsGreenhouseConnectionSettingsSettings",
    "ItemConnectorsHeronConnectionSettings",
    "ItemConnectorsHubspotConnectionSettings",
    "ItemConnectorsHubspotConnectionSettingsSettings",
    "ItemConnectorsHubspotConnectionSettingsSettingsOAuth",
    "ItemConnectorsHubspotConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsHubspotConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsHubspotConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsHubspotConnectionSettingsSettingsError",
    "ItemConnectorsIntercomConnectionSettings",
    "ItemConnectorsIntercomConnectionSettingsSettings",
    "ItemConnectorsIntercomConnectionSettingsSettingsOAuth",
    "ItemConnectorsIntercomConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsIntercomConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsIntercomConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsIntercomConnectionSettingsSettingsError",
    "ItemConnectorsJiraConnectionSettings",
    "ItemConnectorsJiraConnectionSettingsSettings",
    "ItemConnectorsJiraConnectionSettingsSettingsOAuth",
    "ItemConnectorsJiraConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsJiraConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsJiraConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsJiraConnectionSettingsSettingsError",
    "ItemConnectorsKustomerConnectionSettings",
    "ItemConnectorsKustomerConnectionSettingsSettings",
    "ItemConnectorsKustomerConnectionSettingsSettingsOAuth",
    "ItemConnectorsKustomerConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsKustomerConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsKustomerConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsKustomerConnectionSettingsSettingsError",
    "ItemConnectorsLeverConnectionSettings",
    "ItemConnectorsLeverConnectionSettingsSettings",
    "ItemConnectorsLeverConnectionSettingsSettingsOAuth",
    "ItemConnectorsLeverConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsLeverConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsLeverConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsLeverConnectionSettingsSettingsError",
    "ItemConnectorsLinearConnectionSettings",
    "ItemConnectorsLinearConnectionSettingsSettings",
    "ItemConnectorsLinearConnectionSettingsSettingsOAuth",
    "ItemConnectorsLinearConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsLinearConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsLinearConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsLinearConnectionSettingsSettingsError",
    "ItemConnectorsLunchmoneyConnectionSettings",
    "ItemConnectorsMercuryConnectionSettings",
    "ItemConnectorsMergeConnectionSettings",
    "ItemConnectorsMergeConnectionSettingsSettings",
    "ItemConnectorsMicrosoftConnectionSettings",
    "ItemConnectorsMicrosoftConnectionSettingsSettings",
    "ItemConnectorsMicrosoftConnectionSettingsSettingsOAuth",
    "ItemConnectorsMicrosoftConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsMicrosoftConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsMicrosoftConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsMicrosoftConnectionSettingsSettingsError",
    "ItemConnectorsMongoDBConnectionSettings",
    "ItemConnectorsMongoDBConnectionSettingsSettings",
    "ItemConnectorsMootaConnectionSettings",
    "ItemConnectorsOnebrickConnectionSettings",
    "ItemConnectorsOnebrickConnectionSettingsSettings",
    "ItemConnectorsOutreachConnectionSettings",
    "ItemConnectorsOutreachConnectionSettingsSettings",
    "ItemConnectorsOutreachConnectionSettingsSettingsOAuth",
    "ItemConnectorsOutreachConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsOutreachConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsOutreachConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsOutreachConnectionSettingsSettingsError",
    "ItemConnectorsPipedriveConnectionSettings",
    "ItemConnectorsPipedriveConnectionSettingsSettings",
    "ItemConnectorsPipedriveConnectionSettingsSettingsOAuth",
    "ItemConnectorsPipedriveConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsPipedriveConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsPipedriveConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsPipedriveConnectionSettingsSettingsError",
    "ItemConnectorsPlaidConnectionSettings",
    "ItemConnectorsPlaidConnectionSettingsSettings",
    "ItemConnectorsPostgresConnectionSettings",
    "ItemConnectorsPostgresConnectionSettingsSettings",
    "ItemConnectorsPostgresConnectionSettingsSettingsSourceQueries",
    "ItemConnectorsQboConnectionSettings",
    "ItemConnectorsQboConnectionSettingsSettings",
    "ItemConnectorsQboConnectionSettingsSettingsOAuth",
    "ItemConnectorsQboConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsQboConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsQboConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsQboConnectionSettingsSettingsError",
    "ItemConnectorsRampConnectionSettings",
    "ItemConnectorsRampConnectionSettingsSettings",
    "ItemConnectorsRevertConnectionSettings",
    "ItemConnectorsRevertConnectionSettingsSettings",
    "ItemConnectorsSalesforceConnectionSettings",
    "ItemConnectorsSalesforceConnectionSettingsSettings",
    "ItemConnectorsSalesforceConnectionSettingsSettingsOAuth",
    "ItemConnectorsSalesforceConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsSalesforceConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsSalesforceConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsSalesforceConnectionSettingsSettingsError",
    "ItemConnectorsSalesloftConnectionSettings",
    "ItemConnectorsSalesloftConnectionSettingsSettings",
    "ItemConnectorsSalesloftConnectionSettingsSettingsOAuth",
    "ItemConnectorsSalesloftConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsSalesloftConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsSalesloftConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsSalesloftConnectionSettingsSettingsError",
    "ItemConnectorsSaltedgeConnectionSettings",
    "ItemConnectorsSlackConnectionSettings",
    "ItemConnectorsSlackConnectionSettingsSettings",
    "ItemConnectorsSlackConnectionSettingsSettingsOAuth",
    "ItemConnectorsSlackConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsSlackConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsSlackConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsSlackConnectionSettingsSettingsError",
    "ItemConnectorsSplitwiseConnectionSettings",
    "ItemConnectorsSplitwiseConnectionSettingsSettings",
    "ItemConnectorsSplitwiseConnectionSettingsSettingsCurrentUser",
    "ItemConnectorsSplitwiseConnectionSettingsSettingsCurrentUserNotifications",
    "ItemConnectorsSplitwiseConnectionSettingsSettingsCurrentUserPicture",
    "ItemConnectorsSpreadsheetConnectionSettings",
    "ItemConnectorsSpreadsheetConnectionSettingsSettings",
    "ItemConnectorsStripeConnectionSettings",
    "ItemConnectorsStripeConnectionSettingsSettings",
    "ItemConnectorsTellerConnectionSettings",
    "ItemConnectorsTellerConnectionSettingsSettings",
    "ItemConnectorsTogglConnectionSettings",
    "ItemConnectorsTogglConnectionSettingsSettings",
    "ItemConnectorsTwentyConnectionSettings",
    "ItemConnectorsTwentyConnectionSettingsSettings",
    "ItemConnectorsVenmoConnectionSettings",
    "ItemConnectorsVenmoConnectionSettingsSettings",
    "ItemConnectorsWebhookConnectionSettings",
    "ItemConnectorsWebhookConnectionSettingsSettings",
    "ItemConnectorsWiseConnectionSettings",
    "ItemConnectorsWiseConnectionSettingsSettings",
    "ItemConnectorsXeroConnectionSettings",
    "ItemConnectorsXeroConnectionSettingsSettings",
    "ItemConnectorsXeroConnectionSettingsSettingsOAuth",
    "ItemConnectorsXeroConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsXeroConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsXeroConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsXeroConnectionSettingsSettingsError",
    "ItemConnectorsYodleeConnectionSettings",
    "ItemConnectorsYodleeConnectionSettingsSettings",
    "ItemConnectorsYodleeConnectionSettingsSettingsAccessToken",
    "ItemConnectorsYodleeConnectionSettingsSettingsProviderAccount",
    "ItemConnectorsZohodeskConnectionSettings",
    "ItemConnectorsZohodeskConnectionSettingsSettings",
    "ItemConnectorsZohodeskConnectionSettingsSettingsOAuth",
    "ItemConnectorsZohodeskConnectionSettingsSettingsOAuthCredentials",
    "ItemConnectorsZohodeskConnectionSettingsSettingsOAuthCredentialsRaw",
    "ItemConnectorsZohodeskConnectionSettingsSettingsOAuthConnectionConfig",
    "ItemConnectorsZohodeskConnectionSettingsSettingsError",
    "ItemConnectorsGoogledriveConnectionSettings",
]


class ItemConnectorsAircallConnectionSettingsSettings(BaseModel):
    api_id: str = FieldInfo(alias="apiId")

    api_token: str = FieldInfo(alias="apiToken")


class ItemConnectorsAircallConnectionSettings(BaseModel):
    connector_name: Literal["aircall"]

    settings: ItemConnectorsAircallConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsAirtableConnectionSettingsSettings(BaseModel):
    airtable_base: str = FieldInfo(alias="airtableBase")

    api_key: str = FieldInfo(alias="apiKey")


class ItemConnectorsAirtableConnectionSettings(BaseModel):
    connector_name: Literal["airtable"]

    settings: ItemConnectorsAirtableConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsApolloConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsApolloConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsApolloConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsApolloConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsApolloConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsApolloConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsApolloConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsApolloConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsApolloConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsApolloConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsApolloConnectionSettingsSettingsError] = None


class ItemConnectorsApolloConnectionSettings(BaseModel):
    connector_name: Literal["apollo"]

    settings: ItemConnectorsApolloConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsBeancountConnectionSettings(BaseModel):
    connector_name: Literal["beancount"]

    settings: None

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsBrexConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")


class ItemConnectorsBrexConnectionSettings(BaseModel):
    connector_name: Literal["brex"]

    settings: ItemConnectorsBrexConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsCodaConnectionSettingsSettings(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ItemConnectorsCodaConnectionSettings(BaseModel):
    connector_name: Literal["coda"]

    settings: ItemConnectorsCodaConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsConfluenceConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsConfluenceConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsConfluenceConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsConfluenceConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsConfluenceConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsConfluenceConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsConfluenceConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsConfluenceConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsConfluenceConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsConfluenceConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsConfluenceConnectionSettingsSettingsError] = None


class ItemConnectorsConfluenceConnectionSettings(BaseModel):
    connector_name: Literal["confluence"]

    settings: ItemConnectorsConfluenceConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsDebugConnectionSettings(BaseModel):
    connector_name: Literal["debug"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    settings: Optional[object] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsDiscordConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsDiscordConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsDiscordConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsDiscordConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsDiscordConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsDiscordConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsDiscordConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsDiscordConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsDiscordConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsDiscordConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsDiscordConnectionSettingsSettingsError] = None


class ItemConnectorsDiscordConnectionSettings(BaseModel):
    connector_name: Literal["discord"]

    settings: ItemConnectorsDiscordConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsFinchConnectionSettingsSettings(BaseModel):
    access_token: str


class ItemConnectorsFinchConnectionSettings(BaseModel):
    connector_name: Literal["finch"]

    settings: ItemConnectorsFinchConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember0ServiceAccount(BaseModel):
    project_id: str

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember0(BaseModel):
    role: Literal["admin"]

    service_account: ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember0ServiceAccount = FieldInfo(
        alias="serviceAccount"
    )


class ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson(BaseModel):
    app_name: str = FieldInfo(alias="appName")

    sts_token_manager: Dict[str, object] = FieldInfo(alias="stsTokenManager")

    uid: str

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember0(BaseModel):
    method: Literal["userJson"]

    user_json: ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson = FieldInfo(
        alias="userJson"
    )


class ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember1(BaseModel):
    custom_token: str = FieldInfo(alias="customToken")

    method: Literal["customToken"]


class ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember2(BaseModel):
    email: str

    method: Literal["emailPassword"]

    password: str


ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthData: TypeAlias = Union[
    ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember0,
    ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember1,
    ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthDataUnionMember2,
]


class ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1FirebaseConfig(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")

    app_id: str = FieldInfo(alias="appId")

    auth_domain: str = FieldInfo(alias="authDomain")

    database_url: str = FieldInfo(alias="databaseURL")

    project_id: str = FieldInfo(alias="projectId")

    measurement_id: Optional[str] = FieldInfo(alias="measurementId", default=None)

    messaging_sender_id: Optional[str] = FieldInfo(alias="messagingSenderId", default=None)

    storage_bucket: Optional[str] = FieldInfo(alias="storageBucket", default=None)


class ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1(BaseModel):
    auth_data: ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1AuthData = FieldInfo(alias="authData")

    firebase_config: ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1FirebaseConfig = FieldInfo(
        alias="firebaseConfig"
    )

    role: Literal["user"]


ItemConnectorsFirebaseConnectionSettingsSettings: TypeAlias = Union[
    ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember0,
    ItemConnectorsFirebaseConnectionSettingsSettingsUnionMember1,
]


class ItemConnectorsFirebaseConnectionSettings(BaseModel):
    connector_name: Literal["firebase"]

    settings: ItemConnectorsFirebaseConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsForeceiptConnectionSettingsSettings(BaseModel):
    env_name: Literal["staging", "production"] = FieldInfo(alias="envName")

    api_id: Optional[object] = FieldInfo(alias="_id", default=None)

    credentials: Optional[object] = None

    options: Optional[object] = None


class ItemConnectorsForeceiptConnectionSettings(BaseModel):
    connector_name: Literal["foreceipt"]

    settings: ItemConnectorsForeceiptConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsFsConnectionSettingsSettings(BaseModel):
    base_path: str = FieldInfo(alias="basePath")


class ItemConnectorsFsConnectionSettings(BaseModel):
    connector_name: Literal["fs"]

    settings: ItemConnectorsFsConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsGitHubConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsGitHubConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsGitHubConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsGitHubConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsGitHubConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsGitHubConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsGitHubConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsGitHubConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsGitHubConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsGitHubConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsGitHubConnectionSettingsSettingsError] = None


class ItemConnectorsGitHubConnectionSettings(BaseModel):
    connector_name: Literal["github"]

    settings: ItemConnectorsGitHubConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsGongConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsGongConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsGongConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsGongConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsGongConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsGongConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsGongConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsGongConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsGongConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsGongConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsGongConnectionSettingsSettingsError] = None


class ItemConnectorsGongConnectionSettings(BaseModel):
    connector_name: Literal["gong"]

    settings: ItemConnectorsGongConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsGoogleConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsGoogleConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsGoogleConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsGoogleConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsGoogleConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsGoogleConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsGoogleConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsGoogleConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsGoogleConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsGoogleConnectionSettingsSettingsOAuth

    client_id: Optional[str] = None

    error: Optional[ItemConnectorsGoogleConnectionSettingsSettingsError] = None


class ItemConnectorsGoogleConnectionSettings(BaseModel):
    connector_name: Literal["google"]

    settings: ItemConnectorsGoogleConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsGreenhouseConnectionSettingsSettings(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ItemConnectorsGreenhouseConnectionSettings(BaseModel):
    connector_name: Literal["greenhouse"]

    settings: ItemConnectorsGreenhouseConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsHeronConnectionSettings(BaseModel):
    connector_name: Literal["heron"]

    settings: None

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsHubspotConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsHubspotConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsHubspotConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsHubspotConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsHubspotConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsHubspotConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsHubspotConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsHubspotConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsHubspotConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsHubspotConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsHubspotConnectionSettingsSettingsError] = None

    extra: Optional[object] = None


class ItemConnectorsHubspotConnectionSettings(BaseModel):
    connector_name: Literal["hubspot"]

    settings: ItemConnectorsHubspotConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsIntercomConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsIntercomConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsIntercomConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsIntercomConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsIntercomConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsIntercomConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsIntercomConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsIntercomConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsIntercomConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsIntercomConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsIntercomConnectionSettingsSettingsError] = None


class ItemConnectorsIntercomConnectionSettings(BaseModel):
    connector_name: Literal["intercom"]

    settings: ItemConnectorsIntercomConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsJiraConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsJiraConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsJiraConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsJiraConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsJiraConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsJiraConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsJiraConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsJiraConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsJiraConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsJiraConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsJiraConnectionSettingsSettingsError] = None


class ItemConnectorsJiraConnectionSettings(BaseModel):
    connector_name: Literal["jira"]

    settings: ItemConnectorsJiraConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsKustomerConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsKustomerConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsKustomerConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsKustomerConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsKustomerConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsKustomerConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsKustomerConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsKustomerConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsKustomerConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsKustomerConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsKustomerConnectionSettingsSettingsError] = None


class ItemConnectorsKustomerConnectionSettings(BaseModel):
    connector_name: Literal["kustomer"]

    settings: ItemConnectorsKustomerConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsLeverConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsLeverConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsLeverConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsLeverConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsLeverConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsLeverConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsLeverConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsLeverConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsLeverConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsLeverConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsLeverConnectionSettingsSettingsError] = None


class ItemConnectorsLeverConnectionSettings(BaseModel):
    connector_name: Literal["lever"]

    settings: ItemConnectorsLeverConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsLinearConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsLinearConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsLinearConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsLinearConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsLinearConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsLinearConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsLinearConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsLinearConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsLinearConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsLinearConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsLinearConnectionSettingsSettingsError] = None


class ItemConnectorsLinearConnectionSettings(BaseModel):
    connector_name: Literal["linear"]

    settings: ItemConnectorsLinearConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsLunchmoneyConnectionSettings(BaseModel):
    connector_name: Literal["lunchmoney"]

    settings: None

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsMercuryConnectionSettings(BaseModel):
    connector_name: Literal["mercury"]

    settings: None

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsMergeConnectionSettingsSettings(BaseModel):
    account_token: str = FieldInfo(alias="accountToken")

    account_details: Optional[object] = FieldInfo(alias="accountDetails", default=None)


class ItemConnectorsMergeConnectionSettings(BaseModel):
    connector_name: Literal["merge"]

    settings: ItemConnectorsMergeConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsMicrosoftConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsMicrosoftConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsMicrosoftConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsMicrosoftConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsMicrosoftConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsMicrosoftConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsMicrosoftConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsMicrosoftConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsMicrosoftConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsMicrosoftConnectionSettingsSettingsOAuth

    client_id: Optional[str] = None

    error: Optional[ItemConnectorsMicrosoftConnectionSettingsSettingsError] = None


class ItemConnectorsMicrosoftConnectionSettings(BaseModel):
    connector_name: Literal["microsoft"]

    settings: ItemConnectorsMicrosoftConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsMongoDBConnectionSettingsSettings(BaseModel):
    database_name: str = FieldInfo(alias="databaseName")

    database_url: str = FieldInfo(alias="databaseUrl")


class ItemConnectorsMongoDBConnectionSettings(BaseModel):
    connector_name: Literal["mongodb"]

    settings: ItemConnectorsMongoDBConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsMootaConnectionSettings(BaseModel):
    connector_name: Literal["moota"]

    settings: None

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsOnebrickConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")


class ItemConnectorsOnebrickConnectionSettings(BaseModel):
    connector_name: Literal["onebrick"]

    settings: ItemConnectorsOnebrickConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsOutreachConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsOutreachConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsOutreachConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsOutreachConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsOutreachConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsOutreachConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsOutreachConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsOutreachConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsOutreachConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsOutreachConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsOutreachConnectionSettingsSettingsError] = None


class ItemConnectorsOutreachConnectionSettings(BaseModel):
    connector_name: Literal["outreach"]

    settings: ItemConnectorsOutreachConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsPipedriveConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsPipedriveConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsPipedriveConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsPipedriveConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsPipedriveConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsPipedriveConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsPipedriveConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsPipedriveConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsPipedriveConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsPipedriveConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsPipedriveConnectionSettingsSettingsError] = None


class ItemConnectorsPipedriveConnectionSettings(BaseModel):
    connector_name: Literal["pipedrive"]

    settings: ItemConnectorsPipedriveConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsPlaidConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")

    institution: Optional[object] = None

    item: Optional[object] = None

    item_id: Optional[str] = FieldInfo(alias="itemId", default=None)

    status: Optional[object] = None

    webhook_item_error: None = FieldInfo(alias="webhookItemError", default=None)


class ItemConnectorsPlaidConnectionSettings(BaseModel):
    connector_name: Literal["plaid"]

    settings: ItemConnectorsPlaidConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsPostgresConnectionSettingsSettingsSourceQueries(BaseModel):
    invoice: Optional[str] = None


class ItemConnectorsPostgresConnectionSettingsSettings(BaseModel):
    database_url: str = FieldInfo(alias="databaseUrl")

    migrate_tables: Optional[bool] = FieldInfo(alias="migrateTables", default=None)

    source_queries: Optional[ItemConnectorsPostgresConnectionSettingsSettingsSourceQueries] = FieldInfo(
        alias="sourceQueries", default=None
    )


class ItemConnectorsPostgresConnectionSettings(BaseModel):
    connector_name: Literal["postgres"]

    settings: ItemConnectorsPostgresConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsQboConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    realm_id: str = FieldInfo(alias="realmId")


class ItemConnectorsQboConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsQboConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsQboConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsQboConnectionSettingsSettingsOAuth(BaseModel):
    connection_config: ItemConnectorsQboConnectionSettingsSettingsOAuthConnectionConfig

    credentials: ItemConnectorsQboConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None


class ItemConnectorsQboConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsQboConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsQboConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsQboConnectionSettingsSettingsError] = None


class ItemConnectorsQboConnectionSettings(BaseModel):
    connector_name: Literal["qbo"]

    settings: ItemConnectorsQboConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsRampConnectionSettingsSettings(BaseModel):
    access_token: Optional[str] = FieldInfo(alias="accessToken", default=None)

    start_after_transaction_id: Optional[str] = FieldInfo(alias="startAfterTransactionId", default=None)


class ItemConnectorsRampConnectionSettings(BaseModel):
    connector_name: Literal["ramp"]

    settings: ItemConnectorsRampConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsRevertConnectionSettingsSettings(BaseModel):
    tenant_id: str


class ItemConnectorsRevertConnectionSettings(BaseModel):
    connector_name: Literal["revert"]

    settings: ItemConnectorsRevertConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsSalesforceConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsSalesforceConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsSalesforceConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsSalesforceConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsSalesforceConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsSalesforceConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsSalesforceConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsSalesforceConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsSalesforceConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsSalesforceConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsSalesforceConnectionSettingsSettingsError] = None


class ItemConnectorsSalesforceConnectionSettings(BaseModel):
    connector_name: Literal["salesforce"]

    settings: ItemConnectorsSalesforceConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsSalesloftConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsSalesloftConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsSalesloftConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsSalesloftConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsSalesloftConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsSalesloftConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsSalesloftConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsSalesloftConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsSalesloftConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsSalesloftConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsSalesloftConnectionSettingsSettingsError] = None


class ItemConnectorsSalesloftConnectionSettings(BaseModel):
    connector_name: Literal["salesloft"]

    settings: ItemConnectorsSalesloftConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsSaltedgeConnectionSettings(BaseModel):
    connector_name: Literal["saltedge"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    settings: Optional[object] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsSlackConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsSlackConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsSlackConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsSlackConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsSlackConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsSlackConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsSlackConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsSlackConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsSlackConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsSlackConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsSlackConnectionSettingsSettingsError] = None


class ItemConnectorsSlackConnectionSettings(BaseModel):
    connector_name: Literal["slack"]

    settings: ItemConnectorsSlackConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsSplitwiseConnectionSettingsSettingsCurrentUserNotifications(BaseModel):
    added_as_friend: bool

    added_to_group: bool

    announcements: bool

    bills: bool

    expense_added: bool

    expense_updated: bool

    monthly_summary: bool

    payments: bool


class ItemConnectorsSplitwiseConnectionSettingsSettingsCurrentUserPicture(BaseModel):
    large: Optional[str] = None

    medium: Optional[str] = None

    original: Optional[str] = None

    small: Optional[str] = None

    xlarge: Optional[str] = None

    xxlarge: Optional[str] = None


class ItemConnectorsSplitwiseConnectionSettingsSettingsCurrentUser(BaseModel):
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

    notifications: ItemConnectorsSplitwiseConnectionSettingsSettingsCurrentUserNotifications

    notifications_count: float

    notifications_read: str

    picture: ItemConnectorsSplitwiseConnectionSettingsSettingsCurrentUserPicture

    registration_status: str


class ItemConnectorsSplitwiseConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")

    current_user: Optional[ItemConnectorsSplitwiseConnectionSettingsSettingsCurrentUser] = FieldInfo(
        alias="currentUser", default=None
    )


class ItemConnectorsSplitwiseConnectionSettings(BaseModel):
    connector_name: Literal["splitwise"]

    settings: ItemConnectorsSplitwiseConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsSpreadsheetConnectionSettingsSettings(BaseModel):
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


class ItemConnectorsSpreadsheetConnectionSettings(BaseModel):
    connector_name: Literal["spreadsheet"]

    settings: ItemConnectorsSpreadsheetConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsStripeConnectionSettingsSettings(BaseModel):
    secret_key: str = FieldInfo(alias="secretKey")


class ItemConnectorsStripeConnectionSettings(BaseModel):
    connector_name: Literal["stripe"]

    settings: ItemConnectorsStripeConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsTellerConnectionSettingsSettings(BaseModel):
    token: str


class ItemConnectorsTellerConnectionSettings(BaseModel):
    connector_name: Literal["teller"]

    settings: ItemConnectorsTellerConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsTogglConnectionSettingsSettings(BaseModel):
    api_token: str = FieldInfo(alias="apiToken")

    email: Optional[str] = None

    password: Optional[str] = None


class ItemConnectorsTogglConnectionSettings(BaseModel):
    connector_name: Literal["toggl"]

    settings: ItemConnectorsTogglConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsTwentyConnectionSettingsSettings(BaseModel):
    access_token: str


class ItemConnectorsTwentyConnectionSettings(BaseModel):
    connector_name: Literal["twenty"]

    settings: ItemConnectorsTwentyConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsVenmoConnectionSettingsSettings(BaseModel):
    credentials: Optional[object] = None

    me: Optional[object] = None


class ItemConnectorsVenmoConnectionSettings(BaseModel):
    connector_name: Literal["venmo"]

    settings: ItemConnectorsVenmoConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsWebhookConnectionSettingsSettings(BaseModel):
    destination_url: str = FieldInfo(alias="destinationUrl")


class ItemConnectorsWebhookConnectionSettings(BaseModel):
    connector_name: Literal["webhook"]

    settings: ItemConnectorsWebhookConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsWiseConnectionSettingsSettings(BaseModel):
    env_name: Literal["sandbox", "live"] = FieldInfo(alias="envName")

    api_token: Optional[str] = FieldInfo(alias="apiToken", default=None)


class ItemConnectorsWiseConnectionSettings(BaseModel):
    connector_name: Literal["wise"]

    settings: ItemConnectorsWiseConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsXeroConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsXeroConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsXeroConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsXeroConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsXeroConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsXeroConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsXeroConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsXeroConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsXeroConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsXeroConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsXeroConnectionSettingsSettingsError] = None


class ItemConnectorsXeroConnectionSettings(BaseModel):
    connector_name: Literal["xero"]

    settings: ItemConnectorsXeroConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsYodleeConnectionSettingsSettingsAccessToken(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")

    expires_in: float = FieldInfo(alias="expiresIn")

    issued_at: str = FieldInfo(alias="issuedAt")


class ItemConnectorsYodleeConnectionSettingsSettingsProviderAccount(BaseModel):
    id: float

    aggregation_source: str = FieldInfo(alias="aggregationSource")

    created_date: str = FieldInfo(alias="createdDate")

    dataset: List[object]

    is_manual: bool = FieldInfo(alias="isManual")

    provider_id: float = FieldInfo(alias="providerId")

    status: Literal["LOGIN_IN_PROGRESS", "USER_INPUT_REQUIRED", "IN_PROGRESS", "PARTIAL_SUCCESS", "SUCCESS", "FAILED"]

    is_deleted: Optional[bool] = FieldInfo(alias="isDeleted", default=None)


class ItemConnectorsYodleeConnectionSettingsSettings(BaseModel):
    login_name: str = FieldInfo(alias="loginName")

    provider_account_id: Union[float, str] = FieldInfo(alias="providerAccountId")

    access_token: Optional[ItemConnectorsYodleeConnectionSettingsSettingsAccessToken] = FieldInfo(
        alias="accessToken", default=None
    )

    provider: None = None

    provider_account: Optional[ItemConnectorsYodleeConnectionSettingsSettingsProviderAccount] = FieldInfo(
        alias="providerAccount", default=None
    )

    user: None = None


class ItemConnectorsYodleeConnectionSettings(BaseModel):
    connector_name: Literal["yodlee"]

    settings: ItemConnectorsYodleeConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsZohodeskConnectionSettingsSettingsOAuthCredentialsRaw(BaseModel):
    access_token: str

    token_type: str

    expires_at: Optional[datetime] = None

    expires_in: Optional[float] = None

    refresh_token: Optional[str] = None

    refresh_token_expires_in: Optional[float] = None

    scope: Optional[str] = None


class ItemConnectorsZohodeskConnectionSettingsSettingsOAuthCredentials(BaseModel):
    raw: ItemConnectorsZohodeskConnectionSettingsSettingsOAuthCredentialsRaw

    type: Literal["OAUTH2", "OAUTH1", "BASIC", "API_KEY"]

    access_token: Optional[str] = None

    api_key: Optional[str] = None

    expires_at: Optional[datetime] = None

    refresh_token: Optional[str] = None


class ItemConnectorsZohodeskConnectionSettingsSettingsOAuthConnectionConfig(BaseModel):
    instance_url: Optional[str] = None

    portal_id: Optional[float] = FieldInfo(alias="portalId", default=None)

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ItemConnectorsZohodeskConnectionSettingsSettingsOAuth(BaseModel):
    credentials: ItemConnectorsZohodeskConnectionSettingsSettingsOAuthCredentials

    metadata: Optional[Dict[str, object]] = None

    connection_config: Optional[ItemConnectorsZohodeskConnectionSettingsSettingsOAuthConnectionConfig] = None


class ItemConnectorsZohodeskConnectionSettingsSettingsError(BaseModel):
    code: Union[Literal["refresh_token_external_error"], str]

    message: Optional[str] = None


class ItemConnectorsZohodeskConnectionSettingsSettings(BaseModel):
    oauth: ItemConnectorsZohodeskConnectionSettingsSettingsOAuth

    error: Optional[ItemConnectorsZohodeskConnectionSettingsSettingsError] = None


class ItemConnectorsZohodeskConnectionSettings(BaseModel):
    connector_name: Literal["zohodesk"]

    settings: ItemConnectorsZohodeskConnectionSettingsSettings

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsGoogledriveConnectionSettings(BaseModel):
    connector_name: Literal["googledrive"]

    settings: None

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


Item: TypeAlias = Union[
    ItemConnectorsAircallConnectionSettings,
    ItemConnectorsAirtableConnectionSettings,
    ItemConnectorsApolloConnectionSettings,
    ItemConnectorsBeancountConnectionSettings,
    ItemConnectorsBrexConnectionSettings,
    ItemConnectorsCodaConnectionSettings,
    ItemConnectorsConfluenceConnectionSettings,
    ItemConnectorsDebugConnectionSettings,
    ItemConnectorsDiscordConnectionSettings,
    ItemConnectorsFinchConnectionSettings,
    ItemConnectorsFirebaseConnectionSettings,
    ItemConnectorsForeceiptConnectionSettings,
    ItemConnectorsFsConnectionSettings,
    ItemConnectorsGitHubConnectionSettings,
    ItemConnectorsGongConnectionSettings,
    ItemConnectorsGoogleConnectionSettings,
    ItemConnectorsGreenhouseConnectionSettings,
    ItemConnectorsHeronConnectionSettings,
    ItemConnectorsHubspotConnectionSettings,
    ItemConnectorsIntercomConnectionSettings,
    ItemConnectorsJiraConnectionSettings,
    ItemConnectorsKustomerConnectionSettings,
    ItemConnectorsLeverConnectionSettings,
    ItemConnectorsLinearConnectionSettings,
    ItemConnectorsLunchmoneyConnectionSettings,
    ItemConnectorsMercuryConnectionSettings,
    ItemConnectorsMergeConnectionSettings,
    ItemConnectorsMicrosoftConnectionSettings,
    ItemConnectorsMongoDBConnectionSettings,
    ItemConnectorsMootaConnectionSettings,
    ItemConnectorsOnebrickConnectionSettings,
    ItemConnectorsOutreachConnectionSettings,
    ItemConnectorsPipedriveConnectionSettings,
    ItemConnectorsPlaidConnectionSettings,
    ItemConnectorsPostgresConnectionSettings,
    ItemConnectorsQboConnectionSettings,
    ItemConnectorsRampConnectionSettings,
    ItemConnectorsRevertConnectionSettings,
    ItemConnectorsSalesforceConnectionSettings,
    ItemConnectorsSalesloftConnectionSettings,
    ItemConnectorsSaltedgeConnectionSettings,
    ItemConnectorsSlackConnectionSettings,
    ItemConnectorsSplitwiseConnectionSettings,
    ItemConnectorsSpreadsheetConnectionSettings,
    ItemConnectorsStripeConnectionSettings,
    ItemConnectorsTellerConnectionSettings,
    ItemConnectorsTogglConnectionSettings,
    ItemConnectorsTwentyConnectionSettings,
    ItemConnectorsVenmoConnectionSettings,
    ItemConnectorsWebhookConnectionSettings,
    ItemConnectorsWiseConnectionSettings,
    ItemConnectorsXeroConnectionSettings,
    ItemConnectorsYodleeConnectionSettings,
    ItemConnectorsZohodeskConnectionSettings,
    ItemConnectorsGoogledriveConnectionSettings,
]


class GetConnectionResponse(BaseModel):
    items: List[Item]

    limit: int

    offset: int

    total: float

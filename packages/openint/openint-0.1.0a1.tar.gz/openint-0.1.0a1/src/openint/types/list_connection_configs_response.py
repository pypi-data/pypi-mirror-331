# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "ListConnectionConfigsResponse",
    "Item",
    "ItemConnectorsAircallConnectorConfig",
    "ItemConnectorsAirtableConnectorConfig",
    "ItemConnectorsApolloConnectorConfig",
    "ItemConnectorsBeancountConnectorConfig",
    "ItemConnectorsBrexConnectorConfig",
    "ItemConnectorsBrexConnectorConfigConfig",
    "ItemConnectorsBrexConnectorConfigConfigOAuth",
    "ItemConnectorsCodaConnectorConfig",
    "ItemConnectorsConfluenceConnectorConfig",
    "ItemConnectorsConfluenceConnectorConfigConfig",
    "ItemConnectorsConfluenceConnectorConfigConfigOAuth",
    "ItemConnectorsDebugConnectorConfig",
    "ItemConnectorsDiscordConnectorConfig",
    "ItemConnectorsDiscordConnectorConfigConfig",
    "ItemConnectorsDiscordConnectorConfigConfigOAuth",
    "ItemConnectorsFinchConnectorConfig",
    "ItemConnectorsFinchConnectorConfigConfig",
    "ItemConnectorsFirebaseConnectorConfig",
    "ItemConnectorsForeceiptConnectorConfig",
    "ItemConnectorsFsConnectorConfig",
    "ItemConnectorsGitHubConnectorConfig",
    "ItemConnectorsGitHubConnectorConfigConfig",
    "ItemConnectorsGitHubConnectorConfigConfigOAuth",
    "ItemConnectorsGongConnectorConfig",
    "ItemConnectorsGongConnectorConfigConfig",
    "ItemConnectorsGongConnectorConfigConfigOAuth",
    "ItemConnectorsGoogleConnectorConfig",
    "ItemConnectorsGoogleConnectorConfigConfig",
    "ItemConnectorsGoogleConnectorConfigConfigIntegrations",
    "ItemConnectorsGoogleConnectorConfigConfigIntegrationsCalendar",
    "ItemConnectorsGoogleConnectorConfigConfigIntegrationsDocs",
    "ItemConnectorsGoogleConnectorConfigConfigIntegrationsDrive",
    "ItemConnectorsGoogleConnectorConfigConfigIntegrationsGmail",
    "ItemConnectorsGoogleConnectorConfigConfigIntegrationsSheets",
    "ItemConnectorsGoogleConnectorConfigConfigIntegrationsSlides",
    "ItemConnectorsGoogleConnectorConfigConfigOAuth",
    "ItemConnectorsGreenhouseConnectorConfig",
    "ItemConnectorsHeronConnectorConfig",
    "ItemConnectorsHeronConnectorConfigConfig",
    "ItemConnectorsHubspotConnectorConfig",
    "ItemConnectorsHubspotConnectorConfigConfig",
    "ItemConnectorsHubspotConnectorConfigConfigOAuth",
    "ItemConnectorsIntercomConnectorConfig",
    "ItemConnectorsIntercomConnectorConfigConfig",
    "ItemConnectorsIntercomConnectorConfigConfigOAuth",
    "ItemConnectorsJiraConnectorConfig",
    "ItemConnectorsJiraConnectorConfigConfig",
    "ItemConnectorsJiraConnectorConfigConfigOAuth",
    "ItemConnectorsKustomerConnectorConfig",
    "ItemConnectorsKustomerConnectorConfigConfig",
    "ItemConnectorsKustomerConnectorConfigConfigOAuth",
    "ItemConnectorsLeverConnectorConfig",
    "ItemConnectorsLeverConnectorConfigConfig",
    "ItemConnectorsLeverConnectorConfigConfigOAuth",
    "ItemConnectorsLinearConnectorConfig",
    "ItemConnectorsLinearConnectorConfigConfig",
    "ItemConnectorsLinearConnectorConfigConfigOAuth",
    "ItemConnectorsLunchmoneyConnectorConfig",
    "ItemConnectorsLunchmoneyConnectorConfigConfig",
    "ItemConnectorsMercuryConnectorConfig",
    "ItemConnectorsMercuryConnectorConfigConfig",
    "ItemConnectorsMercuryConnectorConfigConfigOAuth",
    "ItemConnectorsMergeConnectorConfig",
    "ItemConnectorsMergeConnectorConfigConfig",
    "ItemConnectorsMicrosoftConnectorConfig",
    "ItemConnectorsMicrosoftConnectorConfigConfig",
    "ItemConnectorsMicrosoftConnectorConfigConfigIntegrations",
    "ItemConnectorsMicrosoftConnectorConfigConfigIntegrationsOutlook",
    "ItemConnectorsMicrosoftConnectorConfigConfigIntegrationsSharepoint",
    "ItemConnectorsMicrosoftConnectorConfigConfigIntegrationsTeams",
    "ItemConnectorsMicrosoftConnectorConfigConfigOAuth",
    "ItemConnectorsMongoDBConnectorConfig",
    "ItemConnectorsMootaConnectorConfig",
    "ItemConnectorsMootaConnectorConfigConfig",
    "ItemConnectorsOnebrickConnectorConfig",
    "ItemConnectorsOnebrickConnectorConfigConfig",
    "ItemConnectorsOutreachConnectorConfig",
    "ItemConnectorsOutreachConnectorConfigConfig",
    "ItemConnectorsOutreachConnectorConfigConfigOAuth",
    "ItemConnectorsPipedriveConnectorConfig",
    "ItemConnectorsPipedriveConnectorConfigConfig",
    "ItemConnectorsPipedriveConnectorConfigConfigOAuth",
    "ItemConnectorsPlaidConnectorConfig",
    "ItemConnectorsPlaidConnectorConfigConfig",
    "ItemConnectorsPlaidConnectorConfigConfigCredentials",
    "ItemConnectorsPostgresConnectorConfig",
    "ItemConnectorsQboConnectorConfig",
    "ItemConnectorsQboConnectorConfigConfig",
    "ItemConnectorsQboConnectorConfigConfigOAuth",
    "ItemConnectorsRampConnectorConfig",
    "ItemConnectorsRampConnectorConfigConfig",
    "ItemConnectorsRampConnectorConfigConfigOAuth",
    "ItemConnectorsRevertConnectorConfig",
    "ItemConnectorsRevertConnectorConfigConfig",
    "ItemConnectorsSalesforceConnectorConfig",
    "ItemConnectorsSalesforceConnectorConfigConfig",
    "ItemConnectorsSalesforceConnectorConfigConfigOAuth",
    "ItemConnectorsSalesloftConnectorConfig",
    "ItemConnectorsSalesloftConnectorConfigConfig",
    "ItemConnectorsSalesloftConnectorConfigConfigOAuth",
    "ItemConnectorsSaltedgeConnectorConfig",
    "ItemConnectorsSaltedgeConnectorConfigConfig",
    "ItemConnectorsSlackConnectorConfig",
    "ItemConnectorsSlackConnectorConfigConfig",
    "ItemConnectorsSlackConnectorConfigConfigOAuth",
    "ItemConnectorsSplitwiseConnectorConfig",
    "ItemConnectorsSpreadsheetConnectorConfig",
    "ItemConnectorsSpreadsheetConnectorConfigConfig",
    "ItemConnectorsStripeConnectorConfig",
    "ItemConnectorsStripeConnectorConfigConfig",
    "ItemConnectorsStripeConnectorConfigConfigOAuth",
    "ItemConnectorsTellerConnectorConfig",
    "ItemConnectorsTellerConnectorConfigConfig",
    "ItemConnectorsTogglConnectorConfig",
    "ItemConnectorsTwentyConnectorConfig",
    "ItemConnectorsVenmoConnectorConfig",
    "ItemConnectorsVenmoConnectorConfigConfig",
    "ItemConnectorsVenmoConnectorConfigConfigProxy",
    "ItemConnectorsWebhookConnectorConfig",
    "ItemConnectorsWiseConnectorConfig",
    "ItemConnectorsXeroConnectorConfig",
    "ItemConnectorsXeroConnectorConfigConfig",
    "ItemConnectorsXeroConnectorConfigConfigOAuth",
    "ItemConnectorsYodleeConnectorConfig",
    "ItemConnectorsYodleeConnectorConfigConfig",
    "ItemConnectorsYodleeConnectorConfigConfigProxy",
    "ItemConnectorsZohodeskConnectorConfig",
    "ItemConnectorsZohodeskConnectorConfigConfig",
    "ItemConnectorsZohodeskConnectorConfigConfigOAuth",
    "ItemConnectorsGoogledriveConnectorConfig",
    "ItemConnectorsGoogledriveConnectorConfigConfig",
]


class ItemConnectorsAircallConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["aircall"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsAirtableConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["airtable"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsApolloConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["apollo"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsBeancountConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["beancount"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsBrexConnectorConfigConfigOAuth(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ItemConnectorsBrexConnectorConfigConfig(BaseModel):
    apikey_auth: Optional[bool] = FieldInfo(alias="apikeyAuth", default=None)

    oauth: Optional[ItemConnectorsBrexConnectorConfigConfigOAuth] = None


class ItemConnectorsBrexConnectorConfig(BaseModel):
    config: ItemConnectorsBrexConnectorConfigConfig

    connector_name: Literal["brex"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsCodaConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["coda"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsConfluenceConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsConfluenceConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsConfluenceConnectorConfigConfigOAuth


class ItemConnectorsConfluenceConnectorConfig(BaseModel):
    config: ItemConnectorsConfluenceConnectorConfigConfig

    connector_name: Literal["confluence"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsDebugConnectorConfig(BaseModel):
    connector_name: Literal["debug"]

    id: Optional[str] = None

    config: Optional[object] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsDiscordConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsDiscordConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsDiscordConnectorConfigConfigOAuth


class ItemConnectorsDiscordConnectorConfig(BaseModel):
    config: ItemConnectorsDiscordConnectorConfigConfig

    connector_name: Literal["discord"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsFinchConnectorConfigConfig(BaseModel):
    client_id: str

    client_secret: str

    products: List[
        Literal["company", "directory", "individual", "ssn", "employment", "payment", "pay_statement", "benefits"]
    ]

    api_version: Optional[str] = None


class ItemConnectorsFinchConnectorConfig(BaseModel):
    config: ItemConnectorsFinchConnectorConfigConfig

    connector_name: Literal["finch"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsFirebaseConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["firebase"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsForeceiptConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["foreceipt"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsFsConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["fs"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsGitHubConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsGitHubConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsGitHubConnectorConfigConfigOAuth


class ItemConnectorsGitHubConnectorConfig(BaseModel):
    config: ItemConnectorsGitHubConnectorConfigConfig

    connector_name: Literal["github"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsGongConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsGongConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsGongConnectorConfigConfigOAuth


class ItemConnectorsGongConnectorConfig(BaseModel):
    config: ItemConnectorsGongConnectorConfigConfig

    connector_name: Literal["gong"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsGoogleConnectorConfigConfigIntegrationsCalendar(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ItemConnectorsGoogleConnectorConfigConfigIntegrationsDocs(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ItemConnectorsGoogleConnectorConfigConfigIntegrationsDrive(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ItemConnectorsGoogleConnectorConfigConfigIntegrationsGmail(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ItemConnectorsGoogleConnectorConfigConfigIntegrationsSheets(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ItemConnectorsGoogleConnectorConfigConfigIntegrationsSlides(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ItemConnectorsGoogleConnectorConfigConfigIntegrations(BaseModel):
    calendar: Optional[ItemConnectorsGoogleConnectorConfigConfigIntegrationsCalendar] = None

    docs: Optional[ItemConnectorsGoogleConnectorConfigConfigIntegrationsDocs] = None

    drive: Optional[ItemConnectorsGoogleConnectorConfigConfigIntegrationsDrive] = None

    gmail: Optional[ItemConnectorsGoogleConnectorConfigConfigIntegrationsGmail] = None

    sheets: Optional[ItemConnectorsGoogleConnectorConfigConfigIntegrationsSheets] = None

    slides: Optional[ItemConnectorsGoogleConnectorConfigConfigIntegrationsSlides] = None


class ItemConnectorsGoogleConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsGoogleConnectorConfigConfig(BaseModel):
    integrations: ItemConnectorsGoogleConnectorConfigConfigIntegrations

    oauth: ItemConnectorsGoogleConnectorConfigConfigOAuth


class ItemConnectorsGoogleConnectorConfig(BaseModel):
    config: ItemConnectorsGoogleConnectorConfigConfig

    connector_name: Literal["google"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsGreenhouseConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["greenhouse"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsHeronConnectorConfigConfig(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ItemConnectorsHeronConnectorConfig(BaseModel):
    config: ItemConnectorsHeronConnectorConfigConfig

    connector_name: Literal["heron"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsHubspotConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsHubspotConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsHubspotConnectorConfigConfigOAuth


class ItemConnectorsHubspotConnectorConfig(BaseModel):
    config: ItemConnectorsHubspotConnectorConfigConfig

    connector_name: Literal["hubspot"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsIntercomConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsIntercomConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsIntercomConnectorConfigConfigOAuth


class ItemConnectorsIntercomConnectorConfig(BaseModel):
    config: ItemConnectorsIntercomConnectorConfigConfig

    connector_name: Literal["intercom"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsJiraConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsJiraConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsJiraConnectorConfigConfigOAuth


class ItemConnectorsJiraConnectorConfig(BaseModel):
    config: ItemConnectorsJiraConnectorConfigConfig

    connector_name: Literal["jira"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsKustomerConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsKustomerConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsKustomerConnectorConfigConfigOAuth


class ItemConnectorsKustomerConnectorConfig(BaseModel):
    config: ItemConnectorsKustomerConnectorConfigConfig

    connector_name: Literal["kustomer"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsLeverConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsLeverConnectorConfigConfig(BaseModel):
    env_name: Literal["sandbox", "production"] = FieldInfo(alias="envName")

    oauth: ItemConnectorsLeverConnectorConfigConfigOAuth


class ItemConnectorsLeverConnectorConfig(BaseModel):
    config: ItemConnectorsLeverConnectorConfigConfig

    connector_name: Literal["lever"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsLinearConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsLinearConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsLinearConnectorConfigConfigOAuth


class ItemConnectorsLinearConnectorConfig(BaseModel):
    config: ItemConnectorsLinearConnectorConfigConfig

    connector_name: Literal["linear"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsLunchmoneyConnectorConfigConfig(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")


class ItemConnectorsLunchmoneyConnectorConfig(BaseModel):
    config: ItemConnectorsLunchmoneyConnectorConfigConfig

    connector_name: Literal["lunchmoney"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsMercuryConnectorConfigConfigOAuth(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ItemConnectorsMercuryConnectorConfigConfig(BaseModel):
    apikey_auth: Optional[bool] = FieldInfo(alias="apikeyAuth", default=None)

    oauth: Optional[ItemConnectorsMercuryConnectorConfigConfigOAuth] = None


class ItemConnectorsMercuryConnectorConfig(BaseModel):
    config: ItemConnectorsMercuryConnectorConfigConfig

    connector_name: Literal["mercury"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsMergeConnectorConfigConfig(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ItemConnectorsMergeConnectorConfig(BaseModel):
    config: ItemConnectorsMergeConnectorConfigConfig

    connector_name: Literal["merge"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsMicrosoftConnectorConfigConfigIntegrationsOutlook(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ItemConnectorsMicrosoftConnectorConfigConfigIntegrationsSharepoint(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ItemConnectorsMicrosoftConnectorConfigConfigIntegrationsTeams(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ItemConnectorsMicrosoftConnectorConfigConfigIntegrations(BaseModel):
    outlook: Optional[ItemConnectorsMicrosoftConnectorConfigConfigIntegrationsOutlook] = None

    sharepoint: Optional[ItemConnectorsMicrosoftConnectorConfigConfigIntegrationsSharepoint] = None

    teams: Optional[ItemConnectorsMicrosoftConnectorConfigConfigIntegrationsTeams] = None


class ItemConnectorsMicrosoftConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsMicrosoftConnectorConfigConfig(BaseModel):
    integrations: ItemConnectorsMicrosoftConnectorConfigConfigIntegrations

    oauth: ItemConnectorsMicrosoftConnectorConfigConfigOAuth


class ItemConnectorsMicrosoftConnectorConfig(BaseModel):
    config: ItemConnectorsMicrosoftConnectorConfigConfig

    connector_name: Literal["microsoft"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsMongoDBConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["mongodb"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsMootaConnectorConfigConfig(BaseModel):
    token: str


class ItemConnectorsMootaConnectorConfig(BaseModel):
    config: ItemConnectorsMootaConnectorConfigConfig

    connector_name: Literal["moota"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsOnebrickConnectorConfigConfig(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")

    env_name: Literal["sandbox", "production"] = FieldInfo(alias="envName")

    public_token: str = FieldInfo(alias="publicToken")

    access_token: Optional[str] = FieldInfo(alias="accessToken", default=None)

    redirect_url: Optional[str] = FieldInfo(alias="redirectUrl", default=None)


class ItemConnectorsOnebrickConnectorConfig(BaseModel):
    config: ItemConnectorsOnebrickConnectorConfigConfig

    connector_name: Literal["onebrick"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsOutreachConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsOutreachConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsOutreachConnectorConfigConfigOAuth


class ItemConnectorsOutreachConnectorConfig(BaseModel):
    config: ItemConnectorsOutreachConnectorConfigConfig

    connector_name: Literal["outreach"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsPipedriveConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsPipedriveConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsPipedriveConnectorConfigConfigOAuth


class ItemConnectorsPipedriveConnectorConfig(BaseModel):
    config: ItemConnectorsPipedriveConnectorConfigConfig

    connector_name: Literal["pipedrive"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsPlaidConnectorConfigConfigCredentials(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ItemConnectorsPlaidConnectorConfigConfig(BaseModel):
    client_name: str = FieldInfo(alias="clientName")

    country_codes: List[
        Literal["US", "GB", "ES", "NL", "FR", "IE", "CA", "DE", "IT", "PL", "DK", "NO", "SE", "EE", "LT", "LV"]
    ] = FieldInfo(alias="countryCodes")

    env_name: Literal["sandbox", "development", "production"] = FieldInfo(alias="envName")

    language: Literal["en", "fr", "es", "nl", "de"]

    products: List[
        Literal[
            "assets",
            "auth",
            "balance",
            "identity",
            "investments",
            "liabilities",
            "payment_initiation",
            "identity_verification",
            "transactions",
            "credit_details",
            "income",
            "income_verification",
            "deposit_switch",
            "standing_orders",
            "transfer",
            "employment",
            "recurring_transactions",
        ]
    ]

    credentials: Optional[ItemConnectorsPlaidConnectorConfigConfigCredentials] = None


class ItemConnectorsPlaidConnectorConfig(BaseModel):
    config: ItemConnectorsPlaidConnectorConfigConfig

    connector_name: Literal["plaid"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsPostgresConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["postgres"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsQboConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsQboConnectorConfigConfig(BaseModel):
    env_name: Literal["sandbox", "production"] = FieldInfo(alias="envName")

    oauth: ItemConnectorsQboConnectorConfigConfigOAuth

    url: Optional[str] = None

    verifier_token: Optional[str] = FieldInfo(alias="verifierToken", default=None)


class ItemConnectorsQboConnectorConfig(BaseModel):
    config: ItemConnectorsQboConnectorConfigConfig

    connector_name: Literal["qbo"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsRampConnectorConfigConfigOAuth(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ItemConnectorsRampConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsRampConnectorConfigConfigOAuth


class ItemConnectorsRampConnectorConfig(BaseModel):
    config: ItemConnectorsRampConnectorConfigConfig

    connector_name: Literal["ramp"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsRevertConnectorConfigConfig(BaseModel):
    api_token: str

    api_version: Optional[str] = None


class ItemConnectorsRevertConnectorConfig(BaseModel):
    config: ItemConnectorsRevertConnectorConfigConfig

    connector_name: Literal["revert"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsSalesforceConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsSalesforceConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsSalesforceConnectorConfigConfigOAuth


class ItemConnectorsSalesforceConnectorConfig(BaseModel):
    config: ItemConnectorsSalesforceConnectorConfigConfig

    connector_name: Literal["salesforce"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsSalesloftConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsSalesloftConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsSalesloftConnectorConfigConfigOAuth


class ItemConnectorsSalesloftConnectorConfig(BaseModel):
    config: ItemConnectorsSalesloftConnectorConfigConfig

    connector_name: Literal["salesloft"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsSaltedgeConnectorConfigConfig(BaseModel):
    app_id: str = FieldInfo(alias="appId")

    secret: str

    url: Optional[str] = None


class ItemConnectorsSaltedgeConnectorConfig(BaseModel):
    config: ItemConnectorsSaltedgeConnectorConfigConfig

    connector_name: Literal["saltedge"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsSlackConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsSlackConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsSlackConnectorConfigConfigOAuth


class ItemConnectorsSlackConnectorConfig(BaseModel):
    config: ItemConnectorsSlackConnectorConfigConfig

    connector_name: Literal["slack"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsSplitwiseConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["splitwise"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsSpreadsheetConnectorConfigConfig(BaseModel):
    enabled_presets: Optional[
        List[
            Literal[
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
        ]
    ] = FieldInfo(alias="enabledPresets", default=None)

    source_providers: Optional[List[object]] = FieldInfo(alias="sourceProviders", default=None)


class ItemConnectorsSpreadsheetConnectorConfig(BaseModel):
    connector_name: Literal["spreadsheet"]

    id: Optional[str] = None

    config: Optional[ItemConnectorsSpreadsheetConnectorConfigConfig] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsStripeConnectorConfigConfigOAuth(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ItemConnectorsStripeConnectorConfigConfig(BaseModel):
    apikey_auth: Optional[bool] = FieldInfo(alias="apikeyAuth", default=None)

    oauth: Optional[ItemConnectorsStripeConnectorConfigConfigOAuth] = None


class ItemConnectorsStripeConnectorConfig(BaseModel):
    config: ItemConnectorsStripeConnectorConfigConfig

    connector_name: Literal["stripe"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsTellerConnectorConfigConfig(BaseModel):
    application_id: str = FieldInfo(alias="applicationId")

    token: Optional[str] = None


class ItemConnectorsTellerConnectorConfig(BaseModel):
    config: ItemConnectorsTellerConnectorConfigConfig

    connector_name: Literal["teller"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsTogglConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["toggl"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsTwentyConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["twenty"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsVenmoConnectorConfigConfigProxy(BaseModel):
    cert: str

    url: str


class ItemConnectorsVenmoConnectorConfigConfig(BaseModel):
    proxy: Optional[ItemConnectorsVenmoConnectorConfigConfigProxy] = None

    v1_base_url: Optional[str] = FieldInfo(alias="v1BaseURL", default=None)

    v5_base_url: Optional[str] = FieldInfo(alias="v5BaseURL", default=None)


class ItemConnectorsVenmoConnectorConfig(BaseModel):
    config: ItemConnectorsVenmoConnectorConfigConfig

    connector_name: Literal["venmo"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsWebhookConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["webhook"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsWiseConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["wise"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsXeroConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsXeroConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsXeroConnectorConfigConfigOAuth


class ItemConnectorsXeroConnectorConfig(BaseModel):
    config: ItemConnectorsXeroConnectorConfigConfig

    connector_name: Literal["xero"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsYodleeConnectorConfigConfigProxy(BaseModel):
    cert: str

    url: str


class ItemConnectorsYodleeConnectorConfigConfig(BaseModel):
    admin_login_name: str = FieldInfo(alias="adminLoginName")

    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")

    env_name: Literal["sandbox", "development", "production"] = FieldInfo(alias="envName")

    proxy: Optional[ItemConnectorsYodleeConnectorConfigConfigProxy] = None

    sandbox_login_name: Optional[str] = FieldInfo(alias="sandboxLoginName", default=None)


class ItemConnectorsYodleeConnectorConfig(BaseModel):
    config: ItemConnectorsYodleeConnectorConfigConfig

    connector_name: Literal["yodlee"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsZohodeskConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ItemConnectorsZohodeskConnectorConfigConfig(BaseModel):
    oauth: ItemConnectorsZohodeskConnectorConfigConfigOAuth


class ItemConnectorsZohodeskConnectorConfig(BaseModel):
    config: ItemConnectorsZohodeskConnectorConfigConfig

    connector_name: Literal["zohodesk"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ItemConnectorsGoogledriveConnectorConfigConfig(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[List[str]] = None


class ItemConnectorsGoogledriveConnectorConfig(BaseModel):
    config: ItemConnectorsGoogledriveConnectorConfigConfig

    connector_name: Literal["googledrive"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


Item: TypeAlias = Union[
    ItemConnectorsAircallConnectorConfig,
    ItemConnectorsAirtableConnectorConfig,
    ItemConnectorsApolloConnectorConfig,
    ItemConnectorsBeancountConnectorConfig,
    ItemConnectorsBrexConnectorConfig,
    ItemConnectorsCodaConnectorConfig,
    ItemConnectorsConfluenceConnectorConfig,
    ItemConnectorsDebugConnectorConfig,
    ItemConnectorsDiscordConnectorConfig,
    ItemConnectorsFinchConnectorConfig,
    ItemConnectorsFirebaseConnectorConfig,
    ItemConnectorsForeceiptConnectorConfig,
    ItemConnectorsFsConnectorConfig,
    ItemConnectorsGitHubConnectorConfig,
    ItemConnectorsGongConnectorConfig,
    ItemConnectorsGoogleConnectorConfig,
    ItemConnectorsGreenhouseConnectorConfig,
    ItemConnectorsHeronConnectorConfig,
    ItemConnectorsHubspotConnectorConfig,
    ItemConnectorsIntercomConnectorConfig,
    ItemConnectorsJiraConnectorConfig,
    ItemConnectorsKustomerConnectorConfig,
    ItemConnectorsLeverConnectorConfig,
    ItemConnectorsLinearConnectorConfig,
    ItemConnectorsLunchmoneyConnectorConfig,
    ItemConnectorsMercuryConnectorConfig,
    ItemConnectorsMergeConnectorConfig,
    ItemConnectorsMicrosoftConnectorConfig,
    ItemConnectorsMongoDBConnectorConfig,
    ItemConnectorsMootaConnectorConfig,
    ItemConnectorsOnebrickConnectorConfig,
    ItemConnectorsOutreachConnectorConfig,
    ItemConnectorsPipedriveConnectorConfig,
    ItemConnectorsPlaidConnectorConfig,
    ItemConnectorsPostgresConnectorConfig,
    ItemConnectorsQboConnectorConfig,
    ItemConnectorsRampConnectorConfig,
    ItemConnectorsRevertConnectorConfig,
    ItemConnectorsSalesforceConnectorConfig,
    ItemConnectorsSalesloftConnectorConfig,
    ItemConnectorsSaltedgeConnectorConfig,
    ItemConnectorsSlackConnectorConfig,
    ItemConnectorsSplitwiseConnectorConfig,
    ItemConnectorsSpreadsheetConnectorConfig,
    ItemConnectorsStripeConnectorConfig,
    ItemConnectorsTellerConnectorConfig,
    ItemConnectorsTogglConnectorConfig,
    ItemConnectorsTwentyConnectorConfig,
    ItemConnectorsVenmoConnectorConfig,
    ItemConnectorsWebhookConnectorConfig,
    ItemConnectorsWiseConnectorConfig,
    ItemConnectorsXeroConnectorConfig,
    ItemConnectorsYodleeConnectorConfig,
    ItemConnectorsZohodeskConnectorConfig,
    ItemConnectorsGoogledriveConnectorConfig,
]


class ListConnectionConfigsResponse(BaseModel):
    items: List[Item]

    limit: int

    offset: int

    total: float

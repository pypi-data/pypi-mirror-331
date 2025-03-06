# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "ListConnectionConfigsResponse",
    "ConnectorsAircallConnectorConfig",
    "ConnectorsAirtableConnectorConfig",
    "ConnectorsApolloConnectorConfig",
    "ConnectorsBeancountConnectorConfig",
    "ConnectorsBrexConnectorConfig",
    "ConnectorsBrexConnectorConfigConfig",
    "ConnectorsBrexConnectorConfigConfigOAuth",
    "ConnectorsCodaConnectorConfig",
    "ConnectorsConfluenceConnectorConfig",
    "ConnectorsConfluenceConnectorConfigConfig",
    "ConnectorsConfluenceConnectorConfigConfigOAuth",
    "ConnectorsDebugConnectorConfig",
    "ConnectorsDiscordConnectorConfig",
    "ConnectorsDiscordConnectorConfigConfig",
    "ConnectorsDiscordConnectorConfigConfigOAuth",
    "ConnectorsFinchConnectorConfig",
    "ConnectorsFinchConnectorConfigConfig",
    "ConnectorsFirebaseConnectorConfig",
    "ConnectorsForeceiptConnectorConfig",
    "ConnectorsFsConnectorConfig",
    "ConnectorsGitHubConnectorConfig",
    "ConnectorsGitHubConnectorConfigConfig",
    "ConnectorsGitHubConnectorConfigConfigOAuth",
    "ConnectorsGongConnectorConfig",
    "ConnectorsGongConnectorConfigConfig",
    "ConnectorsGongConnectorConfigConfigOAuth",
    "ConnectorsGoogleConnectorConfig",
    "ConnectorsGoogleConnectorConfigConfig",
    "ConnectorsGoogleConnectorConfigConfigIntegrations",
    "ConnectorsGoogleConnectorConfigConfigIntegrationsCalendar",
    "ConnectorsGoogleConnectorConfigConfigIntegrationsDocs",
    "ConnectorsGoogleConnectorConfigConfigIntegrationsDrive",
    "ConnectorsGoogleConnectorConfigConfigIntegrationsGmail",
    "ConnectorsGoogleConnectorConfigConfigIntegrationsSheets",
    "ConnectorsGoogleConnectorConfigConfigIntegrationsSlides",
    "ConnectorsGoogleConnectorConfigConfigOAuth",
    "ConnectorsGreenhouseConnectorConfig",
    "ConnectorsHeronConnectorConfig",
    "ConnectorsHeronConnectorConfigConfig",
    "ConnectorsHubspotConnectorConfig",
    "ConnectorsHubspotConnectorConfigConfig",
    "ConnectorsHubspotConnectorConfigConfigOAuth",
    "ConnectorsIntercomConnectorConfig",
    "ConnectorsIntercomConnectorConfigConfig",
    "ConnectorsIntercomConnectorConfigConfigOAuth",
    "ConnectorsJiraConnectorConfig",
    "ConnectorsJiraConnectorConfigConfig",
    "ConnectorsJiraConnectorConfigConfigOAuth",
    "ConnectorsKustomerConnectorConfig",
    "ConnectorsKustomerConnectorConfigConfig",
    "ConnectorsKustomerConnectorConfigConfigOAuth",
    "ConnectorsLeverConnectorConfig",
    "ConnectorsLeverConnectorConfigConfig",
    "ConnectorsLeverConnectorConfigConfigOAuth",
    "ConnectorsLinearConnectorConfig",
    "ConnectorsLinearConnectorConfigConfig",
    "ConnectorsLinearConnectorConfigConfigOAuth",
    "ConnectorsLunchmoneyConnectorConfig",
    "ConnectorsLunchmoneyConnectorConfigConfig",
    "ConnectorsMercuryConnectorConfig",
    "ConnectorsMercuryConnectorConfigConfig",
    "ConnectorsMercuryConnectorConfigConfigOAuth",
    "ConnectorsMergeConnectorConfig",
    "ConnectorsMergeConnectorConfigConfig",
    "ConnectorsMicrosoftConnectorConfig",
    "ConnectorsMicrosoftConnectorConfigConfig",
    "ConnectorsMicrosoftConnectorConfigConfigIntegrations",
    "ConnectorsMicrosoftConnectorConfigConfigIntegrationsOutlook",
    "ConnectorsMicrosoftConnectorConfigConfigIntegrationsSharepoint",
    "ConnectorsMicrosoftConnectorConfigConfigIntegrationsTeams",
    "ConnectorsMicrosoftConnectorConfigConfigOAuth",
    "ConnectorsMongoDBConnectorConfig",
    "ConnectorsMootaConnectorConfig",
    "ConnectorsMootaConnectorConfigConfig",
    "ConnectorsOnebrickConnectorConfig",
    "ConnectorsOnebrickConnectorConfigConfig",
    "ConnectorsOutreachConnectorConfig",
    "ConnectorsOutreachConnectorConfigConfig",
    "ConnectorsOutreachConnectorConfigConfigOAuth",
    "ConnectorsPipedriveConnectorConfig",
    "ConnectorsPipedriveConnectorConfigConfig",
    "ConnectorsPipedriveConnectorConfigConfigOAuth",
    "ConnectorsPlaidConnectorConfig",
    "ConnectorsPlaidConnectorConfigConfig",
    "ConnectorsPlaidConnectorConfigConfigCredentials",
    "ConnectorsPostgresConnectorConfig",
    "ConnectorsQboConnectorConfig",
    "ConnectorsQboConnectorConfigConfig",
    "ConnectorsQboConnectorConfigConfigOAuth",
    "ConnectorsRampConnectorConfig",
    "ConnectorsRampConnectorConfigConfig",
    "ConnectorsRampConnectorConfigConfigOAuth",
    "ConnectorsRevertConnectorConfig",
    "ConnectorsRevertConnectorConfigConfig",
    "ConnectorsSalesforceConnectorConfig",
    "ConnectorsSalesforceConnectorConfigConfig",
    "ConnectorsSalesforceConnectorConfigConfigOAuth",
    "ConnectorsSalesloftConnectorConfig",
    "ConnectorsSalesloftConnectorConfigConfig",
    "ConnectorsSalesloftConnectorConfigConfigOAuth",
    "ConnectorsSaltedgeConnectorConfig",
    "ConnectorsSaltedgeConnectorConfigConfig",
    "ConnectorsSlackConnectorConfig",
    "ConnectorsSlackConnectorConfigConfig",
    "ConnectorsSlackConnectorConfigConfigOAuth",
    "ConnectorsSplitwiseConnectorConfig",
    "ConnectorsSpreadsheetConnectorConfig",
    "ConnectorsSpreadsheetConnectorConfigConfig",
    "ConnectorsStripeConnectorConfig",
    "ConnectorsStripeConnectorConfigConfig",
    "ConnectorsStripeConnectorConfigConfigOAuth",
    "ConnectorsTellerConnectorConfig",
    "ConnectorsTellerConnectorConfigConfig",
    "ConnectorsTogglConnectorConfig",
    "ConnectorsTwentyConnectorConfig",
    "ConnectorsVenmoConnectorConfig",
    "ConnectorsVenmoConnectorConfigConfig",
    "ConnectorsVenmoConnectorConfigConfigProxy",
    "ConnectorsWebhookConnectorConfig",
    "ConnectorsWiseConnectorConfig",
    "ConnectorsXeroConnectorConfig",
    "ConnectorsXeroConnectorConfigConfig",
    "ConnectorsXeroConnectorConfigConfigOAuth",
    "ConnectorsYodleeConnectorConfig",
    "ConnectorsYodleeConnectorConfigConfig",
    "ConnectorsYodleeConnectorConfigConfigProxy",
    "ConnectorsZohodeskConnectorConfig",
    "ConnectorsZohodeskConnectorConfigConfig",
    "ConnectorsZohodeskConnectorConfigConfigOAuth",
    "ConnectorsGoogledriveConnectorConfig",
    "ConnectorsGoogledriveConnectorConfigConfig",
]


class ConnectorsAircallConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["aircall"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsAirtableConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["airtable"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsApolloConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["apollo"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsBeancountConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["beancount"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsBrexConnectorConfigConfigOAuth(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ConnectorsBrexConnectorConfigConfig(BaseModel):
    apikey_auth: Optional[bool] = FieldInfo(alias="apikeyAuth", default=None)

    oauth: Optional[ConnectorsBrexConnectorConfigConfigOAuth] = None


class ConnectorsBrexConnectorConfig(BaseModel):
    config: ConnectorsBrexConnectorConfigConfig

    connector_name: Literal["brex"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsCodaConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["coda"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsConfluenceConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsConfluenceConnectorConfigConfig(BaseModel):
    oauth: ConnectorsConfluenceConnectorConfigConfigOAuth


class ConnectorsConfluenceConnectorConfig(BaseModel):
    config: ConnectorsConfluenceConnectorConfigConfig

    connector_name: Literal["confluence"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsDebugConnectorConfig(BaseModel):
    connector_name: Literal["debug"]

    id: Optional[str] = None

    config: Optional[object] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsDiscordConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsDiscordConnectorConfigConfig(BaseModel):
    oauth: ConnectorsDiscordConnectorConfigConfigOAuth


class ConnectorsDiscordConnectorConfig(BaseModel):
    config: ConnectorsDiscordConnectorConfigConfig

    connector_name: Literal["discord"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsFinchConnectorConfigConfig(BaseModel):
    client_id: str

    client_secret: str

    products: List[
        Literal["company", "directory", "individual", "ssn", "employment", "payment", "pay_statement", "benefits"]
    ]

    api_version: Optional[str] = None


class ConnectorsFinchConnectorConfig(BaseModel):
    config: ConnectorsFinchConnectorConfigConfig

    connector_name: Literal["finch"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsFirebaseConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["firebase"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsForeceiptConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["foreceipt"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsFsConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["fs"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsGitHubConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsGitHubConnectorConfigConfig(BaseModel):
    oauth: ConnectorsGitHubConnectorConfigConfigOAuth


class ConnectorsGitHubConnectorConfig(BaseModel):
    config: ConnectorsGitHubConnectorConfigConfig

    connector_name: Literal["github"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsGongConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsGongConnectorConfigConfig(BaseModel):
    oauth: ConnectorsGongConnectorConfigConfigOAuth


class ConnectorsGongConnectorConfig(BaseModel):
    config: ConnectorsGongConnectorConfigConfig

    connector_name: Literal["gong"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsGoogleConnectorConfigConfigIntegrationsCalendar(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ConnectorsGoogleConnectorConfigConfigIntegrationsDocs(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ConnectorsGoogleConnectorConfigConfigIntegrationsDrive(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ConnectorsGoogleConnectorConfigConfigIntegrationsGmail(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ConnectorsGoogleConnectorConfigConfigIntegrationsSheets(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ConnectorsGoogleConnectorConfigConfigIntegrationsSlides(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ConnectorsGoogleConnectorConfigConfigIntegrations(BaseModel):
    calendar: Optional[ConnectorsGoogleConnectorConfigConfigIntegrationsCalendar] = None

    docs: Optional[ConnectorsGoogleConnectorConfigConfigIntegrationsDocs] = None

    drive: Optional[ConnectorsGoogleConnectorConfigConfigIntegrationsDrive] = None

    gmail: Optional[ConnectorsGoogleConnectorConfigConfigIntegrationsGmail] = None

    sheets: Optional[ConnectorsGoogleConnectorConfigConfigIntegrationsSheets] = None

    slides: Optional[ConnectorsGoogleConnectorConfigConfigIntegrationsSlides] = None


class ConnectorsGoogleConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsGoogleConnectorConfigConfig(BaseModel):
    integrations: ConnectorsGoogleConnectorConfigConfigIntegrations

    oauth: ConnectorsGoogleConnectorConfigConfigOAuth


class ConnectorsGoogleConnectorConfig(BaseModel):
    config: ConnectorsGoogleConnectorConfigConfig

    connector_name: Literal["google"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsGreenhouseConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["greenhouse"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsHeronConnectorConfigConfig(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ConnectorsHeronConnectorConfig(BaseModel):
    config: ConnectorsHeronConnectorConfigConfig

    connector_name: Literal["heron"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsHubspotConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsHubspotConnectorConfigConfig(BaseModel):
    oauth: ConnectorsHubspotConnectorConfigConfigOAuth


class ConnectorsHubspotConnectorConfig(BaseModel):
    config: ConnectorsHubspotConnectorConfigConfig

    connector_name: Literal["hubspot"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsIntercomConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsIntercomConnectorConfigConfig(BaseModel):
    oauth: ConnectorsIntercomConnectorConfigConfigOAuth


class ConnectorsIntercomConnectorConfig(BaseModel):
    config: ConnectorsIntercomConnectorConfigConfig

    connector_name: Literal["intercom"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsJiraConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsJiraConnectorConfigConfig(BaseModel):
    oauth: ConnectorsJiraConnectorConfigConfigOAuth


class ConnectorsJiraConnectorConfig(BaseModel):
    config: ConnectorsJiraConnectorConfigConfig

    connector_name: Literal["jira"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsKustomerConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsKustomerConnectorConfigConfig(BaseModel):
    oauth: ConnectorsKustomerConnectorConfigConfigOAuth


class ConnectorsKustomerConnectorConfig(BaseModel):
    config: ConnectorsKustomerConnectorConfigConfig

    connector_name: Literal["kustomer"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsLeverConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsLeverConnectorConfigConfig(BaseModel):
    env_name: Literal["sandbox", "production"] = FieldInfo(alias="envName")

    oauth: ConnectorsLeverConnectorConfigConfigOAuth


class ConnectorsLeverConnectorConfig(BaseModel):
    config: ConnectorsLeverConnectorConfigConfig

    connector_name: Literal["lever"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsLinearConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsLinearConnectorConfigConfig(BaseModel):
    oauth: ConnectorsLinearConnectorConfigConfigOAuth


class ConnectorsLinearConnectorConfig(BaseModel):
    config: ConnectorsLinearConnectorConfigConfig

    connector_name: Literal["linear"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsLunchmoneyConnectorConfigConfig(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")


class ConnectorsLunchmoneyConnectorConfig(BaseModel):
    config: ConnectorsLunchmoneyConnectorConfigConfig

    connector_name: Literal["lunchmoney"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsMercuryConnectorConfigConfigOAuth(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ConnectorsMercuryConnectorConfigConfig(BaseModel):
    apikey_auth: Optional[bool] = FieldInfo(alias="apikeyAuth", default=None)

    oauth: Optional[ConnectorsMercuryConnectorConfigConfigOAuth] = None


class ConnectorsMercuryConnectorConfig(BaseModel):
    config: ConnectorsMercuryConnectorConfigConfig

    connector_name: Literal["mercury"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsMergeConnectorConfigConfig(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ConnectorsMergeConnectorConfig(BaseModel):
    config: ConnectorsMergeConnectorConfigConfig

    connector_name: Literal["merge"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsMicrosoftConnectorConfigConfigIntegrationsOutlook(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ConnectorsMicrosoftConnectorConfigConfigIntegrationsSharepoint(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ConnectorsMicrosoftConnectorConfigConfigIntegrationsTeams(BaseModel):
    enabled: Optional[bool] = None

    scopes: Optional[str] = None


class ConnectorsMicrosoftConnectorConfigConfigIntegrations(BaseModel):
    outlook: Optional[ConnectorsMicrosoftConnectorConfigConfigIntegrationsOutlook] = None

    sharepoint: Optional[ConnectorsMicrosoftConnectorConfigConfigIntegrationsSharepoint] = None

    teams: Optional[ConnectorsMicrosoftConnectorConfigConfigIntegrationsTeams] = None


class ConnectorsMicrosoftConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsMicrosoftConnectorConfigConfig(BaseModel):
    integrations: ConnectorsMicrosoftConnectorConfigConfigIntegrations

    oauth: ConnectorsMicrosoftConnectorConfigConfigOAuth


class ConnectorsMicrosoftConnectorConfig(BaseModel):
    config: ConnectorsMicrosoftConnectorConfigConfig

    connector_name: Literal["microsoft"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsMongoDBConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["mongodb"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsMootaConnectorConfigConfig(BaseModel):
    token: str


class ConnectorsMootaConnectorConfig(BaseModel):
    config: ConnectorsMootaConnectorConfigConfig

    connector_name: Literal["moota"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsOnebrickConnectorConfigConfig(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")

    env_name: Literal["sandbox", "production"] = FieldInfo(alias="envName")

    public_token: str = FieldInfo(alias="publicToken")

    access_token: Optional[str] = FieldInfo(alias="accessToken", default=None)

    redirect_url: Optional[str] = FieldInfo(alias="redirectUrl", default=None)


class ConnectorsOnebrickConnectorConfig(BaseModel):
    config: ConnectorsOnebrickConnectorConfigConfig

    connector_name: Literal["onebrick"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsOutreachConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsOutreachConnectorConfigConfig(BaseModel):
    oauth: ConnectorsOutreachConnectorConfigConfigOAuth


class ConnectorsOutreachConnectorConfig(BaseModel):
    config: ConnectorsOutreachConnectorConfigConfig

    connector_name: Literal["outreach"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsPipedriveConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsPipedriveConnectorConfigConfig(BaseModel):
    oauth: ConnectorsPipedriveConnectorConfigConfigOAuth


class ConnectorsPipedriveConnectorConfig(BaseModel):
    config: ConnectorsPipedriveConnectorConfigConfig

    connector_name: Literal["pipedrive"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsPlaidConnectorConfigConfigCredentials(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ConnectorsPlaidConnectorConfigConfig(BaseModel):
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

    credentials: Optional[ConnectorsPlaidConnectorConfigConfigCredentials] = None


class ConnectorsPlaidConnectorConfig(BaseModel):
    config: ConnectorsPlaidConnectorConfigConfig

    connector_name: Literal["plaid"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsPostgresConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["postgres"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsQboConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsQboConnectorConfigConfig(BaseModel):
    env_name: Literal["sandbox", "production"] = FieldInfo(alias="envName")

    oauth: ConnectorsQboConnectorConfigConfigOAuth

    url: Optional[str] = None

    verifier_token: Optional[str] = FieldInfo(alias="verifierToken", default=None)


class ConnectorsQboConnectorConfig(BaseModel):
    config: ConnectorsQboConnectorConfigConfig

    connector_name: Literal["qbo"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsRampConnectorConfigConfigOAuth(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ConnectorsRampConnectorConfigConfig(BaseModel):
    oauth: ConnectorsRampConnectorConfigConfigOAuth


class ConnectorsRampConnectorConfig(BaseModel):
    config: ConnectorsRampConnectorConfigConfig

    connector_name: Literal["ramp"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsRevertConnectorConfigConfig(BaseModel):
    api_token: str

    api_version: Optional[str] = None


class ConnectorsRevertConnectorConfig(BaseModel):
    config: ConnectorsRevertConnectorConfigConfig

    connector_name: Literal["revert"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsSalesforceConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsSalesforceConnectorConfigConfig(BaseModel):
    oauth: ConnectorsSalesforceConnectorConfigConfigOAuth


class ConnectorsSalesforceConnectorConfig(BaseModel):
    config: ConnectorsSalesforceConnectorConfigConfig

    connector_name: Literal["salesforce"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsSalesloftConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsSalesloftConnectorConfigConfig(BaseModel):
    oauth: ConnectorsSalesloftConnectorConfigConfigOAuth


class ConnectorsSalesloftConnectorConfig(BaseModel):
    config: ConnectorsSalesloftConnectorConfigConfig

    connector_name: Literal["salesloft"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsSaltedgeConnectorConfigConfig(BaseModel):
    app_id: str = FieldInfo(alias="appId")

    secret: str

    url: Optional[str] = None


class ConnectorsSaltedgeConnectorConfig(BaseModel):
    config: ConnectorsSaltedgeConnectorConfigConfig

    connector_name: Literal["saltedge"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsSlackConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsSlackConnectorConfigConfig(BaseModel):
    oauth: ConnectorsSlackConnectorConfigConfigOAuth


class ConnectorsSlackConnectorConfig(BaseModel):
    config: ConnectorsSlackConnectorConfigConfig

    connector_name: Literal["slack"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsSplitwiseConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["splitwise"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsSpreadsheetConnectorConfigConfig(BaseModel):
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


class ConnectorsSpreadsheetConnectorConfig(BaseModel):
    connector_name: Literal["spreadsheet"]

    id: Optional[str] = None

    config: Optional[ConnectorsSpreadsheetConnectorConfigConfig] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsStripeConnectorConfigConfigOAuth(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ConnectorsStripeConnectorConfigConfig(BaseModel):
    apikey_auth: Optional[bool] = FieldInfo(alias="apikeyAuth", default=None)

    oauth: Optional[ConnectorsStripeConnectorConfigConfigOAuth] = None


class ConnectorsStripeConnectorConfig(BaseModel):
    config: ConnectorsStripeConnectorConfigConfig

    connector_name: Literal["stripe"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsTellerConnectorConfigConfig(BaseModel):
    application_id: str = FieldInfo(alias="applicationId")

    token: Optional[str] = None


class ConnectorsTellerConnectorConfig(BaseModel):
    config: ConnectorsTellerConnectorConfigConfig

    connector_name: Literal["teller"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsTogglConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["toggl"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsTwentyConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["twenty"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsVenmoConnectorConfigConfigProxy(BaseModel):
    cert: str

    url: str


class ConnectorsVenmoConnectorConfigConfig(BaseModel):
    proxy: Optional[ConnectorsVenmoConnectorConfigConfigProxy] = None

    v1_base_url: Optional[str] = FieldInfo(alias="v1BaseURL", default=None)

    v5_base_url: Optional[str] = FieldInfo(alias="v5BaseURL", default=None)


class ConnectorsVenmoConnectorConfig(BaseModel):
    config: ConnectorsVenmoConnectorConfigConfig

    connector_name: Literal["venmo"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsWebhookConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["webhook"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsWiseConnectorConfig(BaseModel):
    config: None

    connector_name: Literal["wise"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsXeroConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsXeroConnectorConfigConfig(BaseModel):
    oauth: ConnectorsXeroConnectorConfigConfigOAuth


class ConnectorsXeroConnectorConfig(BaseModel):
    config: ConnectorsXeroConnectorConfigConfig

    connector_name: Literal["xero"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsYodleeConnectorConfigConfigProxy(BaseModel):
    cert: str

    url: str


class ConnectorsYodleeConnectorConfigConfig(BaseModel):
    admin_login_name: str = FieldInfo(alias="adminLoginName")

    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")

    env_name: Literal["sandbox", "development", "production"] = FieldInfo(alias="envName")

    proxy: Optional[ConnectorsYodleeConnectorConfigConfigProxy] = None

    sandbox_login_name: Optional[str] = FieldInfo(alias="sandboxLoginName", default=None)


class ConnectorsYodleeConnectorConfig(BaseModel):
    config: ConnectorsYodleeConnectorConfigConfig

    connector_name: Literal["yodlee"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsZohodeskConnectorConfigConfigOAuth(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[str] = None


class ConnectorsZohodeskConnectorConfigConfig(BaseModel):
    oauth: ConnectorsZohodeskConnectorConfigConfigOAuth


class ConnectorsZohodeskConnectorConfig(BaseModel):
    config: ConnectorsZohodeskConnectorConfigConfig

    connector_name: Literal["zohodesk"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


class ConnectorsGoogledriveConnectorConfigConfig(BaseModel):
    client_id: str

    client_secret: str

    scopes: Optional[List[str]] = None


class ConnectorsGoogledriveConnectorConfig(BaseModel):
    config: ConnectorsGoogledriveConnectorConfigConfig

    connector_name: Literal["googledrive"]

    id: Optional[str] = None

    created_at: Optional[datetime] = None

    org_id: Optional[str] = None

    updated_at: Optional[datetime] = None


ListConnectionConfigsResponse: TypeAlias = Union[
    ConnectorsAircallConnectorConfig,
    ConnectorsAirtableConnectorConfig,
    ConnectorsApolloConnectorConfig,
    ConnectorsBeancountConnectorConfig,
    ConnectorsBrexConnectorConfig,
    ConnectorsCodaConnectorConfig,
    ConnectorsConfluenceConnectorConfig,
    ConnectorsDebugConnectorConfig,
    ConnectorsDiscordConnectorConfig,
    ConnectorsFinchConnectorConfig,
    ConnectorsFirebaseConnectorConfig,
    ConnectorsForeceiptConnectorConfig,
    ConnectorsFsConnectorConfig,
    ConnectorsGitHubConnectorConfig,
    ConnectorsGongConnectorConfig,
    ConnectorsGoogleConnectorConfig,
    ConnectorsGreenhouseConnectorConfig,
    ConnectorsHeronConnectorConfig,
    ConnectorsHubspotConnectorConfig,
    ConnectorsIntercomConnectorConfig,
    ConnectorsJiraConnectorConfig,
    ConnectorsKustomerConnectorConfig,
    ConnectorsLeverConnectorConfig,
    ConnectorsLinearConnectorConfig,
    ConnectorsLunchmoneyConnectorConfig,
    ConnectorsMercuryConnectorConfig,
    ConnectorsMergeConnectorConfig,
    ConnectorsMicrosoftConnectorConfig,
    ConnectorsMongoDBConnectorConfig,
    ConnectorsMootaConnectorConfig,
    ConnectorsOnebrickConnectorConfig,
    ConnectorsOutreachConnectorConfig,
    ConnectorsPipedriveConnectorConfig,
    ConnectorsPlaidConnectorConfig,
    ConnectorsPostgresConnectorConfig,
    ConnectorsQboConnectorConfig,
    ConnectorsRampConnectorConfig,
    ConnectorsRevertConnectorConfig,
    ConnectorsSalesforceConnectorConfig,
    ConnectorsSalesloftConnectorConfig,
    ConnectorsSaltedgeConnectorConfig,
    ConnectorsSlackConnectorConfig,
    ConnectorsSplitwiseConnectorConfig,
    ConnectorsSpreadsheetConnectorConfig,
    ConnectorsStripeConnectorConfig,
    ConnectorsTellerConnectorConfig,
    ConnectorsTogglConnectorConfig,
    ConnectorsTwentyConnectorConfig,
    ConnectorsVenmoConnectorConfig,
    ConnectorsWebhookConnectorConfig,
    ConnectorsWiseConnectorConfig,
    ConnectorsXeroConnectorConfig,
    ConnectorsYodleeConnectorConfig,
    ConnectorsZohodeskConnectorConfig,
    ConnectorsGoogledriveConnectorConfig,
]

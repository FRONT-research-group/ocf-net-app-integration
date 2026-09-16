import os
from opencapif_sdk import capif_provider_connector, api_schema_translator
import re

#API_HOST = os.getenv('API_HOST', '10.220.2.43')
PROVIDER_API_HOST = os.getenv('PROVIDER_API_HOST', '127.0.0.1')
PROVIDER_API_PORT = os.getenv('PROVIDER_API_PORT', '8001')
PROVIDER_API_SCHEME=os.getenv("PROVIDER_API_SCHEME", "https")
PROVIDER_API_BASE_PATH = os.getenv("PROVIDER_API_BASE_PATH", "/provider-app/v1")
PROVIDER_CONFIG_FILE = os.getenv('PROVIDER_CONFIG_FILE', './provider_config_sample.json')
PROVIDER_OPENAPI_FILE = os.getenv('PROVIDER_OPENAPI_FILE', './openapi.yaml')
PROVIDER_API_DESC_FILE = os.getenv('PROVIDER_API_DESC_FILE', './provider-api-description.json') # should match the prefix of the URL
#API_DESC_FILE = os.getenv('API_DESC_FILE', './provider-app.json') # should match the prefix of the URL
PROVIDER_SUPPORTED_FEATURES=os.getenv("PROVIDER_SUPPORTED_FEATURES","0")
API_URL = f"{PROVIDER_API_SCHEME}://{PROVIDER_API_HOST}:{PROVIDER_API_PORT}{PROVIDER_API_BASE_PATH}"
#API_URL = f"https://{API_HOST}:{API_PORT}/provider-app/v1"
PROVIDER_AEF_NAMES = os.getenv("PROVIDER_AEF_NAMES", "").strip()

def _natural_key(name: str):
    """sot aef names"""
    return[
        int(part) if part.isdigit() else part
        for part in re.split(r"(\d+)", name)
    ]
def _parse_csv_env(value: str)->list[str]:
    return[item.strip() for item in value.split(",") if item.strip()]
def _get_aef_ids(provider_capif_ids: dict, requested_aef_names: list[str] | None=None)->list[str]:
    available_aefs={
        name: capif_id
        for name, capif_id in provider_capif_ids.items()
        if name.startswith("AEF-")
    }
    if not available_aefs:
        raise RuntimeError("No AEF IDs were returned")
    if requested_aef_names:
        missing=[
            name for name in requested_aef_names
            if name not in available_aefs
        ]
        if missing:
            raise RuntimeError(f"No AEF names were returned from CAPIF. Available AEFs: {available_aefs}")
        return [available_aefs[name] for name in requested_aef_names]
    return [
        available_aefs[name]
        for name in sorted(available_aefs.keys(), key=_natural_key)
    ]
def showcase_capif_nef_connector_publish():
    """
    Demonstrates the process of onboarding a provider and publishing services to CAPIF NEF.
    This function performs the following steps:
    1. Initializes the CAPIF provider connector using the specified configuration file.
    2. Onboards the provider to the CAPIF system.
    3. Translates the OpenAPI schema and builds the API description.
    4. Sets the API description path and retrieves CAPIF IDs for APF and AEF.
    5. Prepares the publish request with APF and AEF IDs, and supported features.
    6. Publishes the provider's services to CAPIF.
    
    Raises:
        Any exceptions raised by the connector or translator methods.
    """

    capif_connector = capif_provider_connector(config_file=PROVIDER_CONFIG_FILE)
    
    capif_connector.onboard_provider()

    translator = api_schema_translator(PROVIDER_OPENAPI_FILE)
    translator.build(API_URL, "0", "0")


    capif_connector.api_description_path = PROVIDER_API_DESC_FILE
    apf = capif_connector.provider_capif_ids["APF-1"]

    #TODO enhancne to support a list of AEFs
    
    request_aef_names=_parse_csv_env(PROVIDER_AEF_NAMES)
    aef_ids=_get_aef_ids(capif_connector.provider_capif_ids, requested_aef_names=request_aef_names,)
    
    #aef = capif_connector.provider_capif_ids["AEF-1"]
    
    capif_connector.publish_req['publisher_apf_id'] = apf
    capif_connector.publish_req['publisher_aefs_ids'] = aef_ids
    capif_connector.supported_features =PROVIDER_SUPPORTED_FEATURES

    capif_connector.publish_services()
    print("Publication of provider's service is completed")

if __name__ == "__main__":
    showcase_capif_nef_connector_publish()

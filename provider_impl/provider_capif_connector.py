import os
from opencapif_sdk import capif_provider_connector, api_schema_translator
# Now import the classes from your sdk.py file

# Get environment variables
API_HOST = os.getenv('API_HOST', '10.220.2.73')
API_PORT = os.getenv('API_PORT', '8000')
CONFIG_FILE = os.getenv('CONFIG_FILE', './provider_config_sample.json')
OPENAPI_FILE = os.getenv('OPENAPI_FILE', './openapi.yaml')
API_DESC_FILE = os.getenv('API_DESC_FILE', './3gpp-monitoring-event.json')

API_URL = "https://{}:{}/3gpp-monitoring-event/v1".format(API_HOST, API_PORT)

capif_connector = capif_provider_connector(config_file=CONFIG_FILE)


def showcase_capif_nef_connector_publish():
    """

    """
    

    capif_connector.onboard_provider()

    print("COMPLETED")


    translator = api_schema_translator(OPENAPI_FILE)
    translator.build(API_URL, "0", "0")


    capif_connector.api_description_path = API_DESC_FILE
    APF = capif_connector.provider_capif_ids["APF-1"]

    #TODO enhancne to support a list of AEFs
    AEF1 = capif_connector.provider_capif_ids["AEF-1"]
    
    capif_connector.publish_req['publisher_apf_id'] = APF
    capif_connector.publish_req['publisher_aefs_ids'] = [AEF1]
    capif_connector.supported_features ="4"

    capif_connector.publish_services()
    print("COMPLETED")






if __name__ == "__main__":
    # Register a NEF to CAPIF. This should happen exactly once
    #showcase_capif_nef_connector_unpublish()
    showcase_capif_nef_connector_publish()

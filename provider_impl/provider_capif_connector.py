import os, argparse
from opencapif_sdk import capif_provider_connector, api_schema_translator


#API_HOST = os.getenv('API_HOST', '10.220.2.43')
API_HOST = os.getenv('API_HOST', '127.0.0.1')
API_PORT = os.getenv('API_PORT', '8000')
CONFIG_FILE = os.getenv('CONFIG_FILE', './provider_config_sample.json')
OPENAPI_FILE = os.getenv('OPENAPI_FILE', './openapi.yaml')
API_DESC_FILE = os.getenv('API_DESC_FILE', './provider-app.json') # should match the prefix of the URL

#API_URL = f"https://{API_HOST}:{API_PORT}/3gpp-monitoring-event/v1"
API_URL = f"https://{API_HOST}:{API_PORT}/provider-app/v1"

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

    parser = argparse.ArgumentParser(description="Argument parser for CAPIF connector")
    
    parser.add_argument("publish", help="Either publish or unpublish the service")

    args = parser.parse_args()
    if args.publish != "publish" and args.publish != "unpublish":
        print("Unknown argument, use 'publish' or 'unpublish'.")
        return
    
    capif_connector = capif_provider_connector(config_file=CONFIG_FILE)

    if args.publish == "unpublish":

        apf = capif_connector.provider_capif_ids["APF-1"]

        #TODO enhancne to support a list of AEFs
        aef = capif_connector.provider_capif_ids["AEF-1"]
        
        capif_connector.publish_req['publisher_apf_id'] = apf
        capif_connector.publish_req['publisher_aefs_ids'] = [aef]
        capif_connector.supported_features ="4"

        capif_connector.unpublish_service()
        print("The unpublish process is completed")
        return
    
    capif_connector.onboard_provider()


    #after build should set the aefId on aef profile of the created_file(e.g. provider-app.json)
    translator = api_schema_translator(OPENAPI_FILE)
    translator.build(API_URL, "0", "0")


    capif_connector.api_description_path = API_DESC_FILE
    apf = capif_connector.provider_capif_ids["APF-1"]

    #TODO enhancne to support a list of AEFs
    aef = capif_connector.provider_capif_ids["AEF-1"]
    
    capif_connector.publish_req['publisher_apf_id'] = apf
    capif_connector.publish_req['publisher_aefs_ids'] = [aef]
    capif_connector.supported_features ="4"

    capif_connector.publish_services()
    print("COMPLETED")

if __name__ == "__main__":
    showcase_capif_nef_connector_publish()

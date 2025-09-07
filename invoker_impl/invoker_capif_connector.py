from opencapif_sdk import capif_invoker_connector,service_discoverer


def write_to_file(filename, content):
    with open(filename, "w") as f:   
        f.write(content)
    print(f"Wrote content to {filename}")

    

def showcase_capif_connector():
    """
        This method showcases how one can use the CAPIFConnector class.
    """

    capif_connector = capif_invoker_connector(config_file="./invoker_config_sample.json")

    capif_connector.onboard_invoker()
    print("COMPLETED")

    discoverer_svc = service_discoverer(config_file="./invoker_config_sample.json")
    discoverer_svc.discover()

    print("COMPLETED")

    discoverer_svc.get_tokens()
    print("COMPLETED")
    jwt_token=discoverer_svc.token

    print("JWT TOKEN: ", jwt_token)

    write_to_file("./invoker_folder/custom_user1/jwt_token.txt", jwt_token)


if __name__ == "__main__":
    # Register invoker to CAPIF. This should happen exactly once
    showcase_capif_connector()

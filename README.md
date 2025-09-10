# OpenCAPIF Authorization Integration Template

This repository provides a **template** for integrating the [OpenCAPIF](https://labs.etsi.org/rep/ocf/capif) framework by the usage of [OpenCAPIF's SDK](https://labs.etsi.org/rep/ocf/sdk) to enable **authorization** for telecom APIs.  

It demonstrates how to onboard and authenticate **Provider** and **Invoker** applications through OpenCAPIF, using **FastAPI** for both service exposure and consumption.  

---

## 🚀 Architecture Overview

The repository includes:

- **Provider App** (`FastAPI`)
  - Publishes a service API via OpenCAPIF.
  - Validates incoming requests using CAPIF-issued certificates and JWT tokens.

- **Invoker App** (`FastAPI`)
  - Discovers and consumes provider's services through OpenCAPIF.
  - Retrieves JWT tokens from CAPIF for authorized requests.

- **Scripts**
  - `provider_capif_connector.py`:  
    Onboards the provider into OpenCAPIF, publishes services, and stores CAPIF’s returned certificate (`capif_cert_server.pem`) inside the `provider_folder/` folder.
  - `invoker_capif_connector.py`:  
    Onboards the invoker into OpenCAPIF, discovers available services, and retrieves a JWT token for consuming provider services that is stored under `invoker_folder/` as `txt`.
  - `user_registration.py`:  
    Registers a new user in OpenCAPIF, enabling the user to act as **provider**, **invoker**, or both.

- **Configuration Files**
  - `<provider/invoker>_config_sample.json`: Input for onboarding scripts (provider/invoker).
  - `capif_sdk_register.json`: Input for user registration.
  - `openapi.yaml`: The OpenAPI specification for the provider app service (used during service publication).

---

## 🔑 Workflow

1. **User Registration**  
   - A user is created in CAPIF using `register_and_login.py` with `capif_sdk_register.json`.  
   - The same user can be both a provider and an invoker depending on configuration.

2. **Provider Onboarding**  
   - The provider is onboarded to CAPIF via `provider_capif_connector.py` using `provider_configuration_sample.json`.  
   - The service is published using the provider's app **OpenAPI YAML schema**.  
   - CAPIF returns `capif_cert_server.pem`, stored under `provider_folder/`, used later for verifying JWT tokens.

3. **Invoker Onboarding & Discovery**  
   - The invoker is onboarded to CAPIF via `invoker_capif_connector.py` using `invoker_configuration_sample.json`.  
   - CAPIF provides service discovery results and returns a **JWT token**.  
   - This token allows the invoker to send **authorized requests** to the provider’s app.

4. **Authorized Communication**  
   - The invoker consumes the provider’s API.  
   - The provider verifies the JWT token against the CAPIF certificate (`capif_cert_server.pem`) to authorize requests.

---

## ⚡ Execution Guide

This section describes how to run the repository step by step.  
Make sure you have a running instance of [OpenCAPIF](https://labs.etsi.org/rep/ocf/capif) and the [OpenCAPIF SDK](https://labs.etsi.org/rep/ocf/sdk) properly configured.

1. **User Registration**

  First, register a new user in OpenCAPIF. This user can later act as a **provider**, **invoker**, or both depending on the configuration.
  ```bash
  python register_and_login.py
  ```
2. **Load Environment Variables**
    
  All environment variables (common to provider and invoker) are stored in the .env file.
  Load them before running the onboarding scripts:
  ```bash
  export $(grep -v '^#' .env | xargs)
  ```
3. **Provider Onboarding & Service Publication**
   
  Onboard the provider into OpenCAPIF and publish its services.
  ```bash
  python provider_capif_connector.py publish
    ```
4. **Invoker Onboarding & Service Discovery**
   
  Onboard the invoker and discover available services.
  ```bash
  python invoker_capif_connector.py
  ```
5. **Start the Provider App**
   
  Run the provider app to expose the published service:
  ```bash
  python -m provider_impl.provider_app.app
  ```
6. **Start the Invoker App**
   
  Finally, run the invoker app to consume the provider’s service with authorized requests:
  ```bash
  python -m invoker_impl.invoker_app.app
  ```

---

## 📊 Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant CAPIF as OpenCAPIF
    participant P as Provider App
    participant I as Invoker App

    U->>CAPIF: Register User (register_and_login.py + capif_sdk_register.json)
    CAPIF-->>U: User registered (can act as Provider/Invoker)

    P->>CAPIF: Onboard & Publish Service (provider_capif_connector.py + provider_configuration_sample.json + openapi.yaml)
    CAPIF-->>P: capif_cert_server.pem (stored under provider_folder/)

    I->>CAPIF: Onboard & Discover Services (invoker_capif_connector.py + invoker_configuration_sample.json)
    CAPIF-->>I: JWT Token + Service Info

    I->>P: Send Request with JWT Token
    P->>CAPIF: Verify JWT Token using capif_cert_server.pem
    P-->>I: Authorized Response

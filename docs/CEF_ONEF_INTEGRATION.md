# CEF + O-NEF CAPIF Integration

## Overview

This repository integrates the CEF CAPIF Provider and Invoker workflows
with O-NEF.

CEF provides the integration layer used to:

1. onboard an API Provider to CAPIF;
2. publish O-NEF northbound service APIs;
3. onboard API Invokers;
4. discover published O-NEF services;
5. establish CAPIF security context;
6. obtain CAPIF access tokens; and
7. invoke O-NEF APIs using CAPIF-issued authorization.

CEF is not required to proxy every O-NEF application request.
The CAPIF control/security workflow is performed through CEF, while the
authorized API request can be sent directly to O-NEF.

## O-NEF provenance

The O-NEF source code is imported under:

    o-nef/

It originates from the FRONT Research Group O-NEF project.

See:

    o-nef/UPSTREAM_IMPORT.md

for the exact upstream repository, branch, commit, tag and import details.

## Architecture

Conceptually:

    O-NEF API
        |
        | publication
        v
    CEF Provider
        |
        v
      CAPIF
        ^
        |
    CEF Invoker
        |
        | discovery + CAPIF token
        v
    API Consumer
        |
        | Authorization: Bearer <CAPIF JWT>
        v
      O-NEF

The CEF Provider represents and publishes the O-NEF northbound APIs to
CAPIF.

The CEF Invoker performs CAPIF onboarding, service discovery, security
context establishment and token retrieval.

## CAPIF-facing O-NEF APIs

The imported O-NEF release exposes two CAPIF-facing northbound API
families that were validated through CEF.

### 1. 3GPP Monitoring Event API

Base API:

    /nef/api/v1/3gpp-monitoring-event/v1

Validated resources:

    GET    /{scsAsId}/subscriptions
    POST   /{scsAsId}/subscriptions
    GET    /{scsAsId}/subscriptions/{subscriptionId}
    PUT    /{scsAsId}/subscriptions/{subscriptionId}
    DELETE /{scsAsId}/subscriptions/{subscriptionId}

### 2. 3GPP As Session with QoS API

Base API:

    /nef/api/v1/3gpp-as-session-with-qos/v1

Validated resources:

    GET    /{scsAsId}/subscriptions
    POST   /{scsAsId}/subscriptions
    GET    /{scsAsId}/subscriptions/{subscriptionId}
    PUT    /{scsAsId}/subscriptions/{subscriptionId}
    DELETE /{scsAsId}/subscriptions/{subscriptionId}

## CEF Provider

The same CEF Provider implementation is used to publish both O-NEF API
families.

Relevant implementation:

    cef/provider/provider_capif_connector.py

The API being published is determined through configuration and the
OpenAPI service description rather than separate API-specific Provider
implementations.

Relevant runtime variables include:

    CAPIF_HOST
    REGISTER_HOST
    CAPIF_REGISTER_PORT
    CAPIF_CA_FILE

    PROVIDER_CONFIG_FILE
    PROVIDER_OPENAPI_FILE
    PROVIDER_API_DESC_FILE

    PROVIDER_API_HOST
    PROVIDER_API_PORT
    PROVIDER_API_SCHEME
    PROVIDER_API_BASE_PATH

Credentials, certificates, generated CAPIF identifiers and runtime
onboarding state must not be committed to Git.

## CEF Invoker

The same CEF Invoker implementation is used for both O-NEF API
families.

Relevant implementation:

    cef/invoker/invoker_capif_connector.py

The workflow is:

    Invoker onboarding
        ->
    service discovery
        ->
    CAPIF security context establishment
        ->
    CAPIF access token retrieval
        ->
    authorized O-NEF API invocation

The discovery filter determines which published O-NEF API is requested.

## O-NEF CAPIF configuration

When CEF manages Provider onboarding and publication, configure O-NEF
with:

    CEF_MANAGES_CAPIF_PROVIDER=true

The CAPIF API names used for authorization must match the names actually
published to CAPIF:

    CAPIF_MONITORING_EVENT_API_NAME=<published-monitoring-api-name>

    CAPIF_SESSION_WITH_QOS_API_NAME=<published-session-with-qos-api-name>

Do not hard-code generated deployment-specific API names in source code.

## CAPIF authorization

O-NEF first verifies the CAPIF JWT cryptographically.

The token scope is then checked against the expected API name.

Conceptually:

    CAPIF JWT
        ->
    signature / expiry validation
        ->
    scope claim
        ->
    expected CAPIF API name
        ->
    allow or HTTP 403

The scope format used by the tested CAPIF deployment contains the
published API name after the final colon:

    <CAPIF-scope-prefix>:<api-name>

Monitoring Event requests are checked against:

    CAPIF_MONITORING_EVENT_API_NAME

Session-with-QoS requests are checked against:

    CAPIF_SESSION_WITH_QOS_API_NAME

A valid CAPIF token issued for another API is rejected with HTTP 403.

## Validation

Both CAPIF-facing API families were tested end-to-end through the same
CEF Provider and Invoker implementations.

| Test | Monitoring Event | Session with QoS |
| --- | --- | --- |
| CEF Provider publication | PASS | PASS |
| CEF Invoker discovery | PASS | PASS |
| CAPIF token issuance | PASS | PASS |
| Missing token rejected | PASS | PASS |
| Invalid token rejected | PASS | PASS |
| Correct API scope accepted | PASS | PASS |
| Wrong API scope rejected | PASS | PASS |
| Cross-API scope isolation | PASS | PASS |
| POST | PASS | PASS |
| GET collection | PASS | PASS |
| GET individual | PASS | PASS |
| PUT | PASS | PASS |
| DELETE | PASS | PASS |
| Persistence | PASS | PASS |
| Asynchronous callback | PASS | PASS |

### Monitoring Event callback validation

A LOCATION_REPORTING subscription was created through the
CAPIF-authorized Monitoring Event API.

O-NEF UE movement triggered the real monitoring logic and O-NEF sent an
asynchronous HTTP notification to the configured callback destination.

### Session-with-QoS callback validation

A GBR Session-with-QoS subscription was created using a CAPIF-authorized
request.

O-NEF UE movement triggered the QoS event handling logic and produced an
asynchronous notification containing a QOS_GUARANTEED event.

## Cross-API authorization

The following authorization matrix was validated:

    Monitoring Event token -> Monitoring Event API    ALLOW
    Monitoring Event token -> Session-with-QoS API    HTTP 403

    Session-with-QoS token -> Session-with-QoS API    ALLOW
    Session-with-QoS token -> Monitoring Event API    HTTP 403

This demonstrates that O-NEF does not merely accept any valid CAPIF
token. The token must also contain the scope for the requested published
API.

## Internal O-NEF APIs

O-NEF also exposes internal management and simulation functionality,
including APIs for UEs, cells, gNBs, paths and UE movement.

These endpoints are not part of the CEF/CAPIF northbound API validation.

For example, the UE movement API was used internally to trigger actual
Monitoring Event and Session-with-QoS callbacks, but it uses O-NEF's
internal authentication rather than a CAPIF service token.

Therefore the supported validation claim is:

    CEF has been validated against all CAPIF-facing northbound API
    families exposed by the imported O-NEF release.

It should not be interpreted as a claim that every internal O-NEF
management endpoint is published through CAPIF.

## Known considerations

- CAPIF API names must be consistent between CEF publication and O-NEF
  scope validation.

- CAPIF access tokens are short-lived and should be refreshed during
  integration tests and demonstrations.

- CEF_MANAGES_CAPIF_PROVIDER=true prevents O-NEF from independently
  performing duplicate Provider onboarding when CEF owns that workflow.

- Runtime-generated JWTs, certificates, private keys, Provider and
  Invoker identifiers, generated CAPIF state and passwords must never be
  committed.

- Session-with-QoS PUT currently populates some Pydantic defaults for
  optional UE identifier fields. This is O-NEF application behavior and
  is independent of the CEF/CAPIF integration.

## Security

Never commit:

    access tokens
    passwords
    private keys
    generated certificates containing private material
    temporary Provider/Invoker runtime folders
    generated CAPIF onboarding state

Use environment variables or local runtime configuration for sensitive
values.

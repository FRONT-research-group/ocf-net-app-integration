*** Settings ***
Library    OperatingSystem
Library    Process
Library    String

*** Variables ***
${REPO_ROOT}                 %{CEF_REPO_ROOT=/home/ubuntu/ocf-net-app-integration}
${PYTHON}                    %{CEF_PYTHON=/home/ubuntu/ocf-net-app-integration/provider_impl/venv/bin/python}
${INVOKER_CONFIG_FILE}       %{INVOKER_CONFIG_FILE=/tmp/cef_invoker_124316.json}

${CAPIF_HOST}                %{CAPIF_HOST=172.21.0.13}
${REGISTER_HOST}             %{REGISTER_HOST=127.0.0.1}
${CAPIF_REGISTER_PORT}       %{CAPIF_REGISTER_PORT=8084}
${CAPIF_GETAUTH_MODE}        %{CAPIF_GETAUTH_MODE=basic_get}
${CAPIF_TLS_VERIFY}          %{CAPIF_TLS_VERIFY=False}
${CAPIF_CA_FILE}             %{CAPIF_CA_FILE=}

${NEF_BASE_URL}              %{NEF_BASE_URL=http://127.0.0.1:8000}
${AF_ID}                     %{NEF_TEST_AF_ID=cef-demo}
${NEF_CONTAINER}             %{NEF_CONTAINER=cef-nef}
${MONGO_CONTAINER}           %{MONGO_CONTAINER=cef-nef-mongo}
${NEF_NETWORK}               %{NEF_NETWORK=nef_nef-network}
${NEF_IMAGE}                 %{NEF_IMAGE=nef-nef}

${CALLBACK_CONTAINER}        %{CALLBACK_CONTAINER=cef-callback-robot}
${CALLBACK_SCRIPT}           ${REPO_ROOT}/tests/robot/resources/callback_receiver.py

${TEST_IMSI}                 %{NEF_TEST_IMSI=001010143245445}
${TEST_MSISDN}               %{NEF_TEST_MSISDN=306912345678}
${TOKEN_FILE}                %{ROBOT_TOKEN_FILE=/tmp/cef_robot_token.txt}
${WRONG_SCOPE_TOKEN_FILE}    %{WRONG_SCOPE_TOKEN_FILE=}

*** Keywords ***
Refresh CAPIF Token
    Remove File    ${TOKEN_FILE}
    ${result}=    Run Process
    ...    ${PYTHON}
    ...    ${REPO_ROOT}/scripts/refresh_capif_token.py
    ...    ${TOKEN_FILE}
    ...    cwd=${REPO_ROOT}
    ...    env:PYTHONPATH=${REPO_ROOT}
    ...    env:INVOKER_CONFIG_FILE=${INVOKER_CONFIG_FILE}
    ...    env:CAPIF_HOST=${CAPIF_HOST}
    ...    env:REGISTER_HOST=${REGISTER_HOST}
    ...    env:CAPIF_REGISTER_PORT=${CAPIF_REGISTER_PORT}
    ...    env:CAPIF_GETAUTH_MODE=${CAPIF_GETAUTH_MODE}
    ...    env:CAPIF_TLS_VERIFY=${CAPIF_TLS_VERIFY}
    ...    env:CAPIF_CA_FILE=${CAPIF_CA_FILE}

    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Token refresh failed.\nSTDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}

    Should Contain    ${result.stderr}    Service APIs successfully discovered
    Should Contain    ${result.stderr}    Security token successfully obtained
    Should Contain    ${result.stdout}    Discovery: OK
    Should Contain    ${result.stdout}    CAPIF JWT: received

    File Should Exist    ${TOKEN_FILE}

Load CAPIF Token
    File Should Exist    ${TOKEN_FILE}

    ${token}=    Get File    ${TOKEN_FILE}
    ${token}=    Strip String    ${token}

    Should Not Be Empty    ${token}

    RETURN    ${token}

GET Subscriptions With Token
    [Arguments]    ${token}

    ${url}=    Set Variable
    ...    ${NEF_BASE_URL}/3gpp-monitoring-event-envelope/v1/${AF_ID}/subscriptions

    ${result}=    Run Process
    ...    curl
    ...    -i
    ...    -sS
    ...    ${url}
    ...    -H
    ...    Authorization: Bearer ${token}

    RETURN    ${result}

GET Subscriptions Without Token
    ${url}=    Set Variable
    ...    ${NEF_BASE_URL}/3gpp-monitoring-event-envelope/v1/${AF_ID}/subscriptions

    ${result}=    Run Process
    ...    curl
    ...    -i
    ...    -sS
    ...    ${url}

    RETURN    ${result}

Seed Demo Location
    ${result}=    Run Process
    ...    python3
    ...    ${REPO_ROOT}/tests/robot/resources/seed_location.py
    ...    --container
    ...    ${MONGO_CONTAINER}
    ...    --imsi
    ...    ${TEST_IMSI}
    ...    --msisdn
    ...    ${TEST_MSISDN}

    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Failed to seed demo location.\nSTDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}

    Should Contain    ${result.stdout}    UELocationTimestamp

Start Callback Receiver
    Run Process
    ...    docker
    ...    rm
    ...    -f
    ...    ${CALLBACK_CONTAINER}

    ${result}=    Run Process
    ...    docker
    ...    run
    ...    -d
    ...    --name
    ...    ${CALLBACK_CONTAINER}
    ...    --network
    ...    ${NEF_NETWORK}
    ...    -v
    ...    ${CALLBACK_SCRIPT}:/tmp/cef_callback_receiver.py:ro
    ...    --entrypoint
    ...    python
    ...    ${NEF_IMAGE}
    ...    -u
    ...    /tmp/cef_callback_receiver.py

    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Could not start callback receiver.\n${result.stderr}

    Wait Until Keyword Succeeds
    ...    10 sec
    ...    1 sec
    ...    Callback Receiver Should Be Ready

Stop Callback Receiver
    Run Process
    ...    docker
    ...    rm
    ...    -f
    ...    ${CALLBACK_CONTAINER}

Callback Receiver Should Be Ready
    ${result}=    Run Process
    ...    docker
    ...    logs
    ...    ${CALLBACK_CONTAINER}

    Should Be Equal As Integers    ${result.rc}    0
    Should Contain    ${result.stdout}    Listening on 0.0.0.0:8001

Get Callback Logs
    ${result}=    Run Process
    ...    docker
    ...    logs
    ...    ${CALLBACK_CONTAINER}

    Should Be Equal As Integers    ${result.rc}    0

    RETURN    ${result.stdout}

Callback Count Should Be
    [Arguments]    ${expected}

    ${logs}=    Get Callback Logs
    ${count}=    Get Count
    ...    ${logs}
    ...    === CALLBACK RECEIVED ===

    Should Be Equal As Integers
    ...    ${count}
    ...    ${expected}

Build Subscription Payload
    ${payload}=    Set Variable    {"msisdn":"${TEST_IMSI}","notificationDestination":"http://${CALLBACK_CONTAINER}:8001/notify","monitoringType":"LOCATION_REPORTING","maximumNumberOfReports":2,"locationType":"CURRENT_LOCATION","repPeriod":{"duration":5}}

    RETURN    ${payload}

Create Authenticated Subscription
    [Arguments]    ${token}

    ${payload}=    Build Subscription Payload

    ${url}=    Set Variable
    ...    ${NEF_BASE_URL}/3gpp-monitoring-event-envelope/v1/${AF_ID}/subscriptions

    ${result}=    Run Process
    ...    curl
    ...    -i
    ...    -sS
    ...    -X
    ...    POST
    ...    ${url}
    ...    -H
    ...    Authorization: Bearer ${token}
    ...    -H
    ...    Content-Type: application/json
    ...    -d
    ...    ${payload}

    RETURN    ${result}

Get NEF Logs
    ${result}=    Run Process
    ...    docker
    ...    logs
    ...    --since
    ...    5m
    ...    ${NEF_CONTAINER}

    Should Be Equal As Integers    ${result.rc}    0

    ${logs}=    Catenate
    ...    SEPARATOR=\n
    ...    ${result.stdout}
    ...    ${result.stderr}

    RETURN    ${logs}

Wait For Two Callbacks
    Wait Until Keyword Succeeds
    ...    20 sec
    ...    1 sec
    ...    Callback Count Should Be
    ...    2

Verify Callback Lifecycle
    ${logs}=    Get Callback Logs

    Should Contain    ${logs}    "cancelInd": false
    Should Contain    ${logs}    "cancelInd": true

    ${count}=    Get Count
    ...    ${logs}
    ...    === CALLBACK RECEIVED ===

    Should Be Equal As Integers    ${count}    2

Verify NEF Authorization And Cleanup
    ${logs}=    Get NEF Logs

    Should Contain    ${logs}    Bearer token received
    Should Contain    ${logs}    CAPIF scope authorization was successful
    Should Contain    ${logs}    Authorization was successful
    Should Contain    ${logs}    This is the last notification
    Should Contain    ${logs}    Subscription
    Should Contain    ${logs}    deleted

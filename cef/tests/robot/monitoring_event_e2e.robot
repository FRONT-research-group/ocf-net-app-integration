*** Settings ***
Resource    resources/common.resource

Suite Setup       Prepare E2E Environment
Suite Teardown    Stop Callback Receiver

*** Keywords ***
Prepare E2E Environment
    Seed Demo Location
    Start Callback Receiver
    Refresh CAPIF Token

*** Test Cases ***
Authenticated MonitoringEvent Subscription Delivers Two Callbacks
    [Tags]    e2e    monitoring-event    callback

    ${token}=    Load CAPIF Token

    ${post}=    Create Authenticated Subscription
    ...    ${token}

    Should Be Equal As Integers
    ...    ${post.rc}
    ...    0

    Should Contain
    ...    ${post.stdout}
    ...    HTTP/1.1 201 Created

    Should Contain
    ...    ${post.stdout}
    ...    location:

    Should Contain
    ...    ${post.stdout}
    ...    "maximumNumberOfReports":2

    Wait For Two Callbacks

    Verify Callback Lifecycle

    Verify NEF Authorization And Cleanup

    ${get}=    GET Subscriptions With Token
    ...    ${token}

    Should Be Equal As Integers
    ...    ${get.rc}
    ...    0

    Should Contain
    ...    ${get.stdout}
    ...    HTTP/1.1 404 Not Found

    Should Contain
    ...    ${get.stdout}
    ...    No subscriptions found for this AF

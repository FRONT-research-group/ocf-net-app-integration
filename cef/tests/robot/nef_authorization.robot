*** Settings ***
Resource    resources/common.resource

Suite Setup    Refresh CAPIF Token

*** Test Cases ***
Missing Bearer Token Is Rejected
    [Tags]    auth    negative

    ${result}=    GET Subscriptions Without Token

    Should Be Equal As Integers
    ...    ${result.rc}
    ...    0

    Should Match Regexp
    ...    ${result.stdout}
    ...    HTTP/1\\.1 (401|403)


Invalid JWT Is Rejected
    [Tags]    auth    negative

    ${result}=    GET Subscriptions With Token
    ...    definitely-not-a-valid-jwt

    Should Be Equal As Integers
    ...    ${result.rc}
    ...    0

    Should Contain
    ...    ${result.stdout}
    ...    HTTP/1.1 401 Unauthorized


Correctly Scoped CAPIF Token Reaches Application Logic
    [Tags]    auth    scope    positive

    ${token}=    Load CAPIF Token

    ${result}=    GET Subscriptions With Token
    ...    ${token}

    Should Be Equal As Integers
    ...    ${result.rc}
    ...    0

    Should Not Contain
    ...    ${result.stdout}
    ...    HTTP/1.1 401 Unauthorized

    Should Not Contain
    ...    ${result.stdout}
    ...    HTTP/1.1 403 Forbidden

    ${logs}=    Get NEF Logs

    Should Contain
    ...    ${logs}
    ...    CAPIF scope authorization was successful

    Should Contain
    ...    ${logs}
    ...    Authorization was successful


Wrong Scope CAPIF Token Is Rejected
    [Tags]    auth    scope    negative    optional

    Skip If
    ...    '${WRONG_SCOPE_TOKEN_FILE}' == ''
    ...    WRONG_SCOPE_TOKEN_FILE was not provided

    File Should Exist
    ...    ${WRONG_SCOPE_TOKEN_FILE}

    ${token}=    Get File
    ...    ${WRONG_SCOPE_TOKEN_FILE}

    ${token}=    Strip String
    ...    ${token}

    ${result}=    GET Subscriptions With Token
    ...    ${token}

    Should Be Equal As Integers
    ...    ${result.rc}
    ...    0

    Should Contain
    ...    ${result.stdout}
    ...    HTTP/1.1 403 Forbidden

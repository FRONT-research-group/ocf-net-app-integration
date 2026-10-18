*** Settings ***
Resource    resources/common.resource

*** Test Cases ***
Reusable CAPIF Discovery And Token Retrieval
    [Tags]    smoke    capif    discovery    token

    Refresh CAPIF Token

    ${token}=    Load CAPIF Token

    Should Not Be Empty    ${token}

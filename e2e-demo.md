# CEF–CAPIF–O-NEF End-to-End Demo


This demo validates the complete implemented CEF–CAPIF–O-NEF integration flow from fresh CAPIF onboarding through O-NEF service execution.

The demonstrated flow is:

```
CEF Provider onboarding
        ↓
O-NEF MonitoringEvent API publication
        ↓
CEF Invoker onboarding
        ↓
CAPIF service discovery
        ↓
CAPIF security-context registration/update
        ↓
CAPIF-issued access token
        ↓
Authenticated O-NEF invocation
        ↓
JWT + AEF/API scope authorization
        ↓
MonitoringEvent execution
        ↓
Asynchronous callbacks
        ↓
Subscription cleanup
```

---

## Important

Provider onboarding, API publication and invoker onboarding create persistent state in CAPIF.

The demo therefore uses a unique `DEMO_ID` for every execution.

The temporary O-NEF demo container can be removed after execution. CAPIF registrations remain until they are explicitly unpublished/offboarded.

---

# 1. Prepare an isolated demo


Create unique demo identifiers and temporary paths:

```bash
export DEMO_ID="$(date +%m%d%H%M%S)"
export API_NAME="3gpp-monitoring-event-cef-${DEMO_ID}"

export PROVIDER_CFG="/tmp/cef_provider_${DEMO_ID}.json"
export INVOKER_CFG="/tmp/cef_invoker_${DEMO_ID}.json"

export PROVIDER_STATE="/tmp/cef-provider-${DEMO_ID}"
export INVOKER_STATE="/tmp/cef-invoker-${DEMO_ID}"

export API_DESC="/tmp/cef_nef_api_${DEMO_ID}.json"
export TOKEN_FILE="/tmp/cef_token_${DEMO_ID}.txt"

export VM_IP="$(hostname -I | awk '{print $1}')"

printf 'DEMO_ID=%s\nAPI_NAME=%s\nVM_IP=%s\n' \
  "$DEMO_ID" "$API_NAME" "$VM_IP"
```

Configure CAPIF connectivity with TLS verification enabled:

```bash
export CAPIF_HOST="capifcore"
export REGISTER_HOST="register"

export CAPIF_REGISTER_PORT="8084"
export CAPIF_GETAUTH_MODE="basic_get"

export CAPIF_TLS_VERIFY="True"
export CAPIF_CA_FILE="$PWD/certs/capif-ca-bundle.pem"
```

---

# 2. Create the provider configuration

```bash
python3 - \
  "$PWD/provider_impl/provider_config_sample.json" \
  "$PROVIDER_CFG" \
  "$PROVIDER_STATE" <<'PY'
import json
import sys

src, dst, state = sys.argv[1:]

with open(src) as f:
    data = json.load(f)

def replace(obj, key, value):
    if isinstance(obj, dict):
        if key in obj:
            obj[key] = value
        for v in obj.values():
            replace(v, key, value)
    elif isinstance(obj, list):
        for v in obj:
            replace(v, key, value)

replace(data, "capif_host", "capifcore")
replace(data, "register_host", "register")
replace(data, "capif_https_port", "443")
replace(data, "capif_register_port", "8084")
replace(data, "provider_folder", state)

with open(dst, "w") as f:
    json.dump(data, f, indent=2)
PY

chmod 600 "$PROVIDER_CFG"
mkdir -p "$PROVIDER_STATE"
```

---

# 3. Create a unique O-NEF API description

The isolated O-NEF demo instance will be exposed on host port `8002`.

```bash
python3 - \
  "$PWD/provider_impl/3gpp-monitoring-event.json" \
  "$API_DESC" \
  "$API_NAME" \
  "$VM_IP" <<'PY'
import json
import sys

src, dst, api_name, host = sys.argv[1:]

with open(src) as f:
    data = json.load(f)

data["apiName"] = api_name

for profile in data.get("aefProfiles", []):
    profile["aefId"] = ""

    if "securityMethods" in profile:
        profile["securityMethods"] = ["OAUTH"]

    for interface in profile.get("interfaceDescriptions", []):
        interface["ipv4Addr"] = host
        interface["port"] = 8002

with open(dst, "w") as f:
    json.dump(data, f, indent=2)
PY
```
---

# 4. Onboard the CEF Provider and publish the O-NEF API

Run the CEF provider connector:

```bash
PROVIDER_CONFIG_FILE="$PROVIDER_CFG" \
PROVIDER_OPENAPI_FILE="$PWD/provider_impl/openapi.yaml" \
PROVIDER_API_DESC_FILE="$API_DESC" \
PROVIDER_API_SCHEME="http" \
PROVIDER_API_HOST="$VM_IP" \
PROVIDER_API_PORT="8002" \
PROVIDER_API_BASE_PATH="/3gpp-monitoring-event-envelope/v1" \
PYTHONPATH="$PWD" \
./provider_impl/venv/bin/python \
provider_impl/provider_capif_connector.py
```

Expected:

```text
POST /api-provider-management/v1/registrations
HTTP 201

Provider onboarded and signed certificate obtained successfully
```

Expected:

```text
POST /published-apis/v1/<APF_ID>/service-apis
HTTP 201

Services published successfully
```
---

# 5. Retrieve the generated AEF ID

Locate the generated provider state:

```bash
export IDS_FILE="$(
  find "$PROVIDER_STATE" \
    -name provider_capif_ids.json \
    -print \
    -quit
)"

echo "$IDS_FILE"
```

Extract the generated AEF ID:

```bash
export AEF_ID="$(
python3 - "$IDS_FILE" <<'PY'
import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

def walk(v):
    if isinstance(v, dict):
        for x in v.values():
            yield from walk(x)
    elif isinstance(v, list):
        for x in v:
            yield from walk(x)
    elif isinstance(v, str):
        yield v

for value in walk(data):
    if value.startswith("AEF"):
        print(value)
        break
PY
)"

printf 'AEF_ID=%s\nAPI_NAME=%s\n' \
  "$AEF_ID" \
  "$API_NAME"
```

The generated AEF ID and API name will later appear in the CAPIF token scope:

```
3gpp#<AEF_ID>:<API_NAME>
```

---

# 6. Create and onboard a CEF Invoker

Create invoker configuration:

```bash
python3 - \
  "$PWD/invoker_impl/app/invoker_onboarding/invoker_config_sample.json" \
  "$INVOKER_CFG" \
  "$INVOKER_STATE" \
  "$API_NAME" <<'PY'
import json
import sys

src, dst, state, api_name = sys.argv[1:]

with open(src) as f:
    data = json.load(f)

def replace(obj, key, value):
    if isinstance(obj, dict):
        if key in obj:
            obj[key] = value
        for v in obj.values():
            replace(v, key, value)
    elif isinstance(obj, list):
        for v in obj:
            replace(v, key, value)

replace(data, "capif_host", "capifcore")
replace(data, "register_host", "register")
replace(data, "capif_https_port", "443")
replace(data, "capif_register_port", "8084")
replace(data, "invoker_folder", state)

def set_filter(obj):
    if isinstance(obj, dict):
        if (
            "discover_filter" in obj
            and isinstance(obj["discover_filter"], dict)
        ):
            obj["discover_filter"]["api-name"] = api_name

        for v in obj.values():
            set_filter(v)

    elif isinstance(obj, list):
        for v in obj:
            set_filter(v)

set_filter(data)

with open(dst, "w") as f:
    json.dump(data, f, indent=2)
PY

chmod 600 "$INVOKER_CFG"
mkdir -p "$INVOKER_STATE"
```

Onboard the invoker:

```bash
export INVOKER_CONFIG_FILE="$INVOKER_CFG"

PYTHONPATH="$PWD" \
./provider_impl/venv/bin/python - <<'PY'
from invoker_impl.app.invoker_onboarding.invoker_capif_connector import onboard_invoker

onboard_invoker()

print()
print("CEF invoker onboarding completed.")
PY
```

Expected:

```text
POST /api-invoker-management/v1/onboardedInvokers
HTTP 201

Invoker registered and onboarded successfully
```

For a new invoker, CAPIF may initially return `404` when updating a non-existing security context. The connector then registers it:

```
PUT /capif-security/v1/trustedInvokers/<INV_ID>
HTTP 201

Security service properly registered
```

---

# 7. Discover the API and obtain a CAPIF access token

Request discovery and security credentials:

```bash
PYTHONPATH="$PWD" \
./provider_impl/venv/bin/python \
scripts/refresh_capif_token.py \
"$TOKEN_FILE"

chmod 600 "$TOKEN_FILE"
```

Expected:

```text
Running CAPIF service discovery...
Service APIs successfully discovered

Requesting CAPIF access token...
Security context correctly updated
Security token successfully obtained

Discovery: OK
CAPIF JWT: received
```

The relevant CAPIF operations are:

```text
GET  /service-apis/v1/allServiceAPIs                  → 200
POST /capif-security/v1/trustedInvokers/<INV>/update → 200
POST /capif-security/v1/securities/<INV>/token       → 200
```

---

# 8. Inspect the token scope

```bash
TOKEN_FILE="$TOKEN_FILE" \
./provider_impl/venv/bin/python - <<'PY'
import os
import jwt

with open(os.environ["TOKEN_FILE"]) as f:
    token = f.read().strip()

header = jwt.get_unverified_header(token)

claims = jwt.decode(
    token,
    options={"verify_signature": False}
)

print("Algorithm:", header.get("alg"))
print("Subject:", claims.get("sub"))
print("Scope:", claims.get("scope"))
PY
```

Expected:

```text
Algorithm: RS256
Scope: 3gpp#<AEF_ID>:<API_NAME>
```
---

# 9. Start an isolated O-NEF instance for the generated scope

Retrieve the current O-NEF image:

```bash
export NEF_IMAGE="$(
  docker inspect cef-nef \
    --format '{{.Config.Image}}'
)"

echo "$NEF_IMAGE"
```

Copy the existing environment into a protected file:

```bash
export DEMO_NEF_ENV="/tmp/cef-nef-${DEMO_ID}.env"

docker inspect cef-nef \
  --format '{{range .Config.Env}}{{println .}}{{end}}' \
  > "$DEMO_NEF_ENV"

chmod 600 "$DEMO_NEF_ENV"
```

Update only the authorization-related values:

```bash
python3 - \
  "$DEMO_NEF_ENV" \
  "$AEF_ID" \
  "$API_NAME" <<'PY'
import sys

path, aef, api = sys.argv[1:]

with open(path) as f:
    lines = [x.rstrip("\n") for x in f]

values = {}

for line in lines:
    if "=" in line:
        k, v = line.split("=", 1)
        values[k] = v

values["AUTH_ENABLED"] = "True"
values["CAPIF_ENFORCE_SCOPE"] = "True"
values["CAPIF_REQUIRED_AEF_ID"] = aef
values["CAPIF_REQUIRED_API_NAME"] = api

with open(path, "w") as f:
    for k, v in values.items():
        f.write(f"{k}={v}\n")
PY
```

Create the isolated container:

```bash
docker rm -f cef-nef-full-demo 2>/dev/null || true

docker create \
  --name cef-nef-full-demo \
  --network capif-network \
  --env-file "$DEMO_NEF_ENV" \
  -p 8002:8000 \
  -v "$HOME/NEF/MonitoringEventAPI/certs/capif_security_server.pub.pem:/app/certs/capif_security_server.pub.pem:ro" \
  "$NEF_IMAGE"
```

Attach the same additional networks used by the working O-NEF instance:

```bash
for NET in $(
  docker inspect cef-nef \
    --format '{{range $name,$cfg := .NetworkSettings.Networks}}{{$name}} {{end}}'
); do

  if [ "$NET" != "capif-network" ]; then
    docker network connect "$NET" cef-nef-full-demo
  fi

done
```

Start the container:

```bash
docker start cef-nef-full-demo
```
---

# 10. Seed MonitoringEvent location data

The demo uses the same helper as the Robot Framework E2E test:

```bash
./provider_impl/venv/bin/python \
tests/robot/resources/seed_location.py
```

This provides test location information for the subscriber used by the MonitoringEvent request.

---

# 11. Invoke O-NEF using the CAPIF-issued JWT

Load the token:

```bash
TOKEN="$(cat "$TOKEN_FILE")"
```

Create a MonitoringEvent subscription:

```bash
curl -i \
  -X POST \
  "http://127.0.0.1:8002/3gpp-monitoring-event-envelope/v1/cef-full-demo/subscriptions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "msisdn": "001010143245445",
    "notificationDestination": "http://cef-callback:8001/notify",
    "monitoringType": "LOCATION_REPORTING",
    "maximumNumberOfReports": 2,
    "locationType": "CURRENT_LOCATION",
    "repPeriod": {
      "duration": 5
    }
  }'
```

Expected:

```
HTTP/1.1 201 Created
```
CAPIF-issued JWT is successfully used to invoke the O-NEF service.

---

# 12. Verify CAPIF authorization inside O-NEF

Inspect the O-NEF authorization logs:

```bash
docker logs cef-nef-full-demo \
  --since 2m \
  2>&1 \
| grep -E \
'Bearer token received|CAPIF scope authorization|Authorization was successful'
```

Expected:

```text
Bearer token received
CAPIF scope authorization was successful
Authorization was successful
```
---

# 13. Verify the asynchronous callback lifecycle

Inspect the callback receiver:

```bash
docker logs cef-callback \
  --since 1m \
  2>&1
```

The first notification should contain:

```
cancelInd=false
```

This means the subscription remains active.

The second notification should contain:

```
cancelInd=true
```

This identifies the final report.

Both callback requests should receive:

```
POST /notify HTTP/1.1 204
```
---

# 14. Verify subscription cleanup

Check O-NEF cleanup:

```bash
docker logs cef-nef-full-demo \
  --since 2m \
  2>&1 \
| grep -E \
'last notification|deleted|Task registry'
```

Expected:

```
This is the last notification...
Subscription ... deleted
Task registry: {}
```
---

# This demo proves

A successful execution demonstrates:

| Capability | Result |
|---|---|
| CEF provider onboarding | `201 Created` |
| O-NEF API publication | `201 Created` |
| CEF invoker onboarding | `201 Created` |
| Service discovery | `200 OK` |
| Security-context registration | `201 Created` |
| Security-context update | `200 OK` |
| CAPIF token retrieval | `200 OK` |
| CAPIF JWT algorithm | `RS256` |
| AEF/API scope binding | Verified |
| O-NEF authenticated invocation | `201 Created` |
| O-NEF CAPIF scope authorization | Successful |
| Callback #1 | `204`, `cancelInd=false` |
| Callback #2 | `204`, `cancelInd=true` |
| Subscription cleanup | Successful |

The complete demonstrated path is:

```text
CEF Provider
      ↓
CAPIF provider onboarding
      ↓
O-NEF API publication
      ↓
CEF Invoker onboarding
      ↓
CAPIF discovery
      ↓
CAPIF security context
      ↓
CAPIF access token
      ↓
O-NEF JWT + scope validation
      ↓
MonitoringEvent service
      ↓
asynchronous callbacks
```


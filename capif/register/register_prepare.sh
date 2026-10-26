#!/bin/bash
set -e

CERTS_FOLDER="/usr/src/app/register_service/certs"

CA_KEY="$CERTS_FOLDER/registerCA.key"
CA_CERT="$CERTS_FOLDER/registerCA.crt"

SERVER_KEY="$CERTS_FOLDER/register_key.key"
SERVER_CSR="$CERTS_FOLDER/register.csr"
SERVER_CERT="$CERTS_FOLDER/register_cert.crt"
SAN_FILE="$CERTS_FOLDER/register_san.ext"

cd "$CERTS_FOLDER"

echo "Preparing Register TLS certificates..."

#
# Keep the existing Register CA across container restarts.
#
if [ ! -f "$CA_KEY" ] || [ ! -f "$CA_CERT" ]; then
    echo "Creating Register CA..."

    openssl req -x509 \
        -sha256 \
        -days 3650 \
        -nodes \
        -newkey rsa:2048 \
        -subj "/CN=register/C=ES/L=Madrid" \
        -keyout "$CA_KEY" \
        -out "$CA_CERT"
else
    echo "Reusing existing Register CA."
fi

#
# Keep the server private key across container restarts.
#
if [ ! -f "$SERVER_KEY" ]; then
    echo "Creating Register server key..."
    openssl genrsa \
        -out "$SERVER_KEY" \
        2048
else
    echo "Reusing existing Register server key."
fi

#
# Create a CSR non-interactively.
#
openssl req -new \
    -key "$SERVER_KEY" \
    -out "$SERVER_CSR" \
    -subj "/C=ES/ST=Madrid/L=Madrid/O=Telefonica I+D/OU=Innovation/CN=register/emailAddress=inno@tid.es"

#
# Extensions required by modern TLS clients such as Python Requests.
#
cat > "$SAN_FILE" <<'SANEOF'
subjectAltName=DNS:register
extendedKeyUsage=serverAuth
keyUsage=digitalSignature,keyEncipherment
SANEOF

#
# Generate the server certificate using the persistent Register CA.
#
openssl x509 -req \
    -in "$SERVER_CSR" \
    -CA "$CA_CERT" \
    -CAkey "$CA_KEY" \
    -CAcreateserial \
    -out "$SERVER_CERT" \
    -days 365 \
    -sha256 \
    -extfile "$SAN_FILE"

echo "Register certificate generated."

openssl x509 \
    -in "$SERVER_CERT" \
    -noout \
    -subject \
    -issuer \
    -ext subjectAltName

exec gunicorn \
    --certfile="$SERVER_CERT" \
    --keyfile="$SERVER_KEY" \
    --bind 0.0.0.0:8080 \
    --chdir /usr/src/app/register_service \
    wsgi:app

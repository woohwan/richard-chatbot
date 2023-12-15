#!/bin/sh
# Root CA
openssl genrsa -out root-ca-key.pem 2048
openssl req -new -x509 -sha256 -key root-ca-key.pem -subj "/C=KR/ST=SEOUL/L=GUROGU/O=ORG/OU=UNIT/CN=openserach.io" -out root-ca.pem -days 730
# Admin cert
openssl genrsa -out admin-key-temp.pem 2048
openssl pkcs8 -inform PEM -outform PEM -in admin-key-temp.pem -topk8 -nocrypt -v1 PBE-SHA1-3DES -out admin-key.pem
openssl req -new -key admin-key.pem -subj "/C=de/L=test/O=client/OU=client/CN=admin" -out admin.csr
openssl x509 -req -in admin.csr -CA root-ca.pem -CAkey root-ca-key.pem -CAcreateserial -sha256 -out admin.pem -days 730
# Node cert
openssl genrsa -out esnode-key-temp.pem 2048
openssl pkcs8 -inform PEM -outform PEM -in esnode-key-temp.pem -topk8 -nocrypt -v1 PBE-SHA1-3DES -out esnode-key.pem
openssl req -new -key esnode-key.pem -subj "/C=KR/ST=SEOUL/L=GUROGU/O=ORG/OU=UNIT/CN=node1.observability.svc" -out esnode.csr
echo 'subjectAltName=DNS:node1.observability.svc DNS:localhost IP Address:0:0:0:0:0:0:0:1 IP Address:127.0.0.1' > esnode.ext
openssl x509 -req -in esnode.csr -CA root-ca.pem -CAkey root-ca-key.pem -CAcreateserial -sha256 -out esnode.pem -days 730 -extfile esnode.ext

# Client cert
openssl genrsa -out client-key-temp.pem 2048
openssl pkcs8 -inform PEM -outform PEM -in client-key-temp.pem -topk8 -nocrypt -v1 PBE-SHA1-3DES -out client-key.pem
openssl req -new -key client-key.pem -subj "/C=KR/ST=SEOUL/L=GUROGU/O=ORG/OU=UNIT/CN=client.observability.svc" -out client.csr
echo 'subjectAltName=DNS:client.observability.svc' > client.ext
openssl x509 -req -in client.csr -CA root-ca.pem -CAkey root-ca-key.pem -CAcreateserial -sha256 -out client.pem -days 730 -extfile client.ext
# Cleanup
rm root-ca.srl
rm admin-key-temp.pem
rm admin.csr
rm esnode-key-temp.pem
rm esnode.csr
rm esnode.ext
rm client-key-temp.pem
rm client.csr
rm client.ext
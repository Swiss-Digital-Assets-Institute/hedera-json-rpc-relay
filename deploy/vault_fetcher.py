#!/usr/bin/env python3
import argparse
import os
from base64 import b64encode

import requests

parser = argparse.ArgumentParser()

parser.add_argument(
    '-o',
    '--output',
    help='File to write to',
    dest='output',
    required=True
)
parser.add_argument(
    '-f',
    '--format',
    help='yaml or dotenv (default is yaml)',
    dest='format',
    default='yaml'
)
parser.add_argument(
    '-n',
    '--namespace',
    help='Which K8S namespace to use',
    dest='namespace',
    required=False
)
parser.add_argument(
    '-s',
    '--secret',
    help='Secret name to get',
    dest='secret',
    required=False
)
parser.add_argument(
    '-r',
    '--resource',
    help='How to name the resource',
    dest='resource',
    required=False,
    default='env'
)

args = parser.parse_args()

VAULT_ADDR = os.getenv('VAULT_ADDR')
APPROLE_PAYLOAD = {
    "role_id": os.getenv('VAULT_ROLE_ID'),
    "secret_id": os.getenv('VAULT_SECRET_ID'),
}
LOGIN_URL = "{0}v1/auth/approle/login".format(VAULT_ADDR)
vault_token = requests.post(LOGIN_URL, data=APPROLE_PAYLOAD).json()['auth']['client_token']
versions = requests.get("{0}v1/kv/metadata/{1}".format(VAULT_ADDR, args.secret), headers={"X-Vault-Token": vault_token}).json()['data']['versions']
latest_available = max([int(k) for k, v in versions.items() if v['destroyed'] == False])

print("Fetching {0} version {1}".format(args.secret, latest_available))
SECRETS_URL = "{0}v1/kv/data/{1}?version={2}".format(VAULT_ADDR, args.secret, latest_available)

secrets = requests.get(SECRETS_URL, headers={"X-Vault-Token": vault_token}).json()['data']['data']

if args.format == "dotenv":
    output = "\n".join(f"{x}={secrets[x]}" for x in secrets)
else:
  output = """apiVersion: v1
kind: Secret
metadata:
  name: {0}
  namespace: {1}
type: Opaque
data:
{2}""".format(args.resource, args.namespace,
              "\n".join("  {0}: {1}".format(x, b64encode(secrets[x].encode()).decode()) for x in secrets))

with open(args.output, 'w+') as fh:
    fh.write(output)

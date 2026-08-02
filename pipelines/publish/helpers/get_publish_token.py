import subprocess

from gcip2.vault import SecretsHandler

client = SecretsHandler("pypi-token")
secret = client.fetch()


subprocess.run([f"poetry config pypi-token.pypi {secret['token']}"], shell=True)

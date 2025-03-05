class Vault:
    """
    The Vault class provides methods to authenticate and interact with Vault.

    Methods:
        - __init__(role_id, secret_id):
            Initializes the Vault class instance.

            :param role_id: The role ID to authenticate with.
            :param secret_id: The secret ID to authenticate with.

        - get_kv_secret(path, mount_point='secret', version=None):
            Retrieves a key-value secret from Vault.

            :param path: The path of the secret.
            :param mount_point: The mount point for the secret engine. Default is 'secret'.
            :param version: The version of the secret. Default is None.
            :return: The secret value.

        - get_dynamic_credentials(mount_point, database):
            Generates dynamic credentials for a database from Vault.

            :param mount_point: The mount point for the database engine.
            :param database: The name of the database.
            :return: The generated credentials (username and password).
    """
    import time
    import struct
    import hvac
    from azure.identity import ClientSecretCredential
    def __init__(self, role_id=None, secret_id=None, token=None):
        """
        Initialize the class instance.

        :param role_id: The role ID to authenticate with.
        :param secret_id: The secret ID to authenticate with.
        """
        hvac = self.hvac
        self.Client = hvac.Client(url='https://vault.mycarrier.tech')
        self.SourceCredentials = None
        if token is not None:
            self.Client.token = token.replace("'",'').replace('"','')
            try:
                assert self.Client.is_authenticated()
            except Exception as error:
                raise f"Vault token is invalid"
        elif role_id is not None and secret_id is not None:
            try:
                self.Client.auth.approle.login(
                    role_id=role_id,
                    secret_id=secret_id,
                )
            except Exception as error:
                raise error
        else:
            raise Exception('Role ID and Secret ID or Vault Token are required')
        self.ServicePrincipalCredentials = None

    def kv_secret(self, path, mount_point='secrets', version=None):
        output = None
        if version is None:
            output = self.Client.secrets.kv.v2.read_secret_version(
                path=path, mount_point=mount_point)
        else:
            output = self.Client.secrets.kv.v2.read_secret_version(
                path=path, mount_point=mount_point, version=version)
        return output
    def create_kv_secret(self, path, mount_point='secrets', **kwargs):
        output = self.Client.secrets.kv.v2.create_or_update_secret(
            path=path, mount_point=mount_point, **kwargs)
        return output
    def db_basic(self, mount_point, database):

        credentials = self.Client.secrets.database.generate_credentials(
            name=database,
            mount_point=mount_point
        )
        output = {
            'username': credentials['username'],
            'password': credentials['password']
        }
        return output

    def db_oauth(self, mount_point, role):
        time = self.time
        struct = self.struct
        ClientSecretCredential = self.ClientSecretCredential
        vaultspnCreds = self.Client.secrets.azure.generate_credentials(
            name=role,
            mount_point=mount_point
        )
        i = 0
        while i < 10:
            i += 1
            try:
                spnCreds = ClientSecretCredential(client_id=vaultspnCreds['client_id'],
                                                  client_secret=vaultspnCreds['client_secret'],
                                                  tenant_id="033c43bf-e5b3-42d4-93d2-e7e0fd5e2d3d")
                time.sleep(10)
                token_bytes = spnCreds.get_token(
                    "https://database.windows.net/.default").token.encode("UTF-16-LE")
                token_struct = struct.pack(
                    f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
                return token_struct
            except Exception as e:
                print(e)
            print('SPN not ready, sleeping 30s')
            time.sleep(30)

    def azure(self, mount_point, role):
        time = self.time
        hvac = self.hvac
        max_retries = 5
        retry_delay = 5
        retry_count = 0
        while retry_count < max_retries:
            try:
                creds = self.Client.secrets.azure.generate_credentials(
                    name=role,
                    mount_point=mount_point
                )
                return creds
            except hvac.exceptions.InternalServerError as e:
                if "deadlocked on lock resources" in str(e):
                    print(
                        f"Deadlock detected when getting SQL dynamic creds, retrying... ({retry_count + 1}/{max_retries})")
                    retry_count += 1
                    time.sleep(retry_delay)
                else:
                    raise
        raise Exception(
            "Max retries reached for generating credentials due to deadlock")
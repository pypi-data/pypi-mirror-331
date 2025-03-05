class dbConnection:
    """
    Class for establishing a database connection and executing queries.

    Args:
        server (str): The name or IP address of the server.
        port (int): The port number of the server.
        db_name (str): The name of the database to connect to.
        driver (str, optional): The ODBC driver name. Defaults to 'ODBC Driver 18 for SQL Server'.
        encrypt (str, optional): Specify whether the connection should be encrypted. Defaults to 'yes'.
        trustservercertificate (str, optional): Specify whether to trust the server certificate. Defaults to 'no'.
        timeout (int, optional): The connection timeout in seconds. Defaults to 30.

    Attributes:
        connection: The pyodbc connection object representing the database connection.

    Methods:
        query: Executes a SQL query and returns the results.
        close: Closes the database connection.

    Examples:
        # Instantiate dbConnection
        conn = dbConnection('localhost', 1433, 'mydb')

        # Execute a query and get all results
        results = conn.query('SELECT * FROM mytable', outputResults='all')

        # Close the connection
        conn.close()
    """
    import snowflake.connector
    import pyodbc
    def __init__(self, connection):
        self.connection = connection

    @property
    def cursor(self):
        return self.connection.cursor

    @classmethod
    def from_sql(cls, server, port, db_name, driver='ODBC Driver 18 for SQL Server', encrypt='yes',
                 trustservercertificate='no', timeout=30, auth_method='token', token=None, username=None,
                 password=None):
        pyodbc = cls.pyodbc

        if username is not None and token is not None:
            print(
                "Token and basic auth are mutually exclusive, please use either username & password or Token")

        if auth_method == 'token':
            if token is None:
                print("Token is required when using Token authentication")
                exit(1)
            SQL_COPT_SS_ACCESS_TOKEN = 1256
            con_string = (f"Driver={{{driver}}}; Server={server},{port}; Database={db_name}; Encrypt={encrypt}; "
                          f"TrustServerCertificate={trustservercertificate}; Connection Timeout={timeout},")

            return cls(pyodbc.connect(con_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token}))

        if auth_method == 'basic':
            if username is None or password is None:
                print("When auth method is basic, username and password are required")
                exit(1)
            conn_string = (f"Driver={{{driver}}}; Server={server},{port}; Database={db_name}; Encrypt={encrypt}; "
                           f"TrustServerCertificate={trustservercertificate}; Connection Timeout={timeout};"
                           f"UID={username};PWD={password}")

            return cls(pyodbc.connect(conn_string))

    @classmethod
    def from_snowflake(cls, user, password, role, account, warehouse, database=None, schema=None):
        snowflake = cls.snowflake
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            role=role,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        return cls(conn)

    def query(self, sql, outputResults: str = None, commit: bool = False, params: tuple = ()):
        cursor = self.cursor()
        try:
            if commit:
                self.connection.autocommit = True
            cursor.execute(sql, params)
            if outputResults == "one":
                return cursor.fetchone()
            if outputResults == "all":
                return cursor.fetchall()
        finally:
            cursor.close()
            self.connection.autocommit = False

    def close(self):
        self.connection.close()
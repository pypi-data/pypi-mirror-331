import clickhouse_connect

def pull_tags(CH_HOST, CH_USER, CH_PASS_SECRET, BRANCH, REPO):
    clickhouse_client = clickhouse_connect.get_client(host=CH_HOST, port=8443, username=CH_USER, password=CH_PASS_SECRET)
    tags = clickhouse_client.query(f'''
        SELECT Service, Component, ImageTag FROM (
            SELECT Service, Component, ImageTag, Timestamp, ROW_NUMBER() OVER (PARTITION BY Service, Component ORDER BY Timestamp DESC) as rn
            FROM ci.buildinfo 
            WHERE BuildBranch like '%{BRANCH}'
            AND BuildRepository = '{REPO}'
            AND BuildStatus = 'OK'
        ) WHERE rn = 1
    ''')
    return tags
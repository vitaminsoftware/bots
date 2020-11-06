import boto3
import logging

from django.db.backends.mysql import base

logger = logging.getLogger(__name__)


class DatabaseWrapper(base.DatabaseWrapper):
    def get_connection_params(self):
        # Django calls this method each time it needs to create a new DB
        # connection. By default, that happens on each request but connection
        # reuse can be enabled by setting the CONN_MAX_AGE database option to a
        # value greater than 0.
        #
        # We need to inject the RDS auth token here before the parameters are
        # passed to `get_new_connection`.
        #
        # With keep-alive connections, RDS MySQL will not close existing
        # connections when the password changes so we are safe from that.
        #
        # If we ever need to optimize connection creation we will need to cache
        # the auth token and only refresh it when the `get_new_connection`
        # method will fail with an authentication error. A good example of
        # implementing this can be found int the custom JDBC drivers maintained
        # by AWS for Secrets Manager:
        # https://github.com/aws/aws-secretsmanager-jdbc/blob/master/src/main/java/com/amazonaws/secretsmanager/sql/AWSSecretsManagerDriver.java
        #
        # And here is a python caching plugin from AWS for Secrets Manager:
        # https://github.com/aws/aws-secretsmanager-caching-python
        params = super(DatabaseWrapper, self).get_connection_params()

        # Remove custom option otherwise the MySQL client will throw an error.
        region = params.pop('aws_region', None)

        rds_client = boto3.client('rds', region_name=region)
        params['passwd'] = rds_client.generate_db_auth_token(
            DBHostname=params.get('host'),
            Port=params.get('port'),
            DBUsername=params.get('user'),
        )
        return params

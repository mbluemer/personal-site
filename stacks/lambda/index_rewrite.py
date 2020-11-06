import logging
import re

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Main function to handle CloudFormation events."""
    request = event['Records'][0]['cf']['request']

    try:
        old_uri = request['uri']
        new_uri = re.sub(r'\/$', '/index.html', old_uri)

        request['uri'] = new_uri

        LOGGER.info('Old URI: "%s", New URI: "%s"', old_uri, new_uri)

        return request
    except Exception as e:
        LOGGER.error('Redirect failed: %s', e)





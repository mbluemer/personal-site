from aws_cdk import core
from aws_cdk.aws_route53 import HostedZone


class HostedZoneStack(core.Stack):
    """
    Simple stack to hold my Hosted Zone. Important to keep separate because these holds some
    manually created records used for mail servers.
    """

    def __init__(self, scope: core.Construct, id: str, domain_name: str,
        **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.hosted_zone = HostedZone(self, 'TheBlueDevHostedZone',
            zone_name=domain_name)


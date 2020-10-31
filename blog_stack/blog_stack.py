from aws_cdk import core
from aws_cdk.aws_certificatemanager import Certificate, CertificateValidation
from aws_cdk.aws_cloudfront import (
    Behavior,
    CloudFrontWebDistribution, OriginAccessIdentity,
    S3OriginConfig, SourceConfiguration,
    ViewerCertificate)
from aws_cdk.aws_iam import CfnAccessKey, User
from aws_cdk.aws_s3 import Bucket

DOMAIN_NAME = 'theblue.dev'

class BlogStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        certificate = Certificate(self, 'Certificate', domain_name=DOMAIN_NAME,
            validation=CertificateValidation.from_dns())

        bucket = Bucket(self, 'Bucket')

        origin_access_identity = OriginAccessIdentity(self, 'OriginAccessIdentity')

        bucket.grant_read(origin_access_identity)

        cloudfront_distribution = CloudFrontWebDistribution(
            self, 'CloudFrontDistribution',
            origin_configs=[
                SourceConfiguration(
                    s3_origin_source=S3OriginConfig(
                        s3_bucket_source=bucket,
                        origin_access_identity=origin_access_identity,
                    ),
                    behaviors=[
                        Behavior(is_default_behavior=True,
                            default_ttl=core.Duration.hours(1))
                    ],
                ),
            ],
            viewer_certificate=ViewerCertificate.from_acm_certificate(certificate,
                aliases=[DOMAIN_NAME]))

        deploy_user = User(self, 'DeployUser')
        user_credentials = CfnAccessKey(self, 'DeployUserCredentials',
            user_name=deploy_user.user_name)
        bucket.grant_read_write(deploy_user)

        core.CfnOutput(self, 'CloudFrontDomain',
            value=cloudfront_distribution.distribution_domain_name)
        core.CfnOutput(self, 'DeployUserAccessKeyId', value=user_credentials.ref)
        core.CfnOutput(self, 'DeployUserSecretAccessKey',
            value=user_credentials.attr_secret_access_key)

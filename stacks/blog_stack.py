from aws_cdk import core
from aws_cdk.aws_certificatemanager import DnsValidatedCertificate, CertificateValidation
from aws_cdk.aws_cloudfront import (
    AliasConfiguration, Behavior,
    CloudFrontWebDistribution, OriginAccessIdentity,
    CustomOriginConfig, SourceConfiguration,
    OriginProtocolPolicy,
    SecurityPolicyProtocol,
    ViewerCertificate)
from aws_cdk.aws_iam import CfnAccessKey, User
from aws_cdk.aws_route53 import ARecord, HostedZone, IHostedZone, RecordTarget
from aws_cdk.aws_route53_targets import CloudFrontTarget
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_s3_deployment import BucketDeployment, Source


class BlogStack(core.Stack):
    """
    Stack to host my blog via S3 and CloudFront with a custom domain name
    and SSL certificate.
    """

    def __init__(self, scope: core.Construct, id: str, hosted_zone: IHostedZone,
        domain_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        certificate = DnsValidatedCertificate(self, 'Certificate', domain_name=f'*.{domain_name}',
            subject_alternative_names=[domain_name],
            hosted_zone=hosted_zone)

        bucket = Bucket(self, 'SiteBucket',
            bucket_name=domain_name,
            website_index_document='index.html',
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY)

        cloudfront_distribution = CloudFrontWebDistribution(
            self, 'CloudFrontDistribution',
            origin_configs=[
                SourceConfiguration(
                    custom_origin_source=CustomOriginConfig(
                        domain_name=bucket.bucket_website_domain_name,
                        origin_protocol_policy=OriginProtocolPolicy.HTTP_ONLY,
                    ),
                    behaviors=[
                        Behavior(is_default_behavior=True,
                            default_ttl=core.Duration.hours(1))
                    ],
                ),
            ],
            alias_configuration=AliasConfiguration(
                acm_cert_ref=certificate.certificate_arn,
                names=[domain_name],
            )
        )

        ARecord(self, 'DefaultRecord',
            target=RecordTarget(alias_target=CloudFrontTarget(
                distribution=cloudfront_distribution)),
            zone=hosted_zone,
            ttl=core.Duration.hours(1))

        BucketDeployment(self, 'DeployWebsite',
            sources=[Source.asset('./site/public')],
            destination_bucket=bucket,
            distribution=cloudfront_distribution)


        core.CfnOutput(self, 'CloudFrontDomain',
            value=cloudfront_distribution.distribution_domain_name)
        core.CfnOutput(self, 'BucketName',
            value=bucket.bucket_name)

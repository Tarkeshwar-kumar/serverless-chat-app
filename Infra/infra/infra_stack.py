from constructs import Construct
from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_iam as iam,
    Duration
)


class InfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cognito_userPool = cognito.UserPool(self, 
            id = "serverless-userpool",
            user_pool_name="serverless-chat-userpool",
            sign_in_case_sensitive=True,
            account_recovery = cognito.AccountRecovery.EMAIL_AND_PHONE_WITHOUT_MFA,
            auto_verify = cognito.AutoVerifiedAttrs(email=True, phone=True),
            email=cognito.UserPoolEmail.with_ses(
                from_email="ktarkeshwar305@gmail.com",
                from_name="Serverless Chat App",
                ses_region = "ap-south-1"
            )
        )
        basic_lambda_role = iam.Role(
            self,
            "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="IAM role for Lambda function",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ReadOnlyAccess")
            ]
        )

        login_test_lambda = _lambda.Function(
            self,
            'login_lambda',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('lambda'),
            handler='login_lambda.handler',
            role=basic_lambda_role,
            timeout=Duration.minutes(10)
        )

        login_lambda_integration = apigateway.LambdaIntegration(login_test_lambda)

        api = apigateway.RestApi(self, 
            id = "serverless-restapi",
            rest_api_name = "serverless-restapi",
            endpoint_configuration = apigateway.EndpointConfiguration(
                types=[apigateway.EndpointType.REGIONAL]
            )
        )
        login_endpoint = api.root.add_resource("login")
        login_endpoint.add_method("POST", login_lambda_integration)

        signUp_endpoint = api.root.add_resource("signup")
        signUp_endpoint.add_method("POST")



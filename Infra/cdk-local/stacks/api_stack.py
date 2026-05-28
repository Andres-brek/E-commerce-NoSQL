import os

from aws_cdk import Duration, Stack
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct


class ApiStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        ecommerce_table: dynamodb.Table,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function — code is the entire Backend/ directory bundled as a zip.
        # LocalStack resolves the path relative to its mounted /workspace/Backend volume.
        handler = lambda_.Function(
            self,
            "EcommerceHandler",
            function_name="ecommerce-handler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="lambdas.ecommerce.handler",
            code=lambda_.Code.from_asset("../../Backend"),
            timeout=Duration.seconds(29),
            memory_size=256,
            environment={
                "TABLE_NAME": ecommerce_table.table_name,
                "DYNAMODB_URL": "http://localstack:4566",
                # Redis is optional — disabled by default. Set REDIS_URL to enable cache.
                "REDIS_URL": os.environ.get("REDIS_URL", ""),
                "CACHE_TTL_SECONDS": "120",
                "PASSWORD_PEPPER": os.environ.get("PASSWORD_PEPPER", "empanada69"),
            },
        )

        ecommerce_table.grant_read_write_data(handler)

        # REST API Gateway — each route proxies to the single Lambda.
        api = apigw.RestApi(
            self,
            "EcommerceApi",
            rest_api_name="ecommerce-api",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        integration = apigw.LambdaIntegration(handler, proxy=True)

        # POST /login
        login = api.root.add_resource("login")
        login.add_method("POST", integration)

        # POST /checkout
        checkout = api.root.add_resource("checkout")
        checkout.add_method("POST", integration)

        # GET /user/{user_id}/profile  and  GET /user/{user_id}/orders
        user = api.root.add_resource("user")
        user_id = user.add_resource("{user_id}")
        user_id.add_resource("profile").add_method("GET", integration)
        user_id.add_resource("orders").add_method("GET", integration)

        # GET /order/{order_id}
        order = api.root.add_resource("order")
        order.add_resource("{order_id}").add_method("GET", integration)

        # GET /products  and  GET /products/{product_id}
        products = api.root.add_resource("products")
        products.add_method("GET", integration)
        products.add_resource("{product_id}").add_method("GET", integration)

        # GET /cache/metrics  and  GET /cache/keys
        cache = api.root.add_resource("cache")
        cache.add_resource("metrics").add_method("GET", integration)
        cache.add_resource("keys").add_method("GET", integration)

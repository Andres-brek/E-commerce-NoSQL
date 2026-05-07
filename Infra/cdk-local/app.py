#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.ecommerce_local_stack import EcommerceLocalStack


app = cdk.App()
EcommerceLocalStack(
    app,
    "EcommerceLocalStack",
    env=cdk.Environment(account="000000000000", region="us-east-1"),
    synthesizer=cdk.LegacyStackSynthesizer(),
)
app.synth()

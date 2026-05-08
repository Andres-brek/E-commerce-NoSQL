#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.persistence_stack import PersistenceStack
from stacks.api_stack import ApiStack

app = cdk.App()

env = cdk.Environment(account="000000000000", region="us-east-1")
synth = cdk.LegacyStackSynthesizer()

persistence = PersistenceStack(app, "PersistenceStack", env=env, synthesizer=synth)

ApiStack(
    app,
    "ApiStack",
    ecommerce_table=persistence.ecommerce_table,
    env=env,
    synthesizer=synth,
)

app.synth()

"""AWS Lambda entry point for API Gateway HTTP API payload format 2.0."""

from mangum import Mangum

from .api import app


# There are no application lifespan hooks. Disabling lifespan avoids sending
# redundant startup/shutdown events on each Lambda invocation.
handler = Mangum(app, lifespan="off")

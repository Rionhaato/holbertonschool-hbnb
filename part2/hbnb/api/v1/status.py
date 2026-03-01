"""Status endpoint for API sanity checks."""

from flask_restx import Namespace, Resource


api = Namespace("status", description="Service status")


@api.route("")
class StatusResource(Resource):
    """Health check endpoint."""

    def get(self):
        return {"status": "OK"}, 200

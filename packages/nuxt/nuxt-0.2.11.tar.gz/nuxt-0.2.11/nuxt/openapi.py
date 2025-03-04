from nuxt.app import WSGIApplicationResponder, ASGIApplicationResponder
from nuxt.routing import BaseRoute, Route, Mount
from nuxt.responses import AsyncHTMLResponse, AsyncResponse
from nuxt.requests import AsyncRequest
import typing
import json
import yaml
import re

swagger_ui_default_parameters = {
    "dom_id": "#swagger-ui",
    "layout": "BaseLayout",
    "deepLinking": True,
    "showExtensions": True,
    "showCommonExtensions": True,
}


class OpenAPIResponse(AsyncResponse):
    media_type = "text/yaml"

    def render(self, content: typing.Any) -> bytes:
        return yaml.dump(content, default_flow_style=False).encode("utf-8")


class EndpointInfo(typing.NamedTuple):
    path: str
    http_method: str
    func: typing.Callable


class SchemaGenerator:

    def __init__(self, base_schema: dict, url_prefx: str = "/docs") -> None:
        self.base_schema = base_schema
        self.url_prefix = url_prefx
        self.url_schema = "%s/%s" % (self.url_prefix.rstrip("/"), "openapi")

    def routes(self):
        return [
            Route(self.url_prefix, self.SwaggerUIResponse, name="async.nuxt.docs", include_in_schema=False),
            Route(self.url_schema, self.OpenAPIResponse, name="async.nuxt.schemas", include_in_schema=False),
        ]

    def get_schema(self, routes: typing.List[BaseRoute]) -> dict:
        schema = dict(self.base_schema)
        schema.setdefault("paths", {})
        endpoints_info = self.get_endpoints(routes)
        for endpoint in endpoints_info:
            parsed = self.parse_docstring(endpoint.func)
            if "responses" not in parsed:
                parsed.update({
                    "responses": {
                        200: {}
                    }
                })
            if endpoint.path not in schema["paths"]:
                schema["paths"][endpoint.path] = {}
            schema["paths"][endpoint.path][endpoint.http_method] = parsed
        return schema

    def get_endpoints(
        self, routes: typing.List[BaseRoute]
    ) -> typing.List[EndpointInfo]:
        """
        Given the routes, yields the following information:

        - path
            eg: /users/
        - http_method
            one of 'get', 'post', 'put', 'patch', 'delete', 'options'
        - func
            method ready to extract the docstring
        """
        endpoints_info: list = []

        for route in routes:
            if isinstance(route, Mount):
                path = self._remove_converter(route.path)
                routes = route.routes or []
                sub_endpoints = [
                    EndpointInfo(
                        path="".join((path, sub_endpoint.path)),
                        http_method=sub_endpoint.http_method,
                        func=sub_endpoint.func,
                    )
                    for sub_endpoint in self.get_endpoints(routes)
                ]
                endpoints_info.extend(sub_endpoints)

            elif not isinstance(route, Route) or not route.include_in_schema:
                continue

            elif isinstance(route.endpoint, ASGIApplicationResponder) or isinstance(route.endpoint, WSGIApplicationResponder):
                path = self._remove_converter(route.path)
                for method in route.methods or ["GET"]:
                    if method == "HEAD":
                        continue
                    endpoints_info.append(
                        EndpointInfo(path, method.lower(), route.endpoint)
                    )

        return endpoints_info

    def _remove_converter(self, path: str) -> str:
        """
        Remove the converter from the path.
        For example, a route like this:
            Route("/users/{id:int}", endpoint=get_user, methods=["GET"])
        Should be represented as `/users/{id}` in the OpenAPI schema.
        """
        return re.sub(r":\w+}", "}", path)

    def parse_docstring(self, func_or_method: typing.Callable) -> dict:
        """
        Given a function, parse the docstring as YAML and return a dictionary of info.
        """
        docstring = func_or_method.__doc__
        if not docstring:
            return {}

        # We support having regular docstrings before the schema
        # definition. Here we return just the schema part from
        # the docstring.
        docstring = docstring.split("---")[-1]

        parsed = yaml.safe_load(docstring)

        if not isinstance(parsed, dict):
            # A regular docstring (not yaml formatted) can return
            # a simple string here, which wouldn't follow the schema.
            return {}

        return parsed

    def OpenAPIResponse(self, request: AsyncRequest) -> AsyncResponse:
        routes = request.app.routes
        schema = self.get_schema(routes=routes)
        return OpenAPIResponse(schema)

    def SwaggerUIResponse(self, request: AsyncRequest) -> AsyncHTMLResponse:
        return get_swagger_ui_html(openapi_url=self.url_schema, title="Docs")


def get_swagger_ui_html(
    *,
    openapi_url: str,
    title: str,
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    swagger_ui_parameters: dict = None,
) -> AsyncHTMLResponse:
    current_swagger_ui_parameters = swagger_ui_default_parameters.copy()
    if swagger_ui_parameters:
        current_swagger_ui_parameters.update(swagger_ui_parameters)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="{swagger_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
    """

    for key, value in current_swagger_ui_parameters.items():
        html += f"{json.dumps(key)}: {json.dumps(value)},\n"

    html += """
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
    })"""

    html += """
    </script>
    </body>
    </html>
    """
    return AsyncHTMLResponse(html)

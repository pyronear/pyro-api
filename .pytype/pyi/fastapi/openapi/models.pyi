# (generated with --quick)

import enum
import logging
from typing import Any, Dict, List, Optional, Type, Union

AnyUrl: Any
BaseModel: Any
EmailStr: Any
Enum: Type[enum.Enum]
Field: Any
SecurityScheme: Type[Union[APIKey, HTTPBase, OAuth2, OpenIdConnect]]
email_validator: Any
logger: logging.Logger

class APIKey(SecurityBase):
    in_: APIKeyIn
    name: str
    type_: Any

class APIKeyIn(enum.Enum):
    cookie: str
    header: str
    query: str

class Components(Any):
    callbacks: Optional[Dict[str, Union[Reference, Dict[str, PathItem]]]]
    examples: Optional[Dict[str, Union[Example, Reference]]]
    headers: Optional[Dict[str, Union[Header, Reference]]]
    links: Optional[Dict[str, Union[Link, Reference]]]
    parameters: Optional[Dict[str, Union[Parameter, Reference]]]
    requestBodies: Optional[Dict[str, Union[Reference, RequestBody]]]
    responses: Optional[Dict[str, Union[Reference, Response]]]
    schemas: Optional[Dict[str, Union[Reference, Schema]]]
    securitySchemes: Optional[Dict[str, Union[APIKey, HTTPBase, OAuth2, OpenIdConnect, Reference]]]

class Contact(Any):
    email: Any
    name: Optional[str]
    url: Any

class Discriminator(Any):
    mapping: Optional[Dict[str, str]]
    propertyName: str

class Encoding(Any):
    allowReserved: Optional[bool]
    contentType: Optional[str]
    explode: Optional[bool]
    headers: Optional[Dict[str, Any]]
    style: Optional[str]

class EncodingWithHeaders(Encoding):
    headers: Optional[Dict[str, Union[Header, Reference]]]

class Example(Any):
    description: Optional[str]
    externalValue: Any
    summary: Optional[str]
    value: Any

class ExternalDocumentation(Any):
    description: Optional[str]
    url: Any

class HTTPBase(SecurityBase):
    scheme: str
    type_: Any

class HTTPBearer(HTTPBase):
    bearerFormat: Optional[str]
    scheme: str

class Header(ParameterBase): ...

class Info(Any):
    contact: Optional[Contact]
    description: Optional[str]
    license: Optional[License]
    termsOfService: Optional[str]
    title: str
    version: str

class License(Any):
    name: str
    url: Any

class Link(Any):
    description: Optional[str]
    operationId: Optional[str]
    operationRef: Optional[str]
    parameters: Optional[Dict[str, Any]]
    requestBody: Any
    server: Optional[Server]

class MediaType(Any):
    encoding: Optional[Dict[str, Encoding]]
    example: Any
    examples: Optional[Dict[str, Union[Example, Reference]]]
    schema_: Optional[Union[Reference, Schema]]

class OAuth2(SecurityBase):
    flows: OAuthFlows
    type_: Any

class OAuthFlow(Any):
    refreshUrl: Optional[str]
    scopes: Dict[str, str]

class OAuthFlowAuthorizationCode(OAuthFlow):
    authorizationUrl: str
    tokenUrl: str

class OAuthFlowClientCredentials(OAuthFlow):
    tokenUrl: str

class OAuthFlowImplicit(OAuthFlow):
    authorizationUrl: str

class OAuthFlowPassword(OAuthFlow):
    tokenUrl: str

class OAuthFlows(Any):
    authorizationCode: Optional[OAuthFlowAuthorizationCode]
    clientCredentials: Optional[OAuthFlowClientCredentials]
    implicit: Optional[OAuthFlowImplicit]
    password: Optional[OAuthFlowPassword]

class OpenAPI(Any):
    components: Optional[Components]
    externalDocs: Optional[ExternalDocumentation]
    info: Info
    openapi: str
    paths: Dict[str, PathItem]
    security: Optional[List[Dict[str, List[str]]]]
    servers: Optional[List[Server]]
    tags: Optional[List[Tag]]

class OpenIdConnect(SecurityBase):
    openIdConnectUrl: str
    type_: Any

class Operation(Any):
    callbacks: Optional[Dict[str, Union[Reference, Dict[str, Any]]]]
    deprecated: Optional[bool]
    description: Optional[str]
    externalDocs: Optional[ExternalDocumentation]
    operationId: Optional[str]
    parameters: Optional[List[Union[Parameter, Reference]]]
    requestBody: Optional[Union[Reference, RequestBody]]
    responses: Dict[str, Response]
    security: Optional[List[Dict[str, List[str]]]]
    servers: Optional[List[Server]]
    summary: Optional[str]
    tags: Optional[List[str]]

class OperationWithCallbacks(Any):
    callbacks: Optional[Dict[str, Union[Reference, Dict[str, PathItem]]]]

class Parameter(ParameterBase):
    in_: ParameterInType
    name: str

class ParameterBase(Any):
    allowReserved: Optional[bool]
    content: Optional[Dict[str, MediaType]]
    deprecated: Optional[bool]
    description: Optional[str]
    example: Any
    examples: Optional[Dict[str, Union[Example, Reference]]]
    explode: Optional[bool]
    required: Optional[bool]
    schema_: Optional[Union[Reference, Schema]]
    style: Optional[str]

class ParameterInType(enum.Enum):
    cookie: str
    header: str
    path: str
    query: str

class PathItem(Any):
    delete: Optional[Operation]
    description: Optional[str]
    get: Optional[Operation]
    head: Optional[Operation]
    options: Optional[Operation]
    parameters: Optional[List[Union[Parameter, Reference]]]
    patch: Optional[Operation]
    post: Optional[Operation]
    put: Optional[Operation]
    ref: Optional[str]
    servers: Optional[List[Server]]
    summary: Optional[str]
    trace: Optional[Operation]

class Reference(Any):
    ref: str

class RequestBody(Any):
    content: Dict[str, MediaType]
    description: Optional[str]
    required: Optional[bool]

class Response(Any):
    content: Optional[Dict[str, MediaType]]
    description: str
    headers: Optional[Dict[str, Union[Header, Reference]]]
    links: Optional[Dict[str, Union[Link, Reference]]]

class Schema(SchemaBase):
    additionalProperties: Optional[Union[bool, Dict[str, Any]]]
    allOf: Optional[List[SchemaBase]]
    anyOf: Optional[List[SchemaBase]]
    items: Optional[SchemaBase]
    not_: Optional[SchemaBase]
    oneOf: Optional[List[SchemaBase]]
    properties: Optional[Dict[str, SchemaBase]]

class SchemaBase(Any):
    additionalProperties: Optional[Union[bool, Dict[str, Any]]]
    allOf: Optional[list]
    anyOf: Optional[list]
    default: Any
    deprecated: Optional[bool]
    description: Optional[str]
    discriminator: Optional[Discriminator]
    enum: Optional[list]
    example: Any
    exclusiveMaximum: Optional[float]
    exclusiveMinimum: Optional[float]
    externalDocs: Optional[ExternalDocumentation]
    format: Optional[str]
    items: Any
    maxItems: Optional[int]
    maxLength: Optional[int]
    maxProperties: Optional[int]
    maximum: Optional[float]
    minItems: Optional[int]
    minLength: Optional[int]
    minProperties: Optional[int]
    minimum: Optional[float]
    multipleOf: Optional[float]
    not_: Any
    nullable: Optional[bool]
    oneOf: Optional[list]
    pattern: Optional[str]
    properties: Optional[Dict[str, Any]]
    readOnly: Optional[bool]
    ref: Optional[str]
    required: Optional[List[str]]
    title: Optional[str]
    type: Optional[str]
    uniqueItems: Optional[bool]
    writeOnly: Optional[bool]
    xml: Optional[XML]

class SecurityBase(Any):
    description: Optional[str]
    type_: SecuritySchemeType

class SecuritySchemeType(enum.Enum):
    apiKey: str
    http: str
    oauth2: str
    openIdConnect: str

class Server(Any):
    description: Optional[str]
    url: Any
    variables: Optional[Dict[str, ServerVariable]]

class ServerVariable(Any):
    default: str
    description: Optional[str]
    enum: Optional[List[str]]

class Tag(Any):
    description: Optional[str]
    externalDocs: Optional[ExternalDocumentation]
    name: str

class XML(Any):
    attribute: Optional[bool]
    name: Optional[str]
    namespace: Optional[str]
    prefix: Optional[str]
    wrapped: Optional[bool]

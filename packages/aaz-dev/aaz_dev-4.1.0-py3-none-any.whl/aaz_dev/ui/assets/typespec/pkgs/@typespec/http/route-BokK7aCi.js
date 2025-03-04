import { createTypeSpecLibrary, paramMessage, createDiagnosticCollector, getMinValue, getMaxValue, ignoreDiagnostics, isArrayModelType, reportDeprecated, validateDecoratorUniqueOnNode, typespecTypeToJson, getDoc, validateDecoratorTarget, SyntaxKind, walkPropertiesInherited, compilerAssert, getProperty, getDiscriminator, filterModelProperties, navigateType, getEncode, isNullType, isErrorModel, isVoidType, getErrorsDoc, getReturnsDoc, listOperationsIn, listServices, navigateProgram, getOverloadedOperation, getOverloads, getVisibility, $visibility, getLifecycleVisibilityEnum, getParameterVisibilityFilter, isVisible as isVisible$1, getEffectiveModelType } from '@typespec/compiler';
import { deepClone, deepEquals, DuplicateTracker, TwoLevelMap } from '@typespec/compiler/utils';

const $lib = createTypeSpecLibrary({
    name: "@typespec/http",
    diagnostics: {
        "http-verb-duplicate": {
            severity: "error",
            messages: {
                default: paramMessage `HTTP verb already applied to ${"entityName"}`,
            },
        },
        "missing-uri-param": {
            severity: "error",
            messages: {
                default: paramMessage `Route reference parameter '${"param"}' but wasn't found in operation parameters`,
            },
        },
        "incompatible-uri-param": {
            severity: "error",
            messages: {
                default: paramMessage `Parameter '${"param"}' is defined in the uri as a ${"uriKind"} but is annotated as a ${"annotationKind"}.`,
            },
        },
        "use-uri-template": {
            severity: "error",
            messages: {
                default: paramMessage `Parameter '${"param"}' is already defined in the uri template. Explode, style and allowReserved property must be defined in the uri template as described by RFC 6570.`,
            },
        },
        "optional-path-param": {
            severity: "error",
            messages: {
                default: paramMessage `Path parameter '${"paramName"}' cannot be optional.`,
            },
        },
        "missing-server-param": {
            severity: "error",
            messages: {
                default: paramMessage `Server url contains parameter '${"param"}' but wasn't found in given parameters`,
            },
        },
        "duplicate-body": {
            severity: "error",
            messages: {
                default: "Operation has multiple @body parameters declared",
                duplicateUnannotated: "Operation has multiple unannotated parameters. There can only be one representing the body",
                bodyAndUnannotated: "Operation has a @body and an unannotated parameter. There can only be one representing the body",
            },
        },
        "duplicate-route-decorator": {
            severity: "error",
            messages: {
                namespace: "@route was defined twice on this namespace and has different values.",
            },
        },
        "operation-param-duplicate-type": {
            severity: "error",
            messages: {
                default: paramMessage `Param ${"paramName"} has multiple types: [${"types"}]`,
            },
        },
        "duplicate-operation": {
            severity: "error",
            messages: {
                default: paramMessage `Duplicate operation "${"operationName"}" routed at "${"verb"} ${"path"}".`,
            },
        },
        "multiple-status-codes": {
            severity: "error",
            messages: {
                default: "Multiple `@statusCode` decorators defined for this operation response.",
            },
        },
        "status-code-invalid": {
            severity: "error",
            messages: {
                default: "statusCode value must be a numeric or string literal or union of numeric or string literals",
                value: "statusCode value must be a three digit code between 100 and 599",
            },
        },
        "content-type-string": {
            severity: "error",
            messages: {
                default: "contentType parameter must be a string literal or union of string literals",
            },
        },
        "content-type-ignored": {
            severity: "warning",
            messages: {
                default: "`Content-Type` header ignored because there is no body.",
            },
        },
        "metadata-ignored": {
            severity: "warning",
            messages: {
                default: paramMessage `${"kind"} property will be ignored as it is inside of a @body property. Use @bodyRoot instead if wanting to mix.`,
            },
        },
        "response-cookie-not-supported": {
            severity: "warning",
            messages: {
                default: paramMessage `@cookie on response is not supported. Property '${"propName"}' will be ignored in the body. If you need 'Set-Cookie', use @header instead.`,
            },
        },
        "no-service-found": {
            severity: "warning",
            messages: {
                default: paramMessage `No namespace with '@service' was found, but Namespace '${"namespace"}' contains routes. Did you mean to annotate this with '@service'?`,
            },
        },
        "invalid-type-for-auth": {
            severity: "error",
            messages: {
                default: paramMessage `@useAuth ${"kind"} only accept Auth model, Tuple of auth model or union of auth model.`,
            },
        },
        "shared-inconsistency": {
            severity: "error",
            messages: {
                default: paramMessage `Each operation routed at "${"verb"} ${"path"}" needs to have the @sharedRoute decorator.`,
            },
        },
        "write-visibility-not-supported": {
            severity: "warning",
            messages: {
                default: `@visibility("write") is not supported. Use @visibility("update"), @visibility("create") or @visibility("create", "update") as appropriate.`,
            },
        },
        "multipart-invalid-content-type": {
            severity: "error",
            messages: {
                default: paramMessage `Content type '${"contentType"}' is not a multipart content type. Supported content types are: ${"supportedContentTypes"}.`,
            },
        },
        "multipart-model": {
            severity: "error",
            messages: {
                default: "Multipart request body must be a model.",
            },
        },
        "multipart-part": {
            severity: "error",
            messages: {
                default: "Expect item to be an HttpPart model.",
            },
        },
        "multipart-nested": {
            severity: "error",
            messages: {
                default: "Cannot use @multipartBody inside of an HttpPart",
            },
        },
        "http-file-extra-property": {
            severity: "error",
            messages: {
                default: paramMessage `File model cannot define extra properties. Found '${"propName"}'.`,
            },
        },
        "formdata-no-part-name": {
            severity: "error",
            messages: {
                default: "Part used in multipart/form-data must have a name.",
            },
        },
        "header-format-required": {
            severity: "error",
            messages: {
                default: `A format must be specified for @header when type is an array. e.g. @header({format: "csv"})`,
            },
        },
    },
    state: {
        authentication: { description: "State for the @auth decorator" },
        header: { description: "State for the @header decorator" },
        cookie: { description: "State for the @cookie decorator" },
        query: { description: "State for the @query decorator" },
        path: { description: "State for the @path decorator" },
        body: { description: "State for the @body decorator" },
        bodyRoot: { description: "State for the @bodyRoot decorator" },
        bodyIgnore: { description: "State for the @bodyIgnore decorator" },
        multipartBody: { description: "State for the @bodyIgnore decorator" },
        statusCode: { description: "State for the @statusCode decorator" },
        verbs: { description: "State for the verb decorators (@get, @post, @put, etc.)" },
        servers: { description: "State for the @server decorator" },
        includeInapplicableMetadataInPayload: {
            description: "State for the @includeInapplicableMetadataInPayload decorator",
        },
        // route.ts
        externalInterfaces: {},
        routeProducer: {},
        routes: {},
        sharedRoutes: { description: "State for the @sharedRoute decorator" },
        routeOptions: {},
        // private
        file: { description: "State for the @Private.file decorator" },
        httpPart: { description: "State for the @Private.httpPart decorator" },
    },
});
const { reportDiagnostic, createDiagnostic, stateKeys: HttpStateKeys } = $lib;

function error(target) {
    return [
        [],
        [
            createDiagnostic({
                code: "status-code-invalid",
                target,
                messageId: "value",
            }),
        ],
    ];
}
// Issue a diagnostic if not valid
function validateStatusCode(code, diagnosticTarget) {
    const codeAsNumber = typeof code === "string" ? parseInt(code, 10) : code;
    if (isNaN(codeAsNumber)) {
        return error(diagnosticTarget);
    }
    if (!Number.isInteger(codeAsNumber)) {
        return error(diagnosticTarget);
    }
    if (codeAsNumber < 100 || codeAsNumber > 599) {
        return error(diagnosticTarget);
    }
    return [[codeAsNumber], []];
}
function getStatusCodesFromType(program, type, diagnosticTarget) {
    switch (type.kind) {
        case "String":
        case "Number":
            return validateStatusCode(type.value, diagnosticTarget);
        case "Union":
            const diagnostics = createDiagnosticCollector();
            const statusCodes = [...type.variants.values()].flatMap((variant) => {
                return diagnostics.pipe(getStatusCodesFromType(program, variant.type, diagnosticTarget));
            });
            return diagnostics.wrap(statusCodes);
        case "Scalar":
            return validateStatusCodeRange(program, type, type, diagnosticTarget);
        case "ModelProperty":
            if (type.type.kind === "Scalar") {
                return validateStatusCodeRange(program, type, type.type, diagnosticTarget);
            }
            else {
                return getStatusCodesFromType(program, type.type, diagnosticTarget);
            }
        default:
            return error(diagnosticTarget);
    }
}
function validateStatusCodeRange(program, type, scalar, diagnosticTarget) {
    if (!isInt32(program, scalar)) {
        return error(diagnosticTarget);
    }
    const range = getStatusCodesRange(program, type);
    if (isRangeComplete(range)) {
        return [[range], []];
    }
    else {
        return error(diagnosticTarget); // TODO better error explaining missing start/end
    }
}
function isRangeComplete(range) {
    return range.start !== undefined && range.end !== undefined;
}
function getStatusCodesRange(program, type, diagnosticTarget) {
    const start = getMinValue(program, type);
    const end = getMaxValue(program, type);
    let baseRange = {};
    if (type.kind === "ModelProperty" &&
        (type.type.kind === "Scalar" || type.type.kind === "ModelProperty")) {
        baseRange = getStatusCodesRange(program, type.type);
    }
    else if (type.kind === "Scalar" && type.baseScalar) {
        baseRange = getStatusCodesRange(program, type.baseScalar);
    }
    return { ...baseRange, start, end };
}
function isInt32(program, type) {
    return ignoreDiagnostics(program.checker.isTypeAssignableTo(
    // eslint-disable-next-line @typescript-eslint/no-deprecated
    type.projectionBase ?? type, program.checker.getStdType("int32"), type));
}

/**
 * Extract params to be interpolated(Wrapped in '{' and '}'}) from a path/url.
 * @param path Path/Url
 *
 * @example "foo/{name}/bar" -> ["name"]
 */
function extractParamsFromPath(path) {
    return path.match(/\{[^}]+\}/g)?.map((s) => s.slice(1, -1)) ?? [];
}

const namespace$1 = "TypeSpec.Http";
const $header = (context, entity, headerNameOrOptions) => {
    const options = {
        type: "header",
        name: entity.name.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase(),
    };
    if (headerNameOrOptions) {
        if (headerNameOrOptions.kind === "String") {
            options.name = headerNameOrOptions.value;
        }
        else if (headerNameOrOptions.kind === "Model") {
            const name = headerNameOrOptions.properties.get("name")?.type;
            if (name?.kind === "String") {
                options.name = name.value;
            }
            const format = headerNameOrOptions.properties.get("format")?.type;
            if (format?.kind === "String") {
                const val = format.value;
                if (val === "csv" ||
                    val === "tsv" ||
                    val === "pipes" ||
                    val === "ssv" ||
                    val === "simple" ||
                    val === "form" ||
                    val === "multi") {
                    options.format = val;
                }
            }
        }
        else {
            return;
        }
    }
    if (entity.type.kind === "Model" &&
        isArrayModelType(context.program, entity.type) &&
        options.format === undefined) {
        reportDiagnostic(context.program, {
            code: "header-format-required",
            target: context.decoratorTarget,
        });
    }
    context.program.stateMap(HttpStateKeys.header).set(entity, options);
};
function getHeaderFieldOptions(program, entity) {
    return program.stateMap(HttpStateKeys.header).get(entity);
}
function getHeaderFieldName(program, entity) {
    return getHeaderFieldOptions(program, entity)?.name;
}
function isHeader(program, entity) {
    return program.stateMap(HttpStateKeys.header).has(entity);
}
/** {@inheritDoc CookieDecorator } */
const $cookie = (context, entity, cookieNameOrOptions) => {
    const paramName = typeof cookieNameOrOptions === "string"
        ? cookieNameOrOptions
        : (cookieNameOrOptions?.name ??
            entity.name.replace(/([a-z])([A-Z])/g, "$1_$2").toLowerCase());
    const options = {
        type: "cookie",
        name: paramName,
    };
    context.program.stateMap(HttpStateKeys.cookie).set(entity, options);
};
/**
 * Get the cookie parameter options for the given entity.
 * @param program
 * @param entity
 * @returns The cookie parameter options or undefined if the entity is not a cookie parameter.
 */
function getCookieParamOptions(program, entity) {
    return program.stateMap(HttpStateKeys.cookie).get(entity);
}
/**
 * Check whether the given entity is a cookie parameter.
 * @param program
 * @param entity
 * @returns True if the entity is a cookie parameter, false otherwise.
 */
function isCookieParam(program, entity) {
    return program.stateMap(HttpStateKeys.cookie).has(entity);
}
const $query = (context, entity, queryNameOrOptions) => {
    const paramName = typeof queryNameOrOptions === "string"
        ? queryNameOrOptions
        : (queryNameOrOptions?.name ?? entity.name);
    const userOptions = typeof queryNameOrOptions === "object" ? queryNameOrOptions : {};
    if (userOptions.format) {
        reportDeprecated(context.program, "The `format` option of `@query` decorator is deprecated. Use `explode: true` instead of `form` and `multi`. `csv` or `simple` is the default now.", entity);
    }
    const options = {
        type: "query",
        explode: userOptions.explode ?? (userOptions.format === "multi" || userOptions.format === "form"),
        format: userOptions.format,
        name: paramName,
    };
    if (entity.type.kind === "Model" &&
        isArrayModelType(context.program, entity.type) &&
        // eslint-disable-next-line @typescript-eslint/no-deprecated
        options.format === undefined) {
        // eslint-disable-next-line @typescript-eslint/no-deprecated
        options.format = userOptions.explode ? "multi" : "csv";
    }
    context.program.stateMap(HttpStateKeys.query).set(entity, options);
};
function getQueryParamOptions(program, entity) {
    return program.stateMap(HttpStateKeys.query).get(entity);
}
function getQueryParamName(program, entity) {
    return getQueryParamOptions(program, entity)?.name;
}
function isQueryParam(program, entity) {
    return program.stateMap(HttpStateKeys.query).has(entity);
}
const $path = (context, entity, paramNameOrOptions) => {
    const paramName = typeof paramNameOrOptions === "string"
        ? paramNameOrOptions
        : (paramNameOrOptions?.name ?? entity.name);
    const userOptions = typeof paramNameOrOptions === "object" ? paramNameOrOptions : {};
    const options = {
        type: "path",
        explode: userOptions.explode ?? false,
        allowReserved: userOptions.allowReserved ?? false,
        style: userOptions.style ?? "simple",
        name: paramName,
    };
    context.program.stateMap(HttpStateKeys.path).set(entity, options);
};
function getPathParamOptions(program, entity) {
    return program.stateMap(HttpStateKeys.path).get(entity);
}
function getPathParamName(program, entity) {
    return getPathParamOptions(program, entity)?.name;
}
function isPathParam(program, entity) {
    return program.stateMap(HttpStateKeys.path).has(entity);
}
const $body = (context, entity) => {
    context.program.stateSet(HttpStateKeys.body).add(entity);
};
const $bodyRoot = (context, entity) => {
    context.program.stateSet(HttpStateKeys.bodyRoot).add(entity);
};
const $bodyIgnore = (context, entity) => {
    context.program.stateSet(HttpStateKeys.bodyIgnore).add(entity);
};
function isBody(program, entity) {
    return program.stateSet(HttpStateKeys.body).has(entity);
}
function isBodyRoot(program, entity) {
    return program.stateSet(HttpStateKeys.bodyRoot).has(entity);
}
function isBodyIgnore(program, entity) {
    return program.stateSet(HttpStateKeys.bodyIgnore).has(entity);
}
const $multipartBody = (context, entity) => {
    context.program.stateSet(HttpStateKeys.multipartBody).add(entity);
};
function isMultipartBodyProperty(program, entity) {
    return program.stateSet(HttpStateKeys.multipartBody).has(entity);
}
const $statusCode = (context, entity) => {
    context.program.stateSet(HttpStateKeys.statusCode).add(entity);
    // eslint-disable-next-line @typescript-eslint/no-deprecated
    setLegacyStatusCodeState(context, entity);
};
/**
 * To not break we keep the legacy behavior of resolving the discrete status code in the decorator and saving them in the state.
 * @deprecated To remove. Added in October 2023 sprint.
 */
function setLegacyStatusCodeState(context, entity) {
    const codes = [];
    if (entity.type.kind === "String") {
        if (validStatusCode(context.program, entity.type.value, entity)) {
            codes.push(entity.type.value);
        }
    }
    else if (entity.type.kind === "Number") {
        if (validStatusCode(context.program, String(entity.type.value), entity)) {
            codes.push(String(entity.type.value));
        }
    }
    else if (entity.type.kind === "Union") {
        for (const variant of entity.type.variants.values()) {
            const option = variant.type;
            if (option.kind === "String") {
                if (validStatusCode(context.program, option.value, option)) {
                    codes.push(option.value);
                }
            }
            else if (option.kind === "Number") {
                if (validStatusCode(context.program, String(option.value), option)) {
                    codes.push(String(option.value));
                }
            }
        }
    }
    // Check status code value: 3 digits with first digit in [1-5]
    // Issue a diagnostic if not valid
    function validStatusCode(program, code, entity) {
        const statusCodePattern = /[1-5][0-9][0-9]/;
        if (code.match(statusCodePattern)) {
            return true;
        }
        reportDiagnostic(program, {
            code: "status-code-invalid",
            target: entity,
            messageId: "value",
        });
        return false;
    }
    context.program.stateMap(HttpStateKeys.statusCode).set(entity, codes);
}
/**
 * @deprecated DO NOT USE, for internal use only.
 */
function setStatusCode(program, entity, codes) {
    program.stateMap(HttpStateKeys.statusCode).set(entity, codes);
}
function isStatusCode(program, entity) {
    return program.stateMap(HttpStateKeys.statusCode).has(entity);
}
function getStatusCodesWithDiagnostics(program, type) {
    return getStatusCodesFromType(program, type, type);
}
function getStatusCodes(program, entity) {
    return ignoreDiagnostics(getStatusCodesWithDiagnostics(program, entity));
}
// Reference: https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
function getStatusCodeDescription(statusCode) {
    if (typeof statusCode === "object") {
        return rangeDescription(statusCode.start, statusCode.end);
    }
    const statusCodeNumber = typeof statusCode === "string" ? parseInt(statusCode, 10) : statusCode;
    switch (statusCodeNumber) {
        case 200:
            return "The request has succeeded.";
        case 201:
            return "The request has succeeded and a new resource has been created as a result.";
        case 202:
            return "The request has been accepted for processing, but processing has not yet completed.";
        case 204:
            return "There is no content to send for this request, but the headers may be useful. ";
        case 301:
            return "The URL of the requested resource has been changed permanently. The new URL is given in the response.";
        case 304:
            return "The client has made a conditional request and the resource has not been modified.";
        case 400:
            return "The server could not understand the request due to invalid syntax.";
        case 401:
            return "Access is unauthorized.";
        case 403:
            return "Access is forbidden.";
        case 404:
            return "The server cannot find the requested resource.";
        case 409:
            return "The request conflicts with the current state of the server.";
        case 412:
            return "Precondition failed.";
        case 503:
            return "Service unavailable.";
    }
    return rangeDescription(statusCodeNumber, statusCodeNumber);
}
function rangeDescription(start, end) {
    if (start >= 100 && end <= 199) {
        return "Informational";
    }
    else if (start >= 200 && end <= 299) {
        return "Successful";
    }
    else if (start >= 300 && end <= 399) {
        return "Redirection";
    }
    else if (start >= 400 && end <= 499) {
        return "Client error";
    }
    else if (start >= 500 && end <= 599) {
        return "Server error";
    }
    return undefined;
}
function setOperationVerb(context, entity, verb) {
    validateVerbUniqueOnNode(context, entity);
    context.program.stateMap(HttpStateKeys.verbs).set(entity, verb);
}
function validateVerbUniqueOnNode(context, type) {
    const verbDecorators = type.decorators.filter((x) => VERB_DECORATORS.includes(x.decorator) &&
        x.node?.kind === SyntaxKind.DecoratorExpression &&
        x.node?.parent === type.node);
    if (verbDecorators.length > 1) {
        reportDiagnostic(context.program, {
            code: "http-verb-duplicate",
            format: { entityName: type.name },
            target: context.decoratorTarget,
        });
        return false;
    }
    return true;
}
function getOperationVerb(program, entity) {
    return program.stateMap(HttpStateKeys.verbs).get(entity);
}
function createVerbDecorator(verb) {
    return (context, entity) => {
        setOperationVerb(context, entity, verb);
    };
}
const $get = createVerbDecorator("get");
const $put = createVerbDecorator("put");
const $post = createVerbDecorator("post");
const $patch = createVerbDecorator("patch");
const $delete = createVerbDecorator("delete");
const $head = createVerbDecorator("head");
const VERB_DECORATORS = [$get, $head, $post, $put, $patch, $delete];
/**
 * Configure the server url for the service.
 * @param context Decorator context
 * @param target Decorator target (must be a namespace)
 * @param description Description for this server.
 * @param parameters @optional Parameters to interpolate in the server url.
 */
const $server = (context, target, url, description, parameters) => {
    const params = extractParamsFromPath(url);
    const parameterMap = new Map(parameters?.properties ?? []);
    for (const declaredParam of params) {
        const param = parameterMap.get(declaredParam);
        if (!param) {
            reportDiagnostic(context.program, {
                code: "missing-server-param",
                format: { param: declaredParam },
                target: context.getArgumentTarget(0),
            });
            parameterMap.delete(declaredParam);
        }
    }
    let servers = context.program.stateMap(HttpStateKeys.servers).get(target);
    if (servers === undefined) {
        servers = [];
        context.program.stateMap(HttpStateKeys.servers).set(target, servers);
    }
    servers.push({ url, description, parameters: parameterMap });
};
function getServers(program, type) {
    return program.stateMap(HttpStateKeys.servers).get(type);
}
function $useAuth(context, entity, authConfig) {
    validateDecoratorUniqueOnNode(context, entity, $useAuth);
    const [auth, diagnostics] = extractAuthentication(context.program, authConfig);
    if (diagnostics.length > 0)
        context.program.reportDiagnostics(diagnostics);
    if (auth !== undefined) {
        setAuthentication(context.program, entity, auth);
    }
}
function setAuthentication(program, entity, auth) {
    program.stateMap(HttpStateKeys.authentication).set(entity, auth);
}
function extractAuthentication(program, type) {
    const diagnostics = createDiagnosticCollector();
    switch (type.kind) {
        case "Model":
            const auth = diagnostics.pipe(extractHttpAuthentication(program, type, type));
            if (auth === undefined)
                return diagnostics.wrap(undefined);
            return diagnostics.wrap({ options: [{ schemes: [auth] }] });
        case "Tuple":
            const option = diagnostics.pipe(extractHttpAuthenticationOption(program, type, type));
            return diagnostics.wrap({ options: [option] });
        case "Union":
            return extractHttpAuthenticationOptions(program, type, type);
        default:
            return [
                undefined,
                [
                    createDiagnostic({
                        code: "invalid-type-for-auth",
                        format: { kind: type.kind },
                        target: type,
                    }),
                ],
            ];
    }
}
function extractHttpAuthenticationOptions(program, tuple, diagnosticTarget) {
    const options = [];
    const diagnostics = createDiagnosticCollector();
    for (const variant of tuple.variants.values()) {
        const value = variant.type;
        switch (value.kind) {
            case "Model":
                const result = diagnostics.pipe(extractHttpAuthentication(program, value, diagnosticTarget));
                if (result !== undefined) {
                    options.push({ schemes: [result] });
                }
                break;
            case "Tuple":
                const option = diagnostics.pipe(extractHttpAuthenticationOption(program, value, diagnosticTarget));
                options.push(option);
                break;
            default:
                diagnostics.add(createDiagnostic({
                    code: "invalid-type-for-auth",
                    format: { kind: value.kind },
                    target: value,
                }));
        }
    }
    return diagnostics.wrap({ options });
}
function extractHttpAuthenticationOption(program, tuple, diagnosticTarget) {
    const schemes = [];
    const diagnostics = createDiagnosticCollector();
    for (const value of tuple.values) {
        switch (value.kind) {
            case "Model":
                const result = diagnostics.pipe(extractHttpAuthentication(program, value, diagnosticTarget));
                if (result !== undefined) {
                    schemes.push(result);
                }
                break;
            default:
                diagnostics.add(createDiagnostic({
                    code: "invalid-type-for-auth",
                    format: { kind: value.kind },
                    target: value,
                }));
        }
    }
    return diagnostics.wrap({ schemes });
}
function extractHttpAuthentication(program, modelType, diagnosticTarget) {
    const [result, diagnostics] = typespecTypeToJson(modelType, diagnosticTarget);
    if (result === undefined) {
        return [result, diagnostics];
    }
    const description = getDoc(program, modelType);
    const auth = result.type === "oauth2"
        ? extractOAuth2Auth(modelType, result)
        : { ...result, model: modelType };
    return [
        {
            ...auth,
            id: modelType.name || result.type,
            ...(description && { description }),
        },
        diagnostics,
    ];
}
function extractOAuth2Auth(modelType, data) {
    // Validation of OAuth2Flow models in this function is minimal because the
    // type system already validates whether the model represents a flow
    // configuration.  This code merely avoids runtime errors.
    const flows = Array.isArray(data.flows) && data.flows.every((x) => typeof x === "object")
        ? data.flows
        : [];
    const defaultScopes = Array.isArray(data.defaultScopes) ? data.defaultScopes : [];
    return {
        id: data.id,
        type: data.type,
        model: modelType,
        flows: flows.map((flow) => {
            const scopes = flow.scopes ? flow.scopes : defaultScopes;
            return {
                ...flow,
                scopes: scopes.map((x) => ({ value: x })),
            };
        }),
    };
}
function getAuthentication(program, entity) {
    return program.stateMap(HttpStateKeys.authentication).get(entity);
}
/**
 * `@route` defines the relative route URI for the target operation
 *
 * The first argument should be a URI fragment that may contain one or more path parameter fields.
 * If the namespace or interface that contains the operation is also marked with a `@route` decorator,
 * it will be used as a prefix to the route URI of the operation.
 *
 * `@route` can only be applied to operations, namespaces, and interfaces.
 */
const $route = (context, entity, path, parameters) => {
    validateDecoratorUniqueOnNode(context, entity, $route);
    // Handle the deprecated `shared` option
    let shared = false;
    const sharedValue = parameters?.properties.get("shared")?.type;
    if (sharedValue !== undefined) {
        reportDeprecated(context.program, "The `shared` option is deprecated, use the `@sharedRoute` decorator instead.", entity);
        // The type checker should have raised a diagnostic if the value isn't boolean
        if (sharedValue.kind === "Boolean") {
            shared = sharedValue.value;
        }
    }
    setRoute(context, entity, {
        path,
        shared,
    });
};
/**
 * `@sharedRoute` marks the operation as sharing a route path with other operations.
 *
 * When an operation is marked with `@sharedRoute`, it enables other operations to share the same
 * route path as long as those operations are also marked with `@sharedRoute`.
 *
 * `@sharedRoute` can only be applied directly to operations.
 */
const $sharedRoute = (context, entity) => {
    setSharedRoute(context.program, entity);
};
/**
 * Specifies if inapplicable metadata should be included in the payload for
 * the given entity. This is true by default unless changed by this
 * decorator.
 *
 * @param entity Target model, namespace, or model property. If applied to a
 *               model or namespace, applies recursively to child models,
 *               namespaces, and model properties unless overridden by
 *               applying this decorator to a child.
 *
 * @param value `true` to include inapplicable metadata in payload, false to
 *               exclude it.
 *
 * @see isApplicableMetadata
 *
 * @ignore Cause issue with conflicting function of same name for now
 */
function $includeInapplicableMetadataInPayload(context, entity, value) {
    if (!validateDecoratorTarget(context, entity, "@includeInapplicableMetadataInPayload", [
        "Namespace",
        "Model",
        "ModelProperty",
    ])) {
        return;
    }
    const state = context.program.stateMap(HttpStateKeys.includeInapplicableMetadataInPayload);
    state.set(entity, value);
}
/**
 * Determines if the given model property should be included in the payload if it is
 * inapplicable metadata.
 *
 * @see isApplicableMetadata
 * @see $includeInapplicableMetadataInPayload
 */
function includeInapplicableMetadataInPayload(program, property) {
    let e;
    for (e = property; e; e = e.kind === "ModelProperty" ? e.model : e.namespace) {
        const value = program.stateMap(HttpStateKeys.includeInapplicableMetadataInPayload).get(e);
        if (value !== undefined) {
            return value;
        }
    }
    return true;
}

/**
 * Resolve the authentication for a given operation.
 * @param program Program
 * @param operation Operation
 * @returns Authentication provided on the operation or containing interface or namespace.
 */
function getAuthenticationForOperation(program, operation) {
    const operationAuth = getAuthentication(program, operation);
    if (operationAuth) {
        return operationAuth;
    }
    if (operation.interface !== undefined) {
        const interfaceAuth = getAuthentication(program, operation.interface);
        if (interfaceAuth) {
            return interfaceAuth;
        }
    }
    let namespace = operation.namespace;
    while (namespace) {
        const namespaceAuth = getAuthentication(program, namespace);
        if (namespaceAuth) {
            return namespaceAuth;
        }
        namespace = namespace.namespace;
    }
    return undefined;
}
/**
 * Compute the authentication for a given service.
 * @param service Http Service
 * @returns The normalized authentication for a service.
 */
function resolveAuthentication(service) {
    let schemes = {};
    let defaultAuth = { options: [] };
    const operationsAuth = new Map();
    if (service.authentication) {
        const { newServiceSchemes, authOptions } = gatherAuth(service.authentication, {});
        schemes = newServiceSchemes;
        defaultAuth = authOptions;
    }
    for (const op of service.operations) {
        if (op.authentication) {
            const { newServiceSchemes, authOptions } = gatherAuth(op.authentication, schemes);
            schemes = newServiceSchemes;
            operationsAuth.set(op.operation, authOptions);
        }
    }
    return { schemes: Object.values(schemes), defaultAuth, operationsAuth };
}
function gatherAuth(authentication, serviceSchemes) {
    const newServiceSchemes = serviceSchemes;
    const authOptions = { options: [] };
    for (const option of authentication.options) {
        const authOption = { all: [] };
        for (const optionScheme of option.schemes) {
            const serviceScheme = serviceSchemes[optionScheme.id];
            let newServiceScheme = optionScheme;
            if (serviceScheme) {
                // If we've seen a different scheme by this id,
                // Make sure to not overwrite it
                if (!authsAreEqual(serviceScheme, optionScheme)) {
                    while (serviceSchemes[newServiceScheme.id]) {
                        newServiceScheme.id = newServiceScheme.id + "_";
                    }
                }
                // Merging scopes when encountering the same Oauth2 scheme
                else if (serviceScheme.type === "oauth2" && optionScheme.type === "oauth2") {
                    const x = mergeOAuthScopes(serviceScheme, optionScheme);
                    newServiceScheme = x;
                }
            }
            const httpAuthRef = makeHttpAuthRef(optionScheme, newServiceScheme);
            newServiceSchemes[newServiceScheme.id] = newServiceScheme;
            authOption.all.push(httpAuthRef);
        }
        authOptions.options.push(authOption);
    }
    return { newServiceSchemes, authOptions };
}
function makeHttpAuthRef(local, reference) {
    if (reference.type === "oauth2" && local.type === "oauth2") {
        const scopes = [];
        for (const flow of local.flows) {
            scopes.push(...flow.scopes.map((x) => x.value));
        }
        return { kind: "oauth2", auth: reference, scopes: scopes };
    }
    else if (reference.type === "noAuth") {
        return { kind: "noAuth", auth: reference };
    }
    else {
        return { kind: "any", auth: reference };
    }
}
function mergeOAuthScopes(scheme1, scheme2) {
    const flows = deepClone(scheme1.flows);
    flows.forEach((flow1, i) => {
        const flow2 = scheme2.flows[i];
        const scopes = Array.from(new Set(flow1.scopes.concat(flow2.scopes)));
        flows[i].scopes = scopes;
    });
    return {
        ...scheme1,
        flows,
    };
}
function ignoreScopes(scheme) {
    const flows = deepClone(scheme.flows);
    flows.forEach((flow) => {
        flow.scopes = [];
    });
    return {
        ...scheme,
        flows,
    };
}
function authsAreEqual(scheme1, scheme2) {
    const { model: _model1, ...withoutModel1 } = scheme1;
    const { model: _model2, ...withoutModel2 } = scheme2;
    if (withoutModel1.type === "oauth2" && withoutModel2.type === "oauth2") {
        return deepEquals(ignoreScopes(withoutModel1), ignoreScopes(withoutModel2));
    }
    return deepEquals(withoutModel1, withoutModel2);
}

/**
 * @deprecated Use `OperationProperty.kind === 'contentType'` instead.
 * Check if the given model property is the content type header.
 * @param program Program
 * @param property Model property.
 * @returns True if the model property is marked as a header and has the name `content-type`(case insensitive.)
 */
function isContentTypeHeader(program, property) {
    const headerName = getHeaderFieldName(program, property);
    return Boolean(headerName && headerName.toLowerCase() === "content-type");
}
/**
 * Resolve the content types from a model property by looking at the value.
 * @property property Model property
 * @returns List of contnet types and any diagnostics if there was an issue.
 */
function getContentTypes(property) {
    const diagnostics = createDiagnosticCollector();
    if (property.type.kind === "String") {
        return [[property.type.value], []];
    }
    else if (property.type.kind === "Union") {
        const contentTypes = [];
        for (const option of property.type.variants.values()) {
            if (option.type.kind === "String") {
                contentTypes.push(option.type.value);
            }
            else {
                diagnostics.add(createDiagnostic({
                    code: "content-type-string",
                    target: property,
                }));
                continue;
            }
        }
        return diagnostics.wrap(contentTypes);
    }
    else if (property.type.kind === "Scalar" && property.type.name === "string") {
        return [["*/*"], []];
    }
    return [[], [createDiagnostic({ code: "content-type-string", target: property })]];
}

/**
 * Find the type of a property in a model
 */
function getHttpProperty(program, property, path, options = {}) {
    const diagnostics = [];
    function createResult(opts) {
        return [{ ...opts, property, path }, diagnostics];
    }
    const annotations = {
        header: getHeaderFieldOptions(program, property),
        cookie: getCookieParamOptions(program, property),
        query: getQueryParamOptions(program, property),
        path: getPathParamOptions(program, property),
        body: isBody(program, property),
        bodyRoot: isBodyRoot(program, property),
        multipartBody: isMultipartBodyProperty(program, property),
        statusCode: isStatusCode(program, property),
    };
    const defined = Object.entries(annotations).filter((x) => !!x[1]);
    const implicit = options.implicitParameter?.(property);
    if (implicit && defined.length > 0) {
        if (implicit.type === "path" && annotations.path) {
            if (annotations.path.explode ||
                annotations.path.style !== "simple" ||
                annotations.path.allowReserved) {
                diagnostics.push(createDiagnostic({
                    code: "use-uri-template",
                    format: {
                        param: property.name,
                    },
                    target: property,
                }));
            }
        }
        else if (implicit.type === "query" && annotations.query) {
            if (annotations.query.explode) {
                diagnostics.push(createDiagnostic({
                    code: "use-uri-template",
                    format: {
                        param: property.name,
                    },
                    target: property,
                }));
            }
        }
        else {
            diagnostics.push(createDiagnostic({
                code: "incompatible-uri-param",
                format: {
                    param: property.name,
                    uriKind: implicit.type,
                    annotationKind: defined[0][0],
                },
                target: property,
            }));
        }
    }
    // if implicit just returns as it is. Validation above would have checked nothing was set explicitly apart from the type and that the type match
    if (implicit) {
        return createResult({
            kind: implicit.type,
            options: implicit,
            property,
        });
    }
    if (defined.length === 0) {
        return createResult({ kind: "bodyProperty" });
    }
    else if (defined.length > 1) {
        diagnostics.push(createDiagnostic({
            code: "operation-param-duplicate-type",
            format: { paramName: property.name, types: defined.map((x) => x[0]).join(", ") },
            target: property,
        }));
    }
    if (annotations.header) {
        if (annotations.header.name.toLowerCase() === "content-type") {
            return createResult({ kind: "contentType" });
        }
        else {
            return createResult({ kind: "header", options: annotations.header });
        }
    }
    else if (annotations.cookie) {
        return createResult({ kind: "cookie", options: annotations.cookie });
    }
    else if (annotations.query) {
        return createResult({ kind: "query", options: annotations.query });
    }
    else if (annotations.path) {
        return createResult({ kind: "path", options: annotations.path });
    }
    else if (annotations.statusCode) {
        return createResult({ kind: "statusCode" });
    }
    else if (annotations.body) {
        return createResult({ kind: "body" });
    }
    else if (annotations.bodyRoot) {
        return createResult({ kind: "bodyRoot" });
    }
    else if (annotations.multipartBody) {
        return createResult({ kind: "multipartBody" });
    }
    compilerAssert(false, `Unexpected http property type`);
}
/**
 * Walks the given input(request parameters or response) and return all the properties and where they should be included(header, query, path, body, as a body property, etc.)
 *
 * @param rootMapOut If provided, the map will be populated to link nested metadata properties to their root properties.
 */
function resolvePayloadProperties(program, type, visibility, disposition, options = {}) {
    const diagnostics = createDiagnosticCollector();
    const httpProperties = new Map();
    if (type.kind !== "Model" || type.properties.size === 0) {
        return diagnostics.wrap([]);
    }
    const visited = new Set();
    function checkModel(model, path) {
        visited.add(model);
        let foundBody = false;
        let foundBodyProperty = false;
        for (const property of walkPropertiesInherited(model)) {
            const propPath = [...path, property.name];
            if (!isVisible(program, property, visibility)) {
                continue;
            }
            let httpProperty = diagnostics.pipe(getHttpProperty(program, property, propPath, options));
            if (shouldTreatAsBodyProperty(httpProperty, disposition)) {
                httpProperty = { kind: "bodyProperty", property, path: propPath };
            }
            // Ignore cookies in response to avoid future breaking changes to @cookie.
            // https://github.com/microsoft/typespec/pull/4761#discussion_r1805082132
            if (httpProperty.kind === "cookie" && disposition === HttpPayloadDisposition.Response) {
                diagnostics.add(createDiagnostic({
                    code: "response-cookie-not-supported",
                    target: property,
                    format: { propName: property.name },
                }));
                continue;
            }
            if (httpProperty.kind === "body" ||
                httpProperty.kind === "bodyRoot" ||
                httpProperty.kind === "multipartBody") {
                foundBody = true;
            }
            if (!(httpProperty.kind === "body" || httpProperty.kind === "multipartBody") &&
                isModelWithProperties(property.type) &&
                !visited.has(property.type)) {
                if (checkModel(property.type, propPath)) {
                    foundBody = true;
                    continue;
                }
            }
            if (httpProperty.kind === "bodyProperty") {
                foundBodyProperty = true;
            }
            httpProperties.set(property, httpProperty);
        }
        return foundBody && !foundBodyProperty;
    }
    checkModel(type, []);
    return diagnostics.wrap([...httpProperties.values()]);
}
function isModelWithProperties(type) {
    return type.kind === "Model" && !type.indexer && type.properties.size > 0;
}
function shouldTreatAsBodyProperty(property, disposition) {
    switch (disposition) {
        case HttpPayloadDisposition.Request:
            return property.kind === "statusCode";
        case HttpPayloadDisposition.Response:
            return property.kind === "query" || property.kind === "path";
        case HttpPayloadDisposition.Multipart:
            return (property.kind === "path" || property.kind === "query" || property.kind === "statusCode");
        default:
            return false;
    }
}

/** @internal */
const namespace = "TypeSpec.Http.Private";
const $plainData = (context, entity) => {
    const { program } = context;
    const decoratorsToRemove = ["$header", "$body", "$query", "$path", "$statusCode"];
    const [headers, bodies, queries, paths, statusCodes] = [
        program.stateMap(HttpStateKeys.header),
        program.stateSet(HttpStateKeys.body),
        program.stateMap(HttpStateKeys.query),
        program.stateMap(HttpStateKeys.path),
        program.stateMap(HttpStateKeys.statusCode),
    ];
    for (const property of entity.properties.values()) {
        // Remove the decorators so that they do not run in the future, for example,
        // if this model is later spread into another.
        property.decorators = property.decorators.filter((d) => !decoratorsToRemove.includes(d.decorator.name));
        // Remove the impact the decorators already had on this model.
        headers.delete(property);
        bodies.delete(property);
        queries.delete(property);
        paths.delete(property);
        statusCodes.delete(property);
    }
};
const $httpFile = (context, target) => {
    context.program.stateSet(HttpStateKeys.file).add(target);
};
/**
 * Check if the given type is an `HttpFile`
 */
function isHttpFile(program, type) {
    return program.stateSet(HttpStateKeys.file).has(type);
}
function isOrExtendsHttpFile(program, type) {
    if (type.kind !== "Model") {
        return false;
    }
    let current = type;
    while (current) {
        if (isHttpFile(program, current)) {
            return true;
        }
        current = current.baseModel;
    }
    return false;
}
function getHttpFileModel(program, type) {
    if (type.kind !== "Model" || !isOrExtendsHttpFile(program, type)) {
        return undefined;
    }
    const contentType = getProperty(type, "contentType");
    const filename = getProperty(type, "filename");
    const contents = getProperty(type, "contents");
    return { contents, contentType, filename, type };
}
const $httpPart = (context, target, type, options) => {
    context.program.stateMap(HttpStateKeys.httpPart).set(target, { type, options });
};
/** Return the http part information on a model that is an `HttpPart` */
function getHttpPart(program, target) {
    return program.stateMap(HttpStateKeys.httpPart).get(target);
}
/** @internal */
const $decorators = {
    "TypeSpec.Http.Private": {
        httpFile: $httpFile,
        httpPart: $httpPart,
        plainData: $plainData,
    },
};

var f2 = /*#__PURE__*/Object.freeze({
    __proto__: null,
    $decorators: $decorators,
    getHttpFileModel: getHttpFileModel,
    getHttpPart: getHttpPart,
    isHttpFile: isHttpFile,
    isOrExtendsHttpFile: isOrExtendsHttpFile,
    namespace: namespace
});

/**
 * The disposition of a payload in an HTTP operation.
 */
var HttpPayloadDisposition;
(function (HttpPayloadDisposition) {
    /**
     * The payload appears in a request.
     */
    HttpPayloadDisposition[HttpPayloadDisposition["Request"] = 0] = "Request";
    /**
     * The payload appears in a response.
     */
    HttpPayloadDisposition[HttpPayloadDisposition["Response"] = 1] = "Response";
    /**
     * The payload appears in a multipart part.
     */
    HttpPayloadDisposition[HttpPayloadDisposition["Multipart"] = 2] = "Multipart";
})(HttpPayloadDisposition || (HttpPayloadDisposition = {}));
function resolveHttpPayload(program, type, visibility, disposition, options = {}) {
    const diagnostics = createDiagnosticCollector();
    const metadata = diagnostics.pipe(resolvePayloadProperties(program, type, visibility, disposition, options));
    const body = diagnostics.pipe(resolveBody(program, type, metadata, visibility, disposition));
    if (body) {
        if (body.contentTypes.includes("multipart/form-data") &&
            body.bodyKind === "single" &&
            body.type.kind !== "Model") {
            diagnostics.add(createDiagnostic({
                code: "multipart-model",
                target: body.property ?? type,
            }));
            return diagnostics.wrap({ body: undefined, metadata });
        }
    }
    return diagnostics.wrap({ body, metadata });
}
function resolveBody(program, requestOrResponseType, metadata, visibility, disposition) {
    const diagnostics = createDiagnosticCollector();
    const resolvedContentTypes = diagnostics.pipe(resolveContentTypes(program, metadata, disposition));
    const file = getHttpFileModel(program, requestOrResponseType);
    if (file !== undefined) {
        const file = getHttpFileModel(program, requestOrResponseType);
        return diagnostics.wrap({
            bodyKind: "single",
            contentTypes: diagnostics.pipe(getContentTypes(file.contentType)),
            contentTypeProperty: file.contentType,
            type: file.contents.type,
            isExplicit: false,
            containsMetadataAnnotations: false,
        });
    }
    // non-model or intrinsic/array model -> response body is response type
    if (requestOrResponseType.kind !== "Model" || isArrayModelType(program, requestOrResponseType)) {
        return diagnostics.wrap({
            bodyKind: "single",
            ...resolvedContentTypes,
            type: requestOrResponseType,
            isExplicit: false,
            containsMetadataAnnotations: false,
        });
    }
    // look for explicit body
    const resolvedBody = diagnostics.pipe(resolveExplicitBodyProperty(program, metadata, resolvedContentTypes, visibility, disposition));
    if (resolvedBody === undefined) {
        // Special case if the model as a parent model then we'll return an empty object as this is assumed to be a nominal type.
        // Special Case if the model has an indexer then it means it can return props so cannot be void.
        if (requestOrResponseType.baseModel || requestOrResponseType.indexer) {
            return diagnostics.wrap({
                bodyKind: "single",
                ...resolvedContentTypes,
                type: requestOrResponseType,
                isExplicit: false,
                containsMetadataAnnotations: false,
            });
        }
        // Special case for legacy purposes if the return type is an empty model with only @discriminator("xyz")
        // Then we still want to return that object as it technically always has a body with that implicit property.
        if (requestOrResponseType.derivedModels.length > 0 &&
            getDiscriminator(program, requestOrResponseType)) {
            return diagnostics.wrap({
                bodyKind: "single",
                ...resolvedContentTypes,
                type: requestOrResponseType,
                isExplicit: false,
                containsMetadataAnnotations: false,
            });
        }
    }
    const unannotatedProperties = filterModelProperties(program, requestOrResponseType, (p) => metadata.some((x) => x.property === p && x.kind === "bodyProperty"));
    if (unannotatedProperties.properties.size > 0) {
        if (resolvedBody === undefined) {
            return diagnostics.wrap({
                bodyKind: "single",
                ...resolvedContentTypes,
                type: unannotatedProperties,
                isExplicit: false,
                containsMetadataAnnotations: false,
            });
        }
        else {
            diagnostics.add(createDiagnostic({
                code: "duplicate-body",
                messageId: "bodyAndUnannotated",
                target: requestOrResponseType,
            }));
        }
    }
    if (resolvedBody === undefined && resolvedContentTypes.contentTypeProperty) {
        diagnostics.add(createDiagnostic({
            code: "content-type-ignored",
            target: resolvedContentTypes.contentTypeProperty,
        }));
    }
    return diagnostics.wrap(resolvedBody);
}
function resolveContentTypes(program, metadata, disposition) {
    for (const prop of metadata) {
        if (prop.kind === "contentType") {
            const [contentTypes, diagnostics] = getContentTypes(prop.property);
            return [{ contentTypes, contentTypeProperty: prop.property }, diagnostics];
        }
    }
    switch (disposition) {
        case HttpPayloadDisposition.Multipart:
            // Figure this out later
            return [{ contentTypes: [] }, []];
        default:
            return [{ contentTypes: ["application/json"] }, []];
    }
}
function resolveExplicitBodyProperty(program, metadata, resolvedContentTypes, visibility, disposition) {
    const diagnostics = createDiagnosticCollector();
    let resolvedBody;
    const duplicateTracker = new DuplicateTracker();
    for (const item of metadata) {
        if (item.kind === "body" || item.kind === "bodyRoot" || item.kind === "multipartBody") {
            duplicateTracker.track("body", item.property);
        }
        switch (item.kind) {
            case "body":
            case "bodyRoot":
                let containsMetadataAnnotations = false;
                if (item.kind === "body") {
                    const valid = diagnostics.pipe(validateBodyProperty(program, item.property, disposition));
                    containsMetadataAnnotations = !valid;
                }
                if (resolvedBody === undefined) {
                    resolvedBody = {
                        bodyKind: "single",
                        ...resolvedContentTypes,
                        type: item.property.type,
                        isExplicit: item.kind === "body",
                        containsMetadataAnnotations,
                        property: item.property,
                        parameter: item.property,
                    };
                }
                break;
            case "multipartBody":
                resolvedBody = diagnostics.pipe(resolveMultiPartBody(program, item.property, resolvedContentTypes, visibility));
                break;
        }
    }
    for (const [_, items] of duplicateTracker.entries()) {
        for (const prop of items) {
            diagnostics.add(createDiagnostic({
                code: "duplicate-body",
                target: prop,
            }));
        }
    }
    return diagnostics.wrap(resolvedBody);
}
/** Validate a property marked with `@body` */
function validateBodyProperty(program, property, disposition) {
    const diagnostics = createDiagnosticCollector();
    navigateType(property.type, {
        modelProperty: (prop) => {
            const kind = isHeader(program, prop)
                ? "header"
                : // also emit metadata-ignored for response cookie
                    (disposition === HttpPayloadDisposition.Request ||
                        disposition === HttpPayloadDisposition.Response) &&
                        isCookieParam(program, prop)
                        ? "cookie"
                        : (disposition === HttpPayloadDisposition.Request ||
                            disposition === HttpPayloadDisposition.Multipart) &&
                            isQueryParam(program, prop)
                            ? "query"
                            : disposition === HttpPayloadDisposition.Request && isPathParam(program, prop)
                                ? "path"
                                : disposition === HttpPayloadDisposition.Response && isStatusCode(program, prop)
                                    ? "statusCode"
                                    : undefined;
            if (kind) {
                diagnostics.add(createDiagnostic({
                    code: "metadata-ignored",
                    format: { kind },
                    target: prop,
                }));
            }
        },
    }, {});
    return diagnostics.wrap(diagnostics.diagnostics.length === 0);
}
function resolveMultiPartBody(program, property, resolvedContentTypes, visibility) {
    const type = property.type;
    if (type.kind === "Model") {
        return resolveMultiPartBodyFromModel(program, property, type, resolvedContentTypes, visibility);
    }
    else if (type.kind === "Tuple") {
        return resolveMultiPartBodyFromTuple(program, property, type, resolvedContentTypes, visibility);
    }
    else {
        return [undefined, [createDiagnostic({ code: "multipart-model", target: property })]];
    }
}
function resolveMultiPartBodyFromModel(program, property, type, resolvedContentTypes, visibility) {
    const diagnostics = createDiagnosticCollector();
    const parts = [];
    for (const item of type.properties.values()) {
        const part = diagnostics.pipe(resolvePartOrParts(program, item.type, visibility));
        if (part) {
            parts.push({ ...part, name: part.name ?? item.name, optional: item.optional });
        }
    }
    return diagnostics.wrap({
        bodyKind: "multipart",
        ...resolvedContentTypes,
        parts,
        property,
        type,
    });
}
const multipartContentTypes = {
    formData: "multipart/form-data",
    mixed: "multipart/mixed",
};
const multipartContentTypesValues = Object.values(multipartContentTypes);
function resolveMultiPartBodyFromTuple(program, property, type, resolvedContentTypes, visibility) {
    const diagnostics = createDiagnosticCollector();
    const parts = [];
    for (const contentType of resolvedContentTypes.contentTypes) {
        if (!multipartContentTypesValues.includes(contentType)) {
            diagnostics.add(createDiagnostic({
                code: "multipart-invalid-content-type",
                format: { contentType, supportedContentTypes: multipartContentTypesValues.join(", ") },
                target: type,
            }));
        }
    }
    for (const [index, item] of type.values.entries()) {
        const part = diagnostics.pipe(resolvePartOrParts(program, item, visibility));
        if (part?.name === undefined &&
            resolvedContentTypes.contentTypes.includes(multipartContentTypes.formData)) {
            diagnostics.add(createDiagnostic({
                code: "formdata-no-part-name",
                target: type.node.values[index],
            }));
        }
        if (part) {
            parts.push(part);
        }
    }
    return diagnostics.wrap({
        bodyKind: "multipart",
        ...resolvedContentTypes,
        parts,
        property,
        type,
    });
}
function resolvePartOrParts(program, type, visibility) {
    if (type.kind === "Model" && isArrayModelType(program, type)) {
        const [part, diagnostics] = resolvePart(program, type.indexer.value, visibility);
        if (part) {
            return [{ ...part, multi: true }, diagnostics];
        }
        return [part, diagnostics];
    }
    else {
        return resolvePart(program, type, visibility);
    }
}
function resolvePart(program, type, visibility) {
    const part = getHttpPart(program, type);
    if (part) {
        const file = getHttpFileModel(program, part.type);
        if (file !== undefined) {
            return getFilePart(part.options.name, file);
        }
        let [{ body, metadata }, diagnostics] = resolveHttpPayload(program, part.type, visibility, HttpPayloadDisposition.Multipart);
        if (body === undefined) {
            return [undefined, diagnostics];
        }
        else if (body.bodyKind === "multipart") {
            return [undefined, [createDiagnostic({ code: "multipart-nested", target: type })]];
        }
        if (body.contentTypes.length === 0) {
            body = { ...body, contentTypes: resolveDefaultContentTypeForPart(program, body.type) };
        }
        return [
            {
                multi: false,
                name: part.options.name,
                body,
                optional: false,
                headers: metadata.filter((x) => x.kind === "header"),
            },
            diagnostics,
        ];
    }
    return [undefined, [createDiagnostic({ code: "multipart-part", target: type })]];
}
function getFilePart(name, file) {
    const [contentTypes, diagnostics] = getContentTypes(file.contentType);
    return [
        {
            multi: false,
            name,
            body: {
                bodyKind: "single",
                contentTypeProperty: file.contentType,
                contentTypes: contentTypes,
                type: file.contents.type,
                isExplicit: false,
                containsMetadataAnnotations: false,
            },
            filename: file.filename,
            optional: false,
            headers: [],
        },
        diagnostics,
    ];
}
function resolveDefaultContentTypeForPart(program, type) {
    function resolve(type) {
        if (type.kind === "Scalar") {
            const encodedAs = getEncode(program, type);
            if (encodedAs) {
                type = encodedAs.type;
            }
            if (ignoreDiagnostics(program.checker.isTypeAssignableTo(
            // eslint-disable-next-line @typescript-eslint/no-deprecated
            type.projectionBase ?? type, program.checker.getStdType("bytes"), type))) {
                return ["application/octet-stream"];
            }
            else {
                return ["text/plain"];
            }
        }
        else if (type.kind === "Union") {
            return [...type.variants.values()].flatMap((x) => resolve(x.type));
        }
        else {
            return ["application/json"];
        }
    }
    return [...new Set(resolve(type))];
}

/**
 * Get the responses for a given operation.
 */
function getResponsesForOperation(program, operation) {
    const diagnostics = createDiagnosticCollector();
    const responseType = operation.returnType;
    const responses = new ResponseIndex();
    if (responseType.kind === "Union") {
        for (const option of responseType.variants.values()) {
            if (isNullType(option.type)) {
                // TODO how should we treat this? https://github.com/microsoft/typespec/issues/356
                continue;
            }
            processResponseType(program, diagnostics, operation, responses, option.type);
        }
    }
    else {
        processResponseType(program, diagnostics, operation, responses, responseType);
    }
    return diagnostics.wrap(responses.values());
}
/**
 * Class keeping an index of all the response by status code
 */
class ResponseIndex {
    #index = new Map();
    get(statusCode) {
        return this.#index.get(this.#indexKey(statusCode));
    }
    set(statusCode, response) {
        this.#index.set(this.#indexKey(statusCode), response);
    }
    values() {
        return [...this.#index.values()];
    }
    #indexKey(statusCode) {
        if (typeof statusCode === "number" || statusCode === "*") {
            return String(statusCode);
        }
        else {
            return `${statusCode.start}-${statusCode.end}`;
        }
    }
}
function processResponseType(program, diagnostics, operation, responses, responseType) {
    // Get body
    let { body: resolvedBody, metadata } = diagnostics.pipe(resolveHttpPayload(program, responseType, Visibility.Read, HttpPayloadDisposition.Response));
    // Get explicity defined status codes
    const statusCodes = diagnostics.pipe(getResponseStatusCodes(program, responseType, metadata));
    // Get response headers
    const headers = getResponseHeaders(program, metadata);
    // If there is no explicit status code, check if it should be 204
    if (statusCodes.length === 0) {
        if (isErrorModel(program, responseType)) {
            statusCodes.push("*");
        }
        else if (isVoidType(responseType)) {
            resolvedBody = undefined;
            statusCodes.push(204); // Only special case for 204 is op test(): void;
        }
        else if (resolvedBody === undefined || isVoidType(resolvedBody.type)) {
            resolvedBody = undefined;
            statusCodes.push(200);
        }
        else {
            statusCodes.push(200);
        }
    }
    // Put them into currentEndpoint.responses
    for (const statusCode of statusCodes) {
        // the first model for this statusCode/content type pair carries the
        // description for the endpoint. This could probably be improved.
        const response = responses.get(statusCode) ?? {
            statusCode: typeof statusCode === "object" ? "*" : String(statusCode),
            statusCodes: statusCode,
            type: responseType,
            description: getResponseDescription(program, operation, responseType, statusCode, metadata),
            responses: [],
        };
        if (resolvedBody !== undefined) {
            response.responses.push({
                body: resolvedBody,
                headers,
                properties: metadata,
            });
        }
        else {
            response.responses.push({ headers, properties: metadata });
        }
        responses.set(statusCode, response);
    }
}
/**
 * Get explicity defined status codes from response type and metadata
 * Return is an array of strings, possibly empty, which indicates no explicitly defined status codes.
 * We do not check for duplicates here -- that will be done by the caller.
 */
function getResponseStatusCodes(program, responseType, metadata) {
    const codes = [];
    const diagnostics = createDiagnosticCollector();
    let statusFound = false;
    for (const prop of metadata) {
        if (prop.kind === "statusCode") {
            if (statusFound) {
                reportDiagnostic(program, {
                    code: "multiple-status-codes",
                    target: responseType,
                });
            }
            statusFound = true;
            codes.push(...diagnostics.pipe(getStatusCodesWithDiagnostics(program, prop.property)));
        }
    }
    // This is only needed to retrieve the * status code set by @defaultResponse.
    // https://github.com/microsoft/typespec/issues/2485
    if (responseType.kind === "Model") {
        for (let t = responseType; t; t = t.baseModel) {
            codes.push(...getExplicitSetStatusCode(program, t));
        }
    }
    return diagnostics.wrap(codes);
}
function getExplicitSetStatusCode(program, entity) {
    return program.stateMap(HttpStateKeys.statusCode).get(entity) ?? [];
}
/**
 * Get response headers from response metadata
 */
function getResponseHeaders(program, metadata) {
    const responseHeaders = {};
    for (const prop of metadata) {
        if (prop.kind === "header") {
            responseHeaders[prop.options.name] = prop.property;
        }
    }
    return responseHeaders;
}
function isResponseEnvelope(metadata) {
    return metadata.some((prop) => prop.kind === "body" ||
        prop.kind === "bodyRoot" ||
        prop.kind === "multipartBody" ||
        prop.kind === "statusCode");
}
function getResponseDescription(program, operation, responseType, statusCode, metadata) {
    // NOTE: If the response type is an envelope and not the same as the body
    // type, then use its @doc as the response description. However, if the
    // response type is the same as the body type, then use the default status
    // code description and don't duplicate the schema description of the body
    // as the response description. This allows more freedom to change how
    // TypeSpec is expressed in semantically equivalent ways without causing
    // the output to change unnecessarily.
    if (isResponseEnvelope(metadata)) {
        const desc = getDoc(program, responseType);
        if (desc) {
            return desc;
        }
    }
    const desc = isErrorModel(program, responseType)
        ? getErrorsDoc(program, operation)
        : getReturnsDoc(program, operation);
    if (desc) {
        return desc;
    }
    return getStatusCodeDescription(statusCode);
}

/**
 * Return the Http Operation details for a given TypeSpec operation.
 * @param operation Operation
 * @param options Optional option on how to resolve the http details.
 */
function getHttpOperation(program, operation, options) {
    return getHttpOperationInternal(program, operation, options, new Map());
}
/**
 * Get all the Http Operation in the given container.
 * @param program Program
 * @param container Namespace or interface containing operations
 * @param options Resolution options
 * @returns
 */
function listHttpOperationsIn(program, container, options) {
    const diagnostics = createDiagnosticCollector();
    const operations = listOperationsIn(container, options?.listOptions);
    const cache = new Map();
    const httpOperations = operations.map((x) => diagnostics.pipe(getHttpOperationInternal(program, x, options, cache)));
    return diagnostics.wrap(httpOperations);
}
/**
 * Returns all the services defined.
 */
function getAllHttpServices(program, options) {
    const diagnostics = createDiagnosticCollector();
    const serviceNamespaces = listServices(program);
    const services = serviceNamespaces.map((x) => diagnostics.pipe(getHttpService(program, x.type, options)));
    if (serviceNamespaces.length === 0) {
        services.push(diagnostics.pipe(getHttpService(program, program.getGlobalNamespaceType(), options)));
    }
    return diagnostics.wrap(services);
}
function getHttpService(program, serviceNamespace, options) {
    const diagnostics = createDiagnosticCollector();
    const httpOperations = diagnostics.pipe(listHttpOperationsIn(program, serviceNamespace, {
        ...options,
        listOptions: {
            recursive: serviceNamespace !== program.getGlobalNamespaceType(),
        },
    }));
    const authentication = getAuthentication(program, serviceNamespace);
    validateProgram(program, diagnostics);
    validateRouteUnique(program, diagnostics, httpOperations);
    const service = {
        namespace: serviceNamespace,
        operations: httpOperations,
        authentication: authentication,
    };
    return diagnostics.wrap(service);
}
/**
 * @deprecated use `getAllHttpServices` instead
 */
function getAllRoutes(program, options) {
    const [services, diagnostics] = getAllHttpServices(program, options);
    return [services[0].operations, diagnostics];
}
function reportIfNoRoutes(program, routes) {
    if (routes.length === 0) {
        navigateProgram(program, {
            namespace: (namespace) => {
                if (namespace.operations.size > 0) {
                    reportDiagnostic(program, {
                        code: "no-service-found",
                        format: {
                            namespace: namespace.name,
                        },
                        target: namespace,
                    });
                }
            },
        });
    }
}
function validateRouteUnique(program, diagnostics, operations) {
    const grouped = new Map();
    for (const operation of operations) {
        const { verb, path } = operation;
        if (operation.overloading !== undefined && isOverloadSameEndpoint(operation)) {
            continue;
        }
        if (isSharedRoute(program, operation.operation)) {
            continue;
        }
        let map = grouped.get(path);
        if (map === undefined) {
            map = new Map();
            grouped.set(path, map);
        }
        let list = map.get(verb);
        if (list === undefined) {
            list = [];
            map.set(verb, list);
        }
        list.push(operation);
    }
    for (const [path, map] of grouped) {
        for (const [verb, routes] of map) {
            if (routes.length >= 2) {
                for (const route of routes) {
                    diagnostics.add(createDiagnostic({
                        code: "duplicate-operation",
                        format: { path, verb, operationName: route.operation.name },
                        target: route.operation,
                    }));
                }
            }
        }
    }
}
function isOverloadSameEndpoint(overload) {
    return overload.path === overload.overloading.path && overload.verb === overload.overloading.verb;
}
function getHttpOperationInternal(program, operation, options, cache) {
    const existing = cache.get(operation);
    if (existing) {
        return [existing, []];
    }
    const diagnostics = createDiagnosticCollector();
    const httpOperationRef = { operation };
    cache.set(operation, httpOperationRef);
    const overloadBase = getOverloadedOperation(program, operation);
    let overloading;
    if (overloadBase) {
        overloading = httpOperationRef.overloading = diagnostics.pipe(getHttpOperationInternal(program, overloadBase, options, cache));
    }
    const route = diagnostics.pipe(resolvePathAndParameters(program, operation, overloading, options ?? {}));
    const responses = diagnostics.pipe(getResponsesForOperation(program, operation));
    const authentication = getAuthenticationForOperation(program, operation);
    const httpOperation = {
        path: route.path,
        uriTemplate: route.uriTemplate,
        pathSegments: [],
        verb: route.parameters.verb,
        container: operation.interface ?? operation.namespace ?? program.getGlobalNamespaceType(),
        parameters: route.parameters,
        responses,
        operation,
        authentication,
    };
    Object.assign(httpOperationRef, httpOperation);
    const overloads = getOverloads(program, operation);
    if (overloads) {
        httpOperationRef.overloads = overloads.map((x) => diagnostics.pipe(getHttpOperationInternal(program, x, options, cache)));
    }
    return diagnostics.wrap(httpOperationRef);
}
function validateProgram(program, diagnostics) {
    navigateProgram(program, {
        modelProperty(property) {
            checkForUnsupportedVisibility(property);
        },
    });
    // NOTE: This is intentionally not checked in the visibility decorator
    // itself as that would be a layering violation, putting a REST
    // interpretation of visibility into the core.
    function checkForUnsupportedVisibility(property) {
        // eslint-disable-next-line @typescript-eslint/no-deprecated
        if (getVisibility(program, property)?.includes("write")) {
            // NOTE: Check for name equality instead of function equality
            // to deal with multiple copies of core being used.
            const decorator = property.decorators.find((d) => d.decorator.name === $visibility.name);
            const arg = decorator?.args.find((a) => a.node?.kind === SyntaxKind.StringLiteral && a.node.value === "write");
            const target = arg?.node ?? property;
            diagnostics.add(createDiagnostic({ code: "write-visibility-not-supported", target }));
        }
    }
}

/**
 * Flags enum representation of well-known visibilities that are used in
 * REST API.
 */
var Visibility;
(function (Visibility) {
    Visibility[Visibility["Read"] = 1] = "Read";
    Visibility[Visibility["Create"] = 2] = "Create";
    Visibility[Visibility["Update"] = 4] = "Update";
    Visibility[Visibility["Delete"] = 8] = "Delete";
    Visibility[Visibility["Query"] = 16] = "Query";
    Visibility[Visibility["None"] = 0] = "None";
    Visibility[Visibility["All"] = 31] = "All";
    /**
     * Additional flag to indicate when something is nested in a collection
     * and therefore no metadata is applicable.
     *
     * Never use this flag. It is used internally by the HTTP core.
     */
    Visibility[Visibility["Item"] = 1048576] = "Item";
    /**
     * Additional flag to indicate when the verb is path and therefore
     * will have fields made optional if request visibility includes update.
     *
     * Never use this flag. It is used internally by the HTTP core.
     */
    Visibility[Visibility["Patch"] = 2097152] = "Patch";
    /**
     * Additional flag to indicate that legacy parameter visibility behavior
     * should be used. This disables effective optionality for the body of
     * PATCH operations, and considers only properties that do not have _explicit_
     * visibility visible. This flag is activated by default when an operation
     * uses `@parameterVisibility` without arguments, and should not be enabled
     * in any other circumstances.
     *
     * Never use this flag. It is used internally by the HTTP core.
     */
    Visibility[Visibility["LegacyParameterVisibility"] = 4194304] = "LegacyParameterVisibility";
    /**
     * Additional flags to indicate the treatment of properties in specific contexts.
     *
     * Never use these flags. They are used internally by the HTTP core.
     */
    Visibility[Visibility["Synthetic"] = 7340032] = "Synthetic";
})(Visibility || (Visibility = {}));
const visibilityToArrayMap = new Map();
function visibilityToArray(visibility) {
    // Synthetic flags are not real visibilities.
    visibility &= ~Visibility.Synthetic;
    let result = visibilityToArrayMap.get(visibility);
    if (!result) {
        result = [];
        if (visibility & Visibility.Read) {
            result.push("read");
        }
        if (visibility & Visibility.Create) {
            result.push("create");
        }
        if (visibility & Visibility.Update) {
            result.push("update");
        }
        if (visibility & Visibility.Delete) {
            result.push("delete");
        }
        if (visibility & Visibility.Query) {
            result.push("query");
        }
        compilerAssert(result.length > 0 || visibility === Visibility.None, "invalid visibility");
        visibilityToArrayMap.set(visibility, result);
    }
    return result;
}
function filterToVisibility(program, filter) {
    const Lifecycle = getLifecycleVisibilityEnum(program);
    compilerAssert(!filter.all, "Unexpected: `all` constraint in visibility filter passed to filterToVisibility");
    compilerAssert(!filter.none, "Unexpected: `none` constraint in visibility filter passed to filterToVisibility");
    if (!filter.any) {
        return Visibility.All;
    }
    else {
        let visibility = Visibility.None;
        for (const modifierConstraint of filter.any ?? []) {
            if (modifierConstraint.enum !== Lifecycle)
                continue;
            switch (modifierConstraint.name) {
                case "Read":
                    visibility |= Visibility.Read;
                    break;
                case "Create":
                    visibility |= Visibility.Create;
                    break;
                case "Update":
                    visibility |= Visibility.Update;
                    break;
                case "Delete":
                    visibility |= Visibility.Delete;
                    break;
                case "Query":
                    visibility |= Visibility.Query;
                    break;
                default:
                    compilerAssert(false, `Unreachable: unrecognized Lifecycle visibility member: '${modifierConstraint.name}'`);
            }
        }
        return visibility;
    }
}
const VISIBILITY_FILTER_CACHE_MAP = new WeakMap();
function getVisibilityFilterCache(program) {
    let cache = VISIBILITY_FILTER_CACHE_MAP.get(program);
    if (!cache) {
        cache = new Map();
        VISIBILITY_FILTER_CACHE_MAP.set(program, cache);
    }
    return cache;
}
/**
 * Convert an HTTP visibility to a visibility filter that can be used to test core visibility and applied to a model.
 *
 * The Item and Patch visibility flags are ignored.
 *
 * @param program - the Program we're working in
 * @param visibility - the visibility to convert to a filter
 * @returns a VisibilityFilter object that selects properties having any of the given visibility flags
 */
function visibilityToFilter(program, visibility) {
    // Synthetic flags are not real visibilities.
    visibility &= ~Visibility.Synthetic;
    if (visibility === Visibility.All)
        return {};
    const cache = getVisibilityFilterCache(program);
    let filter = cache.get(visibility);
    if (!filter) {
        const LifecycleEnum = getLifecycleVisibilityEnum(program);
        const Lifecycle = {
            Create: LifecycleEnum.members.get("Create"),
            Read: LifecycleEnum.members.get("Read"),
            Update: LifecycleEnum.members.get("Update"),
            Delete: LifecycleEnum.members.get("Delete"),
            Query: LifecycleEnum.members.get("Query"),
        };
        const any = new Set();
        if (visibility & Visibility.Read) {
            any.add(Lifecycle.Read);
        }
        if (visibility & Visibility.Create) {
            any.add(Lifecycle.Create);
        }
        if (visibility & Visibility.Update) {
            any.add(Lifecycle.Update);
        }
        if (visibility & Visibility.Delete) {
            any.add(Lifecycle.Delete);
        }
        if (visibility & Visibility.Query) {
            any.add(Lifecycle.Query);
        }
        compilerAssert(any.size > 0 || visibility === Visibility.None, "invalid visibility");
        filter = { any };
        cache.set(visibility, filter);
    }
    return filter;
}
/**
 * Provides a naming suffix to create a unique name for a type with this
 * visibility.
 *
 * The canonical visibility (default Visibility.Read) gets empty suffix,
 * otherwise visibilities are joined in pascal-case with `Or`. And `Item` is
 * if `Visibility.Item` is produced.
 *
 * Examples (with canonicalVisibility = Visibility.Read):
 *  - Visibility.Read => ""
 *  - Visibility.Update => "Update"
 *  - Visibility.Create | Visibility.Update => "CreateOrUpdate"
 *  - Visibility.Create | Visibility.Item => "CreateItem"
 *  - Visibility.Create | Visibility.Update | Visibility.Item => "CreateOrUpdateItem"
 *  */
function getVisibilitySuffix(visibility, canonicalVisibility = Visibility.All) {
    let suffix = "";
    if ((visibility & ~Visibility.Synthetic) !== canonicalVisibility) {
        const visibilities = visibilityToArray(visibility);
        suffix += visibilities.map((v) => v[0].toUpperCase() + v.slice(1)).join("Or");
    }
    if (visibility & Visibility.Item) {
        suffix += "Item";
    }
    return suffix;
}
/**
 * Determines the visibility to use for a request with the given verb.
 *
 * - GET | HEAD => Visibility.Query
 * - POST => Visibility.Update
 * - PUT => Visibility.Create | Update
 * - DELETE => Visibility.Delete
 */
function getDefaultVisibilityForVerb(verb) {
    switch (verb) {
        case "get":
        case "head":
            return Visibility.Query;
        case "post":
            return Visibility.Create;
        case "put":
            return Visibility.Create | Visibility.Update;
        case "patch":
            return Visibility.Update;
        case "delete":
            return Visibility.Delete;
        default:
            compilerAssert(false, `Unreachable: unrecognized HTTP verb: '${verb}'`);
    }
}
/**
 * Determines the visibility to use for a request with the given verb.
 *
 * - GET | HEAD => Visibility.Query
 * - POST => Visibility.Create
 * - PATCH => Visibility.Update
 * - PUT => Visibility.Create | Update
 * - DELETE => Visibility.Delete
 * @param verb The HTTP verb for the operation.
 * @deprecated Use `resolveRequestVisibility` instead, or if you only want the default visibility for a verb, `getDefaultVisibilityForVerb`.
 * @returns The applicable parameter visibility or visibilities for the request.
 */
function getRequestVisibility(verb) {
    let visibility = getDefaultVisibilityForVerb(verb);
    // If the verb is PATCH, then we need to add the patch flag to the visibility in order for
    // later processes to properly apply it
    if (verb === "patch") {
        visibility |= Visibility.Patch;
    }
    return visibility;
}
function HttpVisibilityProvider(verbOrParameterOptions) {
    const hasVerb = typeof verbOrParameterOptions === "string";
    return {
        parameters: (program, operation) => {
            let verb = hasVerb
                ? verbOrParameterOptions
                : (verbOrParameterOptions?.verbSelector?.(program, operation) ??
                    getOperationVerb(program, operation));
            if (!verb) {
                const [httpOperation] = getHttpOperation(program, operation);
                verb = httpOperation.verb;
            }
            return visibilityToFilter(program, getDefaultVisibilityForVerb(verb));
        },
        returnType: (program, _) => {
            const Read = getLifecycleVisibilityEnum(program).members.get("Read");
            // For return types, we always use Read visibility in HTTP.
            return { any: new Set([Read]) };
        },
    };
}
// Hidden internal symbol to mark that parameter visibility was empty. This is used by HTTP
// to set the SkipEffectiveOptionality flag. This is a hack.
const parameterVisibilityIsEmpty = Symbol.for("TypeSpec.Visibility.ParameterVisibilityIsEmpty");
/**
 * Returns the applicable parameter visibility or visibilities for the request if `@requestVisibility` was used.
 * Otherwise, returns the default visibility based on the HTTP verb for the operation.
 * @param operation The TypeSpec Operation for the request.
 * @param verb The HTTP verb for the operation.
 * @returns The applicable parameter visibility or visibilities for the request.
 */
function resolveRequestVisibility(program, operation, verb) {
    // WARNING: This is the only place where we call HttpVisibilityProvider _WITHIN_ the HTTP implementation itself. We
    // _must_ provide the verb directly to the function as the first argument. If the verb is not provided directly, the
    // provider calls getHttpOperation to resolve the verb. Since the current function is called from getHttpOperation, it
    // will cause a stack overflow if the version of HttpVisibilityProvider we use here has to resolve the verb itself.
    const parameterVisibilityFilter = getParameterVisibilityFilter(program, operation, HttpVisibilityProvider(verb));
    let visibility = filterToVisibility(program, parameterVisibilityFilter);
    // If the verb is PATCH, then we need to add the patch flag to the visibility in order for
    // later processes to properly apply it.
    if (verb === "patch") {
        visibility |= Visibility.Patch;
    }
    const isEmptyParameterVisibility = program.stateSet(parameterVisibilityIsEmpty).has(operation);
    if (isEmptyParameterVisibility) {
        visibility |= Visibility.LegacyParameterVisibility;
    }
    return visibility;
}
/**
 * Determines if a property is metadata. A property is defined to be
 * metadata if it is marked `@header`, `@cookie`, `@query`, `@path`, or `@statusCode`.
 */
function isMetadata(program, property) {
    return (isHeader(program, property) ||
        isCookieParam(program, property) ||
        isQueryParam(program, property) ||
        isPathParam(program, property) ||
        isStatusCode(program, property));
}
/**
 * Determines if the given property is visible with the given visibility.
 */
function isVisible(program, property, visibility) {
    if (visibility & Visibility.LegacyParameterVisibility) {
        // This is a hack that preserves the behavior of `@parameterVisibility()` with no arguments for now.
        // eslint-disable-next-line @typescript-eslint/no-deprecated
        return isVisible$1(program, property, []);
    }
    else {
        return isVisible$1(program, property, visibilityToFilter(program, visibility));
    }
}
/**
 * Determines if the given property is metadata that is applicable with the
 * given visibility.
 *
 * - No metadata is applicable with Visibility.Item present.
 * - If only Visibility.Read is present, then only `@header` and `@status`
 *   properties are applicable.
 * - If Visibility.Read is not present, all metadata properties other than
 *   `@statusCode` are applicable.
 */
function isApplicableMetadata(program, property, visibility, isMetadataCallback = isMetadata) {
    return isApplicableMetadataCore(program, property, visibility, false, isMetadataCallback);
}
/**
 * Determines if the given property is metadata or marked `@body` and
 * applicable with the given visibility.
 */
function isApplicableMetadataOrBody(program, property, visibility, isMetadataCallback = isMetadata) {
    return isApplicableMetadataCore(program, property, visibility, true, isMetadataCallback);
}
function isApplicableMetadataCore(program, property, visibility, treatBodyAsMetadata, isMetadataCallback) {
    if (visibility & Visibility.Item) {
        return false; // no metadata is applicable to collection items
    }
    if (treatBodyAsMetadata &&
        (isBody(program, property) ||
            isBodyRoot(program, property) ||
            isMultipartBodyProperty(program, property))) {
        return true;
    }
    if (!isMetadataCallback(program, property)) {
        return false;
    }
    if (visibility & Visibility.Read) {
        return isHeader(program, property) || isStatusCode(program, property);
    }
    if (!(visibility & Visibility.Read)) {
        return !isStatusCode(program, property);
    }
    return true;
}
function createMetadataInfo(program, options) {
    const canonicalVisibility = options?.canonicalVisibility ?? Visibility.All;
    const stateMap = new TwoLevelMap();
    return {
        isEmptied,
        isTransformed,
        isPayloadProperty,
        isOptional,
        getEffectivePayloadType,
    };
    function isEmptied(type, visibility) {
        if (!type) {
            return false;
        }
        const state = getState(type, visibility);
        return state === 2 /* State.Emptied */;
    }
    function isTransformed(type, visibility) {
        if (!type) {
            return false;
        }
        const state = getState(type, visibility);
        switch (state) {
            case 1 /* State.Transformed */:
                return true;
            case 2 /* State.Emptied */:
                return visibility === canonicalVisibility || !isEmptied(type, canonicalVisibility);
            default:
                return false;
        }
    }
    function getState(type, visibility) {
        return stateMap.getOrAdd(type, visibility, () => computeState(type, visibility), 3 /* State.ComputationInProgress */);
    }
    function computeState(type, visibility) {
        switch (type.kind) {
            case "Model":
                return computeStateForModel(type, visibility);
            case "Union":
                return computeStateForUnion(type, visibility);
            default:
                return 0 /* State.NotTransformed */;
        }
    }
    function computeStateForModel(model, visibility) {
        if (computeIsEmptied(model, visibility)) {
            return 2 /* State.Emptied */;
        }
        if (isTransformed(model.indexer?.value, visibility | Visibility.Item) ||
            isTransformed(model.baseModel, visibility)) {
            return 1 /* State.Transformed */;
        }
        for (const property of model.properties.values()) {
            if (isAddedRemovedOrMadeOptional(property, visibility) ||
                isTransformed(property.type, visibility)) {
                return 1 /* State.Transformed */;
            }
        }
        return 0 /* State.NotTransformed */;
    }
    function computeStateForUnion(union, visibility) {
        for (const variant of union.variants.values()) {
            if (isTransformed(variant.type, visibility)) {
                return 1 /* State.Transformed */;
            }
        }
        return 0 /* State.NotTransformed */;
    }
    function isAddedRemovedOrMadeOptional(property, visibility) {
        if (visibility === canonicalVisibility) {
            return false;
        }
        if (isOptional(property, canonicalVisibility) !== isOptional(property, visibility)) {
            return true;
        }
        return (isPayloadProperty(property, visibility, undefined, /* keep shared */ true) !==
            isPayloadProperty(property, canonicalVisibility, undefined, /*keep shared*/ true));
    }
    function computeIsEmptied(model, visibility) {
        if (model.baseModel || model.indexer || model.properties.size === 0) {
            return false;
        }
        for (const property of model.properties.values()) {
            if (isPayloadProperty(property, visibility, undefined, /* keep shared */ true)) {
                return false;
            }
        }
        return true;
    }
    function isOptional(property, visibility) {
        // Properties are made optional for patch requests if the visibility includes
        // update, but not for array elements with the item flag since you must provide
        // all array elements with required properties, even in a patch.
        const hasUpdate = (visibility & Visibility.Update) !== 0;
        const isPatch = (visibility & Visibility.Patch) !== 0;
        const isItem = (visibility & Visibility.Item) !== 0;
        const skipEffectiveOptionality = (visibility & Visibility.LegacyParameterVisibility) !== 0;
        return property.optional || (!skipEffectiveOptionality && hasUpdate && isPatch && !isItem);
    }
    function isPayloadProperty(property, visibility, inExplicitBody, keepShareableProperties) {
        if (!inExplicitBody &&
            (isBodyIgnore(program, property) ||
                isApplicableMetadata(program, property, visibility) ||
                (isMetadata(program, property) && !includeInapplicableMetadataInPayload(program, property)))) {
            return false;
        }
        if (!isVisible(program, property, visibility)) {
            // NOTE: When we check if a model is transformed for a given
            // visibility, we retain shared properties. It is not considered
            // transformed if the only removed properties are shareable. However,
            // if we do create a unique schema for a visibility, then we still
            // drop invisible shareable properties from other uses of
            // isPayloadProperty.
            //
            // For OpenAPI emit, for example, this means that we won't put a
            // readOnly: true property into a specialized schema for a non-read
            // visibility.
            keepShareableProperties ??= visibility === canonicalVisibility;
            return !!(keepShareableProperties && options?.canShareProperty?.(property));
        }
        return true;
    }
    /**
     * If the type is an anonymous model, tries to find a named model that has the same
     * set of properties when non-payload properties are excluded.we
     */
    function getEffectivePayloadType(type, visibility) {
        if (type.kind === "Model" && !type.name) {
            const effective = getEffectiveModelType(program, type, (p) => isPayloadProperty(p, visibility, undefined, /* keep shared */ false));
            if (effective.name) {
                return effective;
            }
        }
        return type;
    }
}

const operators = ["+", "#", ".", "/", ";", "?", "&"];
const uriTemplateRegex = /\{([^{}]+)\}|([^{}]+)/g;
const expressionRegex = /([^:*]*)(?::(\d+)|(\*))?/;
/**
 * Parse a URI template according to [RFC-6570](https://datatracker.ietf.org/doc/html/rfc6570#section-3.2.3)
 */
function parseUriTemplate(template) {
    const parameters = [];
    const segments = [];
    const matches = template.matchAll(uriTemplateRegex);
    for (let [_, expression, literal] of matches) {
        if (expression) {
            let operator;
            if (operators.includes(expression[0])) {
                operator = expression[0];
                expression = expression.slice(1);
            }
            const items = expression.split(",");
            for (const item of items) {
                const match = item.match(expressionRegex);
                const name = match[1];
                const parameter = {
                    name: name,
                    operator,
                    modifier: match[3]
                        ? { type: "explode" }
                        : match[2]
                            ? { type: "prefix", value: Number(match[2]) }
                            : undefined,
                };
                parameters.push(parameter);
                segments.push(parameter);
            }
        }
        else {
            segments.push(literal);
        }
    }
    return { segments, parameters };
}

function getOperationParameters(program, operation, partialUriTemplate, overloadBase, options = {}) {
    const verb = (options?.verbSelector && options.verbSelector(program, operation)) ??
        getOperationVerb(program, operation) ??
        overloadBase?.verb;
    if (verb) {
        return getOperationParametersForVerb(program, operation, verb, partialUriTemplate);
    }
    // If no verb is explicitly specified, it is POST if there is a body and
    // GET otherwise. Theoretically, it is possible to use @visibility
    // strangely such that there is no body if the verb is POST and there is a
    // body if the verb is GET. In that rare case, GET is chosen arbitrarily.
    const post = getOperationParametersForVerb(program, operation, "post", partialUriTemplate);
    return post[0].body
        ? post
        : getOperationParametersForVerb(program, operation, "get", partialUriTemplate);
}
const operatorToStyle = {
    ";": "matrix",
    "#": "fragment",
    ".": "label",
    "/": "path",
};
function getOperationParametersForVerb(program, operation, verb, partialUriTemplate) {
    const diagnostics = createDiagnosticCollector();
    const visibility = resolveRequestVisibility(program, operation, verb);
    const parsedUriTemplate = parseUriTemplate(partialUriTemplate);
    const parameters = [];
    const { body: resolvedBody, metadata } = diagnostics.pipe(resolveHttpPayload(program, operation.parameters, visibility, HttpPayloadDisposition.Request, {
        implicitParameter: (param) => {
            const isTopLevel = param.model === operation.parameters;
            const uriParam = isTopLevel && parsedUriTemplate.parameters.find((x) => x.name === param.name);
            if (!uriParam) {
                return undefined;
            }
            const explode = uriParam.modifier?.type === "explode";
            if (uriParam.operator === "?" || uriParam.operator === "&") {
                return {
                    type: "query",
                    name: uriParam.name,
                    explode,
                };
            }
            else if (uriParam.operator === "+") {
                return {
                    type: "path",
                    name: uriParam.name,
                    explode,
                    allowReserved: true,
                    style: "simple",
                };
            }
            else {
                return {
                    type: "path",
                    name: uriParam.name,
                    explode,
                    allowReserved: false,
                    style: (uriParam.operator && operatorToStyle[uriParam.operator]) ?? "simple",
                };
            }
        },
    }));
    for (const item of metadata) {
        switch (item.kind) {
            case "contentType":
                parameters.push({
                    name: "Content-Type",
                    type: "header",
                    param: item.property,
                });
                break;
            case "path":
                if (item.property.optional) {
                    diagnostics.add(createDiagnostic({
                        code: "optional-path-param",
                        format: { paramName: item.property.name },
                        target: item.property,
                    }));
                }
            // eslint-disable-next-line no-fallthrough
            case "query":
            case "cookie":
            case "header":
                parameters.push({
                    ...item.options,
                    param: item.property,
                });
                break;
        }
    }
    const body = resolvedBody;
    return diagnostics.wrap({
        properties: metadata,
        parameters,
        verb,
        body,
        get bodyType() {
            return body?.type;
        },
        get bodyParameter() {
            return body?.property;
        },
    });
}

// The set of allowed segment separator characters
const AllowedSegmentSeparators = ["/", ":"];
function normalizeFragment(fragment, trimLast = false) {
    if (fragment.length > 0 && AllowedSegmentSeparators.indexOf(fragment[0]) < 0) {
        // Insert the default separator
        fragment = `/${fragment}`;
    }
    if (trimLast && fragment[fragment.length - 1] === "/") {
        return fragment.slice(0, -1);
    }
    return fragment;
}
function joinPathSegments(rest) {
    let current = "";
    for (const [index, segment] of rest.entries()) {
        current += normalizeFragment(segment, index < rest.length - 1);
    }
    return current;
}
function buildPath(pathFragments) {
    // Join all fragments with leading and trailing slashes trimmed
    const path = pathFragments.length === 0 ? "/" : joinPathSegments(pathFragments);
    // The final path must start with a '/'
    return path[0] === "/" ? path : `/${path}`;
}
function resolvePathAndParameters(program, operation, overloadBase, options) {
    const diagnostics = createDiagnosticCollector();
    const { uriTemplate, parameters } = diagnostics.pipe(getUriTemplateAndParameters(program, operation, overloadBase, options));
    const parsedUriTemplate = parseUriTemplate(uriTemplate);
    // Pull out path parameters to verify what's in the path string
    const paramByName = new Set(parameters.parameters
        .filter(({ type }) => type === "path" || type === "query")
        .map((x) => x.name));
    // Ensure that all of the parameters defined in the route are accounted for in
    // the operation parameters
    for (const routeParam of parsedUriTemplate.parameters) {
        const decoded = decodeURIComponent(routeParam.name);
        if (!paramByName.has(routeParam.name) && !paramByName.has(decoded)) {
            diagnostics.add(createDiagnostic({
                code: "missing-uri-param",
                format: { param: routeParam.name },
                target: operation,
            }));
        }
    }
    const path = produceLegacyPathFromUriTemplate(parsedUriTemplate);
    return diagnostics.wrap({
        uriTemplate,
        path,
        parameters,
    });
}
function produceLegacyPathFromUriTemplate(uriTemplate) {
    let result = "";
    for (const segment of uriTemplate.segments ?? []) {
        if (typeof segment === "string") {
            result += segment;
        }
        else if (segment.operator !== "?" && segment.operator !== "&") {
            result += `{${segment.name}}`;
        }
    }
    return result;
}
function collectSegmentsAndOptions(program, source) {
    if (source === undefined)
        return [[], {}];
    const [parentSegments, parentOptions] = collectSegmentsAndOptions(program, source.namespace);
    const route = getRoutePath(program, source)?.path;
    const options = source.kind === "Namespace" ? (getRouteOptionsForNamespace(program, source) ?? {}) : {};
    return [[...parentSegments, ...(route ? [route] : [])], { ...parentOptions, ...options }];
}
function getUriTemplateAndParameters(program, operation, overloadBase, options) {
    const [parentSegments, parentOptions] = collectSegmentsAndOptions(program, operation.interface ?? operation.namespace);
    const routeProducer = getRouteProducer(program, operation) ?? DefaultRouteProducer;
    const [result, diagnostics] = routeProducer(program, operation, parentSegments, overloadBase, {
        ...parentOptions,
        ...options,
    });
    return [
        { uriTemplate: buildPath([result.uriTemplate]), parameters: result.parameters },
        diagnostics,
    ];
}
/**
 * @deprecated DO NOT USE. For internal use only as a workaround.
 * @param program Program
 * @param target Target namespace
 * @param sourceInterface Interface that should be included in namespace.
 */
function includeInterfaceRoutesInNamespace(program, target, sourceInterface) {
    let array = program.stateMap(HttpStateKeys.externalInterfaces).get(target);
    if (array === undefined) {
        array = [];
        program.stateMap(HttpStateKeys.externalInterfaces).set(target, array);
    }
    array.push(sourceInterface);
}
function DefaultRouteProducer(program, operation, parentSegments, overloadBase, options) {
    const diagnostics = createDiagnosticCollector();
    const routePath = getRoutePath(program, operation)?.path;
    const uriTemplate = !routePath && overloadBase
        ? overloadBase.uriTemplate
        : joinPathSegments([...parentSegments, ...(routePath ? [routePath] : [])]);
    const parsedUriTemplate = parseUriTemplate(uriTemplate);
    const parameters = diagnostics.pipe(getOperationParameters(program, operation, uriTemplate, overloadBase, options.paramOptions));
    // Pull out path parameters to verify what's in the path string
    const unreferencedPathParamNames = new Map(parameters.parameters
        .filter(({ type }) => type === "path" || type === "query")
        .map((x) => [x.name, x]));
    // Compile the list of all route params that aren't represented in the route
    for (const uriParam of parsedUriTemplate.parameters) {
        unreferencedPathParamNames.delete(uriParam.name);
    }
    const resolvedUriTemplate = addOperationTemplateToUriTemplate(uriTemplate, [
        ...unreferencedPathParamNames.values(),
    ]);
    return diagnostics.wrap({
        uriTemplate: resolvedUriTemplate,
        parameters,
    });
}
const styleToOperator = {
    matrix: ";",
    label: ".",
    simple: "",
    path: "/",
    fragment: "#",
};
function getUriTemplatePathParam(param) {
    const operator = param.allowReserved ? "+" : styleToOperator[param.style];
    return `{${operator}${param.name}${param.explode ? "*" : ""}}`;
}
function getUriTemplateQueryParamPart(param) {
    return `${escapeUriTemplateParamName(param.name)}${param.explode ? "*" : ""}`;
}
function addQueryParamsToUriTemplate(uriTemplate, params) {
    const queryParams = params.filter((x) => x.type === "query");
    return (uriTemplate +
        (queryParams.length > 0
            ? `{?${queryParams.map((x) => getUriTemplateQueryParamPart(x)).join(",")}}`
            : ""));
}
function addOperationTemplateToUriTemplate(uriTemplate, params) {
    const pathParams = params.filter((x) => x.type === "path").map(getUriTemplatePathParam);
    const queryParams = params.filter((x) => x.type === "query");
    const pathPart = joinPathSegments([uriTemplate, ...pathParams]);
    return addQueryParamsToUriTemplate(pathPart, queryParams);
}
function escapeUriTemplateParamName(name) {
    return name.replaceAll(":", "%3A");
}
function setRouteProducer(program, operation, routeProducer) {
    program.stateMap(HttpStateKeys.routeProducer).set(operation, routeProducer);
}
function getRouteProducer(program, operation) {
    return program.stateMap(HttpStateKeys.routeProducer).get(operation);
}
function setRoute(context, entity, details) {
    if (!validateDecoratorTarget(context, entity, "@route", ["Namespace", "Interface", "Operation"])) {
        return;
    }
    const state = context.program.stateMap(HttpStateKeys.routes);
    if (state.has(entity) && entity.kind === "Namespace") {
        const existingPath = state.get(entity);
        if (existingPath !== details.path) {
            reportDiagnostic(context.program, {
                code: "duplicate-route-decorator",
                messageId: "namespace",
                target: entity,
            });
        }
    }
    else {
        state.set(entity, details.path);
        if (entity.kind === "Operation" && details.shared) {
            setSharedRoute(context.program, entity);
        }
    }
}
function setSharedRoute(program, operation) {
    program.stateMap(HttpStateKeys.sharedRoutes).set(operation, true);
}
function isSharedRoute(program, operation) {
    return program.stateMap(HttpStateKeys.sharedRoutes).get(operation) === true;
}
function getRoutePath(program, entity) {
    const path = program.stateMap(HttpStateKeys.routes).get(entity);
    return path
        ? {
            path,
            shared: entity.kind === "Operation" && isSharedRoute(program, entity),
        }
        : undefined;
}
function setRouteOptionsForNamespace(program, namespace, options) {
    program.stateMap(HttpStateKeys.routeOptions).set(namespace, options);
}
function getRouteOptionsForNamespace(program, namespace) {
    return program.stateMap(HttpStateKeys.routeOptions).get(namespace);
}

export { $body as $, $route as A, $server as B, $sharedRoute as C, $statusCode as D, $useAuth as E, $lib as F, DefaultRouteProducer as G, HttpStateKeys as H, HttpVisibilityProvider as I, addQueryParamsToUriTemplate as J, createMetadataInfo as K, getAllRoutes as L, getAuthentication as M, getAuthenticationForOperation as N, getContentTypes as O, getCookieParamOptions as P, getHeaderFieldName as Q, getHttpFileModel as R, getHttpPart as S, getHttpService as T, getOperationParameters as U, Visibility as V, getOperationVerb as W, getPathParamName as X, getQueryParamName as Y, getRequestVisibility as Z, getResponsesForOperation as _, getHeaderFieldOptions as a, getRouteOptionsForNamespace as a0, getRouteProducer as a1, getServers as a2, getStatusCodeDescription as a3, getStatusCodes as a4, getStatusCodesWithDiagnostics as a5, getUriTemplatePathParam as a6, getVisibilitySuffix as a7, includeInapplicableMetadataInPayload as a8, includeInterfaceRoutesInNamespace as a9, validateRouteUnique as aA, f2 as aB, isApplicableMetadata as aa, isApplicableMetadataOrBody as ab, isBody as ac, isBodyIgnore as ad, isBodyRoot as ae, isContentTypeHeader as af, isCookieParam as ag, isHttpFile as ah, isMetadata as ai, isOrExtendsHttpFile as aj, isOverloadSameEndpoint as ak, isStatusCode as al, isVisible as am, joinPathSegments as an, listHttpOperationsIn as ao, namespace$1 as ap, reportIfNoRoutes as aq, resolveAuthentication as ar, resolvePathAndParameters as as, resolveRequestVisibility as at, setAuthentication as au, setRoute as av, setRouteOptionsForNamespace as aw, setRouteProducer as ax, setSharedRoute as ay, setStatusCode as az, isPathParam as b, getPathParamOptions as c, isQueryParam as d, getQueryParamOptions as e, isMultipartBodyProperty as f, getHttpOperation as g, getRoutePath as h, isHeader as i, getAllHttpServices as j, isSharedRoute as k, $bodyIgnore as l, $bodyRoot as m, $cookie as n, $delete as o, $get as p, $header as q, reportDiagnostic as r, $head as s, $includeInapplicableMetadataInPayload as t, $multipartBody as u, $patch as v, $path as w, $post as x, $put as y, $query as z };

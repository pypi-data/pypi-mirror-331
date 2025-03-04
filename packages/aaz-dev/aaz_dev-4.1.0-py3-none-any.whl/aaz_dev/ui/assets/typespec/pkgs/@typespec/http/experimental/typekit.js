import { ignoreDiagnostics, isErrorModel } from '@typespec/compiler';
import { defineKit } from '@typespec/compiler/experimental/typekit';
import { g as getHttpOperation, i as isHeader, a as getHeaderFieldOptions, b as isPathParam, c as getPathParamOptions, d as isQueryParam, e as getQueryParamOptions, f as isMultipartBodyProperty } from '../route-BokK7aCi.js';
import '@typespec/compiler/utils';

defineKit({
    httpOperation: {
        get(op) {
            return ignoreDiagnostics(getHttpOperation(this.program, op));
        },
        getReturnType(operation, options) {
            let responses = this.httpOperation.getResponses(operation);
            if (!options?.includeErrors) {
                responses = responses.filter((r) => !this.httpResponse.isErrorResponse(r.responseContent));
            }
            const voidType = { kind: "Intrinsic", name: "void" };
            let httpReturnType = voidType;
            if (!responses.length) {
                return voidType;
            }
            if (responses.length > 1) {
                const res = [...new Set(responses.map((r) => r.responseContent.body?.type))];
                httpReturnType = this.union.create({
                    variants: res.map((t) => {
                        return this.unionVariant.create({
                            type: getEffectiveType(this, t),
                        });
                    }),
                });
            }
            else {
                httpReturnType = getEffectiveType(this, responses[0].responseContent.body?.type);
            }
            return httpReturnType;
        },
        getResponses(operation) {
            const responsesMap = [];
            const httpOperation = this.httpOperation.get(operation);
            for (const response of httpOperation.responses) {
                for (const responseContent of response.responses) {
                    const contentTypeProperty = responseContent.properties.find((property) => property.kind === "contentType");
                    let contentType;
                    if (contentTypeProperty) {
                        contentType = contentTypeProperty.property.type.value;
                    }
                    else if (responseContent.body) {
                        contentType = "application/json";
                    }
                    responsesMap.push({ statusCode: response.statusCodes, contentType, responseContent });
                }
            }
            return responsesMap;
        },
    },
});
function getEffectiveType(typekit, type) {
    if (type === undefined) {
        return { kind: "Intrinsic", name: "void" };
    }
    if (typekit.model.is(type)) {
        return typekit.model.getEffectiveModel(type);
    }
    return type;
}

defineKit({
    httpRequest: {
        body: {
            isExplicit(httpOperation) {
                return (httpOperation.parameters.properties.find((p) => p.kind === "body" || p.kind === "bodyRoot") !== undefined);
            },
        },
        getBodyParameters(httpOperation) {
            const body = httpOperation.parameters.body;
            if (!body) {
                return undefined;
            }
            const bodyProperty = body.property;
            if (!bodyProperty) {
                if (body.type.kind === "Model") {
                    return body.type;
                }
                throw new Error("Body property not found");
            }
            const bodyPropertyName = bodyProperty.name ? bodyProperty.name : "body";
            return this.model.create({
                properties: { [bodyPropertyName]: bodyProperty },
            });
        },
        getParameters(httpOperation, kind) {
            const kinds = new Set(Array.isArray(kind) ? kind : [kind]);
            const parameterProperties = [];
            for (const kind of kinds) {
                if (kind === "body") {
                    const bodyParams = Array.from(this.httpRequest.getBodyParameters(httpOperation)?.properties.values() ?? []);
                    if (bodyParams) {
                        parameterProperties.push(...bodyParams);
                    }
                }
                else {
                    const params = httpOperation.parameters.properties
                        .filter((p) => p.kind === kind)
                        .map((p) => p.property);
                    parameterProperties.push(...params);
                }
            }
            if (parameterProperties.length === 0) {
                return undefined;
            }
            const properties = parameterProperties.reduce((acc, prop) => {
                acc[prop.name] = prop;
                return acc;
            }, {});
            return this.model.create({ properties });
        },
    },
});

defineKit({
    httpResponse: {
        isErrorResponse(response) {
            return response.body ? isErrorModel(this.program, response.body.type) : false;
        },
        statusCode: {
            isSingle(statusCode) {
                return typeof statusCode === "number";
            },
            isRange(statusCode) {
                return typeof statusCode === "object" && "start" in statusCode && "end" in statusCode;
            },
            isDefault(statusCode) {
                return statusCode === "*";
            },
        },
    },
});

defineKit({
    modelProperty: {
        getHttpParamOptions(prop) {
            if (isHeader(this.program, prop)) {
                return getHeaderFieldOptions(this.program, prop);
            }
            if (isPathParam(this.program, prop)) {
                return getPathParamOptions(this.program, prop);
            }
            if (isQueryParam(this.program, prop)) {
                return getQueryParamOptions(this.program, prop);
            }
            return undefined;
        },
        getHttpHeaderOptions(prop) {
            return getHeaderFieldOptions(this.program, prop);
        },
        getHttpPathOptions(prop) {
            return getPathParamOptions(this.program, prop);
        },
        getHttpQueryOptions(prop) {
            return getQueryParamOptions(this.program, prop);
        },
        isHttpHeader(prop) {
            return isHeader(this.program, prop);
        },
        isHttpPathParam(prop) {
            return isPathParam(this.program, prop);
        },
        isHttpQueryParam(prop) {
            return isQueryParam(this.program, prop);
        },
        isHttpMultipartBody(prop) {
            return isMultipartBodyProperty(this.program, prop);
        },
    },
});

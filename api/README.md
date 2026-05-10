# API Gateway and Specifications

This directory contains the API Gateway implementation and OpenAPI specifications for the GPU Compute Marketplace Platform.

## API Overview

The platform exposes REST APIs for:
- Compute job management
- Token operations
- Resource discovery
- Billing and usage
- Data center management

## Base URL

- **Production**: `https://api.gpucompute.market`
- **Staging**: `https://staging-api.gpucompute.market`
- **Development**: `http://localhost:8000`

## Authentication

All API requests require authentication via API key:

```http
Authorization: Bearer {api_key}
```

API keys can be generated in the dashboard at `/dashboard/api-keys`.

## Rate Limiting

- **Free Tier**: 100 requests/minute
- **Pro Tier**: 1,000 requests/minute
- **Enterprise**: Custom limits

Rate limit headers:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when window resets

## API Specifications

See [api/openapi.yaml](openapi.yaml) for complete OpenAPI 3.0 specification.

## SDKs

Official SDKs are available:
- **Python**: `pip install gpucompute-sdk`
- **JavaScript/TypeScript**: `npm install @gpucompute/sdk`
- **Go**: `go get github.com/gpucompute/sdk-go`

## Examples

See [api/examples/](examples/) for code examples in various languages.


from fastapi import Request


def get_client_ip(request: Request) -> str:
    # Check for X-Forwarded-For header (proxy/load balancer)
    if request.headers.get("x-forwarded-for"):
        return request.headers["x-forwarded-for"].split(",")[0].strip()
    # Fall back to direct client connection
    if request.client is None:
        return ""
    return request.client.host

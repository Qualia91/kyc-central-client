"""KYC Central — official Python client for the UK company KYC risk assessment API.

Quick start::

    from kyccentral import KYCCentral

    client = KYCCentral(api_key="...")          # or set KYCCENTRAL_API_KEY
    assessment = client.kyc.assess("00445790")

    print(assessment.company_name, assessment.risk_level)
    for flag in assessment.critical_flags:
        print(flag.code, "-", flag.description)

Docs: https://github.com/qualia91/kyccentral-python
API reference: https://kyccentral.co.uk/api-docs
"""

from ._transport import DEFAULT_BASE_URL
from ._version import __version__
from .client import AsyncKYCCentral, KYCCentral
from .errors import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    JobError,
    JobFailedError,
    JobTimeoutError,
    KYCCentralError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    UnprocessableEntityError,
)
from .models import Assessment, RiskFlag, RiskLevel, RuleResult, RuleStatus

__all__ = [
    "DEFAULT_BASE_URL",
    "APIConnectionError",
    "APIStatusError",
    "APITimeoutError",
    # Models
    "Assessment",
    "AsyncKYCCentral",
    "AuthenticationError",
    "BadRequestError",
    "JobError",
    "JobFailedError",
    "JobTimeoutError",
    # Clients
    "KYCCentral",
    # Errors
    "KYCCentralError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "RiskFlag",
    "RiskLevel",
    "RuleResult",
    "RuleStatus",
    "ServerError",
    "ServiceUnavailableError",
    "UnprocessableEntityError",
    "__version__",
]

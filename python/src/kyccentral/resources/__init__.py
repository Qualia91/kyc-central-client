"""Resource namespaces exposed as attributes on the client.

Each namespace has a blocking class and an ``Async``-prefixed awaitable twin with
the same method names and signatures, so porting code between
:class:`~kyccentral.KYCCentral` and :class:`~kyccentral.AsyncKYCCentral` is a
matter of adding ``await``.
"""

from .analysis import Analysis, AsyncAnalysis, AsyncDocs, Docs
from .companies import AsyncCompanies, Companies
from .kyc import (
    AsyncJobs,
    AsyncKyc,
    AsyncRules,
    AsyncRuleSets,
    Jobs,
    Kyc,
    Rules,
    RuleSets,
)
from .registries import (
    AsyncCharity,
    AsyncHmrcVat,
    AsyncJurisdictions,
    AsyncOffshoreJurisdictions,
    Charity,
    HmrcVat,
    Jurisdictions,
    OffshoreJurisdictions,
)
from .screening import (
    AsyncFca,
    AsyncGleif,
    AsyncIndividualInsolvency,
    AsyncNews,
    AsyncOffshoreLeaks,
    AsyncSanctions,
    Fca,
    Gleif,
    IndividualInsolvency,
    News,
    OffshoreLeaks,
    Sanctions,
)

__all__ = [
    "Analysis",
    "AsyncAnalysis",
    "AsyncCharity",
    "AsyncCompanies",
    "AsyncDocs",
    "AsyncFca",
    "AsyncGleif",
    "AsyncHmrcVat",
    "AsyncIndividualInsolvency",
    "AsyncJobs",
    "AsyncJurisdictions",
    "AsyncKyc",
    "AsyncNews",
    "AsyncOffshoreJurisdictions",
    "AsyncOffshoreLeaks",
    "AsyncRuleSets",
    "AsyncRules",
    "AsyncSanctions",
    "Charity",
    "Companies",
    "Docs",
    "Fca",
    "Gleif",
    "HmrcVat",
    "IndividualInsolvency",
    "Jobs",
    "Jurisdictions",
    "Kyc",
    "News",
    "OffshoreJurisdictions",
    "OffshoreLeaks",
    "RuleSets",
    "Rules",
    "Sanctions",
]

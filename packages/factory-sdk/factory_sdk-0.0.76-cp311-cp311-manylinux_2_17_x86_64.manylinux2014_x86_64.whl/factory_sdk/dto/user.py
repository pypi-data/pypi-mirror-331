from pydantic import BaseModel, Field
from uuid import uuid4
from enum import Enum
from typing import List, Optional, Dict


class Role(str, Enum):
    OWNER = "owner"
    MEMBER = "member"


class TenantMember(BaseModel):
    id: str = Field(description="User ID")
    role: Role = Field(description="User role")

class EmailChangeRequest(BaseModel):
    """
    Request schema for initiating an email change process.
    """
    new_email: str

class EmailChangeVerify(BaseModel):
    """
    Schema for verifying and confirming an email change.
    """
    token: str


class UserInfo(BaseModel):
    id: str = Field(description="User ID", default_factory=lambda: str(uuid4()))
    username: str = Field(description="Username")
    firstname: str = Field(description="First Name")
    lastname: str = Field(description="Last Name")
    email: str = Field(description="Email")
    tenant: str = Field(description="Personal Tenant ID")


class LoginData(BaseModel):
    username: str = Field(description="Username")
    password: str = Field(description="Password")


class ResetPasswordData(BaseModel):
    email: str = Field(description="Email")


class FinishResetPasswordData(BaseModel):
    token: str = Field(description="Reset token")
    password: str = Field(description="New password")


class RegisterData(BaseModel):
    firstname: str = Field(description="First Name", min_length=1)
    lastname: str = Field(description="Last Name", min_length=1)
    email: str = Field(description="Email", min_length=1)


class FinishRegistrationData(BaseModel):
    token: str = Field(description="Verification token")
    username: str = Field(description="Username")
    password: str = Field(description="Password")
    questions: Dict[str, str] = Field(description="Background questions")


class SubscriptionLimits(BaseModel):
    max_storage: Optional[float] = Field(description="Max storage in GB")
    max_active_deployments: Optional[int] = Field(description="Max active deployments")
    max_tenants: Optional[int] = Field(description="Max tenants")


class SubscriptionUpdate(BaseModel):
    type: str = Field(description="Subscription type")
    return_to_tenant: Optional[str] = Field(description="Tenant ID to return to")


class Subscription(BaseModel):
    subscription_type: str = Field(description="Subscription type")
    deployment_type: str = Field(description="Deployment type")
    limits: SubscriptionLimits = Field(description="Subscription limits")
    update: Optional[SubscriptionUpdate] = Field(
        description="Subscription update (if any)"
    )


class TenantUsage(BaseModel):
    deployments: int = Field(description="Active deployments")
    storage: float = Field(description="Storage in GB")
    id: str = Field(description="Tenant ID")
    name: str = Field(description="Tenant name")


class AggregatedUsage(BaseModel):
    deployments: int = Field(description="Active deployments")
    storage: float = Field(description="Storage in GB")
    tenants: int = Field(description="Number of tenants")


class Usage(BaseModel):
    tenants: List[TenantUsage] = Field(description="Tenant usage")
    total: AggregatedUsage = Field(description="Total usage")

class UsernameUpdate(BaseModel):
    username: str

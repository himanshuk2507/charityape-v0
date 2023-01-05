from unicodedata import category

from plaid.model import address
from pydantic import BaseModel, validator, ValidationError, HttpUrl
import re
from typing import List, Optional, Literal
from uuid import UUID
import datetime
from pydantic.class_validators import Validator


class EmailListValidator(BaseModel):
    emails: List[str] = []

    @validator("emails")
    def validate_email(cls, v):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        print("------", v)
        for k in v:
            if not re.fullmatch(regex, k):
                raise ValueError("Enter a valid email address")
        return True


class UuidListValidator(BaseModel):
    ids: List[UUID] = []

    # @validator("ids")
    # def validate_uuid_list(cls, v):
    #     for k in v:


class EblastValidator(BaseModel):
    eblast_name: str
    campaign_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    assignee: Optional[UUID] = None


class UuidValidator(BaseModel):
    uuid: UUID


class ValidElementsParams(BaseModel):
    element_name: str
    campaign_id: Optional[UUID] = None
    element_type: Literal["button", "data", "forms", "links"]


class EmailValidator(BaseModel):
    emails: str

    @validator("emails")
    def validate_email(cls, v):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

        if not re.fullmatch(regex, v):
            raise ValueError("Enter a valid email address")
        return True


class MembershipValidator(BaseModel):
    start_date: datetime.datetime
    end_date: datetime.datetime
    auto_renew: bool
    auto_send_email: bool
    receipt_name: str
    address: str
    email_address: str
    payment_method: Literal["stripe", "paypal", "offline"]
    membership_fee: int

    @validator("email_address")
    def validate_email(cls, v):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if not re.fullmatch(regex, v):
            raise ValueError("Enter a valid email address")
        return True


class AdminValidator(BaseModel):
    email: str
    password: Optional[str] = None
    first_name: str
    last_name: str
    type_of: Optional[Literal["user", "invitation"]]
    timezone: Optional[str]
    permission_level: Optional[Literal["administrator", "manager", "coordinator"]]

    @validator("email")
    def validate_email(cls, v):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if not re.fullmatch(regex, v):
            raise ValueError("Enter a valid email address")
        return True


class OrganizationValidator(BaseModel):
    organization_name: str
    organization_email: str
    address: str
    organization_phone: str
    organization_website: HttpUrl
    timezone: str
    organization_logo: str
    statement_description: str
    is_legal: bool
    tax_exemption_verification: str

    @validator("organization_email")
    def validate_email(cls, v):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if not re.fullmatch(regex, v):
            raise ValueError("Enter a valid email address")
        return True

    @validator("organization_phone")
    def validate_phone(cls, v):
        regex = r"(0|91)?[7-9][0-9]{9}\b"
        Pattern = re.compile(regex)
        valid = Pattern.match(v)
        if not valid:
            raise ValueError("Enter a valid phone number")
        return True


def emails_filter(emails):
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    filtered_valid_emails = [
        valid_mail
        for valid_mail in filter(lambda email: re.fullmatch(regex, email), emails)
    ]
    return filtered_valid_emails

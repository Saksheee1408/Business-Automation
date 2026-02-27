from typing import List, Optional, Dict, Any
from pydantic import BaseModel, BaseModel, HttpUrl, Field
from datetime import datetime

class BusinessProfile(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    business_type: Optional[str] = None
    about: Optional[str] = None
    services: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

class ContactInfo(BaseModel):
    email: List[str] = Field(default_factory=list)
    phone: List[str] = Field(default_factory=list)
    address: Optional[str] = None
    social_links: Dict[str, str] = Field(default_factory=dict)

class Branding(BaseModel):
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    primary_color: Optional[str] = None
    color_palette: List[str] = Field(default_factory=list)
    fonts: List[str] = Field(default_factory=list)
    layout_style: Optional[str] = None
    button_style: Dict[str, Any] = Field(default_factory=dict)

class ContentSections(BaseModel):
    homepage_heading: Optional[str] = None
    about_raw: Optional[str] = None
    services_raw: List[str] = Field(default_factory=list)

class TechnicalMetadata(BaseModel):
    is_dynamic: bool = False
    framework_detected: Optional[str] = None
    page_title: Optional[str] = None
    meta_description: Optional[str] = None
    canonical_url: Optional[str] = None

class ScrapedProfile(BaseModel):
    source_url: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    crawl_status: str = "pending"
    confidence_score: float = 0.0

    business_profile: BusinessProfile = Field(default_factory=BusinessProfile)
    contact: ContactInfo = Field(default_factory=ContactInfo)
    branding: Branding = Field(default_factory=Branding)
    content_sections: ContentSections = Field(default_factory=ContentSections)
    technical_metadata: TechnicalMetadata = Field(default_factory=TechnicalMetadata)

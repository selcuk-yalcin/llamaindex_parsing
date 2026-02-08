"""
Pydantic Models for Legal Document Extraction
Advanced Legal Hierarchy Schema (V5) - For Turkish legal documents
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


class HierarchyLevel(str, Enum):
    """Hierarchy level enum"""
    PART = "PART"
    CHAPTER = "CHAPTER"
    ARTICLE = "ARTICLE"
    PARAGRAPH = "PARAGRAPH"
    SUB_CLAUSE = "SUB_CLAUSE"


class ElementType(str, Enum):
    """Page layout element type enum"""
    BODY_TEXT = "BODY_TEXT"
    TABLE = "TABLE"
    PAGE_NUMBER = "PAGE_NUMBER"
    FOOTER = "FOOTER"
    HEADER = "HEADER"


class OfficialGazette(BaseModel):
    """Official Gazette information"""
    date: Optional[str] = Field(None, description="Official Gazette date")
    number: Optional[str] = Field(None, description="Official Gazette number")


class LawMetadata(BaseModel):
    """Law metadata"""
    law_title: str = Field(..., description="Law title")
    law_number: str = Field(..., description="Law number (e.g., 6331)")
    acceptance_date: str = Field(..., description="Acceptance date")
    publication_date: Optional[str] = Field(None, description="Official Gazette publication date")
    official_gazette: Optional[OfficialGazette] = Field(None, description="Official Gazette details")


class Section(BaseModel):
    """Law section (FIRST SECTION, SECOND SECTION, etc.)"""
    section_title: Optional[str] = Field(None, description="Section title (e.g., FIRST SECTION)")
    section_heading: Optional[str] = Field(None, description="Section description (e.g., Purpose, Scope and Definitions)")


class Definition(BaseModel):
    """Definitions used in the law"""
    term: str = Field(..., description="Defined term")
    definition: str = Field(..., description="Term description")


class ContentChild(BaseModel):
    """Sub-article structure (paragraphs, clauses)"""
    level: str = Field(..., description="Hierarchy level")
    index: str = Field(..., description="Numbering (1), a), i)")
    title: Optional[str] = Field(None, description="Sub-article title (optional)")
    text_content: str = Field(..., description="Sub-article text")
    cross_references: List[str] = Field(default_factory=list, description="Cross references")


class ContentStructure(BaseModel):
    """Hierarchical content structure - Article and paragraph structure"""
    level: str = Field(..., description="Hierarchy level (PART, CHAPTER, ARTICLE, PARAGRAPH, SUB_CLAUSE)")
    index: str = Field(..., description="Numbering (Article 1, (1), a))")
    title: Optional[str] = Field(None, description="Title (optional)")
    text_content: str = Field(..., description="Article text")
    children: List[ContentChild] = Field(default_factory=list, description="Sub-articles (paragraphs, clauses)")
    cross_references: List[str] = Field(default_factory=list, description="Cross references to other articles")


class Penalty(BaseModel):
    """Administrative penalty information"""
    violated_article: str = Field(..., description="Violated article")
    penalty_amount: str = Field(..., description="Penalty amount")
    penalty_logic: Optional[str] = Field(None, description="Penalty logic/description")


class AmendmentSummary(BaseModel):
    """Amendment summary"""
    effective_date: str = Field(..., description="Effective date")
    affected_articles: str = Field(..., description="Affected articles")
    amending_law_number: str = Field(..., description="Amending law number")


class LayoutAnalysis(BaseModel):
    """Page layout analysis"""
    element_type: str = Field(..., description="Element type (BODY_TEXT, TABLE, PAGE_NUMBER, FOOTER, HEADER)")
    content: Optional[str] = Field(None, description="Element content")
    table_markdown: Optional[str] = Field(None, description="Table markdown format")


class LegalDocument(BaseModel):
    """
    Main legal document model - Advanced Legal Hierarchy Schema (V5)
    Nullable fields corrected, hierarchical structure supported.
    """
    law_metadata: LawMetadata = Field(..., description="Law metadata")
    sections: List[Section] = Field(default_factory=list, description="Sections")
    definitions: List[Definition] = Field(default_factory=list, description="Definitions")
    content_structure: List[ContentStructure] = Field(..., description="Hierarchical content structure")
    penalties: List[Penalty] = Field(default_factory=list, description="Administrative penalties")
    amendment_summary: List[AmendmentSummary] = Field(default_factory=list, description="Amendment summary")
    layout_analysis: List[LayoutAnalysis] = Field(default_factory=list, description="Page layout analysis")

    class Config:
        json_schema_extra = {
            "example": {
                "law_metadata": {
                    "law_title": "Occupational Health and Safety Law",
                    "law_number": "6331",
                    "acceptance_date": "20.06.2012",
                    "publication_date": "30.06.2012",
                    "official_gazette": {
                        "date": "30.06.2012",
                        "number": "28339"
                    }
                },
                "sections": [
                    {
                        "section_title": "FIRST SECTION",
                        "section_heading": "Purpose, Scope and Definitions"
                    }
                ],
                "content_structure": [
                    {
                        "level": "ARTICLE",
                        "index": "Article 1",
                        "title": "Purpose",
                        "text_content": "The purpose of this Law is...",
                        "children": [],
                        "cross_references": []
                    }
                ]
            }
        }

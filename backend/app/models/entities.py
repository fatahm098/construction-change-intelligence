import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum,
    Text,
)
from sqlalchemy.orm import relationship
from ..database import Base


class RegionStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class ElementType(str, enum.Enum):
    COLUMN = "column"
    BEAM = "beam"
    SLAB = "slab"
    OTHER = "other"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    drawings = relationship("Drawing", back_populates="project", cascade="all, delete-orphan")
    boq_items = relationship("BOQItem", back_populates="project", cascade="all, delete-orphan")


class Drawing(Base):
    __tablename__ = "drawings"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    revision = Column(Integer, default=0)
    png_path = Column(String(500), nullable=True)
    width_px = Column(Integer, nullable=True)
    height_px = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="drawings")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    drawing_ref_id = Column(Integer, ForeignKey("drawings.id"), nullable=False)
    drawing_rev_id = Column(Integer, ForeignKey("drawings.id"), nullable=False)
    diff_image_path = Column(String(500), nullable=True)
    total_regions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    regions = relationship("ChangeRegion", back_populates="analysis_run", cascade="all, delete-orphan")


class ChangeRegion(Base):
    __tablename__ = "change_regions"

    id = Column(Integer, primary_key=True, index=True)
    analysis_run_id = Column(Integer, ForeignKey("analysis_runs.id"), nullable=False)
    region_index = Column(Integer, nullable=False)
    bbox_x = Column(Integer, nullable=False)
    bbox_y = Column(Integer, nullable=False)
    bbox_w = Column(Integer, nullable=False)
    bbox_h = Column(Integer, nullable=False)
    area = Column(Float, nullable=False)
    crop_v0_path = Column(String(500), nullable=True)
    crop_v1_path = Column(String(500), nullable=True)

    # Hasil ekstraksi OCR awal
    raw_text_v0 = Column(Text, nullable=True)
    raw_text_v1 = Column(Text, nullable=True)
    suggested_dim_v0 = Column(String(50), nullable=True)
    suggested_dim_v1 = Column(String(50), nullable=True)

    status = Column(Enum(RegionStatus), default=RegionStatus.PENDING)

    analysis_run = relationship("AnalysisRun", back_populates="regions")
    verification = relationship("DimensionVerification", uselist=False, back_populates="change_region", cascade="all, delete-orphan")
    cost_impact = relationship("CostImpact", uselist=False, back_populates="change_region", cascade="all, delete-orphan")


class DimensionVerification(Base):
    __tablename__ = "dimension_verifications"

    id = Column(Integer, primary_key=True, index=True)
    change_region_id = Column(Integer, ForeignKey("change_regions.id"), unique=True, nullable=False)
    element_type = Column(Enum(ElementType), default=ElementType.COLUMN)

    # Dimensi setelah dikonfirmasi atau dikoreksi manusia (dalam milimeter)
    dim_before_w = Column(Float, nullable=False)
    dim_before_h = Column(Float, nullable=False)
    dim_after_w = Column(Float, nullable=False)
    dim_after_h = Column(Float, nullable=False)

    height_or_length_m = Column(Float, default=4.0)  # tinggi kolom / panjang balok dalam meter
    volume_before_m3 = Column(Float, nullable=False)
    volume_after_m3 = Column(Float, nullable=False)
    delta_volume_m3 = Column(Float, nullable=False)

    verified_at = Column(DateTime, default=datetime.utcnow)

    change_region = relationship("ChangeRegion", back_populates="verification")


class BOQItem(Base):
    __tablename__ = "boq_items"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    unit = Column(String(20), nullable=False)
    contract_volume = Column(Float, default=0.0)
    unit_price = Column(Float, nullable=False)

    project = relationship("Project", back_populates="boq_items")
    cost_impacts = relationship("CostImpact", back_populates="boq_item")


class CostImpact(Base):
    __tablename__ = "cost_impacts"

    id = Column(Integer, primary_key=True, index=True)
    change_region_id = Column(Integer, ForeignKey("change_regions.id"), unique=True, nullable=False)
    boq_item_id = Column(Integer, ForeignKey("boq_items.id"), nullable=False)
    delta_volume = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_cost_delta = Column(Float, nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    change_region = relationship("ChangeRegion", back_populates="cost_impact")
    boq_item = relationship("BOQItem", back_populates="cost_impacts")

import enum
import json
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
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    drawings = relationship("Drawing", back_populates="project", cascade="all, delete-orphan")
    boq_items = relationship("BOQItem", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    owner = relationship("User", back_populates="projects")
    progress_entries = relationship("ProgressEntry", back_populates="project", cascade="all, delete-orphan")
    variation_orders = relationship("VariationOrder", back_populates="project", cascade="all, delete-orphan")
    rfis = relationship("RFI", back_populates="project", cascade="all, delete-orphan")


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
    ahsp_item_id = Column(Integer, ForeignKey("ahsp_items.id"), nullable=True)

    project = relationship("Project", back_populates="boq_items")
    cost_impacts = relationship("CostImpact", back_populates="boq_item")
    ahsp_item = relationship("AHSPItem", back_populates="boq_items")


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


class DocumentType(str, enum.Enum):
    RKS = "rks"          # Rencana Kerja & Syarat
    KONTRAK = "kontrak"  # Dokumen kontrak
    SNI = "sni"          # Standar nasional
    AHSP = "ahsp"        # Analisa harga satuan
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    INDEXED = "indexed"
    FAILED = "failed"


class Document(Base):
    """Dokumen sumber (RKS/kontrak/SNI/AHSP) untuk RAG Document Q&A."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    doc_type = Column(Enum(DocumentType), default=DocumentType.OTHER)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    num_chunks = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Potongan teks dokumen + embedding (JSON) untuk pencarian semantik."""

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page = Column(Integer, nullable=True)
    text = Column(Text, nullable=False)
    embedding_json = Column(Text, nullable=True)  # JSON list[float]; ganti ke pgvector di produksi

    document = relationship("Document", back_populates="chunks")


class Conversation(Base):
    """Riwayat percakapan Document Q&A per proyek."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources_json = Column(Text, nullable=True)  # JSON list[{filename, page, snippet, score}]
    created_at = Column(DateTime, default=datetime.utcnow)


class AHSPComponentType(str, enum.Enum):
    LABOR = "labor"          # tenaga kerja
    MATERIAL = "material"    # bahan
    EQUIPMENT = "equipment"  # peralatan


class AHSPItem(Base):
    """Analisa Harga Satuan Pekerjaan (AHSP).

    Harga satuan = Σ (koefisien × harga satuan dasar) dari seluruh komponen.
    Perhitungan deterministik — tidak melibatkan LLM.
    """

    __tablename__ = "ahsp_items"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    unit = Column(String(20), nullable=False)
    category = Column(String(50), nullable=True)  # beton, besi, bekisting, dinding, dll.
    created_at = Column(DateTime, default=datetime.utcnow)

    components = relationship(
        "AHSPComponent", back_populates="ahsp_item", cascade="all, delete-orphan"
    )
    boq_items = relationship("BOQItem", back_populates="ahsp_item")

    @property
    def unit_price(self) -> float:
        return round(sum(c.coefficient * c.base_price for c in self.components), 2)


class AHSPComponent(Base):
    """Satu komponen (tenaga/bahan/alat) dalam sebuah AHSP."""

    __tablename__ = "ahsp_components"

    id = Column(Integer, primary_key=True, index=True)
    ahsp_item_id = Column(Integer, ForeignKey("ahsp_items.id"), nullable=False)
    component_type = Column(Enum(AHSPComponentType), nullable=False)
    name = Column(String(255), nullable=False)
    coefficient = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    base_price = Column(Float, nullable=False)  # harga satuan dasar

    ahsp_item = relationship("AHSPItem", back_populates="components")


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ENGINEER = "engineer"
    VIEWER = "viewer"


class User(Base):
    """Akun pengguna (Fase 4 — auth & multi-tenant)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.ENGINEER)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="owner")


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class Job(Base):
    """Pekerjaan latar belakang (Fase 4 — analisis async).

    Dipakai agar endpoint berat (analisis gambar) tidak memblokir request.
    """

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    job_type = Column(String(50), nullable=False)  # mis. "analysis_run"
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, index=True)
    payload_json = Column(Text, nullable=True)   # input (JSON)
    result_json = Column(Text, nullable=True)    # hasil (JSON)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    @property
    def result(self):
        """Hasil job sebagai objek Python (di-decode dari `result_json`)."""
        if not self.result_json:
            return None
        try:
            return json.loads(self.result_json)
        except (ValueError, TypeError):
            return None


class ProgressEntry(Base):
    """Catatan progres periodik untuk kurva-S & analisis Earned Value.

    Semua angka bersifat kumulatif per periode. Perhitungan EVM deterministik
    (bukan LLM) — lihat `modules/progress/service.py`.
    """

    __tablename__ = "progress_entries"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    period = Column(String(20), nullable=False)  # label periode, mis. "2026-01"
    planned_pct = Column(Float, default=0.0)     # % rencana kumulatif
    actual_pct = Column(Float, default=0.0)      # % realisasi kumulatif
    actual_cost = Column(Float, default=0.0)     # biaya aktual kumulatif (ACWP)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="progress_entries")


class VOStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class VariationOrder(Base):
    """Variation Order (perintah perubahan / CCO)."""

    __tablename__ = "variation_orders"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    vo_number = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(VOStatus), default=VOStatus.DRAFT, index=True)
    amount = Column(Float, default=0.0)  # nilai VO (Rp, + menambah / - mengurangi)
    change_region_id = Column(Integer, ForeignKey("change_regions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="variation_orders")


class RFIStatus(str, enum.Enum):
    OPEN = "open"
    ANSWERED = "answered"
    CLOSED = "closed"


class RFI(Base):
    """Request for Information — pertanyaan teknis/klarifikasi kontrak."""

    __tablename__ = "rfis"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    rfi_number = Column(String(50), nullable=False)
    subject = Column(String(255), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(Enum(RFIStatus), default=RFIStatus.OPEN, index=True)
    variation_order_id = Column(Integer, ForeignKey("variation_orders.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    answered_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="rfis")

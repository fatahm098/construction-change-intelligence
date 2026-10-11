import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample_drawings")
PDF_REV0 = os.path.join(DATA_DIR, "drawing_rev0.pdf")
PDF_REV1 = os.path.join(DATA_DIR, "drawing_rev1.pdf")
BOQ_XLSX = os.path.join(DATA_DIR, "sample_boq.xlsx")


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_end_to_end_project_workflow():
    # 1. Create Project
    res = client.post("/api/projects", json={
        "name": "Proyek Menara Sudirman Phase 1",
        "description": "Pengujian automated drawing diff dan linking BOQ."
    })
    assert res.status_code == 200
    project = res.json()
    project_id = project["id"]
    assert project["name"] == "Proyek Menara Sudirman Phase 1"

    # 2. Upload Drawings Rev 0 and Rev 1
    with open(PDF_REV0, "rb") as f0:
        res_dwg0 = client.post(
            "/api/drawings/upload",
            data={"project_id": project_id, "revision": 0},
            files={"file": ("drawing_rev0.pdf", f0, "application/pdf")},
        )
    assert res_dwg0.status_code == 200
    dwg0 = res_dwg0.json()
    assert dwg0["revision"] == 0
    assert os.path.exists(dwg0["png_path"])

    with open(PDF_REV1, "rb") as f1:
        res_dwg1 = client.post(
            "/api/drawings/upload",
            data={"project_id": project_id, "revision": 1},
            files={"file": ("drawing_rev1.pdf", f1, "application/pdf")},
        )
    assert res_dwg1.status_code == 200
    dwg1 = res_dwg1.json()
    assert dwg1["revision"] == 1

    # 3. Upload BOQ Spreadsheet
    with open(BOQ_XLSX, "rb") as fb:
        res_boq = client.post(
            "/api/boq/upload",
            data={"project_id": project_id},
            files={"file": ("sample_boq.xlsx", fb, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
    assert res_boq.status_code == 200
    boq_items = res_boq.json()
    assert len(boq_items) >= 5
    beton_item = next(it for it in boq_items if "Beton Kolom K1" in it["description"])
    assert beton_item["unit_price"] == 1250000.0

    # 4. Run Analysis
    res_analysis = client.post(
        f"/api/analysis/run?project_id={project_id}&drawing_ref_id={dwg0['id']}&drawing_rev_id={dwg1['id']}&min_area=350"
    )
    assert res_analysis.status_code == 200
    analysis_data = res_analysis.json()
    assert analysis_data["total_regions"] >= 1
    assert len(analysis_data["regions"]) == analysis_data["total_regions"]

    # Cari region yang merupakan kolom (yang memiliki bounding box besar atau teks dimensi)
    column_region = analysis_data["regions"][0]
    region_id = column_region["id"]
    assert column_region["status"] == "pending"

    # 5. Verify Dimension & Link ke BOQ
    res_verify = client.post(
        f"/api/analysis/region/{region_id}/verify",
        json={
            "element_type": "column",
            "dim_before_w": 300.0,
            "dim_before_h": 300.0,
            "dim_after_w": 400.0,
            "dim_after_h": 400.0,
            "height_or_length_m": 4.0,
            "link_boq_item_id": beton_item["id"],
        },
    )
    assert res_verify.status_code == 200
    v_data = res_verify.json()
    assert v_data["volume_before_m3"] == 0.36
    assert v_data["volume_after_m3"] == 0.64
    assert round(v_data["delta_volume_m3"], 2) == 0.28

    # 6. Check Project Summary
    res_sum = client.get(f"/api/projects/{project_id}/summary")
    assert res_sum.status_code == 200
    summary = res_sum.json()
    assert summary["verified_regions"] == 1
    # Cost delta = 0.28 m3 * 1,250,000 = 350,000 IDR
    assert summary["total_cost_delta"] == 350000.0

    # 7. Export CSV
    res_csv = client.get(f"/api/export/csv/{project_id}")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "350,000.00" in res_csv.text

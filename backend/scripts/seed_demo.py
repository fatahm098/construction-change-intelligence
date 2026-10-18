"""Seed proyek demo lengkap dari `samples/` (idempoten).

Membuat satu proyek berisi data di semua modul supaya UI bisa langsung dicoba:
BOQ, dua revisi gambar, hasil analisis + cost impact, Variation Order, RFI,
progress/EVM, inspeksi QC, laporan K3, dan dokumen RKS untuk Document Q&A.

Jalankan dari folder `backend/`:

    ./.venv/Scripts/python.exe scripts/seed_demo.py

Kalau proyek dengan nama yang sama sudah ada, script berhenti tanpa mengubah apa pun.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

DEMO_NAME = "Gedung Kantor 2 Lantai — Demo"
SAMPLES = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "samples"))


def _sample(name: str) -> str:
    path = os.path.join(SAMPLES, name)
    if not os.path.exists(path):
        raise SystemExit(f"File sample tidak ditemukan: {path}")
    return path


def main() -> None:
    client = TestClient(app)

    existing = [
        p
        for p in client.get("/api/projects").json()
        if p["name"] == DEMO_NAME
    ]
    if existing:
        print(f"Proyek demo sudah ada (id={existing[0]['id']}), tidak ada perubahan.")
        return

    # 1. Proyek
    project = client.post(
        "/api/projects",
        json={
            "name": DEMO_NAME,
            "description": "Data contoh dari folder samples/: RAB, denah rev A/B, RKS.",
        },
    ).json()
    pid = project["id"]
    print(f"proyek dibuat: id={pid}")

    # 2. BOQ kontrak (rev A)
    with open(_sample("boq_rev_A.xlsx"), "rb") as f:
        boq = client.post(
            f"/api/boq/upload",
            data={"project_id": pid},
            files={"file": ("boq_rev_A.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        ).json()
    print(f"BOQ: {len(boq)} item")

    # 3. Dua revisi gambar
    def upload_drawing(name: str, revision: int) -> int:
        with open(_sample(name), "rb") as f:
            res = client.post(
                "/api/drawings/upload",
                data={"project_id": pid, "revision": revision},
                files={"file": (name, f, "application/pdf")},
            )
        res.raise_for_status()
        return res.json()["id"]

    ref_id = upload_drawing("gambar_denah_rev_A.pdf", 0)
    rev_id = upload_drawing("gambar_denah_rev_B.pdf", 1)
    print(f"gambar: ref={ref_id} rev={rev_id}")

    # 4. Analisis perubahan
    run = client.post(
        f"/api/analysis/run?project_id={pid}&drawing_ref_id={ref_id}&drawing_rev_id={rev_id}"
    ).json()
    print(f"analisis: {run['total_regions']} region")

    # 5. Verifikasi region terbesar sebagai kolom K1 -> K2
    region = max(run["regions"], key=lambda r: r["area"])
    kolom = next(
        (i for i in boq if "kolom" in i["description"].lower() and "beton" in i["description"].lower()),
        boq[0],
    )
    verified = client.post(
        f"/api/analysis/region/{region['id']}/verify",
        json={
            "element_type": "column",
            "dim_before_w": 300,
            "dim_before_h": 300,
            "dim_after_w": 400,
            "dim_after_h": 400,
            "height_or_length_m": 3.5,
            "link_boq_item_id": kolom["id"],
        },
    ).json()
    print(
        f"verifikasi region #{region['region_index']}: "
        f"{verified['volume_before_m3']:.3f} -> {verified['volume_after_m3']:.3f} m3"
    )

    detail = client.get(f"/api/analysis/{run['id']}").json()
    impact = next(
        (r["cost_impact"] for r in detail["regions"] if r["id"] == region["id"] and r.get("cost_impact")),
        None,
    )
    amount = float(impact["total_cost_delta"]) if impact else 0.0
    print(f"cost impact: Rp {amount:,.0f}")

    # 6. Variation Order + RFI
    vo = client.post(
        f"/api/vo/{pid}",
        json={
            "vo_number": "VO-001",
            "title": "Penambahan bay ruang rapat dan kolom K2 400x400",
            "description": (
                "Revisi B memperlebar bangunan 1 bay (10.000 -> 11.000 mm), menambah "
                "ruang pantry, dan mengganti kolom sudut K1 300x300 menjadi K2 400x400."
            ),
            "amount": amount,
            "change_region_id": region["id"],
        },
    ).json()
    client.patch(f"/api/vo/{vo['id']}/status", json={"status": "submitted"})
    rfi = client.post(
        f"/api/rfi/{pid}",
        json={
            "rfi_number": "RFI-001",
            "subject": "Konfirmasi mutu beton kolom K2",
            "question": (
                "RKS Pasal 3 menyebut K-300, sedangkan BOQ revisi B memakai harga K-350. "
                "Mutu mana yang menjadi acuan pelaksanaan?"
            ),
            "variation_order_id": vo["id"],
        },
    ).json()
    client.post(
        f"/api/rfi/{rfi['id']}/answer",
        json={"answer": "Gunakan K-350 sesuai BOQ revisi B; RKS akan diamandemen pada addendum berikutnya."},
    )
    print(f"VO-001 (submitted) + RFI-001 (dijawab)")

    # 7. Progress / EVM (dua periode)
    for period, planned, actual, cost in [
        ("2026-02", 20.0, 18.0, 165_000_000),
        ("2026-03", 45.0, 41.5, 380_000_000),
    ]:
        client.post(
            f"/api/progress/{pid}/entries",
            json={
                "period": period,
                "planned_pct": planned,
                "actual_pct": actual,
                "actual_cost": cost,
                "note": "Laporan bulanan dari site engineer.",
            },
        )
    print("progress: 2 periode")

    # 8. QC — dua inspeksi, satu lulus dan satu tidak, lalu difinalisasi
    inspection = client.post(
        f"/api/qc/{pid}",
        json={
            "inspection_number": "INS-001",
            "title": "Inspeksi pembesian dan bekisting kolom lantai 1",
            "location": "Grid B-2, lantai 1",
            "category": "rebar",
            "inspector": "Ir. Budi Santoso",
            "note": "Inspeksi sebelum pengecoran.",
            "items": [
                {"description": "Diameter tulangan sesuai gambar (D13)", "standard": "SNI 2847:2019", "result": "ok"},
                {"description": "Jarak sengkang 150 mm", "standard": "SNI 2847:2019", "result": "ok"},
                {"description": "Selimut beton 40 mm", "standard": "SNI 2847:2019", "result": "not_ok",
                 "note": "Ditemukan 2 titik selimut 30 mm, perlu spacer tambahan."},
                {"description": "Kebersihan area sebelum cor", "standard": "RKS Pasal 3", "result": "ok"},
            ],
        },
    ).json()
    client.patch(
        f"/api/qc/inspection/{inspection['id']}/status", json={"status": "failed"}
    )

    concrete = client.post(
        f"/api/qc/{pid}",
        json={
            "inspection_number": "INS-002",
            "title": "Uji slump dan benda uji beton K-300",
            "location": "Area batching plant",
            "category": "concrete",
            "inspector": "Siti Rahmawati",
            "items": [
                {"description": "Slump 12 ± 2 cm", "standard": "RKS Pasal 3", "result": "ok"},
                {"description": "Benda uji silinder 28 hari", "standard": "SNI 2847:2019", "result": "ok"},
                {"description": "Suhu beton < 32 °C", "standard": "SNI 2847:2019", "result": "ok"},
            ],
        },
    ).json()
    client.patch(
        f"/api/qc/inspection/{concrete['id']}/status", json={"status": "passed"}
    )
    print(f"QC: {inspection['inspection_number']} (failed) + {concrete['inspection_number']} (passed)")

    # 9. K3
    client.post(
        f"/api/k3/{pid}",
        json={
            "report_number": "K3-001",
            "title": "Pekerja tidak memakai full body harness",
            "category": "unsafe_act",
            "severity": "high",
            "description": "Dua pekerja di lantai 2 bekerja tanpa harness saat memasang bekisting balok.",
            "action_taken": "Pekerjaan dihentikan, toolbox meeting, dan harness pengganti dibagikan.",
            "reported_by": "Petugas K3 — Andi",
        },
    )
    print("K3: 1 laporan")

    # 10. Dokumen RKS untuk Document Q&A
    with open(_sample("rks_gedung_2lantai.pdf"), "rb") as f:
        doc = client.post(
            f"/api/projects/{pid}/documents",
            data={"doc_type": "rks"},
            files={"file": ("rks_gedung_2lantai.pdf", f, "application/pdf")},
        ).json()
    print(f"dokumen RKS: {doc.get('filename')} (status={doc.get('status')})")

    print("\nSelesai. Buka http://localhost:3000 lalu pilih proyek:", DEMO_NAME)


if __name__ == "__main__":
    main()

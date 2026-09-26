import io

from PIL import Image


def _sample_jpeg_bytes(color=(40, 180, 40)) -> bytes:
    img = Image.new("RGB", (200, 200), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_submit_waste_report_returns_ml_prediction(client, auth_headers):
    files = {"image": ("test.jpg", io.BytesIO(_sample_jpeg_bytes()), "image/jpeg")}
    data = {"latitude": "31.1", "longitude": "77.17", "description": "Pile of waste near the gate"}
    resp = client.post("/api/waste/report", data=data, files=files, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["ml_prediction"]["mode"] == "demo"
    assert 0.0 <= body["ml_prediction"]["confidence"] <= 1.0
    assert body["category"] in {
        "Plastic", "Paper", "Glass", "Metal", "Organic", "E-Waste", "Textile", "Other",
    }


def test_waste_report_awards_points(client, auth_headers):
    before = client.get("/api/auth/me", headers=auth_headers).json()["points"]
    files = {"image": ("test.jpg", io.BytesIO(_sample_jpeg_bytes()), "image/jpeg")}
    client.post("/api/waste/report", data={"latitude": "1", "longitude": "1"}, files=files, headers=auth_headers)
    after = client.get("/api/auth/me", headers=auth_headers).json()["points"]
    assert after == before + 10


def test_waste_report_rejects_bad_file_type(client, auth_headers):
    files = {"image": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
    resp = client.post("/api/waste/report", data={"latitude": "1", "longitude": "1"}, files=files, headers=auth_headers)
    assert resp.status_code == 400


def test_ml_classify_endpoint_standalone(client, auth_headers):
    files = {"image": ("test.jpg", io.BytesIO(_sample_jpeg_bytes()), "image/jpeg")}
    resp = client.post("/api/ml/classify", files=files, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) >= {"category", "confidence", "recyclable", "recommended_disposal", "mode"}


def test_ml_classify_requires_auth(client):
    files = {"image": ("test.jpg", io.BytesIO(_sample_jpeg_bytes()), "image/jpeg")}
    resp = client.post("/api/ml/classify", files=files)
    assert resp.status_code == 401

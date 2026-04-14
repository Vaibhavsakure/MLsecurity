"""Tests for the health check endpoint."""


def test_health_returns_ok(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "models" in data
    assert "shap" in data


def test_health_lists_all_platforms(client):
    resp = client.get("/api/health")
    models = resp.json()["models"]
    expected = {"instagram", "twitter", "reddit", "facebook", "linkedin", "youtube"}
    assert set(models.keys()) == expected


def test_health_models_are_loaded(client):
    resp = client.get("/api/health")
    models = resp.json()["models"]
    # At least the 4 real-world models should be loaded
    for platform in ["instagram", "twitter", "reddit", "facebook"]:
        assert models[platform] is True, f"{platform} model not loaded"


def test_health_returns_version(client):
    """Health endpoint should return the API version string."""
    resp = client.get("/api/health")
    data = resp.json()
    assert "version" in data
    assert data["version"] == "5.0.0"


def test_health_returns_uptime(client):
    """Health endpoint should return a non-negative uptime in seconds."""
    resp = client.get("/api/health")
    data = resp.json()
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], int)
    assert data["uptime_seconds"] >= 0


def test_health_returns_models_loaded_count(client):
    """models_loaded should be an int between 0 and 6."""
    resp = client.get("/api/health")
    data = resp.json()
    assert "models_loaded" in data
    assert 0 <= data["models_loaded"] <= 6


def test_health_returns_ensemble_status(client):
    """ensemble field should have an entry for each platform."""
    resp = client.get("/api/health")
    data = resp.json()
    assert "ensemble" in data
    ensemble = data["ensemble"]
    expected = {"instagram", "twitter", "reddit", "facebook", "linkedin", "youtube"}
    assert set(ensemble.keys()) == expected
    for platform, has_ens in ensemble.items():
        assert isinstance(has_ens, bool), f"ensemble[{platform}] should be bool"

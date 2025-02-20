# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 The HuggingFace Authors.


from libcommon.queue import _clean_queue_database
from libcommon.simple_cache import _clean_cache_database
from pytest import MonkeyPatch, fixture, mark
from starlette.testclient import TestClient

from api.app import create_app
from api.config import AppConfig


# see https://github.com/pytest-dev/pytest/issues/363#issuecomment-406536200
@fixture(scope="module")
def real_monkeypatch():
    monkeypatch = MonkeyPatch()
    monkeypatch.setenv("CACHE_MONGO_DATABASE", "datasets_server_cache_test")
    monkeypatch.setenv("QUEUE_MONGO_DATABASE", "datasets_server_queue_test")
    monkeypatch.setenv("COMMON_HF_ENDPOINT", "https://huggingface.co")
    monkeypatch.setenv("COMMON_HF_TOKEN", "")
    yield monkeypatch
    monkeypatch.undo()


@fixture(scope="module")
def real_client(real_monkeypatch: MonkeyPatch) -> TestClient:
    return TestClient(create_app())


@fixture(scope="module")
def real_app_config(real_monkeypatch: MonkeyPatch) -> AppConfig:
    app_config = AppConfig()
    if "test" not in app_config.cache.mongo_database or "test" not in app_config.queue.mongo_database:
        raise ValueError("Test must be launched on a test mongo database")
    if app_config.common.hf_endpoint != "https://huggingface.co":
        raise ValueError("Test must be launched on the production hub")
    return app_config


@fixture(autouse=True)
def real_clean_mongo_databases(real_app_config: AppConfig) -> None:
    _clean_cache_database()
    _clean_queue_database()


@mark.real_dataset
def test_webhook(
    real_client: TestClient,
) -> None:
    dataset = "glue"
    payload = {"event": "add", "repo": {"type": "dataset", "name": dataset, "gitalyUid": "123"}}
    response = real_client.post("/webhook", json=payload)
    assert response.status_code == 200, response.text

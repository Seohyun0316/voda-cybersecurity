"""Flask API routes and request validation."""

from __future__ import annotations

from flask import Flask, jsonify, request

from vibesafe.detector import Detector


def create_app(detector: Detector | None = None) -> Flask:
    app = Flask(__name__)
    service = detector or Detector()

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "rule_engine": {
                    "status": "ready",
                    "rules_loaded": service.rule_count,
                },
                "ml": service.ml_status,
            }
        )

    @app.post("/detect")
    def detect():
        payload = request.get_json(silent=True)
        validation_error = _validate_request(payload)
        if validation_error:
            return jsonify({"error": validation_error}), 400

        return jsonify(
            service.detect(
                code=payload["code"],
                language=payload["language"],
                file_name=payload["file_name"],
            )
        )

    return app


def _validate_request(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return "요청 본문은 JSON 객체여야 합니다."

    for field in ("code", "language", "file_name"):
        if field not in payload:
            return f"필수 필드가 누락되었습니다: {field}"
        if not isinstance(payload[field], str):
            return f"{field} 필드는 문자열이어야 합니다."

    if payload["language"].strip().lower() != "python":
        return "현재 지원하는 language 값은 python뿐입니다."
    if not payload["file_name"].strip():
        return "file_name 필드는 비어 있을 수 없습니다."
    return None

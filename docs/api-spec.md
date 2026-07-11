# /detect API 스펙

## Request
`POST /detect`
```json
{
  "code": "string (검사할 코드)",
  "language": "python | javascript"
}
```

## Response
```json
{
  "findings": [
    {
      "rule_id": "A04-798-01",
      "cwe": "CWE-798",
      "line": 12,
      "severity": "high",
      "risk_score": 18,
      "message": "하드코딩된 API 키가 감지되었습니다.",
      "legal_note": "개인정보보호법 위반 소지가 있습니다."
    }
  ]
}
```

> TODO: M·F 파트 합의된 최종 스키마로 갱신

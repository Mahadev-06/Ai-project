# ClaimLens REST API Reference

## Base URL
```
http://localhost:8000/api/v1
```

All requests and responses use `application/json` payloads unless otherwise specified.

---

## 1. Authentication
Analyses in ClaimLens are protected by job-scoped access tokens. When a job is created via `POST /analyses`, the server generates a cryptographically secure random token returned in `access_token`. Subsequent requests to view or cancel that specific job must provide the token in the HTTP `Authorization` header:

```http
Authorization: Bearer <access_token>
```

---

## 2. Endpoints

### 2.1 Submit New Analysis
Enqueues an analysis job for processing. Returns HTTP 202 Accepted.

- **Method:** `POST`
- **Path:** `/analyses`
- **Headers:** `Content-Type: application/json`

#### Request Body
```json
{
  "input_text": "Water boils at 100 degrees Celsius under standard atmospheric pressure.",
  "evidence_mode": "local"
}
```

Or for article URL analysis:
```json
{
  "input_url": "https://example.org/article-to-verify",
  "evidence_mode": "local"
}
```

#### Fields
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `input_text` | `string` | Optional* | Text containing factual claims (max 10,000 characters). |
| `input_url` | `string` | Optional* | Valid HTTP/HTTPS article URL (*Either `input_text` or `input_url` required). |
| `evidence_mode` | `string` | No | `"local"` (default) or `"live"`. |

#### Response (202 Accepted)
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "queued",
  "stage": "queued",
  "created_at": "2026-09-20T17:00:00.000000Z",
  "access_token": "a4d8c7e91f0b2a3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c"
}
```

---

### 2.2 Retrieve Analysis Status & Report
Polls the execution state or returns the finished verification findings.

- **Method:** `GET`
- **Path:** `/analyses/{job_id}`
- **Headers:** `Authorization: Bearer <access_token>`

#### Response (200 OK — While Running)
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "running",
  "stage": "comparing",
  "created_at": "2026-09-20T17:00:00.000000Z",
  "completed_at": null,
  "report": null
}
```

#### Response (200 OK — When Completed)
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "completed",
  "stage": "completed",
  "created_at": "2026-09-20T17:00:00.000000Z",
  "completed_at": "2026-09-20T17:00:03.500000Z",
  "report": {
    "input_summary": "Water boils at 100 degrees Celsius under standard atmospheric pressure.",
    "analysis_date": "2026-09-20T17:00:01.000000Z",
    "evidence_mode": "local",
    "corpus_version": "1.0.0",
    "model_versions": {
      "spacy": "en_core_web_sm",
      "encoder": "sentence-transformers/all-MiniLM-L6-v2",
      "nli": "cross-encoder/nli-deberta-v3-small"
    },
    "coverage_warnings": [],
    "claims": [
      {
        "id": "claim-1",
        "claim_text": "Water boils at 100 degrees Celsius under standard atmospheric pressure.",
        "original_sentence": "Water boils at 100 degrees Celsius under standard atmospheric pressure.",
        "char_start": 0,
        "char_end": 71,
        "outcome": "supported",
        "reason": "This claim is supported by 1 evidence passage(s) (water-boiling-p0). The retrieved evidence directly aligns with the claim's assertion.",
        "linguistic_features": {
          "entities": [{"text": "100 degrees Celsius", "label": "QUANTITY"}],
          "dates": [],
          "numbers": ["100"],
          "noun_phrases": ["Water", "100 degrees Celsius", "standard atmospheric pressure"],
          "has_negation": false,
          "has_qualifier": false,
          "has_attribution": false
        },
        "evidence": [
          {
            "id": "water-boiling-p0",
            "doc_id": "water-boiling",
            "title": "Boiling Point of Water and Thermodynamic Properties",
            "publisher": "National Institute of Standards and Technology / USGS",
            "url": "https://www.usgs.gov/special-topics/water-science-school/science/water-density",
            "publication_date": "2023-04-15",
            "excerpt": "Under standard atmospheric pressure of 1 atmosphere (101.325 kPa), the boiling point of pure water is defined as 100 degrees Celsius (212 degrees Fahrenheit).",
            "full_context": "Under standard atmospheric pressure of 1 atmosphere (101.325 kPa), the boiling point of pure water is defined as 100 degrees Celsius (212 degrees Fahrenheit). As altitude increases and atmospheric pressure decreases, the boiling temperature of water decreases correspondingly.",
            "stance": "supports",
            "stance_scores": {
              "entailment": 0.9412,
              "contradiction": 0.0083,
              "neutral": 0.0505
            },
            "relevance_score": 0.825,
            "source_credibility": {
              "provenance_category": "documented",
              "signals": [
                {
                  "name": "Identifiable publisher",
                  "value": "National Institute of Standards and Technology / USGS",
                  "status": "observed",
                  "reason": "Publisher name is available in the source metadata."
                },
                {
                  "name": "Editorial/corrections policy",
                  "value": "Available",
                  "status": "observed",
                  "reason": "This publisher is known to have editorial review processes."
                }
              ]
            }
          }
        ]
      }
    ]
  }
}
```

---

### 2.3 Cancel Analysis
Cancels an ongoing analysis task.

- **Method:** `POST`
- **Path:** `/analyses/{job_id}/cancel`
- **Headers:** `Authorization: Bearer <access_token>`

#### Response (200 OK)
```json
{
  "status": "cancelled",
  "detail": "Cancellation requested. Currently running model call may finish first."
}
```

---

### 2.4 Delete Analysis
Removes the job and its verification report from the server.

- **Method:** `DELETE`
- **Path:** `/analyses/{job_id}`
- **Headers:** `Authorization: Bearer <access_token>`

#### Response (200 OK)
```json
{
  "status": "deleted"
}
```

---

### 2.5 Liveness Probe
- **Method:** `GET`
- **Path:** `/health`
- **Response:** `{"status": "ok", "version": "0.1.0"}`

---

### 2.6 Readiness Probe
Inspects models, corpus status, and provider configs.

- **Method:** `GET`
- **Path:** `/health/readiness`
- **Response:**
```json
{
  "ready": true,
  "models": {
    "spacy": "en_core_web_sm",
    "encoder": "sentence-transformers/all-MiniLM-L6-v2",
    "nli": "cross-encoder/nli-deberta-v3-small"
  },
  "corpus": {
    "loaded": true,
    "version": "1.0.0",
    "passages": 124
  },
  "providers": {
    "brave_configured": false,
    "google_factcheck_configured": false
  }
}
```

---

## 3. Error Responses

| Code | Status | Meaning |
| :--- | :--- | :--- |
| **400** | Bad Request | Input text exceeded 10,000 chars, non-English detected, or invalid URL. |
| **403** | Forbidden | Missing or invalid access token. |
| **404** | Not Found | Job ID does not exist or expired. |
| **429** | Too Many Requests | Server capacity reached (`MAX_QUEUE_SIZE = 10`). |
| **500** | Internal Error | Unexpected failure; returns safe generic explanation. |

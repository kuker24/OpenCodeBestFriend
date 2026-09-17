# Storyboard JSON Schema (`storyboard.schema.md`)

Specification and validation rules for `demos/<slug>/storyboard.json`.

## Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DemoStoryboard",
  "type": "object",
  "required": [
    "slug",
    "target_duration_s",
    "voice",
    "lang",
    "scenes"
  ],
  "properties": {
    "slug": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "description": "Unique folder identifier for the demo"
    },
    "target_duration_s": {
      "type": "integer",
      "minimum": 30,
      "maximum": 1200,
      "description": "Total target duration in seconds (e.g. 600 for 10 minutes)"
    },
    "voice": {
      "type": "string",
      "enum": ["id-ID-GadisNeural", "id-ID-ArdiNeural"],
      "description": "Selected Edge TTS voice"
    },
    "lang": {
      "type": "string",
      "const": "id",
      "description": "Language code (strictly 'id' for Indonesian)"
    },
    "scenes": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/definitions/Scene"
      }
    }
  },
  "definitions": {
    "Scene": {
      "type": "object",
      "required": [
        "id",
        "title",
        "duration_s",
        "narration",
        "actions"
      ],
      "properties": {
        "id": {
          "type": "string",
          "pattern": "^scene-[0-9]{2}$",
          "description": "Numbered scene identifier, e.g. scene-01"
        },
        "title": {
          "type": "string",
          "description": "Human-readable scene title"
        },
        "duration_s": {
          "type": "number",
          "minimum": 5,
          "maximum": 180,
          "description": "Target duration for this scene in seconds"
        },
        "narration": {
          "type": "string",
          "description": "Full Indonesian spoken voiceover text for this scene"
        },
        "actions": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/Action"
          }
        }
      }
    },
    "Action": {
      "type": "object",
      "required": ["type"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["goto", "wait", "click", "type", "scroll", "hover", "highlight"]
        },
        "selector": {
          "type": "string",
          "description": "CSS selector or Playwright locator"
        },
        "value": {
          "type": "string",
          "description": "Text value to type or URL to navigate to"
        },
        "duration_ms": {
          "type": "integer",
          "description": "Wait time or scroll animation duration in milliseconds"
        }
      }
    }
  }
}
```

## Duration Validation Contract

The sum of all scene durations must match `target_duration_s` within a tolerance of ±15 seconds:

$$\left| \left( \sum_{i=1}^{N} \text{scene}_i.\text{duration\_s} \right) - \text{target\_duration\_s} \right| \le 15$$

If the difference exceeds 15 seconds, storyboard validation fails and prompts adjustment before synthesis or capture begins.

## Example `storyboard.json`

```json
{
  "slug": "crm-demo-2026",
  "target_duration_s": 120,
  "voice": "id-ID-GadisNeural",
  "lang": "id",
  "scenes": [
    {
      "id": "scene-01",
      "title": "Halaman Utama & Navigasi",
      "duration_s": 55,
      "narration": "Selamat datang di sistem manajemen relasi pelanggan. Pada layar utama, kita dapat melihat metrik ringkasan penjualan dan antrean tugas aktif hari ini.",
      "actions": [
        {"type": "goto", "value": "http://localhost:3000/dashboard"},
        {"type": "wait", "duration_ms": 2000},
        {"type": "hover", "selector": "[data-testid='metric-sales']"},
        {"type": "scroll", "value": "down"}
      ]
    },
    {
      "id": "scene-02",
      "title": "Pencatatan Prospek Baru",
      "duration_s": 65,
      "narration": "Untuk menambahkan prospek baru, klik tombol Tambah di sudut kanan atas. Masukkan nama kontak, email perusahaan, dan nilai estimasi kontrak.",
      "actions": [
        {"type": "click", "selector": "button#btn-new-lead"},
        {"type": "type", "selector": "input#lead-name", "value": "PT Solusi Nusantara"},
        {"type": "type", "selector": "input#lead-email", "value": "halo@solusinusantara.id"},
        {"type": "click", "selector": "button#btn-save"},
        {"type": "wait", "duration_ms": 1500}
      ]
    }
  ]
}
```

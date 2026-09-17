# Beat Sheet Planning (`beats.md`)

Guidelines for constructing timed scene beats for application walkthroughs and contest demos.

## Timing Model

- **Target Duration**: Typically 600 seconds (10 minutes) for full contest demos, or 180–300 seconds for feature spotlights.
- **Tolerance Gate**: `sum(scene_duration) == target_duration ± 15 seconds`.
- **Clip Count**: 8 to 12 clips for a 10-minute demo. Each clip lasts between 40 and 90 seconds.
- **Pacing**: 130–150 spoken Indonesian words per minute (~2.2 to 2.5 words per second).

## Standard 10-Minute Beat Template (8–10 Scenes)

| Scene | Title | Duration | Spoken Words | Focus |
|---|---|---|---|---|
| `scene-01` | Pengenalan & Masalah Nyata | 50s | 110–120 | Masalah pengguna tanpa aplikasi. Optional HyperFrames title card (5s). |
| `scene-02` | Halaman Masuk & Dashboard | 60s | 130–150 | Login dengan akun seed, navigasi ringkasan metrik utama. |
| `scene-03` | Alur Kerja Utama (Langkah 1) | 75s | 165–185 | Pembuatan data baru, pengisian formulir, validasi input. |
| `scene-04` | Alur Kerja Utama (Langkah 2) | 80s | 175–200 | Proses pemrosesan sistem, interaksi tabel, pemilihan filter. |
| `scene-05` | Fitur Kunci & Keunggulan | 75s | 165–185 | Fitur diferensiasi (misal: otomatisasi, deteksi, kalkulasi). |
| `scene-06` | Penanganan Kondisi Khusus | 65s | 140–160 | Validasi error ramah pengguna atau keamanan akses. |
| `scene-07` | Laporan & Ekspor Data | 65s | 140–160 | Visualisasi hasil, unduh laporan PDF/CSV atau audit log. |
| `scene-08` | Ringkasan Dampak & Penutup | 55s | 120–135 | Rangkuman manfaat terukur, CTA, optional HyperFrames end card. |
| **Total** | | **525s (8m45s)** | **1145–1335** | *Sesuai target ±15s bila ditargetkan 9 menit, atau tambah 1 scene untuk 10m.* |

## Writing Rules for Indonesian Spoken Narration

1. **Short, Oral Sentences**: 8–16 words per sentence. Write for the ear, not an academic journal.
2. **Action Synchronization**: Match every phrase to what the cursor is doing at that second.
3. **No Empty Fluff (Anti-Slop)**:
   - ❌ *"Di era digital yang serba cepat ini..."* → ✅ *"Mari kita lihat proses verifikasi dokumen pelanggan."*
   - ❌ *"Aplikasi ini memanfaatkan solusi AI inovatif yang seamless..."* → ✅ *"Sistem membaca data formulir dan mengisi kolom otomatis dalam dua detik."*
   - ❌ *"Fitur cutting-edge yang menjadi game changer..."* → ✅ *"Fitur ini memangkas langkah manual dari lima tahap menjadi satu klik."*
4. **Pronunciation Clarity**: Write acronyms phonetically if needed (e.g. `API` diucapkan *A-P-I*, bukan *api* membara).

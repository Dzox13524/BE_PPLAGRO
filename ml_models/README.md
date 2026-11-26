# ml_models/

Letakkan file model hasil training di folder ini. Nama file dapat diatur lewat `.env`.

| AI | File default | Format didukung | Lokasi kode loader |
|----|--------------|-----------------|--------------------|
| AI Diagnosis Citra Selada | `best_lettuce_yolo26_v2.pt` | `.pt` (Ultralytics YOLO / PyTorch), `.h5/.keras` (TensorFlow), `.onnx` (ONNX Runtime) | `app/modules/diagnosis/cv_detector.py` → `LettuceDiagnosisDetector.load()` |

## Kontrak model

**AI Diagnosis (klasifikasi citra daun)** – input RGB citra daun selada (dengan opsional kalibrasi temperature scaling `temperature.txt`), output kelas penyakit:
`["Bacterial", "Downy_mildew", "Lettuce Mosaic Virus", "Powdery_mildew", "Septoria_Blight"]`.

Selama file model belum ada, API otomatis memakai
**fallback inference** (heuristik analisis warna daun) sehingga semua endpoint tetap berfungsi.


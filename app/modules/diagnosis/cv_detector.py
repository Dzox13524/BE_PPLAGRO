"""AI 2 - Lettuce Image Diagnosis (Computer Vision Adapter + Singleton).

Model dimuat SEKALI saat FastAPI lifespan startup (`lettuce_detector.load(...)`).

Dukungan Model:
1. **Ultralytics YOLO (Classification / Detection)**:
   Mendukung model YOLO format `.pt` (misal `best_lettuce_yolo26_v2.pt`).
   Mendukung Temperature Scaling post-processing menggunakan parameter dari `temperature.txt`
   untuk kalibrasi probabilitas kelas penyakit.
2. **PyTorch standard CNN** (`.pt`, `.pth`).
3. **TensorFlow/Keras** (`.h5`, `.keras`).
4. **ONNX Runtime** (`.onnx`).
5. **Fallback Heuristic** berbasis analisis ruang warna HSV untuk ketahanan sistem
   jika file model belum tersedia.
"""
from __future__ import annotations

import io
import logging
import os
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageOps

from app.core.config import BASE_DIR, settings

logger = logging.getLogger(__name__)

# Atur direktori konfigurasi Ultralytics agar tidak gagal menulis ke roaming AppData
os.environ.setdefault("YOLO_CONFIG_DIR", str((BASE_DIR / ".ultralytics").resolve()))

# ---------------------------------------------------------------------------
# Label kelas model YOLO dan Fallback
# ---------------------------------------------------------------------------
YOLO_CLASSES: list[str] = [
    "Bacterial",
    "Downy_mildew",
    "Lettuce Mosaic Virus",
    "Powdery_mildew",
    "Septoria_Blight",
]

FALLBACK_CLASSES: list[str] = [
    "Healthy",
    "Tip Burn",
    "Leaf Blight",
    "Downy Mildew",
]

# Gabungan seluruh label kelas yang didukung untuk filter & metadata
CLASS_LABELS: list[str] = YOLO_CLASSES + [c for c in FALLBACK_CLASSES if c not in YOLO_CLASSES]

IMG_SIZE = 224
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

# ---------------------------------------------------------------------------
# Basis pengetahuan penyakit selada (Knowledge Base)
# ---------------------------------------------------------------------------
DISEASE_KB: dict[str, dict[str, Any]] = {
    # --- Kelas Model YOLO ---
    "Bacterial": {
        "display": "Bacterial (Hawar Bakteri / Busuk Bakteri)",
        "disease_info": (
            "Penyakit hawar daun bakteri (Xanthomonas campestris pv. vitians atau Pseudomonas cichorii) pada selada. "
            "Gejala awal berupa bercak basah (water-soaked) kecil bersudut yang kemudian berubah warna menjadi cokelat "
            "hingga hitam, sering dikelilingi halo kekuningan. Pada kondisi lembap, bercak cepat meluas dan membusuk basah."
        ),
        "summary": "Terdeteksi infeksi bakteri pada helaian daun selada.",
        "treatments": [
            "Segera buang dan musnahkan daun atau tanaman terinfeksi agar tidak menular ke talang lain.",
            "Kurangi kelembapan lingkungan dan pastikan daun tidak terkena cipratan air atau tetesan embun pipa.",
            "Semprotkan bakterisida berbahan tembaga (copper hydroxide/oxychloride) atau agens hayati Bacillus subtilis sesuai dosis.",
            "Sterilkan netpot, talang, dan instalasi hidroponik dengan larutan klorin sebelum siklus tanam berikutnya.",
        ],
    },
    "Downy_mildew": {
        "display": "Downy Mildew (Embun Bulu)",
        "disease_info": (
            "Downy mildew disebabkan oleh oomycete Bremia lactucae. Gejala berupa bercak kuning pucat bersudut "
            "yang dibatasi tulang daun di permukaan atas helaian, dengan lapisan spora putih keabu-abuan seperti bulu halus "
            "di permukaan bawah daun. Berkembang pesat pada kelembapan tinggi (> 85%) dan suhu sejuk 15 - 20°C."
        ),
        "summary": "Terdapat indikasi infeksi embun bulu (Bremia lactucae) pada permukaan daun.",
        "treatments": [
            "Pisahkan tanaman terinfeksi dan segera pangkas daun-daun yang menunjukkan gejala.",
            "Turunkan kelembapan kanopi dengan menyalakan kipas/blower sirkulasi dan perbaiki ventilasi greenhouse.",
            "Aplikasikan fungisida spesifik oomycete (misal berbahan aktif mandipropamid atau metalaksil) sesuai anjuran.",
            "Gunakan varietas selada tahan Bremia lactucae untuk siklus penanaman selanjutnya.",
        ],
    },
    "Lettuce Mosaic Virus": {
        "display": "Lettuce Mosaic Virus (Virus Mosaik Selada)",
        "disease_info": (
            "Penyakit sistemik yang disebabkan oleh Lettuce Mosaic Virus (Potyvirus / LMV). Gejala meliputi pola mosaik belang "
            "hijau muda dan hijau tua pada daun, malformasi helai daun (berkerut/mengerut/lepuh), tepi daun bergelombang, "
            "serta pertumbuhan tanaman yang kerdil. Ditularkan melalui benih terinfeksi dan disebarkan vektor kutu daun (aphids)."
        ),
        "summary": "Terdeteksi gejala infeksi virus mosaik selada (LMV) yang memicu daun berkerut dan belang.",
        "treatments": [
            "Cabut dan musnahkan tanaman yang terinfeksi virus segera (tanaman terinfeksi virus tidak dapat diobati).",
            "Kendalikan vektor serangga (terutama kutu daun/aphids) menggunakan yellow sticky trap atau insektisida nabati/kontak.",
            "Gunakan benih bersertifikat bebas virus (LMV-free certified seeds).",
            "Bersihkan gulma di sekitar area instalasi yang berpotensi menjadi inang perantara kutu daun.",
        ],
    },
    "Powdery_mildew": {
        "display": "Powdery Mildew (Embun Tepung)",
        "disease_info": (
            "Disebabkan jamur Erysiphe cichoracearum (Golovinomyces cichoracearum). Gejala ditandai dengan munculnya bercak atau "
            "lapisan putih menyerupai bedak/tepung di permukaan daun. Daun yang terserang berat menguning, mengering, dan gugur. "
            "Jamur ini menyukai kelembapan relatif tinggi namun berkembang optimal tanpa adanya air bebas di permukaan daun."
        ),
        "summary": "Terdeteksi lapisan spora putih khas embun tepung pada permukaan daun.",
        "treatments": [
            "Pangkas dan buang helai daun yang tertutup lapisan embun tepung.",
            "Semprotkan larutan kalium bikarbonat (3 g/L) atau agen hayati Trichoderma harzianum / minyak nimba (neem oil).",
            "Hindari pemberian pupuk berkadar Nitrogen terlalu tinggi yang menyebabkan jaringan daun terlalu lunak.",
            "Tingkatkan ventilasi udara dan hindari penempatan tanaman yang terlalu rapat.",
        ],
    },
    "Septoria_Blight": {
        "display": "Septoria Blight (Hawar Daun Septoria)",
        "disease_info": (
            "Disebabkan oleh jamur Septoria lactucae. Gejala berupa bercak daun nekrotik tidak beraturan yang membesar, "
            "berwarna cokelat zaitun hingga cokelat tua dengan bintik-bintik hitam kecil (piknidia) di tengah bercak. Sering "
            "menyerang daun tua di bagian bawah terlebih dahulu dan menyebar ke atas lewat percikan air nutrisi.",
        ),
        "summary": "Terdeteksi bercak nekrotik hawar Septoria dengan risiko penyebaran ke helai daun lain.",
        "treatments": [
            "Petik dan musnahkan daun-daun bagian bawah yang bergejala.",
            "Hindari penyiraman atau percikan air langsung ke atas daun (hindari overhead watering).",
            "Aplikasikan fungisida protektif berbahan tembaga atau fungisida kontak berspektrum luas sesuai petunjuk teknis.",
            "Pastikan sirkulasi udara baik dan bersihkan sisa-sisa daun mati di sekitar instalasi.",
        ],
    },

    # --- Kelas Fallback / Kompatibilitas ---
    "Healthy": {
        "display": "Healthy (Sehat)",
        "disease_info": (
            "Tidak terdeteksi gejala penyakit. Daun berwarna hijau segar merata, turgor baik, "
            "tanpa bercak, klorosis, maupun nekrosis pada tepi daun."
        ),
        "summary": "Tanaman dalam kondisi sehat dan tumbuh normal.",
        "treatments": [
            "Pertahankan pH larutan 5.5 - 6.5 dan nutrisi 560 - 840 ppm (EC 0.8 - 1.2 mS/cm).",
            "Lanjutkan monitoring rutin minimal 2 kali seminggu.",
            "Jaga sirkulasi udara dan kebersihan instalasi hidroponik.",
        ],
    },
    "Tip Burn": {
        "display": "Tip Burn (Ujung Daun Terbakar)",
        "disease_info": (
            "Tip burn adalah gangguan fisiologis akibat kekurangan kalsium lokal pada jaringan daun muda yang tumbuh cepat. "
            "Gejala: tepi/ujung daun mengering, berwarna cokelat hingga hitam. Dipicu oleh transpirasi rendah, kelembapan tinggi, "
            "suhu panas, atau EC/PPM terlalu tinggi."
        ),
        "summary": "Terjadi kerusakan jaringan pada tepi daun yang menandakan distribusi kalsium terganggu.",
        "treatments": [
            "Tambahkan sumber kalsium (Calcium Nitrate / Kalsium Nitrat) pada larutan nutrisi A.",
            "Turunkan konsentrasi nutrisi bila PPM > 840 untuk mengurangi stres osmotik.",
            "Tingkatkan sirkulasi udara (kipas) agar transpirasi lancar, terutama malam hari.",
            "Hindari suhu > 26°C dengan paranet/naungan; potong daun yang terdampak parah.",
        ],
    },
    "Leaf Blight": {
        "display": "Leaf Blight (Hawar Daun)",
        "disease_info": (
            "Hawar daun disebabkan jamur atau bakteri (mis. Alternaria, Xanthomonas campestris pv. vitians). "
            "Gejala: bercak cokelat kehitaman berbentuk tidak beraturan di helaian daun yang meluas dan menyatu.",
        ),
        "summary": "Terdapat bercak nekrotik pada helaian daun yang mengindikasikan infeksi hawar.",
        "treatments": [
            "Segera buang dan musnahkan daun/tanaman yang terinfeksi agar tidak menular.",
            "Kurangi kelembapan dan hindari penyiraman dari atas daun; perbaiki jarak tanam.",
            "Aplikasikan bakterisida/fungisida tembaga atau agens hayati sesuai dosis.",
        ],
    },
    "Downy Mildew": {
        "display": "Downy Mildew (Embun Bulu)",
        "disease_info": (
            "Downy mildew disebabkan oomycete Bremia lactucae. Gejala: bercak kuning pucat bersudut "
            "dibatasi tulang daun di permukaan atas, dengan lapisan spora putih keabu-abuan di bawah daun.",
        ),
        "summary": "Terdapat bercak kuning bersudut dan indikasi lapisan keabu-abuan khas embun bulu.",
        "treatments": [
            "Pisahkan tanaman terinfeksi dan buang daun bergejala.",
            "Turunkan kelembapan (ventilasi, kipas) dan hindari daun basah lebih dari 4 jam.",
            "Aplikasikan fungisida sistemik untuk oomycete sesuai petunjuk teknis.",
        ],
    },
}


@dataclass
class DiagnosisResult:
    diagnosis_label: str
    diagnosis_result: str
    confidence: float
    severity: str
    nutrient_condition: str
    disease_info: str
    plant_condition_summary: str
    treatment_recommendations: list[str] = field(default_factory=list)
    top_predictions: list[dict[str, Any]] = field(default_factory=list)
    image_analysis: dict[str, Any] = field(default_factory=dict)
    model_source: str = "FALLBACK_HEURISTIC"
    model_version: str = "hsv-color-heuristic-v1"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x))
    return e / e.sum()


class LettuceDiagnosisDetector:
    """Singleton adapter untuk model diagnosis citra selada berbasis YOLO & CNN."""

    _instance: "LettuceDiagnosisDetector | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "LettuceDiagnosisDetector":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instance = instance
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._model: Any = None
        self._backend: str | None = None  # "yolo" | "torch" | "keras" | "onnx"
        self._temperature: float = 1.0
        self._classes: list[str] = list(CLASS_LABELS)
        self.model_version = "hsv-color-heuristic-v1"
        self.is_loaded = False
        self._initialized = True

    # ------------------------------------------------------------------ load
    def load(self, model_dir: Path | None = None) -> None:
        model_dir = model_dir or settings.ML_MODELS_DIR
        possible_dirs = [
            model_dir,
            BASE_DIR.parent / "model",
            BASE_DIR / "ml_models",
        ]

        # 1. Cari file model
        model_path: Path | None = None
        candidate_names = [
            getattr(settings, "DIAGNOSIS_MODEL_FILE", "best_lettuce_yolo26_v2.pt"),
            "best_lettuce_yolo26_v2.pt",
            "lettuce_diagnosis.pt",
        ]
        for pdir in possible_dirs:
            for name in candidate_names:
                candidate = pdir / name
                if candidate.exists():
                    model_path = candidate
                    break
            if model_path:
                break

        # 2. Cari file temperature scaling
        temp_file = getattr(settings, "DIAGNOSIS_TEMPERATURE_FILE", "temperature.txt")
        for pdir in possible_dirs:
            tcandidate = pdir / temp_file
            if tcandidate.exists():
                try:
                    val = float(tcandidate.read_text(encoding="utf-8").strip())
                    if val > 0:
                        self._temperature = val
                        logger.info("[AI-2] Ditemukan file temperature scaling (%s): T=%.6f", tcandidate, val)
                except Exception as exc:
                    logger.warning("[AI-2] Gagal membaca temperature scaling dari %s: %s", tcandidate, exc)
                break

        if not model_path or not model_path.exists():
            logger.warning("[AI-2] File model diagnosis tidak ditemukan di %s - memakai fallback heuristic.", model_dir)
            self.is_loaded = True
            return

        suffix = model_path.suffix.lower()
        logger.info("[AI-2] Memuat model diagnosis dari %s ...", model_path)

        # 3. Mencoba memuat model menggunakan Ultralytics YOLO
        if suffix in (".pt", ".pth") or "yolo" in model_path.name.lower():
            try:
                from ultralytics import YOLO  # noqa: WPS433

                yolo = YOLO(str(model_path))
                self._model = yolo
                self._backend = "yolo"
                if hasattr(yolo, "names") and isinstance(yolo.names, dict):
                    self._classes = [yolo.names[i] for i in sorted(yolo.names.keys())]
                self.model_version = f"{model_path.name} (YOLO, T={self._temperature:.3f})"
                logger.info(
                    "[AI-2] Model YOLO (%d kelas: %s) berhasil dimuat dari %s dengan T=%.4f",
                    len(self._classes),
                    ", ".join(self._classes),
                    model_path,
                    self._temperature,
                )
                self.is_loaded = True
                return
            except Exception as yolo_err:
                logger.warning("[AI-2] Ultralytics YOLO load gagal: %s. Mencoba PyTorch standard...", yolo_err)

        # 4. Standard PyTorch fallback
        if suffix in (".pt", ".pth"):
            try:
                import torch  # noqa: WPS433

                self._model = torch.load(str(model_path), map_location="cpu", weights_only=False)
                if hasattr(self._model, "eval"):
                    self._model.eval()
                self._backend = "torch"
                self.model_version = model_path.name
                logger.info("[AI-2] Model PyTorch berhasil dimuat dari %s", model_path)
                self.is_loaded = True
                return
            except Exception as torch_err:
                logger.warning("[AI-2] PyTorch standard load gagal: %s", torch_err)

        # 5. Keras / TensorFlow
        if suffix in (".h5", ".keras"):
            try:
                import tensorflow as tf  # noqa: WPS433

                self._model = tf.keras.models.load_model(str(model_path))
                self._backend = "keras"
                self.model_version = model_path.name
                logger.info("[AI-2] Model Keras berhasil dimuat dari %s", model_path)
                self.is_loaded = True
                return
            except Exception as keras_err:
                logger.warning("[AI-2] Keras load gagal: %s", keras_err)

        # 6. ONNX
        if suffix == ".onnx":
            try:
                import onnxruntime as ort  # noqa: WPS433

                self._model = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
                self._backend = "onnx"
                self.model_version = model_path.name
                logger.info("[AI-2] Model ONNX berhasil dimuat dari %s", model_path)
                self.is_loaded = True
                return
            except Exception as onnx_err:
                logger.warning("[AI-2] ONNX load gagal: %s", onnx_err)

        logger.warning("[AI-2] Tidak dapat menginisialisasi model %s. Memakai fallback heuristic.", model_path)
        self._model, self._backend = None, None
        self.is_loaded = True

    @property
    def mode(self) -> str:
        return f"AI_MODEL:{self._backend}" if self._model is not None else "FALLBACK_HEURISTIC"

    # --------------------------------------------------------------- predict
    def predict(self, image_bytes: bytes) -> DiagnosisResult:
        image = Image.open(io.BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image).convert("RGB")
        features = self._extract_color_features(image)

        probs: np.ndarray | None = None
        source, version = "FALLBACK_HEURISTIC", "hsv-color-heuristic-v1"
        classes = self._classes if (self._classes and len(self._classes) > 0) else CLASS_LABELS

        if self._model is not None:
            try:
                if self._backend == "yolo":
                    probs = self._predict_with_yolo(image)
                    source = "AI_MODEL:yolo"
                    version = self.model_version
                    classes = self._classes
                else:
                    probs = self._predict_with_cnn(image)
                    source = f"AI_MODEL:{self._backend}"
                    version = self.model_version
            except Exception:
                logger.exception("[AI-2] Inference model gagal - memakai fallback heuristic")
                probs = None

        if probs is None:
            probs = self._heuristic_probabilities(features)
            source, version = "FALLBACK_HEURISTIC", "hsv-color-heuristic-v1"
            classes = FALLBACK_CLASSES

        return self._build_result(probs, features, source, version, classes=classes)

    # ------------------------------------------------------- YOLO inference
    def _predict_with_yolo(self, image: Image.Image) -> np.ndarray:
        results = self._model.predict(image, verbose=False)
        r = results[0]
        if hasattr(r, "probs") and r.probs is not None:
            raw_probs = r.probs.data.cpu().numpy().astype(np.float64)
        else:
            raise RuntimeError("Hasil prediksi YOLO tidak memiliki atribut `probs` (bukan model klasifikasi).")

        # Terapkan Temperature Scaling jika parameter T dikonfigurasi
        if self._temperature > 0 and abs(self._temperature - 1.0) > 1e-4:
            logits = np.log(np.clip(raw_probs, 1e-9, 1.0))
            return _softmax(logits / self._temperature)

        return raw_probs

    # ---------------------------------------------------- CNN model inference
    def _predict_with_cnn(self, image: Image.Image) -> np.ndarray:
        arr = np.asarray(image.resize((IMG_SIZE, IMG_SIZE)), dtype=np.float32) / 255.0
        arr = (arr - IMAGENET_MEAN) / IMAGENET_STD

        if self._backend == "torch":
            import torch  # noqa: WPS433

            tensor = torch.from_numpy(arr.transpose(2, 0, 1)).unsqueeze(0)
            with torch.no_grad():
                output = self._model(tensor)
            logits = output.detach().cpu().numpy()[0]
        elif self._backend == "keras":
            logits = np.asarray(self._model.predict(arr[np.newaxis, ...], verbose=0))[0]
        elif self._backend == "onnx":
            input_name = self._model.get_inputs()[0].name
            logits = self._model.run(None, {input_name: arr.transpose(2, 0, 1)[np.newaxis].astype(np.float32)})[0][0]
        else:
            raise RuntimeError("Backend model tidak dikenal")

        logits = np.asarray(logits, dtype=np.float64).ravel()
        already_prob = np.all(logits >= 0) and abs(float(logits.sum()) - 1.0) < 1e-3
        return logits if already_prob else _softmax(logits)

    # ------------------------------------------------ fallback: color features
    @staticmethod
    def _extract_color_features(image: Image.Image) -> dict[str, float]:
        img = image.copy()
        img.thumbnail((256, 256))
        hsv = np.asarray(img.convert("HSV"), dtype=np.float32)
        h = hsv[..., 0] * (360.0 / 255.0)
        s = hsv[..., 1] / 255.0
        v = hsv[..., 2] / 255.0

        green = (h >= 65) & (h <= 170) & (s >= 0.20) & (v >= 0.15)
        yellow = (h >= 40) & (h < 65) & (s >= 0.30) & (v >= 0.35)
        brown = (h >= 5) & (h < 40) & (s >= 0.25) & (v >= 0.10) & (v < 0.75)
        dark = v < 0.15
        gray_white = (s < 0.12) & (v >= 0.55)
        plant = green | yellow | brown

        rows, cols = plant.shape
        margin = max(1, int(0.2 * min(rows, cols)))
        border = np.ones_like(plant, dtype=bool)
        border[margin:-margin, margin:-margin] = False

        total = float(plant.size)
        plant_n = max(float(plant.sum()), 1.0)
        plant_border = max(float((plant & border).sum()), 1.0)
        plant_center = max(float((plant & ~border).sum()), 1.0)

        return {
            "plant_coverage": float(plant.sum()) / total,
            "green_ratio": float(green.sum()) / plant_n,
            "yellow_ratio": float(yellow.sum()) / plant_n,
            "brown_ratio": float(brown.sum()) / plant_n,
            "brown_edge_ratio": float((brown & border).sum()) / plant_border,
            "brown_center_ratio": float((brown & ~border).sum()) / plant_center,
            "dark_ratio": float(dark.sum()) / total,
            "gray_white_ratio": float(gray_white.sum()) / total,
            "mean_plant_saturation": float(s[plant].mean()) if plant.any() else 0.0,
            "mean_plant_brightness": float(v[plant].mean()) if plant.any() else 0.0,
        }

    @staticmethod
    def _heuristic_probabilities(f: dict[str, float]) -> np.ndarray:
        g, y, b = f["green_ratio"], f["yellow_ratio"], f["brown_ratio"]
        logits = np.array([
            0.8 + 4.0 * g - 5.0 * y - 7.0 * b,                                       # Healthy
            -1.0 + 9.0 * f["brown_edge_ratio"] + 2.0 * b,                            # Tip Burn
            -1.0 + 8.0 * f["brown_center_ratio"] + 3.0 * min(f["dark_ratio"], 0.3),  # Leaf Blight
            -1.2 + 6.0 * y + 4.0 * min(f["gray_white_ratio"], 0.5),                  # Downy Mildew
        ], dtype=np.float64)
        probs = _softmax(logits * 1.5)
        if f["plant_coverage"] < 0.08:
            probs = 0.5 * probs + 0.5 * np.full_like(probs, 1.0 / len(probs))
        return probs

    # ----------------------------------------------------------- result builder
    @staticmethod
    def _analyze_nutrients(label: str, f: dict[str, float]) -> str:
        notes: list[str] = []
        if label == "Tip Burn":
            notes.append("Indikasi kekurangan Kalsium (Ca) pada jaringan daun muda; "
                         "dapat diperparah PPM/EC terlalu tinggi atau transpirasi rendah.")
        elif label == "Bacterial":
            notes.append("Gejala hawar/busuk bakteri diperparah daun terlalu sukulen akibat kelebihan Nitrogen (N). "
                         "Kurangi suplai N dan pastikan sirkulasi udara baik.")
        elif label in ("Downy_mildew", "Downy Mildew"):
            notes.append("Infeksi jamur embun bulu (Bremia lactucae). Jaga keseimbangan hara AB Mix dan kurangi kelembapan kanopi.")
        elif label == "Lettuce Mosaic Virus":
            notes.append("Gejala malformasi akibat infeksi sistemik virus mosaik (LMV); bukan defisiensi hara langsung, "
                         "namun nutrisi optimal menjaga daya tahan tanaman lain di sekitarnya.")
        elif label == "Powdery_mildew":
            notes.append("Infeksi embun tepung. Hindari kelebihan Nitrogen yang menyebabkan daun terlalu lunak dan mudah ditembus spora.")
        elif label == "Septoria_Blight":
            notes.append("Hawar daun Septoria. Pastikan kecukupan Kalium (K) untuk memperkuat ketahanan dinding sel daun terhadap penetrasi jamur.")

        if f["yellow_ratio"] >= 0.20 and label not in ("Downy_mildew", "Downy Mildew", "Lettuce Mosaic Virus"):
            notes.append("Terdeteksi klorosis/menguning merata: kemungkinan kekurangan Nitrogen (N).")
        if (label == "Healthy" and f["green_ratio"] >= 0.9
                and f["mean_plant_brightness"] < 0.35 and f["mean_plant_saturation"] > 0.55):
            notes.append("Daun hijau sangat gelap: kemungkinan kelebihan Nitrogen.")
        if not notes:
            notes.append("Normal - ketersediaan hara dalam rentang stabil.")
        return " ".join(notes)

    @staticmethod
    def _severity(label: str, f: dict[str, float], confidence: float) -> str:
        if label == "Healthy":
            return "NONE"
        affected = f["yellow_ratio"] + f["brown_ratio"]
        if confidence >= 0.85 or affected >= 0.25:
            return "BERAT"
        if confidence >= 0.55 or affected >= 0.10:
            return "SEDANG"
        return "RINGAN"

    def _build_result(
        self,
        probs: np.ndarray,
        f: dict[str, float],
        source: str,
        version: str,
        classes: list[str] | None = None,
    ) -> DiagnosisResult:
        classes = classes or self._classes or CLASS_LABELS
        idx = int(np.argmax(probs))
        label = classes[idx] if idx < len(classes) else "Unknown"
        confidence = float(round(float(probs[idx]), 4))

        kb = DISEASE_KB.get(label)
        if not kb:
            # Fallback untuk label lain yang belum terdaftar di DISEASE_KB
            clean_display = label.replace("_", " ").title()
            kb = {
                "display": f"{clean_display} (Terdeteksi)",
                "disease_info": f"Terdeteksi indikasi penyakit selada kelas {clean_display}.",
                "summary": f"Tanaman terindikasi mengalami gejala {clean_display}.",
                "treatments": [
                    "Lakukan observasi visual menyeluruh pada permukaan daun.",
                    "Periksa stabilitas parameter larutan hidroponik (pH 5.5 - 6.5, EC 0.8 - 1.2 mS/cm).",
                    "Pisahkan tanaman terinfeksi dari talang utama untuk mencegah penularan.",
                ],
            }

        severity = self._severity(label, f, confidence)
        nutrient = self._analyze_nutrients(label, f)

        ranking: list[dict[str, Any]] = []
        for i, p in enumerate(probs):
            c_label = classes[i] if i < len(classes) else f"Class_{i}"
            c_kb = DISEASE_KB.get(c_label, {})
            c_display = c_kb.get("display", c_label.replace("_", " ").title())
            ranking.append({
                "label": c_label,
                "display": c_display,
                "confidence": round(float(p), 4),
            })
        ranking.sort(key=lambda item: item["confidence"], reverse=True)

        treatments = list(kb.get("treatments", []))
        summary_parts = [
            f"Hasil analisis AI: tanaman terdeteksi {kb['display']} dengan keyakinan {confidence:.1%}"
            + (f" (tingkat keparahan: {severity})." if severity != "NONE" else "."),
            kb["summary"],
            f"Komposisi warna daun: hijau sehat ±{f['green_ratio']:.0%}, menguning ±{f['yellow_ratio']:.0%}, "
            f"kecokelatan/nekrosis ±{f['brown_ratio']:.0%}.",
            f"Kondisi nutrisi: {nutrient}",
            "Rekomendasi penanganan: " + " ".join(f"{i}) {t}" for i, t in enumerate(treatments, 1)),
        ]
        if f["plant_coverage"] < 0.08:
            summary_parts.insert(1, "Catatan: objek tanaman pada gambar kurang terlihat jelas; "
                                    "ambil ulang foto daun dari jarak dekat dengan pencahayaan cukup.")
        if confidence < 0.45 and label != "Healthy":
            summary_parts.append("Keyakinan model relatif rendah - disarankan verifikasi visual langsung oleh staf kebun.")

        return DiagnosisResult(
            diagnosis_label=label,
            diagnosis_result=kb["display"],
            confidence=confidence,
            severity=severity,
            nutrient_condition=nutrient,
            disease_info=kb["disease_info"],
            plant_condition_summary=" ".join(summary_parts),
            treatment_recommendations=treatments,
            top_predictions=ranking,
            image_analysis={k: round(v, 4) for k, v in f.items()},
            model_source=source,
            model_version=version,
        )


lettuce_detector = LettuceDiagnosisDetector()

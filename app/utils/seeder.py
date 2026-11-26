"""Auto-seed sesuai ERD `hidroponik_selada`:
- `users`: 1 `owner` & 1 `karyawan`
- `disease_infos` & `nutrition_conditions`: basis pengetahuan penyakit & nutrisi selada
- `inventory_items` & `stock_movements`: contoh stok bibit & nutrisi
- `plants` & `growth_records`: contoh batch tanaman & riwayat pertumbuhan untuk demo grafik
"""
import logging
import shutil
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from PIL import Image, ImageDraw
from sqlalchemy import func, select

from app.common.enums import InventoryType, PlantPart, PlantStatus, StockMovementType, UserRole
from app.common.time import utcnow
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.diagnosis.cv_detector import lettuce_detector
from app.modules.diagnosis.models import DiagnosisRecord
from app.modules.employees.models import User
from app.modules.knowledge_base.models import DiseaseInfo, NutritionCondition
from app.modules.plants.models import GrowthRecord, Plant
from app.modules.plants.service import reference_height, reference_leaves, reference_weight
from app.modules.stocks.models import InventoryItem, StockMovement

logger = logging.getLogger(__name__)


def _get_or_create_user(db, *, nama: str, username: str, password: str, role: UserRole) -> tuple[User, bool]:
    uname = username.strip().lower()
    user = db.scalar(select(User).where(func.lower(User.username) == uname))
    if user:
        return user, False
    user = User(nama=nama, username=uname, password=hash_password(password), role=role)
    db.add(user)
    db.flush()
    return user, True


def _seed_knowledge_base(db) -> None:
    if not db.scalar(select(func.count(DiseaseInfo.id))):
        db.add_all([
            DiseaseInfo(
                nama_penyakit="Healthy (Sehat)",
                deskripsi="Tanaman selada dalam kondisi sehat, tidak terdeteksi gejala penyakit maupun gangguan fisiologis.",
                gejala="Daun hijau segar merata, turgor baik, tanpa bercak, klorosis, ataupun nekrosis di tepi daun.",
                penanganan_awal="Pertahankan pH 5.5 - 6.5, EC 0.8 - 1.2 mS/cm, sirkulasi udara baik, dan monitoring rutin.",
            ),
            DiseaseInfo(
                nama_penyakit="Tip Burn (Ujung Daun Terbakar)",
                deskripsi="Gangguan fisiologis akibat defisiensi kalsium lokal pada jaringan daun muda yang tumbuh cepat.",
                gejala="Ujung dan tepi daun muda mengering, berwarna cokelat hingga hitam, daun tampak mengeriting.",
                penanganan_awal="Tambahkan Kalsium Nitrat, turunkan EC bila terlalu pekat, tingkatkan sirkulasi udara (kipas), dan jaga suhu < 26°C.",
            ),
            DiseaseInfo(
                nama_penyakit="Leaf Blight (Hawar Daun)",
                deskripsi="Infeksi jamur/bakteri (mis. Alternaria atau Xanthomonas) yang menyebabkan nekrosis pada helaian daun.",
                gejala="Bercak cokelat kehitaman tidak beraturan pada helaian daun yang meluas dan menyatu, kadang dikelilingi halo kuning.",
                penanganan_awal="Buang daun/tanaman terinfeksi, kurangi kelembapan, hindari cipratan air ke daun, aplikasikan bakterisida/fungisida tembaga atau agen hayati.",
            ),
            DiseaseInfo(
                nama_penyakit="Downy Mildew (Embun Bulu)",
                deskripsi="Penyakit akibat oomycete Bremia lactucae yang berkembang cepat pada kondisi lembap dan sejuk.",
                gejala="Bercak kuning pucat bersudut dibatasi tulang daun di permukaan atas dan lapisan spora putih keabu-abuan di bawah daun.",
                penanganan_awal="Isolasi tanaman sakit, tingkatkan ventilasi untuk menurunkan kelembapan (< 85%), dan gunakan fungisida spesifik oomycete.",
            ),
            DiseaseInfo(
                nama_penyakit="Bacterial (Hawar Bakteri / Busuk Bakteri)",
                deskripsi="Penyakit hawar dan busuk bakteri (Xanthomonas campestris pv. vitians atau Pseudomonas cichorii) pada selada.",
                gejala="Bercak basah kecil bersudut yang kemudian berubah cokelat hingga hitam, seringkali dikelilingi halo kuning dan membusuk basah.",
                penanganan_awal="Segera buang tanaman terinfeksi, kurangi kelembapan, hindari cipratan air ke daun, dan semprotkan bakterisida tembaga atau Bacillus subtilis.",
            ),
            DiseaseInfo(
                nama_penyakit="Lettuce Mosaic Virus (Virus Mosaik Selada)",
                deskripsi="Penyakit sistemik akibat Lettuce Mosaic Virus (LMV / Potyvirus) yang ditularkan melalui benih dan vektor kutu daun (aphids).",
                gejala="Pola mosaik belang hijau tua dan hijau muda pada daun, daun berkerut atau melepuh, tepi daun bergelombang, serta pertumbuhan kerdil.",
                penanganan_awal="Cabut dan musnahkan tanaman yang terinfeksi segera, kendalikan vektor kutu daun dengan perangkap kuning atau insektisida nabati, dan gunakan benih bebas virus.",
            ),
            DiseaseInfo(
                nama_penyakit="Powdery Mildew (Embun Tepung)",
                deskripsi="Infeksi jamur Erysiphe cichoracearum (Golovinomyces cichoracearum) yang membentuk lapisan tepung putih pada permukaan daun.",
                gejala="Muncul bercak atau lapisan putih seperti bedak/tepung di permukaan helai daun; daun terserang parah akan menguning dan mengering.",
                penanganan_awal="Buang daun terdampak, semprotkan kalium bikarbonat (3 g/L) atau neem oil, perbaiki ventilasi greenhouse, dan hindari kelebihan pupuk Nitrogen.",
            ),
            DiseaseInfo(
                nama_penyakit="Septoria Blight (Hawar Daun Septoria)",
                deskripsi="Penyakit bercak dan hawar daun akibat jamur Septoria lactucae yang menyerang helaian daun selada.",
                gejala="Bercak nekrotik tidak beraturan berwarna cokelat zaitun hingga cokelat tua dengan bintik-bintik hitam kecil (piknidia) di tengah bercak.",
                penanganan_awal="Petik dan musnahkan daun tua bergejala, hindari penyiraman overhead, aplikasikan fungisida tembaga/kontak, dan bersihkan sisa daun mati.",
            ),
        ])

    if not db.scalar(select(func.count(NutritionCondition.id))):
        db.add_all([
            NutritionCondition(
                nama_kondisi="Normal (Nutrisi Seimbang)",
                unsur_nutrisi="Lengkap (AB Mix)",
                deskripsi="Ketersediaan dan penyerapan unsur hara makro & mikro berada pada rentang optimal.",
                gejala="Warna daun hijau cerah merata dan pertumbuhan sesuai umur.",
                penanganan_awal="Pertahankan EC 0.8 - 1.2 mS/cm (560 - 840 ppm) dan pH 5.5 - 6.5.",
            ),
            NutritionCondition(
                nama_kondisi="Kekurangan Kalsium (Ca)",
                unsur_nutrisi="Kalsium (Ca)",
                deskripsi="Transport kalsium ke jaringan daun muda terhambat (sering memicu Tip Burn).",
                gejala="Tepi daun muda mengering/cokelat (tip burn), pertumbuhan titik tumbuh terhambat.",
                penanganan_awal="Pastikan stok A (Kalsium Nitrat) cukup, jaga EC tidak terlalu tinggi, dan pasang kipas untuk membantu transpirasi.",
            ),
            NutritionCondition(
                nama_kondisi="Kekurangan Nitrogen (N)",
                unsur_nutrisi="Nitrogen (N)",
                deskripsi="Konsentrasi nutrisi terlalu rendah sehingga sintesis klorofil menurun.",
                gejala="Klorosis (menguning merata) dimulai dari daun tua bagian bawah, pertumbuhan kerdil/lambat.",
                penanganan_awal="Naikkan konsentrasi larutan AB Mix hingga EC 1.0 - 1.4 mS/cm dan periksa pH larutan.",
            ),
            NutritionCondition(
                nama_kondisi="Kekurangan Kalium (K)",
                unsur_nutrisi="Kalium (K)",
                deskripsi="Defisiensi kalium menurunkan ketahanan jaringan daun terhadap penyakit.",
                gejala="Klorosis di tepi daun tua diikuti bercak nekrotik kecokelatan.",
                penanganan_awal="Gunakan nutrisi AB Mix sayuran daun yang seimbang dan ganti larutan tandon secara berkala.",
            ),
            NutritionCondition(
                nama_kondisi="Kelebihan Nitrogen (N)",
                unsur_nutrisi="Nitrogen (N)",
                deskripsi="Konsentrasi nitrogen berlebih membuat jaringan daun terlalu sukulen dan rentan penyakit.",
                gejala="Daun hijau sangat gelap, rapuh, dan berisiko akumulasi nitrat tinggi.",
                penanganan_awal="Turunkan EC larutan dengan menambah air baku; bilas air biasa 1 - 2 hari sebelum panen.",
            ),
        ])
    db.flush()


def _seed_sample_data(db, owner: User, karyawan: User) -> bool:
    if db.scalar(select(func.count(InventoryItem.id))) or db.scalar(select(func.count(Plant.id))):
        return False

    now = utcnow()
    today = date.today()
    items = [
        InventoryItem(
            nama_barang="Bibit Selada Grand Rapids", jenis=InventoryType.bibit, satuan="biji",
            jumlah_stok=Decimal("1000.00"), stok_minimum=Decimal("200.00"),
            keterangan="Benih selada keriting hijau", created_by=owner.id,
        ),
        InventoryItem(
            nama_barang="Bibit Selada Romaine", jenis=InventoryType.bibit, satuan="biji",
            jumlah_stok=Decimal("150.00"), stok_minimum=Decimal("200.00"),
            keterangan="Stok di bawah minimum (contoh peringatan)", created_by=owner.id,
        ),
        InventoryItem(
            nama_barang="Nutrisi AB Mix Sayuran Daun", jenis=InventoryType.nutrisi, satuan="pack",
            jumlah_stok=Decimal("12.00"), stok_minimum=Decimal("3.00"),
            keterangan="AB Mix 5 liter pekatan", created_by=owner.id,
        ),
        InventoryItem(
            nama_barang="Kalsium Nitrat (Calcinit)", jenis=InventoryType.nutrisi, satuan="kg",
            jumlah_stok=Decimal("5.00"), stok_minimum=Decimal("2.00"),
            keterangan="Tambahan pencegah tip burn", created_by=owner.id,
        ),
        InventoryItem(
            nama_barang="Rockwool Cultilene", jenis=InventoryType.lainnya, satuan="slab",
            jumlah_stok=Decimal("20.00"), stok_minimum=Decimal("5.00"),
            keterangan="Media tanam semai", created_by=owner.id,
        ),
    ]
    db.add_all(items)
    db.flush()
    for it in items:
        db.add(StockMovement(
            inventory_item_id=it.id, recorded_by=owner.id, jenis_pergerakan=StockMovementType.masuk,
            jumlah=it.jumlah_stok, tanggal=now - timedelta(days=30), keterangan="Stok awal (seeder)",
        ))

    batches = [
        ("SLD-DEMO-001", "Selada Keriting", "Grand Rapids", 28, PlantStatus.pertumbuhan,
         "Greenhouse A - Rak 1 (120 lubang NFT)", 1.0),
        ("SLD-DEMO-002", "Selada Cos", "Romaine", 14, PlantStatus.pertumbuhan,
         "Greenhouse A - Rak 2 (80 lubang NFT)", 0.85),
    ]
    for kode, nama, varietas, age, st, ket, vigor in batches:
        tanam = today - timedelta(days=age)
        plant = Plant(
            created_by=karyawan.id, kode_tanaman=kode, nama=nama, varietas=varietas,
            tanggal_tanam=tanam, tanggal_panen=tanam + timedelta(days=40), status=st, keterangan=ket,
        )
        db.add(plant)
        db.flush()
        for day in range(3, age + 1, 4):
            obs_dt = datetime.combine(tanam + timedelta(days=day), datetime.min.time()).replace(hour=8)
            ec_val = round(0.9 + day * 0.015, 3)
            db.add(GrowthRecord(
                plant_id=plant.id,
                recorded_by=karyawan.id,
                tanggal_pengamatan=obs_dt,
                umur_tanaman=day,
                tinggi_cm=Decimal(str(round(reference_height(day) * vigor, 2))),
                jumlah_daun=max(2, round(reference_leaves(day) * vigor)),
                berat_gram=Decimal(str(round(reference_weight(day) * vigor, 2))),
                ph_air=Decimal(str(round(5.8 + (day % 5) * 0.1, 2))),
                suhu_air=Decimal("22.00"),
                ec=Decimal(str(ec_val)),
                suhu_c=Decimal("25.50"),
                kelembapan_persen=Decimal("70.00"),
                intensitas_cahaya=Decimal("14500.00"),
                sumber_data="internal",
                catatan=f"Pengamatan rutin HST {day}",
            ))
    return True


def _ensure_seed_diagnosis_image(filename: str, source_name: str, rgb_color: tuple[int, int, int]) -> str:
    rel_path = f"diagnosis/{filename}"
    dest = settings.UPLOAD_DIR / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        fe_sample = Path(__file__).resolve().parents[3] / "PPL-AGRO-KEL-5" / "public" / "images" / "beds" / source_name
        if fe_sample.is_file():
            shutil.copyfile(fe_sample, dest)
        else:
            img = Image.new("RGB", (640, 480), rgb_color)
            draw = ImageDraw.Draw(img)
            draw.ellipse((140, 80, 500, 400), fill=(52, 168, 83))
            img.save(dest, format="JPEG", quality=85)
    return rel_path


def _seed_diagnoses(db, karyawan: User) -> bool:
    changed = False
    plants = db.scalars(select(Plant).order_by(Plant.id)).all()
    if not plants:
        return False

    if not db.scalar(select(func.count(DiagnosisRecord.id))):
        now = utcnow()
        healthy_di = db.scalar(select(DiseaseInfo).where(DiseaseInfo.nama_penyakit.ilike("%Healthy%")))
        tipburn_di = db.scalar(select(DiseaseInfo).where(DiseaseInfo.nama_penyakit.ilike("%Tip Burn%")))
        normal_nc = db.scalar(select(NutritionCondition).where(NutritionCondition.nama_kondisi.ilike("%Normal%")))
        ca_nc = db.scalar(select(NutritionCondition).where(NutritionCondition.nama_kondisi.ilike("%Kalsium%")))

        img1 = _ensure_seed_diagnosis_image("seed_sld_demo_001.jpg", "bed_a01.jpg", (42, 128, 72))
        img2 = _ensure_seed_diagnosis_image("seed_sld_demo_002.jpg", "bed_a02.jpg", (54, 145, 78))

        p1 = plants[0]
        p2 = plants[1] if len(plants) > 1 else plants[0]

        db.add_all([
            DiagnosisRecord(
                plant_id=p1.id,
                diagnosed_by=karyawan.id,
                tanggal_diagnosis=now - timedelta(hours=4),
                image_path=img1,
                plant_part=PlantPart.daun,
                kelas_diagnosis="Healthy",
                confidence=Decimal("0.98400"),
                disease_info_id=healthy_di.id if healthy_di else None,
                nutrition_condition_id=normal_nc.id if normal_nc else None,
                model="SVM",
                versi_model=lettuce_detector.model_version[:50],
                sumber_data="seeder",
                keterangan="Tanaman dalam kondisi sehat, daun hijau segar merata tanpa bercak maupun nekrosis.",
                rekomendasi="1) Pertahankan pH larutan 5.5 - 6.5 dan nutrisi 560 - 840 ppm. 2) Lanjutkan monitoring rutin.",
            ),
            DiagnosisRecord(
                plant_id=p2.id,
                diagnosed_by=karyawan.id,
                tanggal_diagnosis=now - timedelta(days=1),
                image_path=img2,
                plant_part=PlantPart.daun,
                kelas_diagnosis="Tip Burn",
                confidence=Decimal("0.91200"),
                disease_info_id=tipburn_di.id if tipburn_di else None,
                nutrition_condition_id=ca_nc.id if ca_nc else None,
                model="SVM",
                versi_model=lettuce_detector.model_version[:50],
                sumber_data="seeder",
                keterangan="Terdeteksi gejala ringan ujung daun mengering akibat distribusi Kalsium (Ca) belum merata.",
                rekomendasi="1) Tambahkan Kalsium Nitrat pada larutan nutrisi A. 2) Tingkatkan sirkulasi udara (kipas) pada kanopi.",
            ),
        ])
        changed = True

    return changed


def run_seeder() -> None:
    db = SessionLocal()
    try:
        owner, owner_new = _get_or_create_user(
            db, nama=settings.SEED_OWNER_NAMA, username=settings.SEED_OWNER_USERNAME,
            password=settings.SEED_OWNER_PASSWORD, role=UserRole.owner,
        )
        karyawan, karyawan_new = _get_or_create_user(
            db, nama=settings.SEED_KARYAWAN_NAMA, username=settings.SEED_KARYAWAN_USERNAME,
            password=settings.SEED_KARYAWAN_PASSWORD, role=UserRole.karyawan,
        )
        _seed_knowledge_base(db)
        sample = _seed_sample_data(db, owner, karyawan) if settings.SEED_SAMPLE_DATA else False
        ai_sample = _seed_diagnoses(db, karyawan) if settings.SEED_SAMPLE_DATA else False
        sample = sample or ai_sample
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Seeder gagal")
        raise
    finally:
        db.close()

    line = "=" * 64
    print(f"\n{line}")
    print("  HIDROPONIK SELADA API - DEFAULT CREDENTIALS (tabel `users`)")
    print(line)
    print(f"  owner    -> username: {settings.SEED_OWNER_USERNAME:<12} | password: {settings.SEED_OWNER_PASSWORD}"
          f"   {'(baru dibuat)' if owner_new else '(sudah ada)'}")
    print(f"  karyawan -> username: {settings.SEED_KARYAWAN_USERNAME:<12} | password: {settings.SEED_KARYAWAN_PASSWORD}"
          f"   {'(baru dibuat)' if karyawan_new else '(sudah ada)'}")
    if sample:
        print("  Basis pengetahuan + contoh inventaris & tanaman telah di-seed.")
    print(f"  Swagger UI : {settings.PUBLIC_BASE_URL}/docs")
    print(f"  ReDoc      : {settings.PUBLIC_BASE_URL}/redoc")
    print(f"{line}\n", flush=True)


if __name__ == "__main__":  # python -m app.utils.seeder
    from app.core.database import init_db

    init_db()
    run_seeder()

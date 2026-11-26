# 🥬 Hidroponik Selada API (FastAPI)

Backend REST API **Sistem Diagnosis Kesehatan Selada Hidroponik** untuk proyek PPL.
Struktur tabel & relasi **100% mengikuti ERD `hidroponik_selada`** (`konteks_erd.md`).

## 🗄️ Pemetaan Tabel ERD → Modul

| Tabel ERD | Enum terkait | Modul |
|---|---|---|
| `users` | `user_role` (`owner`, `karyawan`) | `app/modules/employees/models.py` |
| `plants` | `plant_status` (`pembibitan`, `pertumbuhan`, `siap_panen`, `dipanen`, `mati`) | `app/modules/plants/models.py` |
| `growth_records` | — | `app/modules/plants/models.py` |
| `diagnosis_records` | `plant_part` (`daun`, `akar`, `seluruh_tanaman`), `model` | `app/modules/diagnosis/models.py` |
| `disease_infos` | — | `app/modules/knowledge_base/models.py` |
| `nutrition_conditions` | — | `app/modules/knowledge_base/models.py` |
| `inventory_items` | `inventory_type` (`bibit`, `nutrisi`, `lainnya`) | `app/modules/stocks/models.py` |
| `stock_movements` | `stock_movement_type` (`masuk`, `keluar`) | `app/modules/stocks/models.py` |

## 🚀 Menjalankan

```powershell
cd lettuce-backend-api
venv\Scripts\activate
uvicorn app.main:app --reload
```

Buka **http://localhost:8000/docs** → klik **Authorize** → login:

| Role (`user_role`) | Username | Password |
|---|---|---|
| `owner` | `owner` | `owner123` |
| `karyawan` | `karyawan` | `karyawan123` |

Untuk MySQL sesuai `konteks_erd.md`, aktifkan `PyMySQL` di `requirements.txt` dan set di `.env`:
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/hidroponik_selada
```

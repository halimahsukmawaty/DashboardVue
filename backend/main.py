import json
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Path as FastApiPath, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Setup path ke file seed data JSON
SEED_FILE_PATH = Path(__file__).parent / "books.json"


def muat_data_seed() -> list[dict]:
    """Memuat data awal (seed) dari file books.json."""
    if SEED_FILE_PATH.exists():
        try:
            with open(SEED_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Peringatan: Gagal membaca file seed ({e}), menggunakan data fallback.")
    return [
        {
            "id": 1,
            "judul": "Clean Code",
            "penulis": "Robert C. Martin",
            "kategori": "Teknologi",
            "stok": 10,
        }
    ]


# Database in-memory yang di-seed dari file JSON saat startup
books_db: list[dict] = muat_data_seed()

# Inisialisasi aplikasi FastAPI dengan dokumentasi OpenAPI yang terstruktur
app = FastAPI(
    title="Library Management API — UTS Dashboard Perpustakaan",
    description=(
        "REST API backend untuk pengelolaan data buku perpustakaan.\n\n"
        "Fitur Utama:\n"
        "- **GET /books**: Mengambil daftar seluruh buku dengan opsi pencarian.\n"
        "- **GET /books/{id}**: Mengambil detail satu buku berdasarkan ID.\n"
        "- **POST /books**: Menambahkan buku baru dengan validasi Pydantic.\n"
        "- **PUT /books/{id}**: Memperbarui informasi buku (Fitur Bonus).\n"
        "- **DELETE /books/{id}**: Menghapus buku dari perpustakaan.\n"
        "- **POST /books/reset**: Mengembalikan data awal dari file seed JSON.\n\n"
        "Dibuat untuk evaluasi Ujian Tengah Semester (UTS) mata kuliah Pengembangan Aplikasi Web."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Konfigurasi CORS agar frontend Vue 3 (Vite) dapat mengakses API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# SKEMA PYDANTIC
# ==========================================
class BookBase(BaseModel):
    judul: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Judul buku perpustakaan",
        examples=["Clean Code: A Handbook of Agile Software Craftsmanship"],
    )
    penulis: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Nama penulis atau pengarang buku",
        examples=["Robert C. Martin"],
    )
    kategori: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Kategori atau genre buku",
        examples=["Teknologi"],
    )
    stok: int = Field(
        ...,
        ge=0,
        description="Jumlah fisik eksemplar buku (harus angka positif / >= 0)",
        examples=[12],
    )


class BookCreate(BookBase):
    """Skema untuk request pembuatan buku baru."""
    pass


class BookUpdate(BaseModel):
    """Skema untuk request pembaruan data buku (Fitur Bonus)."""
    judul: Optional[str] = Field(None, min_length=1, max_length=200)
    penulis: Optional[str] = Field(None, min_length=1, max_length=150)
    kategori: Optional[str] = Field(None, min_length=1, max_length=100)
    stok: Optional[int] = Field(None, ge=0)


class BookOut(BookBase):
    """Skema response data buku lengkap beserta ID unik."""
    id: int = Field(..., description="ID unik buku", examples=[1])


# ==========================================
# ENDPOINTS REST API
# ==========================================
@app.get(
    "/",
    tags=["Root"],
    summary="Health check root endpoint",
    description="Memastikan backend FastAPI berjalan dengan baik.",
)
def baca_root():
    return {
        "status": "online",
        "pesan": "Backend FastAPI Perpustakaan berjalan dengan baik",
        "total_buku": len(books_db),
        "dokumentasi": "/docs",
    }


@app.get(
    "/books",
    tags=["Books"],
    response_model=list[BookOut],
    summary="Ambil seluruh daftar buku",
    description=(
        "Mengembalikan seluruh data buku dari in-memory storage. "
        "Dapat disaring opsional dengan query parameter `q` (berdasarkan judul atau penulis)."
    ),
)
def ambil_semua_buku(
    q: Optional[str] = Query(
        default=None,
        description="Kata kunci pencarian judul atau penulis buku",
    ),
    kategori: Optional[str] = Query(
        default=None,
        description="Filter berdasarkan kategori buku",
    ),
):
    hasil = books_db

    if kategori and isinstance(kategori, str):
        kat_clean = kategori.strip().lower()
        hasil = [b for b in hasil if b["kategori"].lower() == kat_clean]

    if q and isinstance(q, str):
        kata_kunci = q.strip().lower()
        hasil = [
            b
            for b in hasil
            if kata_kunci in b["judul"].lower()
            or kata_kunci in b["penulis"].lower()
        ]

    return hasil



@app.get(
    "/books/{book_id}",
    tags=["Books"],
    response_model=BookOut,
    summary="Ambil detail satu buku berdasarkan ID",
    description="Mengembalikan informasi lengkap satu buku sesuai ID yang diminta.",
)
def ambil_satu_buku(
    book_id: int = FastApiPath(..., ge=1, description="ID unik buku yang dicari"),
):
    for buku in books_db:
        if buku["id"] == book_id:
            return buku
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Buku dengan ID {book_id} tidak ditemukan",
    )


@app.post(
    "/books",
    status_code=status.HTTP_201_CREATED,
    tags=["Books"],
    response_model=BookOut,
    summary="Tambah buku baru",
    description=(
        "Menambahkan buku baru ke dalam daftar perpustakaan. "
        "ID akan di-generate otomatis secara increment. Input divalidasi oleh Pydantic."
    ),
)
def tambah_buku(buku: BookCreate):
    # Validasi string tidak hanya spasi kosong
    if not buku.judul.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Judul buku tidak boleh hanya berisi spasi kosong.",
        )
    if not buku.penulis.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nama penulis tidak boleh hanya berisi spasi kosong.",
        )
    if not buku.kategori.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Kategori tidak boleh hanya berisi spasi kosong.",
        )

    id_baru = max((b["id"] for b in books_db), default=0) + 1
    data_buku_baru = {
        "id": id_baru,
        "judul": buku.judul.strip(),
        "penulis": buku.penulis.strip(),
        "kategori": buku.kategori.strip(),
        "stok": buku.stok,
    }
    books_db.append(data_buku_baru)
    return data_buku_baru


@app.put(
    "/books/{book_id}",
    tags=["Books"],
    response_model=BookOut,
    summary="Perbarui data buku (Fitur Bonus)",
    description="Memperbarui data atribut judul, penulis, kategori, atau stok buku yang sudah ada.",
)
def perbarui_buku(
    buku_update: BookUpdate,
    book_id: int = FastApiPath(..., ge=1, description="ID buku yang ingin diperbarui"),
):
    for buku in books_db:
        if buku["id"] == book_id:
            if buku_update.judul is not None:
                if not buku_update.judul.strip():
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Judul tidak boleh kosong.",
                    )
                buku["judul"] = buku_update.judul.strip()

            if buku_update.penulis is not None:
                if not buku_update.penulis.strip():
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Penulis tidak boleh kosong.",
                    )
                buku["penulis"] = buku_update.penulis.strip()

            if buku_update.kategori is not None:
                if not buku_update.kategori.strip():
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Kategori tidak boleh kosong.",
                    )
                buku["kategori"] = buku_update.kategori.strip()

            if buku_update.stok is not None:
                buku["stok"] = buku_update.stok

            return buku

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Buku dengan ID {book_id} tidak ditemukan",
    )


@app.delete(
    "/books/{book_id}",
    tags=["Books"],
    summary="Hapus buku berdasarkan ID",
    description="Menghapus satu buku dari koleksi perpustakaan.",
)
def hapus_buku(
    book_id: int = FastApiPath(..., ge=1, description="ID buku yang ingin dihapus"),
):
    for index, buku in enumerate(books_db):
        if buku["id"] == book_id:
            judul_terhapus = buku["judul"]
            books_db.pop(index)
            return {
                "pesan": f"Buku '{judul_terhapus}' berhasil dihapus dari perpustakaan.",
                "id": book_id,
            }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Buku dengan ID {book_id} tidak ditemukan",
    )


@app.post(
    "/books/reset",
    tags=["Books"],
    summary="Reset database ke seed awal",
    description="Mengembalikan list buku ke 25 seed data awal dari books.json.",
)
def reset_buku():
    global books_db
    books_db = muat_data_seed()
    return {
        "pesan": "Data buku berhasil direset ke seed awal",
        "total_buku": len(books_db),
    }

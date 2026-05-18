import json
import os
from tarif import Tarif, Kullanici

KLASOR = os.path.dirname(os.path.abspath(__file__))
TARIFLER_DOSYA = os.path.join(KLASOR, "tarifler.json")
KULLANICILAR_DOSYA = os.path.join(KLASOR, "kullanicilar.json")


# ── TARİF VERİTABANI İŞLEMLERİ ──────────────────────────────────────────────

def tarifleri_kaydet(tarif_listesi):
    veri = [t.to_dict() for t in tarif_listesi]
    with open(TARIFLER_DOSYA, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)


def tarifleri_yukle():
    if not os.path.exists(TARIFLER_DOSYA):
        return []
    try:
        with open(TARIFLER_DOSYA, "r", encoding="utf-8") as f:
            veri = json.load(f)
        return [Tarif.from_dict(t) for t in veri]
    except (json.JSONDecodeError, KeyError):
        return []


def tarif_bul(tarif_listesi, tarif_id):
    for t in tarif_listesi:
        if t.tarif_id == tarif_id:
            return t
    return None


def tarif_sil(tarif_listesi, tarif_id):
    for i, t in enumerate(tarif_listesi):
        if t.tarif_id == tarif_id:
            tarif_listesi.pop(i)
            return True
    return False


def kategoriye_gore_filtrele(tarif_listesi, kategori):
    return [t for t in tarif_listesi if t.kategori.lower() == kategori.lower()]


# ── KULLANICI VERİTABANI İŞLEMLERİ ─────────────────────────────────────────

def kullanicilari_kaydet(kullanici_listesi):
    veri = [k.to_dict() for k in kullanici_listesi]
    with open(KULLANICILAR_DOSYA, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)


def kullanicilari_yukle():
    if not os.path.exists(KULLANICILAR_DOSYA):
        return []
    try:
        with open(KULLANICILAR_DOSYA, "r", encoding="utf-8") as f:
            veri = json.load(f)
        return [Kullanici.from_dict(k) for k in veri]
    except (json.JSONDecodeError, KeyError):
        return []


def kullanici_bul(kullanici_listesi, kullanici_id):
    for k in kullanici_listesi:
        if k.kullanici_id == kullanici_id:
            return k
    return None


def kullanici_sil(kullanici_listesi, kullanici_id):
    for i, k in enumerate(kullanici_listesi):
        if k.kullanici_id == kullanici_id:
            kullanici_listesi.pop(i)
            return True
    return False

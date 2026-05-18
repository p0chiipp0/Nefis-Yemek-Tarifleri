# 🍽️ Nefis Yemek Tarifleri

Python ve Tkinter ile geliştirilmiş masaüstü yemek tarifi yönetim uygulaması.

---

## 📋 İçindekiler

- [Genel Bakış](#genel-bakış)
- [Özellikler](#özellikler)
- [Kurulum](#kurulum)
- [Dosya Yapısı](#dosya-yapısı)
- [Kullanım](#kullanım)
- [Mimari](#mimari)
- [Veri Yapısı](#veri-yapısı)
- [Geliştirici Notları](#geliştirici-notları)

---

## Genel Bakış

| Alan | Bilgi |
|---|---|
| **Programlama Dili** | Python 3.x |
| **Arayüz Kütüphanesi** | tkinter (standart kütüphane) |
| **Veri Saklama** | JSON dosyaları |
| **Mimari** | MVC benzeri katmanlı yapı |
| **Dosya Sayısı** | 5 Python + 2 JSON |

---

## Özellikler

- Tarif ekleme, düzenleme ve silme
- Kategoriye göre filtreleme (Çorbalar, Ana Yemekler, Salatalar, Tatlılar, Atıştırmalıklar, İçecekler, Kahvaltılık)
- Anlık arama
- 1–5 yıldız puanlama ve yorum sistemi
- Kullanıcı kaydı ve girişi
- Kalıcı JSON veri saklama
- Kaydırılabilir, yeniden boyutlandırılabilir arayüz (min. 900×600)

---

## Kurulum

**Gereksinimler:** Python 3.x (tkinter standart kütüphaneyle birlikte gelir, ek kurulum gerekmez.)

```bash
# Repoyu klonla
git clone https://github.com/kullanici/nefis-yemek-tarifleri.git
cd nefis-yemek-tarifleri

# Uygulamayı başlat
python main.py
```

---

## Dosya Yapısı

```
nefis-yemek-tarifleri/
│
├── main.py            # Giriş noktası — tkinter penceresini başlatır
├── gui.py             # Tüm kullanıcı arayüzü (TarifApp sınıfı)
├── tarif.py           # Veri modelleri (Tarif, Malzeme, Kullanici)
├── veritabani.py      # JSON okuma/yazma ve sorgulama fonksiyonları
│
├── tarifler.json      # Tariflerin kalıcı depolandığı JSON dosyası
└── kullanicilar.json  # Kayıtlı kullanıcıların depolandığı JSON dosyası
```

---

## Kullanım

### Tarif Ekleme
Sol kenar çubuğundaki **"Yeni Tarif"** butonuna tıklayın. Form açılır; tarif adı, kategori, hazırlama süresi, malzemeler ve yapılış adımlarını girin. **Kaydet** ile JSON'a yazılır.

### Tarif Düzenleme / Silme
Her tarif kartında **Düzenle** ve **Sil** butonları bulunur.

### Arama ve Filtreleme
- Üst arama çubuğuna yazarken liste anlık olarak filtrelenir.
- Sol kenar çubuğundaki kategori butonlarıyla kategori filtresi uygulanır.

### Kullanıcı İşlemleri
- **Kayıt Ol:** Yeni kullanıcı oluşturur ve otomatik giriş yapar.
- **Giriş Yap:** Kullanıcı adıyla mevcut hesaba giriş yapılır.
- Giriş yapan kullanıcılar tariflere **1–5 yıldız puan + yorum** ekleyebilir.

---

## Mimari

Proje, MVC benzeri katmanlı bir yapı kullanır:

| Katman | Dosya | Açıklama |
|---|---|---|
| **Model** | `tarif.py` | `Tarif`, `Malzeme`, `Kullanici` sınıfları |
| **Kalıcılık** | `veritabani.py` | JSON okuma/yazma fonksiyonları |
| **View** | `gui.py` | Tüm tkinter widget'ları ve ekranlar |
| **Controller** | `gui.py` | Olay (event) fonksiyonları |
| **Giriş Noktası** | `main.py` | Pencere oluşturma ve başlatış |

Bu yapı sayesinde veri modeli (`tarif.py`) ve kalıcılık katmanı (`veritabani.py`) arayüzden bağımsız olarak test edilebilir ve geliştirilebilir.

---

## Veri Yapısı

### tarifler.json

```json
{
  "tarif_id": 1,
  "tarif_adi": "Menemen",
  "kategori": "Kahvaltılık",
  "hazirlama_suresi": 48,
  "malzemeler": [
    { "malzeme_adi": "Domates", "miktar": "300 g" }
  ],
  "yapilis": ["1. adım...", "2. adım..."],
  "puf_nokta": "Tavaya önceden yağ koyun",
  "degerlendirmeler": [["kullanici_adi", 5, "yorum"]]
}
```

### kullanicilar.json

```json
{
  "kullanici_id": 8,
  "ad": "selin arslanpencesi"
}
```

---

## Geliştirici Notları

- Parola sistemi yoktur; giriş yalnızca kullanıcı adıyla yapılır.
- Tüm veriler çalışma sırasında bellekte tutulur; değişiklikler anında JSON'a yazılır.
- Tarif ve kullanıcı ID'leri uygulama yeniden başlatıldığında JSON'dan doğru şekilde devam eder.
- Fare tekerleği ile kaydırma tüm içerik alanlarına varsayılan olarak bağlıdır.

---

## Kategoriler

| Emoji | Kategori |
|---|---|
| 🍲 | Çorbalar |
| 🍖 | Ana Yemekler |
| 🥗 | Salatalar |
| 🍰 | Tatlılar |
| 🥨 | Atıştırmalıklar |
| 🥤 | İçecekler |
| 🍳 | Kahvaltılık |

---

## Renk Paleti

| Değişken | Renk | Kullanım |
|---|---|---|
| `BG_ANA` | `#FFF8F0` | Sıcak krem arka plan |
| `BG_SIDEBAR` | `#1A1A2E` | Koyu lacivert kenar çubuğu |
| `TURUNCU` | `#FF6B35` | Ana vurgu rengi |
| `SARI` | `#FFB830` | Altın sarısı aksan |
| `YESIL` | `#27AE60` | Salata kategorisi |
| `KIRMIZI` | `#C0392B` | Silme / hata rengi |

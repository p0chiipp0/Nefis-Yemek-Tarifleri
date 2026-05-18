class Malzeme:
    def __init__(self, malzeme_adi, miktar):
        self.malzeme_adi = malzeme_adi
        self.miktar = miktar

    def bilgi_goster(self):
        return f"{self.malzeme_adi}: {self.miktar}"

    def to_dict(self):
        return {
            "malzeme_adi": self.malzeme_adi,
            "miktar": self.miktar
        }

    @staticmethod
    def from_dict(veri):
        return Malzeme(veri["malzeme_adi"], veri["miktar"])


class Tarif:
    _id_sayaci = 1

    def __init__(self, tarif_adi, kategori, hazirlama_suresi, malzemeler=None, tarif_id=None, yapilis=None, puf_nokta=None):
        if tarif_id:
            self.tarif_id = tarif_id
        else:
            self.tarif_id = Tarif._id_sayaci
            Tarif._id_sayaci += 1

        self.tarif_adi = tarif_adi
        self.kategori = kategori
        self.hazirlama_suresi = hazirlama_suresi  # dakika cinsinden
        self.malzemeler = malzemeler if malzemeler else []
        self.degerlendirmeler = []  # (kullanici_adi, puan, yorum) tuple listesi
        self.yapilis = yapilis if yapilis else []  # adım adım yapılış listesi
        self.puf_nokta = puf_nokta if puf_nokta else ""  # püf nokta metni

    def tarif_ekle(self, malzeme):
        """Tarife yeni malzeme ekler."""
        self.malzemeler.append(malzeme)

    def tarif_guncelle(self, tarif_adi=None, kategori=None, hazirlama_suresi=None):
        """Tarif bilgilerini günceller."""
        if tarif_adi:
            self.tarif_adi = tarif_adi
        if kategori:
            self.kategori = kategori
        if hazirlama_suresi:
            self.hazirlama_suresi = hazirlama_suresi

    def ortalama_puan(self):
        if not self.degerlendirmeler:
            return 0.0
        return sum(d[1] for d in self.degerlendirmeler) / len(self.degerlendirmeler)

    def bilgi_goster(self):
        bilgi = f"[ID: {self.tarif_id}] {self.tarif_adi}\n"
        bilgi += f"  Kategori: {self.kategori} | Süre: {self.hazirlama_suresi} dk\n"
        if self.malzemeler:
            bilgi += "  Malzemeler:\n"
            for m in self.malzemeler:
                bilgi += f"    - {m.bilgi_goster()}\n"
        else:
            bilgi += "  Malzeme eklenmemiş.\n"
        puan = self.ortalama_puan()
        bilgi += f"  Ortalama Puan: {puan:.1f}/5"
        if self.degerlendirmeler:
            bilgi += f" ({len(self.degerlendirmeler)} değerlendirme)"
        return bilgi

    def to_dict(self):
        return {
            "tarif_id": self.tarif_id,
            "tarif_adi": self.tarif_adi,
            "kategori": self.kategori,
            "hazirlama_suresi": self.hazirlama_suresi,
            "malzemeler": [m.to_dict() for m in self.malzemeler],
            "degerlendirmeler": self.degerlendirmeler,
            "yapilis": self.yapilis,
            "puf_nokta": self.puf_nokta
        }

    @staticmethod
    def from_dict(veri):
        malzemeler = [Malzeme.from_dict(m) for m in veri.get("malzemeler", [])]
        t = Tarif(
            tarif_adi=veri["tarif_adi"],
            kategori=veri["kategori"],
            hazirlama_suresi=veri["hazirlama_suresi"],
            malzemeler=malzemeler,
            tarif_id=veri["tarif_id"],
            yapilis=veri.get("yapilis", []),
            puf_nokta=veri.get("puf_nokta", "")
        )
        t.degerlendirmeler = veri.get("degerlendirmeler", [])
        if veri["tarif_id"] >= Tarif._id_sayaci:
            Tarif._id_sayaci = veri["tarif_id"] + 1
        return t


class Kullanici:
    _id_sayaci = 1

    def __init__(self, ad, kullanici_id=None):
        if kullanici_id:
            self.kullanici_id = kullanici_id
        else:
            self.kullanici_id = Kullanici._id_sayaci
            Kullanici._id_sayaci += 1

        self.ad = ad

    def tarif_degerlendir(self, tarif, puan, yorum=""):
        """Kullanıcı bir tarifi değerlendirir (1-5 puan)."""
        if not (1 <= puan <= 5):
            raise ValueError("Puan 1 ile 5 arasında olmalıdır.")
        tarif.degerlendirmeler.append((self.ad, puan, yorum))
        return f"{self.ad} tarafından '{tarif.tarif_adi}' tarifinе {puan} puan verildi."

    def bilgi_goster(self):
        return f"[ID: {self.kullanici_id}] Kullanıcı: {self.ad}"

    def to_dict(self):
        return {
            "kullanici_id": self.kullanici_id,
            "ad": self.ad
        }

    @staticmethod
    def from_dict(veri):
        k = Kullanici(
            ad=veri["ad"],
            kullanici_id=veri["kullanici_id"]
        )
        if veri["kullanici_id"] >= Kullanici._id_sayaci:
            Kullanici._id_sayaci = veri["kullanici_id"] + 1
        return k

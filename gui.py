import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import json
import os
import sys

# ── IMPORT DÜZELTME: aynı klasörden import ──────────────────────────────────
_KLASOR = os.path.dirname(os.path.abspath(__file__))
if _KLASOR not in sys.path:
    sys.path.insert(0, _KLASOR)

from tarif import Tarif, Malzeme, Kullanici
from veritabani import (
    tarifleri_kaydet, tarifleri_yukle, tarif_bul, tarif_sil, kategoriye_gore_filtrele,
    kullanicilari_kaydet, kullanicilari_yukle, kullanici_bul, kullanici_sil
)

# ── NEFIS YEMEK TARİFLERİ RENK PALETİ ────────────────────────────────────────
BG_ANA        = "#FFF8F0"   # Sıcak krem arka plan
BG_SIDEBAR    = "#1A1A2E"   # Koyu lacivert sidebar
BG_KART       = "#FFFFFF"   # Beyaz kartlar
BG_GIRDI      = "#FFF3E8"   # Açık şeftali input
TURUNCU       = "#FF6B35"   # Ana turuncu (nefis.com tonu)
TURUNCU_HOV   = "#E8581F"   # Koyu hover
SARI          = "#FFB830"   # Altın sarısı aksan
KIRMIZI       = "#C0392B"   # Koyu kırmızı
YESIL         = "#27AE60"   # Taze yeşil
YAZI_ANA      = "#2C3E50"   # Koyu slate yazı
YAZI_ACIK     = "#7F8C8D"   # Açık gri yazı
YAZI_BEYAZ    = "#FFFFFF"
GRI_CIZGI     = "#ECE0D0"   # Sıcak gri ayırıcı
KART_GOLGE    = "#F0E6D3"

KATEGORILER = ["Çorbalar", "Ana Yemekler", "Salatalar", "Tatlılar", "Atıştırmalıklar", "İçecekler", "Kahvaltılık"]
KATEGORI_IKONLARI = {"Çorbalar": "🍲", "Ana Yemekler": "🍽️", "Salatalar": "🥗", 
                      "Tatlılar": "🍰", "Atıştırmalıklar": "🥨", "İçecekler": "🍹", 
                      "Kahvaltılık": "🥞", "Tümü": "📋"}


def stil_buton(parent, text, command, bg=TURUNCU, fg=YAZI_BEYAZ, width=None, font_size=10):
    kw = dict(
        text=text, command=command,
        bg=bg, fg=fg, relief="flat", cursor="hand2",
        font=("Georgia", font_size, "bold"), padx=12, pady=6,
        activebackground=TURUNCU_HOV, activeforeground=fg, bd=0
    )
    if width:
        kw["width"] = width
    btn = tk.Button(parent, **kw)
    btn.bind("<Enter>", lambda e: btn.config(bg=TURUNCU_HOV if bg == TURUNCU else bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def ayirici(parent, renk=GRI_CIZGI, pady=4):
    f = tk.Frame(parent, bg=renk, height=1)
    f.pack(fill="x", pady=pady)
    return f


class TarifApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🍴 Nefis Yemek Tarifleri")
        self.root.geometry("1100x700")
        self.root.configure(bg=BG_ANA)
        self.root.resizable(True, True)
        self.root.minsize(900, 600)

        # Veri
        self.tarifler = tarifleri_yukle()
        self.kullanicilar = kullanicilari_yukle()
        self.aktif_kullanici = None
        self.aktif_sayfa = "tarifler"

        self._arayuz_kur()
        self.tarif_listesi_goster()

    # ─────────────────────────────────────────────────────────────────────────
    # ANA LAYOUT
    # ─────────────────────────────────────────────────────────────────────────
    def _arayuz_kur(self):
        # ── ÜST BANNER ──────────────────────────────────────────────────────
        self.banner = tk.Frame(self.root, bg=TURUNCU, height=60)
        self.banner.pack(fill="x", side="top")
        self.banner.pack_propagate(False)

        tk.Label(self.banner, text="🍴", font=("Georgia", 22), bg=TURUNCU, fg=YAZI_BEYAZ).pack(side="left", padx=(18,4), pady=8)
        tk.Label(self.banner, text="Nefis Yemek Tarifleri", font=("Georgia", 20, "bold"), bg=TURUNCU, fg=YAZI_BEYAZ).pack(side="left", pady=8)
        tk.Label(self.banner, text="Lezzetin Adresi", font=("Georgia", 10, "italic"), bg=TURUNCU, fg="#FFE5CC").pack(side="left", padx=10, pady=8)

        # Kullanıcı bölümü (sağ)
        self.kullanici_frame = tk.Frame(self.banner, bg=TURUNCU)
        self.kullanici_frame.pack(side="right", padx=15)
        self._kullanici_banner_guncelle()

        # ── ANA GÖVDE ───────────────────────────────────────────────────────
        self.govde = tk.Frame(self.root, bg=BG_ANA)
        self.govde.pack(fill="both", expand=True)

        # Sol Sidebar
        self.sidebar = tk.Frame(self.govde, bg=BG_SIDEBAR, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._sidebar_kur()

        # Sağ İçerik
        self.icerik_cerceve = tk.Frame(self.govde, bg=BG_ANA)
        self.icerik_cerceve.pack(side="left", fill="both", expand=True)

        # Arama Çubuğu
        self._arama_kur()

        # Scroll'lu içerik alanı
        self.canvas = tk.Canvas(self.icerik_cerceve, bg=BG_ANA, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.icerik_cerceve, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.icerik = tk.Frame(self.canvas, bg=BG_ANA)
        self.canvas_pencere = self.canvas.create_window((0, 0), window=self.icerik, anchor="nw")
        self.icerik.bind("<Configure>", self._scroll_guncelle)
        self.canvas.bind("<Configure>", self._canvas_genislik)
        self.canvas.bind_all("<MouseWheel>", self._fare_scroll)

    def _scroll_guncelle(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _canvas_genislik(self, event):
        self.canvas.itemconfig(self.canvas_pencere, width=event.width)

    def _fare_scroll(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _kullanici_banner_guncelle(self):
        for w in self.kullanici_frame.winfo_children():
            w.destroy()
        if self.aktif_kullanici:
            tk.Label(self.kullanici_frame, text=f"👤 {self.aktif_kullanici.ad}", 
                     font=("Georgia", 10, "bold"), bg=TURUNCU, fg=YAZI_BEYAZ).pack(side="left", padx=6)
            stil_buton(self.kullanici_frame, "Çıkış", self._cikis_yap, bg=KIRMIZI, font_size=9).pack(side="left")
        else:
            stil_buton(self.kullanici_frame, "👤 Giriş Yap", self._giris_ekrani_ac, bg=BG_SIDEBAR, font_size=9).pack(side="left", padx=4)
            stil_buton(self.kullanici_frame, "Kayıt Ol", self._kayit_ekrani_ac, bg=SARI, fg=YAZI_ANA, font_size=9).pack(side="left", padx=4)

    def _sidebar_kur(self):
        tk.Label(self.sidebar, text="KATEGORİLER", font=("Georgia", 9, "bold"),
                 bg=BG_SIDEBAR, fg="#888BAA").pack(pady=(18, 6), padx=16, anchor="w")

        self.sidebar_butonlari = {}
        for kat in ["Tümü"] + KATEGORILER:
            ikon = KATEGORI_IKONLARI.get(kat, "🍴")
            btn = tk.Button(
                self.sidebar, text=f"  {ikon}  {kat}",
                font=("Georgia", 10), bg=BG_SIDEBAR, fg="#C8C9D4",
                relief="flat", anchor="w", cursor="hand2",
                activebackground="#2E2E4A", activeforeground=YAZI_BEYAZ,
                padx=10, pady=8, bd=0,
                command=lambda k=kat: self._kategori_sec(k)
            )
            btn.pack(fill="x", padx=6, pady=1)
            self.sidebar_butonlari[kat] = btn

        ayirici(self.sidebar, renk="#333355", pady=10)

        tk.Label(self.sidebar, text="YÖNETİM", font=("Georgia", 9, "bold"),
                 bg=BG_SIDEBAR, fg="#888BAA").pack(pady=(4, 6), padx=16, anchor="w")

        tk.Button(self.sidebar, text="  ➕  Yeni Tarif",
                  font=("Georgia", 10), bg=TURUNCU, fg=YAZI_BEYAZ,
                  relief="flat", anchor="w", cursor="hand2",
                  activebackground=TURUNCU_HOV, padx=10, pady=8, bd=0,
                  command=self._yeni_tarif_ekrani).pack(fill="x", padx=6, pady=1)

        tk.Button(self.sidebar, text="  👥  Kullanıcılar",
                  font=("Georgia", 10), bg=BG_SIDEBAR, fg="#C8C9D4",
                  relief="flat", anchor="w", cursor="hand2",
                  activebackground="#2E2E4A", activeforeground=YAZI_BEYAZ,
                  padx=10, pady=8, bd=0,
                  command=self._kullanici_yonetimi_ekrani).pack(fill="x", padx=6, pady=1)

    def _arama_kur(self):
        arama_bar = tk.Frame(self.icerik_cerceve, bg=BG_ANA, pady=10)
        arama_bar.pack(fill="x", padx=20)

        tk.Label(arama_bar, text="🔍", font=("Georgia", 13), bg=BG_ANA, fg=TURUNCU).pack(side="left")
        self.arama_degiskeni = tk.StringVar()
        self.arama_degiskeni.trace("w", lambda *a: self.tarif_listesi_goster())
        arama_girdi = tk.Entry(arama_bar, textvariable=self.arama_degiskeni,
                               font=("Georgia", 11), bg=BG_KART, fg=YAZI_ANA,
                               relief="flat", bd=0, insertbackground=TURUNCU)
        arama_girdi.pack(side="left", fill="x", expand=True, ipady=8, padx=8)
        tk.Frame(arama_bar, bg=GRI_CIZGI, height=2).pack(side="bottom", fill="x")

    # ─────────────────────────────────────────────────────────────────────────
    # TARİF LİSTESİ
    # ─────────────────────────────────────────────────────────────────────────
    def _kategori_sec(self, kategori):
        self.aktif_kategori = None if kategori == "Tümü" else kategori
        for k, b in self.sidebar_butonlari.items():
            if k == kategori:
                b.config(bg="#2E2E4A", fg=SARI, font=("Georgia", 10, "bold"))
            else:
                b.config(bg=BG_SIDEBAR, fg="#C8C9D4", font=("Georgia", 10))
        self.tarif_listesi_goster()

    def tarif_listesi_goster(self, kategori=None):
        for w in self.icerik.winfo_children():
            w.destroy()

        filtre = getattr(self, "aktif_kategori", None)
        arama = self.arama_degiskeni.get().strip().lower() if hasattr(self, "arama_degiskeni") else ""

        liste = self.tarifler
        if filtre:
            liste = [t for t in liste if t.kategori == filtre]
        if arama:
            liste = [t for t in liste if arama in t.tarif_adi.lower()]

        # Başlık
        baslik_f = tk.Frame(self.icerik, bg=BG_ANA)
        baslik_f.pack(fill="x", padx=20, pady=(16, 8))
        baslik_text = f"{'Tüm Tarifler' if not filtre else filtre} ({len(liste)} tarif)"
        tk.Label(baslik_f, text=baslik_text, font=("Georgia", 16, "bold"),
                 bg=BG_ANA, fg=YAZI_ANA).pack(side="left")

        if not liste:
            tk.Label(self.icerik, text="🍽️\n\nHenüz tarif eklenmemiş.\nYeni tarif eklemek için sol menüyü kullanın.",
                     font=("Georgia", 13), bg=BG_ANA, fg=YAZI_ACIK,
                     justify="center").pack(pady=60)
            return

        # Grid kartlar
        grid = tk.Frame(self.icerik, bg=BG_ANA)
        grid.pack(fill="both", expand=True, padx=16, pady=4)
        
        for i, tarif in enumerate(liste):
            satir, sutun = divmod(i, 3)
            self._tarif_karti_olustur(grid, tarif, satir, sutun)

    def _tarif_karti_olustur(self, parent, tarif, satir, sutun):
        kart = tk.Frame(parent, bg=BG_KART, relief="flat", bd=0,
                        highlightbackground=GRI_CIZGI, highlightthickness=1)
        kart.grid(row=satir, column=sutun, padx=8, pady=8, sticky="nsew")
        parent.columnconfigure(sutun, weight=1)

        # Renk bandı - kategoriye göre renk
        kat_renkler = {"Çorbalar": "#E74C3C", "Ana Yemekler": TURUNCU,
                       "Salatalar": YESIL, "Tatlılar": "#9B59B6",
                       "Atıştırmalıklar": SARI, "İçecekler": "#3498DB", "Kahvaltılık": "#E67E22"}
        bant_renk = kat_renkler.get(tarif.kategori, TURUNCU)

        bant = tk.Frame(kart, bg=bant_renk, height=5)
        bant.pack(fill="x")

        ic = tk.Frame(kart, bg=BG_KART, padx=14, pady=12)
        ic.pack(fill="both", expand=True)

        # İkon + kategori
        kat_row = tk.Frame(ic, bg=BG_KART)
        kat_row.pack(fill="x")
        ikon = KATEGORI_IKONLARI.get(tarif.kategori, "🍴")
        tk.Label(kat_row, text=f"{ikon} {tarif.kategori}", font=("Georgia", 9),
                 bg=BG_KART, fg=bant_renk).pack(side="left")

        # Puan
        puan = tarif.ortalama_puan()
        yildiz = "★" * round(puan) + "☆" * (5 - round(puan))
        tk.Label(kat_row, text=yildiz, font=("Georgia", 9),
                 bg=BG_KART, fg=SARI).pack(side="right")

        # Tarif adı
        tk.Label(ic, text=tarif.tarif_adi, font=("Georgia", 13, "bold"),
                 bg=BG_KART, fg=YAZI_ANA, wraplength=200, justify="left").pack(anchor="w", pady=(6, 2))

        # Süre
        tk.Label(ic, text=f"⏱  {tarif.hazirlama_suresi} dakika  •  {len(tarif.malzemeler)} malzeme",
                 font=("Georgia", 9), bg=BG_KART, fg=YAZI_ACIK).pack(anchor="w", pady=(0, 8))

        # Butonlar
        btn_row = tk.Frame(ic, bg=BG_KART)
        btn_row.pack(fill="x")
        stil_buton(btn_row, "Görüntüle", lambda t=tarif: self._tarif_detay_ekrani(t),
                   bg=TURUNCU, font_size=9).pack(side="left", padx=(0, 4))
        stil_buton(btn_row, "Düzenle", lambda t=tarif: self._tarif_duzenle_ekrani(t),
                   bg=BG_ANA, fg=YAZI_ANA, font_size=9).pack(side="left", padx=2)
        stil_buton(btn_row, "🗑", lambda t=tarif: self._tarif_sil(t),
                   bg="#FDECEA", fg=KIRMIZI, font_size=9).pack(side="right")

    # ─────────────────────────────────────────────────────────────────────────
    # TARİF DETAY
    # ─────────────────────────────────────────────────────────────────────────
    def _tarif_detay_ekrani(self, tarif):
        pencere = tk.Toplevel(self.root)
        pencere.title(f"🍴 {tarif.tarif_adi}")
        pencere.geometry("1000x750")
        pencere.configure(bg=BG_ANA)
        pencere.grab_set()
        pencere.minsize(800, 600)

        # ── ÜST BAŞLIK BANDI ────────────────────────────────────────────────
        bant = tk.Frame(pencere, bg=TURUNCU, pady=22)
        bant.pack(fill="x")
        ikon = KATEGORI_IKONLARI.get(tarif.kategori, "🍴")
        tk.Label(bant, text=f"{ikon}  {tarif.tarif_adi}", font=("Georgia", 22, "bold"),
                 bg=TURUNCU, fg=YAZI_BEYAZ, wraplength=900).pack(padx=30)
        tk.Label(bant, text=f"{tarif.kategori}   •   {tarif.hazirlama_suresi} dakika   •   ⭐ {tarif.ortalama_puan():.1f} / 5",
                 font=("Georgia", 13), bg=TURUNCU, fg="#FFE5CC").pack(pady=6)

        # ── SCROLL ALTYAPISI ────────────────────────────────────────────────
        canvas = tk.Canvas(pencere, bg=BG_ANA, highlightthickness=0)
        sb = ttk.Scrollbar(pencere, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        ic = tk.Frame(canvas, bg=BG_ANA)
        win_id = canvas.create_window((0, 0), window=ic, anchor="nw")

        def _scroll_guncelle(e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _canvas_genislik(e):
            canvas.itemconfig(win_id, width=e.width)
        def _fare_scroll(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        ic.bind("<Configure>", _scroll_guncelle)
        canvas.bind("<Configure>", _canvas_genislik)
        canvas.bind_all("<MouseWheel>", _fare_scroll)

        # ── YAN YANA ALAN (Malzemeler | Yapılış) ────────────────────────────
        ust_cerceve = tk.Frame(ic, bg=BG_ANA)
        ust_cerceve.pack(fill="both", expand=True, padx=24, pady=18)
        ust_cerceve.columnconfigure(0, weight=1)
        ust_cerceve.columnconfigure(1, weight=2)

        # ── SOL: MALZEMELER ─────────────────────────────────────────────────
        sol = tk.Frame(ust_cerceve, bg=BG_ANA)
        sol.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(sol, text="📋 Malzemeler", font=("Georgia", 15, "bold"),
                 bg=BG_ANA, fg=YAZI_ANA).pack(anchor="w", pady=(0, 8))

        malzeme_f = tk.Frame(sol, bg=BG_KART, padx=18, pady=14,
                             highlightbackground=GRI_CIZGI, highlightthickness=1)
        malzeme_f.pack(fill="both", expand=True)

        if tarif.malzemeler:
            for malzeme in tarif.malzemeler:
                satir = tk.Frame(malzeme_f, bg=BG_KART)
                satir.pack(fill="x", pady=4)
                tk.Label(satir, text="•", font=("Georgia", 13), bg=BG_KART,
                         fg=TURUNCU).pack(side="left", padx=(0, 10))
                tk.Label(satir, text=malzeme.malzeme_adi, font=("Georgia", 13, "bold"),
                         bg=BG_KART, fg=YAZI_ANA, anchor="w").pack(side="left")
                tk.Label(satir, text=malzeme.miktar, font=("Georgia", 12),
                         bg=BG_KART, fg=YAZI_ACIK).pack(side="right")
        else:
            tk.Label(malzeme_f, text="Malzeme eklenmemiş.", font=("Georgia", 12),
                     bg=BG_KART, fg=YAZI_ACIK).pack()

        # ── SAĞ: YAPILIŞ ────────────────────────────────────────────────────
        sag = tk.Frame(ust_cerceve, bg=BG_ANA)
        sag.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        yapilis = getattr(tarif, "yapilis", [])
        tk.Label(sag, text="👨‍🍳 Yapılış", font=("Georgia", 15, "bold"),
                 bg=BG_ANA, fg=YAZI_ANA).pack(anchor="w", pady=(0, 8))

        yapilis_f = tk.Frame(sag, bg=BG_KART, padx=18, pady=14,
                             highlightbackground=GRI_CIZGI, highlightthickness=1)
        yapilis_f.pack(fill="both", expand=True)

        if yapilis:
            for idx, adim in enumerate(yapilis, 1):
                satir = tk.Frame(yapilis_f, bg=BG_KART)
                satir.pack(fill="x", pady=5)
                tk.Label(satir, text=f"{idx}.", font=("Georgia", 13, "bold"),
                         bg=BG_KART, fg=TURUNCU, width=3, anchor="n").pack(side="left", anchor="n", pady=1)
                tk.Label(satir, text=adim, font=("Georgia", 13),
                         bg=BG_KART, fg=YAZI_ANA, wraplength=560,
                         justify="left").pack(side="left", fill="x", expand=True)
        else:
            tk.Label(yapilis_f, text="Yapılış bilgisi eklenmemiş.", font=("Georgia", 12),
                     bg=BG_KART, fg=YAZI_ACIK).pack()

        # ── ALT: PÜF NOKTA (tam genişlik) ───────────────────────────────────
        puf_nokta = getattr(tarif, "puf_nokta", "")
        if puf_nokta:
            alt_cerceve = tk.Frame(ic, bg=BG_ANA, padx=24)
            alt_cerceve.pack(fill="x", pady=(0, 10))
            tk.Label(alt_cerceve, text="💡 Püf Nokta", font=("Georgia", 15, "bold"),
                     bg=BG_ANA, fg=YAZI_ANA).pack(anchor="w", pady=(0, 6))
            puf_f = tk.Frame(alt_cerceve, bg="#FFFBEA", padx=20, pady=14,
                             highlightbackground=SARI, highlightthickness=2)
            puf_f.pack(fill="x")
            tk.Label(puf_f, text=f"✨   {puf_nokta}", font=("Georgia", 13, "italic"),
                     bg="#FFFBEA", fg="#7D6608", wraplength=920, justify="left").pack(anchor="w")

        # ── DEĞERLENDİRMELER ────────────────────────────────────────────────
        deg_cerceve = tk.Frame(ic, bg=BG_ANA, padx=24)
        deg_cerceve.pack(fill="x", pady=(4, 4))

        tk.Label(deg_cerceve, text="💬 Değerlendirmeler", font=("Georgia", 15, "bold"),
                 bg=BG_ANA, fg=YAZI_ANA).pack(anchor="w", pady=(0, 6))

        deg_f = tk.Frame(deg_cerceve, bg=BG_KART, padx=18, pady=12,
                         highlightbackground=GRI_CIZGI, highlightthickness=1)
        deg_f.pack(fill="x")

        if tarif.degerlendirmeler:
            for kullanici_ad, puan, yorum in tarif.degerlendirmeler:
                d_satir = tk.Frame(deg_f, bg=BG_KART)
                d_satir.pack(fill="x", pady=4)
                yildiz = "★" * puan + "☆" * (5 - puan)
                tk.Label(d_satir, text=f"👤 {kullanici_ad}", font=("Georgia", 12, "bold"),
                         bg=BG_KART, fg=YAZI_ANA).pack(side="left")
                tk.Label(d_satir, text=yildiz, font=("Georgia", 12),
                         bg=BG_KART, fg=SARI).pack(side="left", padx=8)
                if yorum:
                    tk.Label(d_satir, text=yorum, font=("Georgia", 11, "italic"),
                             bg=BG_KART, fg=YAZI_ACIK).pack(side="left")
        else:
            tk.Label(deg_f, text="Henüz değerlendirme yok.", font=("Georgia", 12),
                     bg=BG_KART, fg=YAZI_ACIK).pack()

        # Değerlendirme Ekle
        if self.aktif_kullanici:
            tk.Label(deg_cerceve, text="⭐ Değerlendirme Ekle", font=("Georgia", 13, "bold"),
                     bg=BG_ANA, fg=YAZI_ANA).pack(anchor="w", pady=(12, 4))
            puan_frame = tk.Frame(deg_cerceve, bg=BG_ANA)
            puan_frame.pack(fill="x")
            tk.Label(puan_frame, text="Puan (1-5):", font=("Georgia", 12),
                     bg=BG_ANA, fg=YAZI_ANA).pack(side="left", padx=(0, 8))
            puan_var = tk.IntVar(value=5)
            ttk.Spinbox(puan_frame, from_=1, to=5, textvariable=puan_var,
                        width=4, font=("Georgia", 12)).pack(side="left")
            yorum_var = tk.StringVar()
            tk.Entry(deg_cerceve, textvariable=yorum_var, font=("Georgia", 12),
                     bg=BG_GIRDI, relief="flat", bd=2).pack(fill="x", pady=6, ipady=5)

            def degerlendirme_ekle():
                try:
                    self.aktif_kullanici.tarif_degerlendir(tarif, puan_var.get(), yorum_var.get())
                    tarifleri_kaydet(self.tarifler)
                    messagebox.showinfo("✅ Başarılı", "Değerlendirmeniz eklendi!", parent=pencere)
                    pencere.destroy()
                    self.tarif_listesi_goster()
                except ValueError as e:
                    messagebox.showerror("Hata", str(e), parent=pencere)

            stil_buton(deg_cerceve, "⭐ Değerlendirmeyi Gönder", degerlendirme_ekle, font_size=11).pack(pady=6)

        buton_cerceve = tk.Frame(ic, bg=BG_ANA, padx=24)
        buton_cerceve.pack(fill="x", pady=(4, 16))
        stil_buton(buton_cerceve, "Kapat", pencere.destroy, bg=GRI_CIZGI, fg=YAZI_ANA, font_size=11).pack()

    # ─────────────────────────────────────────────────────────────────────────
    # YENİ TARİF / DÜZENLE
    # ─────────────────────────────────────────────────────────────────────────
    def _yeni_tarif_ekrani(self):
        self._tarif_form_ekrani(None)

    def _tarif_duzenle_ekrani(self, tarif):
        self._tarif_form_ekrani(tarif)

    def _tarif_form_ekrani(self, tarif=None):
        pencere = tk.Toplevel(self.root)
        baslik_text = "✏️ Tarif Düzenle" if tarif else "➕ Yeni Tarif Ekle"
        pencere.title(baslik_text)
        pencere.geometry("550x700")
        pencere.configure(bg=BG_ANA)
        pencere.grab_set()

        # Başlık
        bant = tk.Frame(pencere, bg=TURUNCU, pady=16)
        bant.pack(fill="x")
        tk.Label(bant, text=baslik_text, font=("Georgia", 16, "bold"),
                 bg=TURUNCU, fg=YAZI_BEYAZ).pack()

        # Scroll
        canvas = tk.Canvas(pencere, bg=BG_ANA, highlightthickness=0)
        sb = ttk.Scrollbar(pencere, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        ic = tk.Frame(canvas, bg=BG_ANA, padx=24, pady=16)
        canvas.create_window((0, 0), window=ic, anchor="nw")
        ic.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def etiket(text):
            tk.Label(ic, text=text, font=("Georgia", 10, "bold"),
                     bg=BG_ANA, fg=YAZI_ANA).pack(anchor="w", pady=(8, 2))

        def girdi(var, placeholder=""):
            e = tk.Entry(ic, textvariable=var, font=("Georgia", 11),
                         bg=BG_GIRDI, fg=YAZI_ANA, relief="flat", bd=0,
                         insertbackground=TURUNCU)
            e.pack(fill="x", ipady=7)
            tk.Frame(ic, bg=GRI_CIZGI, height=1).pack(fill="x")
            return e

        # Form alanları
        etiket("🍴 Tarif Adı")
        ad_var = tk.StringVar(value=tarif.tarif_adi if tarif else "")
        girdi(ad_var)

        etiket("📂 Kategori")
        kat_var = tk.StringVar(value=tarif.kategori if tarif else KATEGORILER[0])
        kat_combo = ttk.Combobox(ic, textvariable=kat_var, values=KATEGORILER,
                                  font=("Georgia", 11), state="readonly")
        kat_combo.pack(fill="x", pady=2)

        etiket("⏱ Hazırlama Süresi (dakika)")
        sure_var = tk.StringVar(value=str(tarif.hazirlama_suresi) if tarif else "30")
        girdi(sure_var)

        ayirici(ic, pady=12)
        tk.Label(ic, text="📋 Malzemeler", font=("Georgia", 12, "bold"),
                 bg=BG_ANA, fg=YAZI_ANA).pack(anchor="w")

        malzeme_frame = tk.Frame(ic, bg=BG_ANA)
        malzeme_frame.pack(fill="x", pady=6)
        malzeme_listesi = []

        def malzeme_satiri_ekle(ad="", miktar=""):
            satir = tk.Frame(malzeme_frame, bg=BG_ANA)
            satir.pack(fill="x", pady=2)
            ad_v = tk.StringVar(value=ad)
            mik_v = tk.StringVar(value=miktar)
            tk.Entry(satir, textvariable=ad_v, font=("Georgia", 10), bg=BG_GIRDI,
                     relief="flat", placeholder_text="Malzeme adı").pack(side="left", fill="x", expand=True, ipady=5)
            tk.Label(satir, text=" : ", bg=BG_ANA, fg=YAZI_ACIK).pack(side="left")
            tk.Entry(satir, textvariable=mik_v, font=("Georgia", 10), bg=BG_GIRDI,
                     width=10, relief="flat").pack(side="left", ipady=5)
            def sil():
                satir.destroy()
                malzeme_listesi.remove((ad_v, mik_v))
            tk.Button(satir, text="✕", bg="#FDECEA", fg=KIRMIZI, relief="flat",
                      font=("Georgia", 9), command=sil, cursor="hand2").pack(side="left", padx=4)
            malzeme_listesi.append((ad_v, mik_v))

        if tarif and tarif.malzemeler:
            for m in tarif.malzemeler:
                malzeme_satiri_ekle(m.malzeme_adi, m.miktar)
        
        stil_buton(ic, "+ Malzeme Ekle", malzeme_satiri_ekle, bg=BG_KART, fg=TURUNCU, font_size=9).pack(anchor="w", pady=4)

        ayirici(ic, pady=8)

        def kaydet():
            ad = ad_var.get().strip()
            kat = kat_var.get().strip()
            try:
                sure = int(sure_var.get())
            except ValueError:
                messagebox.showerror("Hata", "Hazırlama süresi sayı olmalıdır!", parent=pencere)
                return
            if not ad:
                messagebox.showerror("Hata", "Tarif adı boş olamaz!", parent=pencere)
                return

            malzemeler = [Malzeme(a.get().strip(), m.get().strip())
                          for a, m in malzeme_listesi if a.get().strip()]

            if tarif:
                tarif.tarif_guncelle(tarif_adi=ad, kategori=kat, hazirlama_suresi=sure)
                tarif.malzemeler = malzemeler
                messagebox.showinfo("✅", "Tarif güncellendi!", parent=pencere)
            else:
                yeni = Tarif(ad, kat, sure, malzemeler)
                self.tarifler.append(yeni)
                messagebox.showinfo("✅", "Tarif eklendi!", parent=pencere)

            tarifleri_kaydet(self.tarifler)
            pencere.destroy()
            self.tarif_listesi_goster()

        stil_buton(ic, "💾 Kaydet", kaydet, font_size=11).pack(fill="x", pady=8)
        stil_buton(ic, "İptal", pencere.destroy, bg=GRI_CIZGI, fg=YAZI_ANA).pack(fill="x")

    def _tarif_sil(self, tarif):
        if messagebox.askyesno("Tarif Sil", f"'{tarif.tarif_adi}' tarifini silmek istediğinizden emin misiniz?"):
            tarif_sil(self.tarifler, tarif.tarif_id)
            tarifleri_kaydet(self.tarifler)
            self.tarif_listesi_goster()

    # ─────────────────────────────────────────────────────────────────────────
    # KULLANICI YÖNETİMİ
    # ─────────────────────────────────────────────────────────────────────────
    def _kullanici_yonetimi_ekrani(self):
        pencere = tk.Toplevel(self.root)
        pencere.title("👥 Kullanıcı Yönetimi")
        pencere.geometry("460x500")
        pencere.configure(bg=BG_ANA)
        pencere.grab_set()

        bant = tk.Frame(pencere, bg=BG_SIDEBAR, pady=16)
        bant.pack(fill="x")
        tk.Label(bant, text="👥 Kullanıcılar", font=("Georgia", 16, "bold"),
                 bg=BG_SIDEBAR, fg=YAZI_BEYAZ).pack()

        ic = tk.Frame(pencere, bg=BG_ANA, padx=20, pady=16)
        ic.pack(fill="both", expand=True)

        def listeyi_yenile():
            for w in liste_frame.winfo_children():
                w.destroy()
            for k in self.kullanicilar:
                satir = tk.Frame(liste_frame, bg=BG_KART, padx=12, pady=8,
                                 highlightbackground=GRI_CIZGI, highlightthickness=1)
                satir.pack(fill="x", pady=3)
                tk.Label(satir, text=f"👤 {k.ad}", font=("Georgia", 11),
                         bg=BG_KART, fg=YAZI_ANA).pack(side="left")
                tk.Label(satir, text=f"ID: {k.kullanici_id}", font=("Georgia", 9),
                         bg=BG_KART, fg=YAZI_ACIK).pack(side="left", padx=8)
                stil_buton(satir, "🗑 Sil", lambda kid=k.kullanici_id: _kullanici_sil(kid),
                           bg="#FDECEA", fg=KIRMIZI, font_size=9).pack(side="right")

        def _kullanici_sil(kid):
            kullanici_sil(self.kullanicilar, kid)
            kullanicilari_kaydet(self.kullanicilar)
            listeyi_yenile()

        # Yeni kullanıcı ekle
        ekle_f = tk.Frame(ic, bg=BG_ANA)
        ekle_f.pack(fill="x", pady=(0, 12))
        tk.Label(ekle_f, text="Yeni Kullanıcı Adı:", font=("Georgia", 10),
                 bg=BG_ANA, fg=YAZI_ANA).pack(side="left", padx=(0, 6))
        ad_var = tk.StringVar()
        tk.Entry(ekle_f, textvariable=ad_var, font=("Georgia", 10),
                 bg=BG_GIRDI, relief="flat").pack(side="left", fill="x", expand=True, ipady=5)
        
        def kullanici_ekle():
            ad = ad_var.get().strip()
            if not ad:
                messagebox.showerror("Hata", "Ad boş olamaz!", parent=pencere)
                return
            self.kullanicilar.append(Kullanici(ad))
            kullanicilari_kaydet(self.kullanicilar)
            ad_var.set("")
            listeyi_yenile()

        stil_buton(ekle_f, "Ekle", kullanici_ekle, font_size=9).pack(side="left", padx=6)

        ayirici(ic)
        liste_frame = tk.Frame(ic, bg=BG_ANA)
        liste_frame.pack(fill="both", expand=True)
        listeyi_yenile()

    # ─────────────────────────────────────────────────────────────────────────
    # GİRİŞ / KAYIT
    # ─────────────────────────────────────────────────────────────────────────
    def _giris_ekrani_ac(self):
        pencere = tk.Toplevel(self.root)
        pencere.title("👤 Giriş Yap")
        pencere.geometry("380x280")
        pencere.configure(bg=BG_ANA)
        pencere.grab_set()

        bant = tk.Frame(pencere, bg=TURUNCU, pady=16)
        bant.pack(fill="x")
        tk.Label(bant, text="🍴 Hoş Geldiniz!", font=("Georgia", 16, "bold"),
                 bg=TURUNCU, fg=YAZI_BEYAZ).pack()

        ic = tk.Frame(pencere, bg=BG_ANA, padx=30, pady=20)
        ic.pack(fill="both", expand=True)

        tk.Label(ic, text="Kullanıcı Adı:", font=("Georgia", 10, "bold"),
                 bg=BG_ANA, fg=YAZI_ANA).pack(anchor="w")
        ad_var = tk.StringVar()
        tk.Entry(ic, textvariable=ad_var, font=("Georgia", 11),
                 bg=BG_GIRDI, relief="flat").pack(fill="x", ipady=6, pady=4)

        def giris_yap():
            ad = ad_var.get().strip()
            bulunan = next((k for k in self.kullanicilar if k.ad.lower() == ad.lower()), None)
            if bulunan:
                self.aktif_kullanici = bulunan
                self._kullanici_banner_guncelle()
                pencere.destroy()
                messagebox.showinfo("✅", f"Hoş geldiniz, {bulunan.ad}!")
            else:
                messagebox.showerror("Hata", "Kullanıcı bulunamadı. Önce kayıt olun.", parent=pencere)

        stil_buton(ic, "Giriş Yap", giris_yap, font_size=11).pack(fill="x", pady=8)
        stil_buton(ic, "İptal", pencere.destroy, bg=GRI_CIZGI, fg=YAZI_ANA).pack(fill="x")

    def _kayit_ekrani_ac(self):
        pencere = tk.Toplevel(self.root)
        pencere.title("📝 Kayıt Ol")
        pencere.geometry("380x260")
        pencere.configure(bg=BG_ANA)
        pencere.grab_set()

        bant = tk.Frame(pencere, bg=SARI, pady=16)
        bant.pack(fill="x")
        tk.Label(bant, text="📝 Yeni Üyelik", font=("Georgia", 16, "bold"),
                 bg=SARI, fg=YAZI_ANA).pack()

        ic = tk.Frame(pencere, bg=BG_ANA, padx=30, pady=20)
        ic.pack(fill="both", expand=True)

        tk.Label(ic, text="Kullanıcı Adı:", font=("Georgia", 10, "bold"),
                 bg=BG_ANA, fg=YAZI_ANA).pack(anchor="w")
        ad_var = tk.StringVar()
        tk.Entry(ic, textvariable=ad_var, font=("Georgia", 11),
                 bg=BG_GIRDI, relief="flat").pack(fill="x", ipady=6, pady=4)

        def kayit_ol():
            ad = ad_var.get().strip()
            if not ad:
                messagebox.showerror("Hata", "Kullanıcı adı boş olamaz!", parent=pencere)
                return
            if any(k.ad.lower() == ad.lower() for k in self.kullanicilar):
                messagebox.showerror("Hata", "Bu kullanıcı adı zaten alınmış!", parent=pencere)
                return
            yeni_k = Kullanici(ad)
            self.kullanicilar.append(yeni_k)
            kullanicilari_kaydet(self.kullanicilar)
            self.aktif_kullanici = yeni_k
            self._kullanici_banner_guncelle()
            pencere.destroy()
            messagebox.showinfo("✅", f"Kayıt başarılı! Hoş geldiniz, {ad}!")

        stil_buton(ic, "Kayıt Ol", kayit_ol, bg=SARI, fg=YAZI_ANA, font_size=11).pack(fill="x", pady=8)
        stil_buton(ic, "İptal", pencere.destroy, bg=GRI_CIZGI, fg=YAZI_ANA).pack(fill="x")

    def _cikis_yap(self):
        self.aktif_kullanici = None
        self._kullanici_banner_guncelle()

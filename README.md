# YouTube Video Indirme

Clipboard'a kopyalanan YouTube linklerini otomatik indiren portable Windows sistemi.

## Hizli Baslangic

```
1. kur.bat            cift tikla  →  gerekli araclar indirilir
2. Basla.bat          cift tikla  →  izleyici system tray'e yerlesir
3. YouTube linki kopyala          →  video otomatik iner
```

## Dosya Yapisi

```
Video-indirme/
├── kur.bat           # Tek tikla kurulum (araclar + python + paketler)
├── Basla.bat         # Clipboard izleyiciyi baslatir (tray ikonu)
├── indir.bat         # Manuel indirme (link yapistir veya parametre ver)
├── paket-kur.bat     # Python paketlerini gunceller
├── izleyici.pyw      # Ana script - clipboard izleme + tray + bildirim
├── .gitignore        # Buyuk dosyalar haric tutulur
├── araçlar/          # (.gitignore - kur.bat ile indirilir)
│   ├── yt-dlp.exe
│   ├── ffmpeg.exe
│   ├── deno.exe
│   └── python/       # Portable Python 3.12
└── videolar/         # (.gitignore - indirilen videolar)
```

## Ozellikler

- **Otomatik indirme**: YouTube linki kopyalaninca aninda indirir
- **System tray**: Arka planda calisir, tray ikonundan yonetilir
- **Toast bildirim**: Indirme basladi / bitti / hata bildirimi
- **Portable**: Sistemde kurulum gerektirmez, klasoru tasi calissin
- **Akilli format**: En iyi kalite video+ses, MP4 olarak birlestirir
- **Tekrar koruma**: Ayni linki iki kez indirmez

## Desteklenen Link Formatlari

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`

## Manuel Kullanim

```bat
:: Parametre ile
indir.bat https://www.youtube.com/watch?v=VIDEO_ID

:: Interaktif - link sorar
indir.bat
```

## Yeni Bilgisayara Kurulum

1. Bu repoyu klonla
2. `kur.bat` cift tikla
3. Bitti. `Basla.bat` ile kullanmaya basla

## Gereksinimler

- Windows 10/11 (64-bit)
- Internet baglantisi (ilk kurulum icin)
- ~300 MB disk alani (araclar icin)

## Teknik Detaylar

| Arac | Gorevi |
|------|--------|
| yt-dlp | YouTube video indirme motoru |
| ffmpeg | Video + ses birlestirme |
| deno | yt-dlp icin JavaScript runtime (YouTube sifre cozme) |
| Python 3.12 | Clipboard izleyici scripti |
| pyperclip | Pano erisimi |
| pystray + pillow | System tray ikonu |
| winotify | Windows toast bildirimleri |

## Sorun Giderme

**"No supported JavaScript runtime" hatasi:**
`kur.bat` calistir, deno otomatik indirilecek.

**Indirme baslamiyor:**
yt-dlp'yi guncelle: `araçlar\yt-dlp.exe -U`

**Clipboard izleyici calismadi:**
`paket-kur.bat` ile Python paketlerini yeniden kur.

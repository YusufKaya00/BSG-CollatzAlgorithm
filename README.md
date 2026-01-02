# Güvenli ve Dengeli Collatz Algoritması (Secure Balanced Collatz)

Bu proje, ünlü **Collatz Sanısı**'nı (3n+1 problemi) kriptografik güvenlik yöntemleriyle birleştirerek, tamamen rastgele ve istatistiksel olarak mükemmel dengede (eşit sayıda 0 ve 1) ikili (binary) diziler üreten bir algoritma sunar.

## 📁 Dosya İçeriği
- `secure_collatz.py`: Algoritmanın kaynak kodu ve istatistiksel testler.

---

## 🛠 Nasıl Çalışır? (Detaylı Mantık)

Bu algoritma, standart Collatz dizisinin ($n \to n/2$ veya $n \to 3n+1$) öngörülemez yapısını kullanır ancak güvenliği artırmak için deterministik sabit $+1$ yerine, kriptografik bir anahtarla (Key) türetilen dinamik bir $+k$ değeri kullanır.

### Temel Prensipler:
1.  **Kriptografik Başlangıç (Seed):** Python'un `secrets` modülü kullanılarak 256-bitlik tahmin edilemez bir başlangıç sayısı ($n$) ve 32-byte'lık gizli bir anahtar (Key) oluşturulur.
2.  **Güvenli Collatz Adımı ($3n + k$):** 
    - Standart Collatz'da sayı tek ise $3n+1$ yapılır.
    - Bu algoritmada, sayı tek ise $3n+k$ yapılır. 
    - **$k$ Değeri:** Gizli anahtar ve mevcut $n$ sayısı **HMAC-SHA256** ile şifrelenerek türetilir. Bu, $k$'nın dışarıdan tahmin edilmesini imkansız kılar ve dizinin yörüngesini kaotik hale getirir.
3.  **Bit Üretimi ve Denge (Balance):**
    - $n$ çift ise: Aday bit **'1'** (işlem $n/2$).
    - $n$ tek ise: Aday bit **'0'** (işlem $3n+k$).
    - **Zorunlu Eşitlik:** Algoritma, üretilen şifrenin uzunluğu boyunca 0 ve 1 sayısını sayar. Eğer 0 kotası dolduysa ve yeni bir 0 üretilirse, bu bit **kaydedilmez** (çöpe atılır) ancak sayısal yörünge ($n$) ilerlemeye devam eder. Bu sayede sonuçta **kesinlikle** eşit sayıda 0 ve 1 elde edilir.

---

## 📝 Sözde Kod (Pseudocode)

```text
BAŞLA
    GİRDİ: İstenen uzunluk (L) (Çift sayı olmalı)
    
    // 1. Hazırlık
    Hedef_0_Sayısı = L / 2
    Hedef_1_Sayısı = L / 2
    Mevcut_0 = 0, Mevcut_1 = 0
    Şifre = ""
    
    // 2. Kriptografik Başlangıç
    n = Rastgele_Güvenli_Sayı(256 bit)
    Anahtar = Rastgele_Byte_Dizisi(32 byte)
    
    DÖNGÜ (Şifre uzunluğu < L olduğu sürece):
        
        // Parite Kontrolü
        EĞER (n Çift ise):
            Aday_Bit = '1'
        DEĞİLSE (n Tek ise):
            Aday_Bit = '0'
        
        // 3. Dengeleme (Rejection Sampling)
        EĞER (Aday_Bit == '0' VE Mevcut_0 < Hedef_0_Sayısı):
            Şifre'ye '0' ekle
            Mevcut_0 artır
        DEĞİLSE EĞER (Aday_Bit == '1' VE Mevcut_1 < Hedef_1_Sayısı):
            Şifre'ye '1' ekle
            Mevcut_1 artır
        // Kotası dolan bitler reddedilir, şifreye eklenmez
        
        // 4. Sonraki Adım (Durum Güncelleme)
        EĞER (n Çift ise):
            n = n / 2
        DEĞİLSE:
            // Güvenli k türetimi
            k = HMAC_SHA256(Anahtar, n)
            n = 3 * n + k
            
    DÖNGÜ SONU
    
    // 5. Doğrulama
    İstatistiksel_Testleri_Çalıştır(Şifre)
    YAZDIR Şifre
BİTİR
```

---

## 📊 Akış Şeması (Flowchart)

```mermaid
graph TD
    A[Başlat] --> B{Uzunluk Çift mi?};
    B -- Hayır --> C[Hata Ver ve Çık];
    B -- Evet --> D[Başlangıç n ve Key Üret];
    D --> E{Şifre Tamamlandı mı?};
    E -- Evet --> K[Testleri Yap ve Sonucu Yaz];
    E -- Hayır --> F{n Çift mi?};
    
    F -- Evet (Bit: 1) --> G[Aday Bit: 1];
    F -- Hayır (Bit: 0) --> H[Aday Bit: 0];
    
    G --> I{1 Kotası Doldu mu?};
    H --> J{0 Kotası Doldu mu?};
    
    I -- Hayır --> L[Şifreye 1 Ekle];
    I -- Evet --> M[Biti Atla];
    J -- Hayır --> N[Şifreye 0 Ekle];
    J -- Evet --> M;
    
    L --> O[Durum Güncelle];
    N --> O;
    M --> O;
    
    O --> P{n Çift mi?};
    P -- Evet --> R[n = n / 2];
    P -- Hayır --> S[n = 3n + HMAC(n, Key)];
    
    R --> E;
    S --> E;
```

---

## 📈 İstatistiksel Testler ve Çıktılar

Algoritma, üretilen çıktının kalitesini kanıtlamak için her çalıştırmada iki temel test uygular:

### 1. Ki-Kare Testi (Chi-Square Test)
*   **Amaç:** Üretilen dizideki 0 ve 1 dağılımının "Uniform" (Eşit) olup olmadığını ölçer.
*   **Beklenen:** Algoritmamız yapısı gereği bunu zorladığı için her zaman **Mükemmel (Statistic: 0.0)** sonuç verir. 
*   **Sonuç:** `PASS` (0 ve 1 sayıları eşittir).

### 2. Seri Testi (Runs Test / Wald-Wolfowitz)
*   **Amaç:** Dizinin rastgeleliğini ve bağımsızlığını ölçer. Arka arkaya gelen bitlerin (örneğin `0000` veya `101010`) beklenen doğal sıklıkta olup olmadığına bakar.
*   **Z-Skoru:** -1.96 ile +1.96 arasında ise dizi rastgeledir.
*   **Örnek:** `00110011` (Kümeli) veya `01010101` (Ardışık) gibi yapay desenler bu testten geçemez.
*   **Sonuç:** `PASS` (Dizi istatistiksel olarak rastgele dağılmıştır).

---

## 🚀 Çalıştırma

Kodu çalıştırmak için terminalde şu komutu kullanın:

```bash
python secure_collatz.py --length 128
```

*   `--length`: Üretilecek bit uzunluğu (varsayılan 128, çift sayı olmalı).

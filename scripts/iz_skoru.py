"""Metindeki AI yazım izlerinin yoğunluğunu 0-100 arası kaba bir skora çevirir.

Bu bir AI dedektörü DEĞİLDİR; hiçbir dedektörün sonucunu tahmin etmez.
Yalnızca references/kaliplar.md'deki ölçülebilir izleri sayar. Eşikler kaba ayardır.

Doğrulama (küçük, 2026-11): ChatGPT öncesi 30 DergiPark Türkçe özetine karşı
AI ile sıfırdan yazılmış 30 özette AUC 0,83, AI ile cilalanmış aynı 30 özette
AUC 0,59. Ağırlıklar bu veriye göre seçildi; iyimser bir tahmindir. Noktalı
virgül ve uzun cümle bu veride ters yönde çalıştığı için (insanlar daha çok
kullanıyor) skora girmez, yalnızca bilgi olarak gösterilir.

Kullanım: python -I iz_skoru.py metin.txt
"""
import re
import statistics
import sys

# Çoğu kalıp omerfarukersin/turkce-akademik-humanizer'ın DergiPark verisiyle
# doğrulanmış listesinden (TR kodları references/kaliplar.md'de). Orada AI izi
# olarak doğrulanmayan "günümüzde", "son yıllarda", "göz önünde bulundurulduğunda"
# bilerek listede yok. Alan terimleri (kritik değer, derinlemesine görüşme,
# çok boyutlu ölçekleme) dışarıda tutulur.
TR_KALIP = r"""önemli (bir )?rol|kilit rol|büyük önem|önem arz|hayati önem|kritik(?! (değer|dönem))|
altını çiz|ışık tut|kayda değer|dikkat çekici|çarpıcı|vurgulamaktadır|önemini vurgula|
keşfet|katkıda bulun|ile sonuçlan|zemin hazırla|önünü aç|köprü kur|teşvik et|olanak (tanı|sağla|sun)|
kapsamlı|derinlemesine(?! görüşme)|çok (boyutlu|yönlü)(?! ölçekleme)|bütüncül|dinamikler|potansiyel|
içgörü|girift|yenilikçi|dönüştürücü|stratejik|paydaş|perspektif|zorluklar|uzun vadeli|giderek artan|
farkındalık (yarat|artır)|\w+ bir şekilde|hizmet etmekte|işlev gör|
amaçlamaktadır|ortaya koymaktadır|Bu bulgular,|değerli (bilgi|bulgu|katkı)|politika yapıcı|
gelecekteki (araştırma|çalışma)|teorik ve (pratik|uygulamalı)|
bu bağlamda|bu doğrultuda|bu çerçevede|Buna ek olarak|Bunun yanı sıra|sinerji|katma değer|
, (ama|ancak|fakat|oysa|lakin) |şudur:|tam da|tam anlamıyla|gerçekten de|esasen|nihayetinde|
bir bakıma|gerçek anlamda|sadece .{1,40} değil|aynı zamanda|, ki bu da"""
EN_KALIP = r"""pivotal|crucial|vital|groundwork|complemented by|underscore|highlight|landscape|leverag|
robust|comprehensive|novel|seamless|testament|delve|foster|showcas|in order to|serves as"""
SIRA = r"\b(Birincisi|İkincisi|Üçüncüsü|Dördüncüsü|Firstly|Secondly|Thirdly)\b"

# (ad, ağırlık, açıklama)
OLCUTLER = [
    ("tekduzelik", 50, "cümle uzunluklarının birbirine benzerliği (değişim katsayısı 0,6 ve üstü = sıfır)"),
    ("kalip", 40, "100 kelimede katalog ifadesi (2 ve üstü = tam puan)"),
    ("sira_sozcugu", 10, "1000 kelimede Birincisi/İkincisi… (1,5 ve üstü = tam puan)"),
]
# Skora girmeyen, okunabilirlik için gösterilen ölçüler
BILGI = [
    ("noktali_virgul", "cümle başına noktalı virgül"),
    ("uzun_cumle", "40+ kelimelik cümle oranı"),
]


def cumleler(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ(\"])", text.strip())
    return [s for s in parts if len(s.split()) >= 3]


def skor(text):
    sents = cumleler(text)
    if not sents:
        return {"skor": 0, "parcalar": {}, "bilgi": {}}
    words = len(text.split())
    lens = [len(s.split()) for s in sents]
    turkce = len(re.findall(r"[çğışöüÇĞİŞÖÜ]", text)) > len(text) * 0.005
    kalip = re.compile((TR_KALIP if turkce else EN_KALIP).replace("\n", ""), re.I)
    cv = statistics.pstdev(lens) / statistics.mean(lens) if len(lens) > 1 else 0
    bilgi = {
        "noktali_virgul": round(text.count(";") / len(sents), 2),
        "uzun_cumle": round(sum(l >= 40 for l in lens) / len(sents), 2),
    }
    oran = {
        "tekduzelik": 1 - min(cv / 0.6, 1) if len(lens) > 2 else 0,
        "kalip": min(len(kalip.findall(text)) / words * 100 / 2, 1),
        "sira_sozcugu": min(len(re.findall(SIRA, text)) / words * 1000 / 1.5, 1),
    }
    parcalar = {ad: round(oran[ad] * w, 1) for ad, w, _ in OLCUTLER}
    return {"skor": round(sum(parcalar.values())), "parcalar": parcalar, "bilgi": bilgi}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8")
    r = skor(open(sys.argv[1], encoding="utf-8").read())
    print(f"AI iz skoru: {r['skor']}/100  (dedektör sonucu değildir)")
    for ad, w, aciklama in OLCUTLER:
        print(f"  {ad:15} {r['parcalar'].get(ad, 0):5}/{w}  {aciklama}")
    print("Bilgi (skora girmez, okunabilirlik):")
    for ad, aciklama in BILGI:
        print(f"  {ad:15} {r['bilgi'].get(ad, 0):5}  {aciklama}")

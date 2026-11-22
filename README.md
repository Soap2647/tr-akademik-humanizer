# tr-akademik-humanizer

Türkçe akademik metinlerdeki yapay zekâ izlerini temizleyen bir [Claude Code](https://claude.com/claude-code) skill'i. Asıl hedefi TÜBİTAK önerileri ve raporları (1001, 1002, 1501, 1505, 2209-A/B…), ama tez, makale, kalkınma ajansı başvurusu ve proje raporlarında da çalışır.

İngilizce humanizer'lar metne "kişilik" katmaya çalışır: fikir, mizah, birinci şahıs. Proje önerisinde bu ters teper. Bu skill başka bir ilkeyle çalışıyor: **süs değil, somutluk.** Genel cümle yerine projeye özgü ayrıntı, tekdüze "-mektedir" yerine çeşitli ritim, noktalı virgül zinciri yerine düz cümleler.

## Ne yapar

- 40 maddelik bir **Türkçe AI kalıp kataloğuyla** metni tarar. Her kalıbın kanıt düzeyi işaretli: `[V]` DergiPark verisiyle AI izi olarak doğrulanmış, `[K]` doğrulanmamış (yalnızca kalite sorunu). Bir **koruma listesi** de var: "Bu çalışmada … amaçlanmıştır" gibi Türkçe akademik yazının meşru kalıplarına dokunmaz ([`references/kaliplar.md`](references/kaliplar.md)). Katalogda "Günümüzde hızla gelişen…" açılışları, "önemli bir rol oynamaktadır", isim tamlaması zincirleri, boş "gerçekleştirilecektir"ler, çeviri kokusu, şişirilmiş yaygın etki, noktalı virgül zincirleri, "Birincisi… İkincisi…" sayımları, "…, ancak" virgülü ve "şudur:" kalıbı var.
- Uzun belgede önce her paragrafı ölçer, yüksek, orta ve temiz diye ayırır, sonra hangilerine dokunacağını sana sorar.
- **Ritme bakar.** Testte AI metnini en iyi ayıran sinyal, cümle uzunluklarının tekdüzeliği çıktı. Bu yüzden her paragrafta kısa ve uzun cümleleri karıştırır, uzun cümleyi eşit parçalara bölmekten kaçınır. `iz_skoru.py --paragraf` tekdüze paragrafları listeler.
- **Yazım modu:** metni baştan yazdırıyorsan kuralları sonradan değil, yazarken uygular. Önce sayı, veri ve yöntem gerekçesi gibi malzemeyi senden ister; malzeme yoksa uydurmaz, işaret bırakır.
- Metni yeniden yazar, ardından "yorgun bir panelist bunu okusa neresine takılır?" diye kendini denetler.
- **Uydurmaz.** Kanıtı olmayan iddiaya kaynak eklemez; yerine `[KAYNAK?]`, `[ÖLÇÜT?]` ya da `[NETLEŞTİR: …]` işareti koyar.
- **Dokunulmazlar:** sayılar, atıflar, terimler, iş paketi numaraları, form başlıkları. Metin orijinalden uzun olamaz, çünkü TÜBİTAK formlarında sayfa sınırı var.
- `.docx` dosyasıyla çalışır. Orijinal dosyanın üzerine yazmaz, yanına `<ad>_insanlastirilmis.docx` çıkarır.

## Kurulum

```bash
git clone https://github.com/Soap2647/tr-akademik-humanizer ~/.claude/skills/tr-akademik-humanizer
```

Windows (PowerShell):

```powershell
git clone https://github.com/Soap2647/tr-akademik-humanizer "$env:USERPROFILE\.claude\skills\tr-akademik-humanizer"
```

Claude Code yeni oturumda skill'i kendisi görür. Script'ler yalnızca Python standart kütüphanesini kullanır. `.docx` işleri için `python-docx` gerekir.

## Kullanım

Claude Code'a şöyle yazman yeterli:

- "Bu TÜBİTAK metnini insanlaştır" (metni yapıştır ya da dosya yolunu ver)
- "Özgün değer bölümüm AI gibi duruyor, düzelt"
- "`öneri.docx` dosyasını panelist gözüyle oku ve düzelt"

İstersen AI kullanmadan kendi yazdığın bir metin de ver. Skill cümle uzunluğuna, bağlaç tercihlerine ve "biz" kullanımına bakıp yeniden yazımı senin sesine uydurur.

## Örnek

> **Önce:** Günümüzde yapay zekâ teknolojilerinin hızla gelişmesiyle birlikte sağlık alanında birçok yenilikçi uygulama ortaya çıkmaktadır. Bu bağlamda, söz konusu yöntem ilgili veri seti üzerinde uygulanacaktır.
>
> **Sonra:** Türkiye'de radyolog başına düşen yıllık BT incelemesi [sayı] [KAYNAK?]; bu yük raporlama süresini uzatıyor. Yöntem PlantVillage veri setine uygulanacak.

## Script'ler

**Sayı ve atıf kontrolü.** Orijinal ile yeni metin arasında kaybolan ya da yeni eklenen sayıları ve atıfları bulur:

```bash
python -I scripts/kontrol.py orijinal.txt yeni.txt
```

**AI iz skoru.** Metni 0–100 arası bir skora çevirir: cümle uzunluklarının tekdüzeliği (50), katalogdaki kalıp ifadeler (40) ve "Birincisi… İkincisi…" sayımı (10). Noktalı virgül ve uzun cümle oranını da gösterir ama bunlar skora girmez (aşağıya bak):

```bash
python -I scripts/iz_skoru.py metin.txt
```

### Skor ne kadar güvenilir?

Küçük bir testle ölçtük. ChatGPT öncesi (2011–2020) 30 gerçek DergiPark Türkçe özeti iki gruba karşı kondu. Gruplar Claude Haiku ile üretildi:

| Karşılaştırma | AUC |
|---|---|
| İnsan özeti ve aynı başlıktan **AI'nın sıfırdan yazdığı** özet | 0,83 |
| İnsan özeti ve aynı özetin **AI ile cilalanmış** hali | 0,59 |

AUC, rastgele seçilen bir AI metninin rastgele bir insan metninden yüksek skor alma olasılığıdır: 0,5 yazı tura, 1,0 kusursuz ayrım demek.

- Sıfırdan AI metnini en iyi **tekdüzelik** ayırdı (tek başına 0,92). İnsan özetlerini aynı uzunluğa kısalttığımızda da 0,87'de kaldı, yani bu fark uzunluktan gelmiyor.
- İlk sürümdeki **noktalı virgül** ve **uzun cümle** ölçütleri **ters çalıştı**. Türk akademisyenler AI'dan daha uzun cümle kuruyor ve daha çok noktalı virgül kullanıyor. Bu yüzden ikisi skordan çıkarıldı. İlk sürüm bu testte 0,44–0,50 alıyordu, yani yazı turadan iyi değildi.
- **Cilalanmış metin** neredeyse ayırt edilemiyor. AI insan metninin kelimelerinin üçte ikisini koruyunca yüzeysel ölçüler yetmiyor.
- **Sınırlar:** n=30, tek bir AI modeli, öneri değil makale özeti. Ağırlıklar aynı veriye bakılarak seçildi (yarı yarıya bölünce 0,82 ve 0,84), bu yüzden sonuç iyimser. Daha büyük ve farklı modellerle bir test gerekiyor.

## Bilmen gerekenler

- **Bu bir dedektör atlatma aracı değil.** Hiçbir yeniden yazım bir AI dedektöründen geçmeyi garanti etmez; dedektörler insanın yazdığı metni de yanlış işaretleyebilir. `iz_skoru.py` de bir dedektörün sonucunu tahmin etmez, yalnızca katalogdaki izleri sayar.
- **Amaç metnin gerçekten iyi okunması.** Bunun ölçüsü dedektör değil, panelist.
- Kurumun AI kullanım beyanı istediği durumlarda (TÜBİTAK PBS'de bunun için ayrı bir alan var) beyanı yine yapman gerekir. Bu skill beyanın yerini tutmaz.

## Teşekkür

- Yapı ve yaklaşım, Siqi Chen'in [humanizer](https://github.com/blader/humanizer) skill'inden (MIT) ve Wikipedia'daki [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) rehberinden esinlenildi.
- Büşra Begçecanlı'nın [turkce-humanizer](https://github.com/bushrabeg/turkce-humanizer) projesinden (MIT) şu fikirler akademik metne uyarlanarak alındı: karşıtlık bağlacından önce virgül, "şudur:" açıklama kalıbı ve cümle içi iki nokta, vurgu dolgu sözcükleri, bitişik "ki" ve eğik çizgi ayıracı, "-mektedir" ve cümle monotonluğu için sayısal eşikler, uzun belgede paragrafları sınıflandırıp kullanıcıya seçenek sunma ve çıktıda temiz bölümleri de belirtme. Oradaki "mutlak yasak" yaklaşımı yerine burada eşik kullanılıyor, çünkü akademik metinde liste ve tanım için noktalı virgül ve iki noktanın meşru kullanımları var. Türkçe genel metinler (blog, deneme, gazetecilik, edebi) için o proje daha uygun.
- Ömer Faruk Ersin'in [turkce-akademik-humanizer](https://github.com/omerfarukersin/turkce-akademik-humanizer) projesinin (MIT) DergiPark bulguları katalogdaki `[V]`/`[K]` kanıt etiketlerinin, 32–38 numaralı kalıpların, koruma listesinin ve `iz_skoru.py` sözcük listesinin dayanağıdır. Metinler kendi cümlelerimizle özetlendi, TR kodları kaynağa geri dönebilmen için korundu. Bu çalışma sayesinde "Günümüzde" açılışı, "Bu," ile başlayan cümle ve uzun çizgi AI izi olmaktan çıkarıldı. Ayrıca bir yanlışımızı düzeltti: edilgeni etkene çevirmek Türkçede AI izini azaltmıyor, artırıyor. Makale özetleri için onların kalibre edilmiş linter'ı (`tr-akademik-lint`) bu skill'e iyi bir tamamlayıcıdır.
- [BatuhanOzdemir7/turkish-academic-humanizer](https://github.com/BatuhanOzdemir7/turkish-academic-humanizer) projesinden üç fikir alındı: anlamsal zincirleme, gereksiz "bir" ve sarkan "…, ki bu da" kuyruğu. Repoda lisans olmadığı için metin kopyalanmadı.
- [mamecodding/akademik-turkce-humanizer](https://github.com/mamecodding/akademik-turkce-humanizer) projesinin model eğitme deneyleri, serbest yeniden yazımda sayı ve atıfların kolayca kaybolduğunu gösteriyor. `kontrol.py`'ye eklenen uzunluk oranı kontrolü bu deneylerin kalite kapılarından esinlendi. Repoda lisans olmadığı için içerik kopyalanmadı.
- TÜBİTAK kuralları, uydurma yasağı, `.docx` akışı ve iki script bu repoya özgü.

## English

A Claude Code skill that removes AI-writing patterns from **Turkish academic text**, with a focus on TÜBİTAK grant proposals. It uses a Turkish pattern catalog, never invents citations or numbers (it inserts `[KAYNAK?]` markers instead), preserves figures and references, and ships with two stdlib-only scripts: a number/citation diff checker and a heuristic "AI trace score". It is not a detector-evasion tool and makes no promise about any detector's output.

## Lisans

[MIT](LICENSE)

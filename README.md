# tr-akademik-humanizer

Türkçe akademik metinlerdeki yapay zekâ izlerini temizleyen bir [Claude Code](https://claude.com/claude-code) skill'i. Asıl hedefi TÜBİTAK önerileri ve raporları (1001, 1002, 1501, 1505, 2209-A/B…), ama tez, makale, kalkınma ajansı başvurusu ve proje raporlarında da çalışır.

İngilizce humanizer'lar metne "kişilik" katmaya çalışır: fikir, mizah, birinci şahıs. Proje önerisinde bu ters teper. Bu skill başka bir ilkeyle çalışıyor: **süs değil, somutluk.** Genel cümle yerine projeye özgü ayrıntı, tekdüze "-mektedir" yerine çeşitli ritim, noktalı virgül zinciri yerine düz cümleler.

## Ne yapar

- 31 maddelik bir **Türkçe AI kalıp kataloğuyla** metni tarar ([`references/kaliplar.md`](references/kaliplar.md)). Katalogda "Günümüzde hızla gelişen…" açılışları, "önemli bir rol oynamaktadır", isim tamlaması zincirleri, boş "gerçekleştirilecektir"ler, çeviri kokusu, şişirilmiş yaygın etki, noktalı virgül zincirleri, "Birincisi… İkincisi…" sayımları, "…, ancak" virgülü ve "şudur:" kalıbı var.
- Uzun belgede önce her paragrafı ölçer, yüksek, orta ve temiz diye ayırır, sonra hangilerine dokunacağını sana sorar.
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

**AI iz skoru.** Metindeki ölçülebilir izleri 0–100 arası bir skora çevirir: noktalı virgül yoğunluğu, 40 kelimeyi aşan cümleler, cümle uzunluklarının tekdüzeliği, kalıp ifadeler ve sıra sözcükleri. Hangi ölçütten kaç puan geldiğini de gösterir:

```bash
python -I scripts/iz_skoru.py metin.txt
```

## Bilmen gerekenler

- **Bu bir dedektör atlatma aracı değil.** Hiçbir yeniden yazım bir AI dedektöründen geçmeyi garanti etmez; dedektörler insanın yazdığı metni de yanlış işaretleyebilir. `iz_skoru.py` de bir dedektörün sonucunu tahmin etmez, yalnızca katalogdaki izleri sayar.
- **Amaç metnin gerçekten iyi okunması.** Bunun ölçüsü dedektör değil, panelist.
- Kurumun AI kullanım beyanı istediği durumlarda (TÜBİTAK PBS'de bunun için ayrı bir alan var) beyanı yine yapman gerekir. Bu skill beyanın yerini tutmaz.

## Teşekkür

- Yapı ve yaklaşım, Siqi Chen'in [humanizer](https://github.com/blader/humanizer) skill'inden (MIT) ve Wikipedia'daki [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) rehberinden esinlenildi.
- Büşra Begçecanlı'nın [turkce-humanizer](https://github.com/bushrabeg/turkce-humanizer) projesinden (MIT) şu fikirler akademik metne uyarlanarak alındı: karşıtlık bağlacından önce virgül, "şudur:" açıklama kalıbı ve cümle içi iki nokta, vurgu dolgu sözcükleri, bitişik "ki" ve eğik çizgi ayıracı, "-mektedir" ve cümle monotonluğu için sayısal eşikler, uzun belgede paragrafları sınıflandırıp kullanıcıya seçenek sunma ve çıktıda temiz bölümleri de belirtme. Oradaki "mutlak yasak" yaklaşımı yerine burada eşik kullanılıyor, çünkü akademik metinde liste ve tanım için noktalı virgül ve iki noktanın meşru kullanımları var. Türkçe genel metinler (blog, deneme, gazetecilik, edebi) için o proje daha uygun.
- TÜBİTAK kuralları, uydurma yasağı, `.docx` akışı ve iki script bu repoya özgü.

## English

A Claude Code skill that removes AI-writing patterns from **Turkish academic text**, with a focus on TÜBİTAK grant proposals. It uses a Turkish pattern catalog, never invents citations or numbers (it inserts `[KAYNAK?]` markers instead), preserves figures and references, and ships with two stdlib-only scripts: a number/citation diff checker and a heuristic "AI trace score". It is not a detector-evasion tool and makes no promise about any detector's output.

## Lisans

[MIT](LICENSE)

# Journals.csv ingestion audit

Generated: 2026-05-29 20:10 UTC

Live audit of every **Active** journal in `Journals.csv`, using the same
validation rules as `src/rssagent/feeds.py` (`fetch_rss_feed`, URL normalization,
HTML-vs-feed detection, website fallback link patterns).

## How to re-run

```bash
pip install -e .
python scripts/audit_journals.py
```

Optional: `--output-json docs/journals-audit-raw.json` saves machine-readable results.

Rate limit: 2 seconds between journals (+ brief probes for suggested fixes).

## Executive summary

**Active journals audited:** 154

| Category | Count |
| --- | ---: |
| RSS OK | 77 |
| RSS fixable | 13 |
| RSS broken; website fallback OK | 1 |
| No RSS — website fallback OK | 2 |
| RSS broken / manual research | 34 |
| RSS broken; website fallback blocked | 10 |
| No RSS — website weak fallback | 12 |
| No RSS — website error | 5 |

### Headline

- **77** journals have working RSS feeds (50%).
- **13** have fixable RSS URLs (scheme, wrong landing page, publisher pattern).
- **3** can fall back to website scraping today (no/broken RSS but site OK).
- **44** need manual CSV research or are fully blocked.
- **0** high-confidence fixes verified live (see fixes CSV). Applying them would raise working RSS from **77 → ~77** (~50%).

### Projected impact after verified fixes

Applying verified rows in `docs/journals-audit-fixes.csv` recovers journals currently classified as **RSS fixable** (wrong landing page, missing scheme, wrong publisher). Remaining gaps: LWW/Ovid HTML wrapper URLs, truncated blog feeds (`...`), empty RSS with weak websites, and publisher 403/404 feeds (OUP, MDPI, Cambridge).

## Recommended actions (priority order)

1. **Apply verified fixes** in `docs/journals-audit-fixes.csv` (prepend https, publisher feed URLs).
2. **Fix truncated blog URLs** (rows ending in `...`) — restore full WordPress/blog feed paths.
3. **Replace HTML landing pages** with real feed endpoints (BMJ `/rss/current.xml`, physiology.org `showFeed`, etc.).
4. **Add OJS/Springer/T&F RSS** for journals with empty RSS but known publisher patterns.
5. **Manual research** for 403/paywall/broken feeds where website fallback also fails.

## Quick wins — verified RSS fixes

_None verified in this run._

## Quick wins — unverified suggestions (test before applying)

_None._

## RSS fixable (CSV corrections likely)

### ACSM Health & Fitness Journal
- **Category:** RSS fixable
- **RSS (CSV):** `https://journals.lww.com/acsm-healthfitness/_layouts/15/Ovid.Custom/rss/feed.aspx?FeedType=CurrentIssue`
- **Website:** `https://journals.lww.com/acsm-healthfitness/pages/default.aspx`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** no_articles — page loads but no article-like links matched

### American Journal of Physical Medicine & Rehabilitation
- **Category:** RSS fixable
- **RSS (CSV):** `https://journals.lww.com/ajpmr/_layouts/15/Ovid.Custom/rss/feed.aspx?FeedType=CurrentIssue`
- **Website:** `https://journals.lww.com/ajpmr/pages/default.aspx`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** no_articles — page loads but no article-like links matched

### Clinical Journal of Sports Medicine
- **Category:** RSS fixable
- **RSS (CSV):** `https://journals.lww.com/cjsportsmed/_layouts/15/Ovid.Custom/rss/feed.aspx?FeedType=CurrentIssue`
- **Website:** `https://journals.lww.com/cjsportsmed/pages/default.aspx`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** no_articles — page loads but no article-like links matched

### Current Sports Medicine Reports
- **Category:** RSS fixable
- **RSS (CSV):** `https://journals.lww.com/acsm-csmr/_layouts/15/Ovid.Custom/rss/feed.aspx?FeedType=CurrentIssue`
- **Website:** `https://journals.lww.com/acsm-csmr/pages/default.aspx`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** no_articles — page loads but no article-like links matched

### Exercise and Sport Sciences Reviews
- **Category:** RSS fixable
- **RSS (CSV):** `https://journals.lww.com/acsm-essr/_layouts/15/Ovid.Custom/rss/feed.aspx?FeedType=CurrentIssue`
- **Website:** `http://www.acsm-essr.com/`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** no_articles — page loads but no article-like links matched

### International Journal of Applied Exercise Physiology
- **Category:** RSS fixable
- **RSS (CSV):** `http://www.ijaep.com/index.php/IJAE/gateway/plugin/WebFeedGatewayPlugin/rss2`
- **Website:** `http://www.ijaep.com/`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** ok — found 12 article-like links

### Journal of Human Sport & Exercise
- **Category:** RSS fixable
- **RSS (CSV):** `https://www.jhse.ua.es/rss`
- **Website:** `https://www.jhse.ua.es/`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** ok — found 90 article-like links

### Journal of Sports Science and Medicine
- **Category:** RSS fixable
- **RSS (CSV):** `https://www.jssm.org/rss/jssm.xml`
- **Website:** `https://www.jssm.org/`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** no_articles — page loads but no article-like links matched

### Journal of Strength and Conditioning Research
- **Category:** RSS fixable
- **RSS (CSV):** `https://journals.lww.com/nsca-jscr/_layouts/15/Ovid.Custom/rss/feed.aspx?FeedType=CurrentIssue`
- **Website:** `https://journals.lww.com/nsca-jscr/`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** no_articles — page loads but no article-like links matched

### Nutrition Journal
- **Category:** RSS fixable
- **RSS (CSV):** `https://nutritionj.biomedcentral.com/articles/most-recent/rss.xml`
- **Website:** `https://nutritionj.biomedcentral.com/`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** ok — found 5 article-like links

### Nutrition and Metabolism
- **Category:** RSS fixable
- **RSS (CSV):** `https://nutritionandmetabolism.biomedcentral.com/articles/most-recent/rss.xml`
- **Website:** `https://nutritionandmetabolism.biomedcentral.com/`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** ok — found 5 article-like links

### Strength and Conditioning Journal
- **Category:** RSS fixable
- **RSS (CSV):** `https://journals.lww.com/nsca-scj/_layouts/15/Ovid.Custom/rss/feed.aspx?FeedType=CurrentIssue`
- **Website:** `https://journals.lww.com/nsca-scj/`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** no_articles — page loads but no article-like links matched

### The Open Sports Sciences Journal
- **Category:** RSS fixable
- **RSS (CSV):** `https://benthamopen.com/TOSSJ/rss/`
- **Website:** `https://benthamopen.com/TOSSJ/home/`
- **RSS detail:** response is HTML, not RSS/Atom (check CSV feed URL)
- **Website:** ok — found 6 article-like links


## No RSS — website fallback OK

### ACE Fitness Blog
- **Category:** No RSS — website weak fallback
- **RSS (CSV):** _(empty)_
- **Website:** `https://acefitness.org`
- **RSS detail:** empty RSS; website loads but scraper may find nothing
- **Website:** no_articles — page loads but no article-like links matched

### Exercise Immunology Review
- **Category:** No RSS — website weak fallback
- **RSS (CSV):** _(empty)_
- **Website:** `http://exerciseimmunology.com/`
- **RSS detail:** empty RSS; website loads but scraper may find nothing
- **Website:** no_articles — page loads but no article-like links matched

### General pubmed query
- **Category:** No RSS — website fallback OK
- **RSS (CSV):** _(empty)_
- **Website:** `https://pubmed.ncbi.nlm.nih.gov/`
- **RSS detail:** empty RSS; website fallback usable
- **Website:** ok — found 1 article-like links

### International Journal of Sports Science
- **Category:** No RSS — website weak fallback
- **RSS (CSV):** _(empty)_
- **Website:** `http://www.sapub.org/journal/aimsandscope.aspx?journalid=1111`
- **RSS detail:** empty RSS; website loads but scraper may find nothing
- **Website:** no_articles — page loads but no article-like links matched

### International Journal of Sports Sciences & Fitness
- **Category:** No RSS — website weak fallback
- **RSS (CSV):** _(empty)_
- **Website:** `http://www.ijssf.org/`
- **RSS detail:** empty RSS; website loads but scraper may find nothing
- **Website:** no_articles — page loads but no article-like links matched

### Journal of Exercise Physiology
- **Category:** No RSS — website weak fallback
- **RSS (CSV):** _(empty)_
- **Website:** `https://www.asep.org/asep/asep/JEPonline.html`
- **RSS detail:** empty RSS; website loads but scraper may find nothing
- **Website:** no_articles — page loads but no article-like links matched

### Journal of Exercise, Sports & Orthopedics
- **Category:** No RSS — website weak fallback
- **RSS (CSV):** _(empty)_
- **Website:** `https://symbiosisonlinepublishing.com/exercise-sports-orthopedics/`
- **RSS detail:** empty RSS; website loads but scraper may find nothing
- **Website:** no_articles — page loads but no article-like links matched

### Journal of Musculoskeletal and Neuronal Interactions
- **Category:** No RSS — website fallback OK
- **RSS (CSV):** _(empty)_
- **Website:** `http://www.ismni.org/jmni/`
- **RSS detail:** empty RSS; website fallback usable
- **Website:** ok — found 16 article-like links

### Journal of Sports Medicine & Doping Studies
- **Category:** No RSS — website weak fallback
- **RSS (CSV):** _(empty)_
- **Website:** `https://www.longdom.org/sports-medicine-doping-studies.html`
- **RSS detail:** empty RSS; website loads but scraper may find nothing
- **Website:** no_articles — page loads but no article-like links matched

### Medicine and Science in Sports and Exercise
- **Category:** No RSS — website weak fallback
- **RSS (CSV):** _(empty)_
- **Website:** `http://acsm-msse.org`
- **RSS detail:** empty RSS; website loads but scraper may find nothing
- **Website:** no_articles — page loads but no article-like links matched

### Montenegrin Journal of Sports Science and Medicine
- **Category:** No RSS — website weak fallback
- **RSS (CSV):** _(empty)_
- **Website:** `http://www.mjssm.me/`
- **RSS detail:** empty RSS; website loads but scraper may find nothing
- **Website:** no_articles — page loads but no article-like links matched

### Muscle, Ligaments and Tendons Journal
- **Category:** No RSS — website weak fallback
- **RSS (CSV):** _(empty)_
- **Website:** `https://www.mltj.online/`
- **RSS detail:** empty RSS; website loads but scraper may find nothing
- **Website:** no_articles — page loads but no article-like links matched

### RP Strength
- **Category:** No RSS — website weak fallback
- **RSS (CSV):** _(empty)_
- **Website:** `https://rpstrength.com`
- **RSS detail:** empty RSS; website loads but scraper may find nothing
- **Website:** no_articles — page loads but no article-like links matched

### Westside Barbell
- **Category:** No RSS — website weak fallback
- **RSS (CSV):** _(empty)_
- **Website:** `https://westside-barbell.com`
- **RSS detail:** empty RSS; website loads but scraper may find nothing
- **Website:** no_articles — page loads but no article-like links matched


## RSS broken — website fallback OK

### Isokinetics and Exercise Science
- **Category:** RSS broken; website fallback OK
- **RSS (CSV):** `https://content.iospress.com/journals/isokinetics-and-exercise-science/rss`
- **Website:** `https://www.iospress.com/catalog/journals/isokinetics-and-exercise-science`
- **RSS detail:** HTTP error: 403 Client Error: Forbidden for url: https://journals.sagepub.com/home/iso
- **Website:** ok — found 15 article-like links


## Manual research / blocked

### Advances in nutrition
- **Category:** RSS broken; website fallback blocked
- **RSS (CSV):** `https://academic.oup.com/rss/site_6142/3182.xml`
- **Website:** `https://academic.oup.com/advances`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://academic.oup.com/rss/site_6142/3182.xml
- **Website:** blocked — HTTP 403 Forbidden

### American Journal of Clinical Nutrition
- **Category:** RSS broken; website fallback blocked
- **RSS (CSV):** `https://academic.oup.com/rss/site_6141/3180.xml`
- **Website:** `https://academic.oup.com/ajcn`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://academic.oup.com/rss/site_6141/3180.xml
- **Website:** blocked — HTTP 403 Forbidden

### American Journal of Sports Science & Medicine
- **Category:** RSS broken / manual research
- **RSS (CSV):** `http://www.sciepub.com/journal/ajssm/rss`
- **Website:** `http://www.sciepub.com/journal/ajssm`
- **RSS detail:** HTTP error: HTTPSConnectionPool(host='www.sciepub.com', port=443): Read timed out. (read timeout=15.0)
- **Website:** no_articles — page loads but no article-like links matched

### Annual Review of Nutrition
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.annualreviews.org/action/showFeed?jc=nutr&type=etoc&feed=rss`
- **Website:** `https://www.annualreviews.org/journal/nutr`
- **RSS detail:** HTTP error: 403 Client Error: Forbidden for url: https://www.annualreviews.org/action/showFeed?jc=nutr&type=etoc&feed=rss
- **Website:** no_articles — page loads but no article-like links matched

### Asian Journal of Sports Medicine
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://sites.kowsarpub.com/asjsm/rss`
- **Website:** `https://sites.kowsarpub.com/asjsm/`
- **RSS detail:** HTTP error: HTTPSConnectionPool(host='sites.kowsarpub.com', port=443): Read timed out. (read timeout=15.0)
- **Website:** error — HTTP error: HTTPSConnectionPool(host='sites.kowsarpub.com', port=443): Read timed out. (read timeout=15.0)

### Biology of Sport
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.termedia.pl/Journal/Biology_of_Sport-78/rss`
- **Website:** `https://www.termedia.pl/Journal/Biology_of_Sport-78`
- **RSS detail:** HTTP error: 400 Client Error: Bad Request for url: https://www.termedia.pl/Journal/Biology_of_Sport-78/rss
- **Website:** no_articles — page loads but no article-like links matched

### British Journal of Nutrition
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.cambridge.org/core/rss/journal/british-journal-of-nutrition`
- **Website:** `https://www.cambridge.org/core/journals/british-journal-of-nutrition`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://www.cambridge.org/core/rss/journal/british-journal-of-nutrition
- **Website:** ok — found 9 article-like links

### Endocrinology & Metabolism
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.e-enm.org/rss.php`
- **Website:** `https://www.e-enm.org/`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://www.e-enm.org/rss.php
- **Website:** no_articles — page loads but no article-like links matched

### Frontiers in Movement Science and Sport Psychology
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.frontiersin.org/journals/movement-science-and-sport-psychology/rss`
- **Website:** `https://www.frontiersin.org/journals/movement-science-and-sport-psychology`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://www.frontiersin.org/journals/movement-science-and-sport-psychology/rss
- **Website:** broken — HTTP error: 404 Client Error: Not Found for url: https://www.frontiersin.org/journals/movement-science-and-sport-psychology

### International Journal of Applied Sports Sciences
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://ijass.org/index.php/ijass/gateway/plugin/WebFeedGatewayPlugin/rss2`
- **Website:** `https://ijass.org/`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://ijass.org/index.php/ijass/gateway/plugin/WebFeedGatewayPlugin/rss2
- **Website:** no_articles — page loads but no article-like links matched

### International Journal of Endocrinology & Metabolism
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://sites.kowsarpub.com/ijem/rss`
- **Website:** `https://sites.kowsarpub.com/ijem/`
- **RSS detail:** HTTP error: HTTPSConnectionPool(host='sites.kowsarpub.com', port=443): Read timed out. (read timeout=15.0)
- **Website:** error — HTTP error: HTTPSConnectionPool(host='sites.kowsarpub.com', port=443): Read timed out. (read timeout=15.0)

### International Journal of Environmental Research and Public Health
- **Category:** RSS broken; website fallback blocked
- **RSS (CSV):** `https://www.mdpi.com/rss/journal/ijerph`
- **Website:** `https://www.mdpi.com/journal/ijerph`
- **RSS detail:** HTTP error: 403 Client Error: Forbidden for url: https://www.mdpi.com/rss/journal/ijerph
- **Website:** blocked — HTTP 403 Forbidden

### International Journal of Kinesiology and Sports Science
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.journals.aiac.org.au/index.php/IJKSS/gateway/plugin/WebFeedGatewayPlugin/rss2`
- **Website:** `https://www.journals.aiac.org.au/index.php/IJKSS`
- **RSS detail:** HTTP error: HTTPSConnectionPool(host='www.journals.aiac.org.au', port=443): Max retries exceeded with url: /index.php/IJKSS/gateway/plugin/WebFeedGatewayPlugin/rss2 (Caused by NameResolutionError("HTTPSConnection(host='www.journals.aiac.org.au', port=443): Failed to resolve 'www.journals.aiac.org.au' ([Errno 8] nodename nor servname provided, or not known)"))
- **Website:** error — HTTP error: HTTPSConnectionPool(host='www.journals.aiac.org.au', port=443): Max retries exceeded with url: /index.php/IJKSS (Caused by NameResolutionError("HTTPSConnection(host='www.journals.aiac.org.au', port=443): Failed to resolve 'www.journals.aiac.org.au' ([Errno 8] nodename nor servname provided, or not known)"))

### International Journal of Sport & Health Science
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.jstage.jst.go.jp/AF03010SelectControl?action=rss&type=2&pub_code=ijshs&lang=en`
- **Website:** `https://www.jstage.jst.go.jp/browse/ijshs`
- **RSS detail:** HTTP error: 404 Client Error: 404 for url: https://www.jstage.jst.go.jp/AF03010SelectControl?action=rss&type=2&pub_code=ijshs&lang=en
- **Website:** ok — found 4 article-like links

### International Journal of Sport Nutrition and Exercise Metabolism
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://journals.humankinetics.com/action/showFeed?jc=ijsnem&type=etoc&feed=rss`
- **Website:** `https://journals.humankinetics.com/view/journals/ijsnem/ijsnem-overview.xml`
- **RSS detail:** HTTP error: 404 Client Error:  for url: https://journals.humankinetics.com/action/showFeed?jc=ijsnem&type=etoc&feed=rss
- **Website:** ok — found 1 article-like links

### International Journal of Sports Medicine
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.thieme-connect.com/products/ejournals/rss/10.1055/s-00000024`
- **Website:** `https://www.thieme.com/books-main/sports-medicine/product/2165-international-journal-of-sports-medicine`
- **RSS detail:** HTTP error: 404 Client Error: 404 for url: https://www.thieme-connect.com/products/ejournals/rss/10.1055/s-00000024
- **Website:** broken — HTTP error: 404 Client Error: Not Found for url: https://www.thieme.com/books-main/sports-medicine/product/2165-international-journal-of-sports-medicine

### International Journal of Sports Physiology and Performance
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://journals.humankinetics.com/action/showFeed?jc=ijspp&type=etoc&feed=rss`
- **Website:** `https://journals.humankinetics.com/view/journals/ijspp/ijspp-overview.xml`
- **RSS detail:** HTTP error: 404 Client Error:  for url: https://journals.humankinetics.com/action/showFeed?jc=ijspp&type=etoc&feed=rss
- **Website:** no_articles — page loads but no article-like links matched

### Journal for the Society of Neurosport
- **Category:** No RSS — website error
- **RSS (CSV):** _(empty)_
- **Website:** `https://neurosport.org/`
- **RSS detail:** empty RSS; website: error
- **Website:** error — HTTP error: HTTPSConnectionPool(host='neurosport.org', port=443): Max retries exceeded with url: / (Caused by NameResolutionError("HTTPSConnection(host='neurosport.org', port=443): Failed to resolve 'neurosport.org' ([Errno 8] nodename nor servname provided, or not known)"))

### Journal of Applied Biomechanics
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://journals.humankinetics.com/action/showFeed?jc=jab&type=etoc&feed=rss`
- **Website:** `https://journals.humankinetics.com/view/journals/jab/jab-overview.xml`
- **RSS detail:** HTTP error: 404 Client Error:  for url: https://journals.humankinetics.com/action/showFeed?jc=jab&type=etoc&feed=rss
- **Website:** no_articles — page loads but no article-like links matched

### Journal of Athletic Enhancement
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.scitechnol.com/athletic-enhancement-rss.xml`
- **Website:** `https://www.scitechnol.com/athletic-enhancement.php`
- **RSS detail:** HTTP error: HTTPSConnectionPool(host='www.scitechnol.com', port=443): Read timed out. (read timeout=15.0)
- **Website:** error — HTTP error: HTTPSConnectionPool(host='www.scitechnol.com', port=443): Read timed out. (read timeout=15.0)

### Journal of Athletic Training
- **Category:** RSS broken; website fallback blocked
- **RSS (CSV):** `https://meridian.allenpress.com/jat/rss/site_1000001/1000011.xml`
- **Website:** `https://meridian.allenpress.com/jat`
- **RSS detail:** HTTP error: 400 Client Error: Bad Request for url: https://jat.kglmeridian.com/
- **Website:** blocked — HTTP 403 Forbidden

### Journal of Australian Strength & Conditioning
- **Category:** No RSS — website error
- **RSS (CSV):** _(empty)_
- **Website:** `https://www.strengthandconditioning.org/jasc`
- **RSS detail:** empty RSS; website: broken
- **Website:** broken — HTTP error: 404 Client Error: Not Found for url: https://www.strengthandconditioning.org/jasc

### Journal of Experimental Biology
- **Category:** RSS broken; website fallback blocked
- **RSS (CSV):** `https://journals.biologists.com/jeb/rss/site_14/15.xml`
- **Website:** `https://journals.biologists.com/jeb`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://journals.biologists.com/jeb/rss/site_14/15.xml
- **Website:** blocked — HTTP 403 Forbidden

### Journal of Functional Morphology and Kinesiology
- **Category:** RSS broken; website fallback blocked
- **RSS (CSV):** `https://www.mdpi.com/rss/journal/jfmk`
- **Website:** `https://www.mdpi.com/journal/jfmk`
- **RSS detail:** HTTP error: 403 Client Error: Forbidden for url: https://www.mdpi.com/rss/journal/jfmk
- **Website:** blocked — HTTP 403 Forbidden

### Journal of Human Kinetics
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://sciendo.com/rss/journal/hukin`
- **Website:** `https://sciendo.com/journal/HUKIN`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://sciendo.com:443/2/rss/journal/hukin
- **Website:** broken — HTTP error: 404 Client Error: Not Found for url: https://reference-global.com:443/journal/HUKIN

### Journal of Motor Learning and Development
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://journals.humankinetics.com/action/showFeed?jc=jmld&type=etoc&feed=rss`
- **Website:** `https://journals.humankinetics.com/view/journals/jmld/jmld-overview.xml`
- **RSS detail:** HTTP error: 404 Client Error:  for url: https://journals.humankinetics.com/action/showFeed?jc=jmld&type=etoc&feed=rss
- **Website:** no_articles — page loads but no article-like links matched

### Journal of Musculoskeletal Research
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.worldscientific.com/action/showFeed?jc=jmsr&type=etoc&feed=rss`
- **Website:** `https://www.worldscientific.com/worldscinet/jmsr`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://www.worldscientific.com/action/showFeed?jc=jmsr&type=etoc&feed=rss
- **Website:** broken — HTTP error: 404 Client Error: Not Found for url: https://www.worldscientific.com/worldscinet/jmsr

### Journal of Nutrition
- **Category:** RSS broken; website fallback blocked
- **RSS (CSV):** `https://academic.oup.com/rss/site_6143/3184.xml`
- **Website:** `https://academic.oup.com/jn`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://academic.oup.com/rss/site_6143/3184.xml
- **Website:** blocked — HTTP 403 Forbidden

### Journal of Physical Activity and Health
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://journals.humankinetics.com/action/showFeed?jc=jpah&type=etoc&feed=rss`
- **Website:** `https://journals.humankinetics.com/view/journals/jpah/jpah-overview.xml`
- **RSS detail:** HTTP error: 404 Client Error:  for url: https://journals.humankinetics.com/action/showFeed?jc=jpah&type=etoc&feed=rss
- **Website:** no_articles — page loads but no article-like links matched

### Journal of Sport and Exercise Psychology
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://journals.humankinetics.com/action/showFeed?jc=jsep&type=etoc&feed=rss`
- **Website:** `https://journals.humankinetics.com/view/journals/jsep/jsep-overview.xml`
- **RSS detail:** HTTP error: 404 Client Error:  for url: https://journals.humankinetics.com/action/showFeed?jc=jsep&type=etoc&feed=rss
- **Website:** no_articles — page loads but no article-like links matched

### Journal of exercise rehabilitation
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.e-jer.org/rss.php`
- **Website:** `https://www.e-jer.org/`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://www.e-jer.org/rss.php
- **Website:** no_articles — page loads but no article-like links matched

### Journal of sport rehabilitation
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://journals.humankinetics.com/action/showFeed?jc=jsr&type=etoc&feed=rss`
- **Website:** `https://journals.humankinetics.com/view/journals/jsr/jsr-overview.xml`
- **RSS detail:** HTTP error: 404 Client Error:  for url: https://journals.humankinetics.com/action/showFeed?jc=jsr&type=etoc&feed=rss
- **Website:** no_articles — page loads but no article-like links matched

### Kinesiology
- **Category:** No RSS — website error
- **RSS (CSV):** _(empty)_
- **Website:** `https://hrcak.srce.hr/kinesiology`
- **RSS detail:** empty RSS; website: broken
- **Website:** broken — HTTP error: 404 Client Error: Not Found for url: https://hrcak.srce.hr/kinesiology

### Motor Control
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://journals.humankinetics.com/action/showFeed?jc=mc&type=etoc&feed=rss`
- **Website:** `https://journals.humankinetics.com/view/journals/mc/mc-overview.xml`
- **RSS detail:** HTTP error: 404 Client Error:  for url: https://journals.humankinetics.com/action/showFeed?jc=mc&type=etoc&feed=rss
- **Website:** no_articles — page loads but no article-like links matched

### Nutrients
- **Category:** RSS broken; website fallback blocked
- **RSS (CSV):** `https://www.mdpi.com/rss/journal/nutrients`
- **Website:** `https://www.mdpi.com/journal/nutrients`
- **RSS detail:** HTTP error: 403 Client Error: Forbidden for url: https://www.mdpi.com/rss/journal/nutrients
- **Website:** blocked — HTTP 403 Forbidden

### Nutrition Research Reviews
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.cambridge.org/core/rss/journal/nutrition-research-reviews`
- **Website:** `https://www.cambridge.org/core/journals/nutrition-research-reviews`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://www.cambridge.org/core/rss/journal/nutrition-research-reviews
- **Website:** ok — found 9 article-like links

### Nutrition Reviews
- **Category:** RSS broken; website fallback blocked
- **RSS (CSV):** `https://academic.oup.com/rss/site_5409/3120.xml`
- **Website:** `https://academic.oup.com/nutritionreviews`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://academic.oup.com/rss/site_5409/3120.xml
- **Website:** blocked — HTTP 403 Forbidden

### Open Access Journal of Sports Medicine
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.dovepress.com/cr_data/oai/dovepress_OAJSM.xml`
- **Website:** `https://www.dovepress.com/open-access-journal-of-sports-medicine-journal`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://www.dovepress.com/cr_data/oai/dovepress_OAJSM.xml
- **Website:** no_articles — page loads but no article-like links matched

### Pediatric Exercise Science
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://journals.humankinetics.com/action/showFeed?jc=pes&type=etoc&feed=rss`
- **Website:** `https://journals.humankinetics.com/view/journals/pes/pes-overview.xml`
- **RSS detail:** HTTP error: 404 Client Error:  for url: https://journals.humankinetics.com/action/showFeed?jc=pes&type=etoc&feed=rss
- **Website:** no_articles — page loads but no article-like links matched

### PeerJ Anatomy and Physiology
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://peerj.com/anatomy-and-physiology.rss`
- **Website:** `https://peerj.com/anatomy-and-physiology/`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://peerj.com/anatomy-and-physiology.rss/
- **Website:** broken — HTTP error: 404 Client Error: Not Found for url: https://peerj.com/anatomy-and-physiology/

### PeerJ Kinesiology
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://peerj.com/kinesiology.rss`
- **Website:** `https://peerj.com/kinesiology`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://peerj.com/kinesiology.rss/
- **Website:** broken — HTTP error: 404 Client Error: Not Found for url: https://peerj.com/kinesiology/

### Proceedings of the Nutrition Society
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.cambridge.org/core/rss/journal/proceedings-of-the-nutrition-society`
- **Website:** `https://www.cambridge.org/core/journals/proceedings-of-the-nutrition-society`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://www.cambridge.org/core/rss/journal/proceedings-of-the-nutrition-society
- **Website:** ok — found 9 article-like links

### Revista Brasileira de Ciências do Esporte
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.scielo.br/rss.php?pid=0101-3289&lang=en`
- **Website:** `https://www.scielo.br/j/rbce/`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://www.scielo.br/j/rss.php/
- **Website:** no_articles — page loads but no article-like links matched

### Revista Brasileira de Medicina do Esporte
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.scielo.br/rss.php?pid=1517-8692&lang=en`
- **Website:** `https://www.scielo.br/j/rbme/`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://www.scielo.br/j/rss.php/
- **Website:** no_articles — page loads but no article-like links matched

### Sport Performance & Science Reports
- **Category:** No RSS — website error
- **RSS (CSV):** _(empty)_
- **Website:** `https://sportperformancescience.com/`
- **RSS detail:** empty RSS; website: error
- **Website:** error — HTTP error: HTTPSConnectionPool(host='sportperformancescience.com', port=443): Max retries exceeded with url: / (Caused by NameResolutionError("HTTPSConnection(host='sportperformancescience.com', port=443): Failed to resolve 'sportperformancescience.com' ([Errno 8] nodename nor servname provided, or not known)"))

### Sport Psychologist
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://journals.humankinetics.com/action/showFeed?jc=tsp&type=etoc&feed=rss`
- **Website:** `https://journals.humankinetics.com/view/journals/tsp/tsp-overview.xml`
- **RSS detail:** HTTP error: 404 Client Error:  for url: https://journals.humankinetics.com/action/showFeed?jc=tsp&type=etoc&feed=rss
- **Website:** no_articles — page loads but no article-like links matched

### Sport Scientific and Practical Aspects
- **Category:** No RSS — website error
- **RSS (CSV):** _(empty)_
- **Website:** `http://sportspa.com.ba/`
- **RSS detail:** empty RSS; website: error
- **Website:** error — HTTP error: HTTPConnectionPool(host='sportspa.com.ba', port=80): Max retries exceeded with url: / (Caused by NameResolutionError("HTTPConnection(host='sportspa.com.ba', port=80): Failed to resolve 'sportspa.com.ba' ([Errno 8] nodename nor servname provided, or not known)"))

### Sports – Open Access Journal
- **Category:** RSS broken; website fallback blocked
- **RSS (CSV):** `https://www.mdpi.com/rss/journal/sports`
- **Website:** `https://www.mdpi.com/journal/sports`
- **RSS detail:** HTTP error: 403 Client Error: Forbidden for url: https://www.mdpi.com/rss/journal/sports
- **Website:** blocked — HTTP 403 Forbidden

### THE JOURNAL OF SPORTS MEDICINE AND PHYSICAL FITNESS
- **Category:** RSS broken / manual research
- **RSS (CSV):** `https://www.minervamedica.it/en/journals/sports-med-physical-fitness/rss.xml`
- **Website:** `https://www.minervamedica.it/en/journals/sports-med-physical-fitness/`
- **RSS detail:** HTTP error: 404 Client Error: Not Found for url: https://www.minervamedica.it/en/journals/sports-med-physical-fitness/rss.xml
- **Website:** no_articles — page loads but no article-like links matched


## RSS OK (no action needed)

77 journals. See raw JSON for full list if needed.

- **Acta Physiologica** — 2 entries — `https://onlinelibrary.wiley.com/feed/17481716/most-recent`
- **American Journal of Physiology. Regulatory, Integrative and Comparative Physiology** — 22 entries — `https://journals.physiology.org/action/showFeed?jc=ajpregu&type=etoc&feed=rss`
- **American Journal of Sports Medicine** — 9 entries — `https://journals.sagepub.com/action/showFeed?jc=ajsa&type=etoc&feed=rss`
- **Amino Acids** — 20 entries — `https://link.springer.com/search.rss?facet-journal-id=726`
- **Applied Physiology, Nutrition and Metabolism** — 60 entries — `https://cdnsciencepub.com/action/showFeed?jc=apnm&type=etoc&feed=rss`
- **BarBend** — 10 entries — `https://barbend.com/feed.xml`
- **Biomechanics and Modeling in Mechanobiology** — 20 entries — `https://link.springer.com/search.rss?facet-journal-id=10237`
- **British Journal of Sports Medicine** — 14 entries — `https://bjsm.bmj.com/rss/current.xml`
- **Cell Metabolism** — 29 entries — `https://www.cell.com/cell-metabolism/inpress.rss`
- **Clinical Biomechanics** — 70 entries — `https://rss.sciencedirect.com/publication/science/02680033`
- **Clinical Nutrition** — 59 entries — `https://rss.sciencedirect.com/publication/science/02615614`
- **Clinical Physiology and Functional Imaging** — 12 entries — `https://onlinelibrary.wiley.com/feed/1475097X/most-recent`
- **Clinics in Sports Medicine** — 19 entries — `https://www.sportsmed.theclinics.com/inpress.rss`
- **Comprehensive Physiology** — 31 entries — `https://onlinelibrary.wiley.com/feed/20404603/most-recent`
- **European Journal of Applied Physiology** — 20 entries — `https://link.springer.com/search.rss?facet-journal-id=421`
- **European Journal of Clinical Nutrition** — 8 entries — `https://www.nature.com/ejcn.rss`
- **European Journal of Nutrition** — 20 entries — `https://link.springer.com/search.rss?facet-journal-id=394`
- **European Journal of Physiology** — 20 entries — `https://link.springer.com/search.rss?facet-journal-id=424`
- **European Journal of Sport Science** — 17 entries — `https://www.tandfonline.com/action/showFeed?jc=tejs20&type=etoc&feed=rss`
- **Experimental Gerontology** — 32 entries — `https://rss.sciencedirect.com/publication/science/05315565`
- **Experimental Physiology** — 91 entries — `https://physoc.onlinelibrary.wiley.com/feed/1469445X/most-recent`
- **FASEB** — 10 entries — `https://faseb.onlinelibrary.wiley.com/feed/15306860/most-recent`
- **Frontiers** — 20 entries — `https://www.frontiersin.org/journals/science/rss`
- **Frontiers in Sports and Active Living** — 20 entries — `https://www.frontiersin.org/journals/sports-and-active-living/rss`
- **Human Movement Science** — 24 entries — `https://rss.sciencedirect.com/publication/science/01679457`
- **International Journal of Performance Analysis in Sport** — 94 entries — `https://www.tandfonline.com/action/showFeed?jc=rpan20&type=etoc&feed=rss`
- **International Journal of Sports Science & Coaching** — 326 entries — `https://journals.sagepub.com/action/showFeed?jc=spoa&type=etoc&feed=rss`
- **International Review of Sport and Exercise Psychology** — 46 entries — `https://www.tandfonline.com/action/showFeed?jc=rirs20&type=etoc&feed=rss`
- **JISSN** — 45 entries — `https://www.tandfonline.com/action/showFeed?jc=rssn20&type=etoc&feed=rss`
- **Journal of Anatomy** — 71 entries — `https://onlinelibrary.wiley.com/feed/14697580/most-recent`
- **Journal of Applied Physiology** — 33 entries — `https://journals.physiology.org/action/showFeed?jc=jappl&type=etoc&feed=rss`
- **Journal of Biomechanics** — 57 entries — `https://rss.sciencedirect.com/publication/science/00219290`
- **Journal of Bodywork and Movement Therapies** — 97 entries — `https://rss.sciencedirect.com/publication/science/13608592`
- **Journal of Electromyography and Kinesiology** — 35 entries — `https://rss.sciencedirect.com/publication/science/10506411`
- **Journal of Exercise Science & Fitness** — 26 entries — `https://rss.sciencedirect.com/publication/science/1728869X`
- **Journal of Motor Behavior** — 23 entries — `https://www.tandfonline.com/action/showFeed?jc=vjmb20&type=etoc&feed=rss`
- **Journal of Muscle Research and Cell Motility** — 20 entries — `https://link.springer.com/search.rss?facet-journal-id=10974`
- **Journal of Neurophysiology** — 25 entries — `https://journals.physiology.org/action/showFeed?jc=jn&type=etoc&feed=rss`
- **Journal of Physiology** — 106 entries — `https://physoc.onlinelibrary.wiley.com/feed/14697793/most-recent`
- **Journal of Science and Medicine in Sport** — 80 entries — `https://www.jsams.org/inpress.rss`
- **Journal of Sport & Health Science** — 100 entries — `https://rss.sciencedirect.com/publication/science/20952546`
- **Journal of Sports Sciences** — 65 entries — `https://www.tandfonline.com/action/showFeed?jc=rjsp20&type=etoc&feed=rss`
- **Journal of dietary supplements** — 15 entries — `https://www.tandfonline.com/action/showFeed?jc=ijds20&type=etoc&feed=rss`
- **Journal of the Academy of Nutrition and Dietetics** — 24 entries — `https://www.jandonline.org/inpress.rss`
- **Juggernaut** — 10 entries — `https://www.jtsstrength.com/feed/`
- **Kath Eats** — 3 entries — `https://katheats.com/feed`
- **Legion Athletics** — 10 entries — `https://legionathletics.com/blog/feed`
- **Metabolism, Clinical & Experimental** — 10 entries — `https://www.metabolismjournal.com/inpress.rss`
- **Muscle & Nerve** — 90 entries — `https://onlinelibrary.wiley.com/feed/10974598/most-recent`
- **NutritionFacts.org** — 30 entries — `https://nutritionfacts.org/feed`
- **OriGym Blog** — 10 entries — `https://origym.co.uk/feed`
- **PLOSOne** — 30 entries — `https://journals.plos.org/plosone/feed/atom`
- **PNAS Physiology** — 92 entries — `https://www.pnas.org/action/showFeed?type=etoc&feed=rss&jc=pnas`
- **Perceptual and Motor Skills** — 9 entries — `https://journals.sagepub.com/action/showFeed?jc=pmsa&type=etoc&feed=rss`
- **Physical Therapy in Sport** — 24 entries — `https://rss.sciencedirect.com/publication/science/1466853X`
- **Physiological Reports** — 5 entries — `https://physoc.onlinelibrary.wiley.com/feed/2051817X/most-recent`
- **Physiology & Behavior** — 37 entries — `https://rss.sciencedirect.com/publication/science/00319384`
- **Precision Nutrition** — 10 entries — `https://www.precisionnutrition.com/blog/feed`
- **Psychology of Sport and Exercise** — 67 entries — `https://rss.sciencedirect.com/publication/science/14690292`
- **Real Mom Nutrition** — 12 entries — `https://realmomnutrition.com/feed`
- **Research Quarterly for Exercise and Sport** — 59 entries — `https://www.tandfonline.com/action/showFeed?jc=urqe20&type=etoc&feed=rss`
- **Research in Sports Medicine** — 30 entries — `https://www.tandfonline.com/action/showFeed?jc=gspm20&type=etoc&feed=rss`
- **Scandinavian Journal of Medicine and Science in Sports** — 4 entries — `https://onlinelibrary.wiley.com/feed/16000838/most-recent`
- **Science & Sports** — 47 entries — `https://rss.sciencedirect.com/publication/science/07651597`
- **South African Journal of Sports Medicine** — 30 entries — `https://journals.assaf.org.za/index.php/sajsm/gateway/plugin/WebFeedGatewayPlugin/rss2`
- **Sport Sciences for Health** — 20 entries — `https://link.springer.com/search.rss?facet-journal-id=11332`
- **Sports Biomechanics** — 76 entries — `https://www.tandfonline.com/action/showFeed?jc=rspb20&type=etoc&feed=rss`
- **Sports Medicine** — 20 entries — `https://link.springer.com/search.rss?facet-journal-id=40279`
- **Squat University** — 10 entries — `https://squatuniversity.com/feed`
- **Starting Strength** — 100 entries — `https://startingstrength.com/rss.rss`
- **StrongFirst** — 23 entries — `https://strongfirst.com/blog/feed`
- **The International Journal of Biochemistry & Cell Biology** — 25 entries — `https://rss.sciencedirect.com/publication/science/13572725`
- **The PTDC** — 100 entries — `https://theptdc.com/feed`
- **Train Heroic** — 10 entries — `https://trainheroic.com/feed`
- **TrainFitness** — 10 entries — `https://train.fitness/feed`
- **european Journal of translational myology** — 30 entries — `https://www.pagepressjournals.org/index.php/bam/gateway/plugin/WebFeedGatewayPlugin/rss2`
- **journal of science in sport and exercise** — 20 entries — `https://link.springer.com/search.rss?facet-journal-id=42978`

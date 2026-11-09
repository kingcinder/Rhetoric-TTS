# Market and Launch Strategy — Rhetoric 1.5.0

- **Assessment date:** 2026-11-08
- **Branch:** `release/1.5.0-final`
- **Status:** Pricing and go-to-market recommendation for owner decision.
  This document does not authorize distribution. Paid launch remains gated
  by `docs/SOFT_LAUNCH.md` / `scripts/soft_launch.py --check` (currently one
  blocker — the draft EULA — and one warning — LGPL notice/source
  obligations). Everything in the marketing plan except taking money can be
  prepared while that gate is closed.
- **Budget constraint:** $0. Every tactic below costs time only. Anything
  that secretly costs money is flagged in §7 with its free alternative.

All prices are USD, gathered 2026-11-08 from the sources cited inline and
listed in §9. Where sources disagreed or a vendor gates its pricing page,
the figure is labeled **unverified at primary source** and given as a range.
Prices change; re-check the cited page before quoting any figure in public
copy.

---

## 1. Market data (current, sourced)

### 1.1 Cloud TTS subscriptions — the meter never stops

| Product | Plan | Price | Notes |
|---|---|---|---|
| ElevenLabs | Starter | $6/mo ($5 annual-equiv.) | 30k credits/mo; commercial license starts here |
| ElevenLabs | Creator | **$22/mo** ($18.33 annual-equiv., $220/yr) | 121k credits/mo ≈ 2 hrs of speech; professional voice cloning |
| ElevenLabs | Pro | **$99/mo** ($82.50 annual-equiv., $990/yr) | 600k credits/mo ≈ 10 hrs; 44.1 kHz API output |
| Murf | Creator | $19/mo billed annually ($228/yr); $29 monthly | 24 hrs of generation **per year**; voice cloning is Enterprise-only |
| Murf | Business | $66/mo billed annually ($792/yr); $99 monthly | 96 hrs/yr |
| LOVO (Genny) | Basic/Pro | ~$24/mo **(unverified at primary source)** | Pricing page renders no figures without JS/login; third parties range $24–$48 for Pro, Pro+ ~$75/mo |
| Typecast | Basic / Pro | ~$5–$8.99 / ~$29–$32.99 per mo **(sources conflict)** | Two pricing models appear across 2026 sources; download-minute caps on older model |
| Resemble AI | Flex | Pay-as-you-go: ~$0.0005/sec TTS + $2/mo per Rapid clone, $5/mo per Pro clone | Resemble has pivoted to detection/enterprise (Team $280–$350/mo, Business $800–$1,000/mo). No creator studio tier remains the story |

ElevenLabs figures are consistent across at least five independent October
2026 price checks of the vendor pricing page (see §9). The subscription
cluster for a working creator is therefore **$19–$99/mo, i.e. $220–$1,188
per year, every year**, with generation allowances that expire monthly.

### 1.2 The cautionary tale: Play.ht is gone

Play.ht / PlayAI was acquired by Meta in July 2025 and **the service shut
down on December 31, 2025**. Its last archived pricing (Creator $31.20/mo
annual-equiv.; "Unlimited" $49–$99/mo with a 2.5M-character fair-use cap)
is now unpurchasable. Murf courted displaced Play.ht users with a free
6-month migration offer. Two strategic consequences:

1. There is a live pool of displaced, paying TTS customers actively looking
   for a new home right now.
2. "Your cloud TTS can be shut down, acquired, or repriced; software on
   your own disk cannot" is no longer a hypothetical pitch. It happened,
   to a named competitor, within the last year.

### 1.3 Local / one-time competitors — the shelf Rhetoric sits on

| Product | Price | Local? | The catch |
|---|---|---|---|
| VoiceStudio (formerly OmniVoice Studio) | **Free**, open source (app AGPL-3.0), active beta (v0.5.7, 2026-10-26) | Yes | Default engine (OmniVoice) weights are **CC-BY-NC — no commercial use**; broad 16-engine studio, no two-speaker-dialogue-first workflow, no paid support, beta stability |
| FineVoice (FineShare) | Perpetual license **$49.99** via deal channels (StackSocial listing in stock 2026-11-08; list price reported up to ~$149.99) | **No** — AI processing requires an internet connection | "Lifetime" of a cloud-dependent product; character/hour packages are one-time pools that do not reset |
| Speechelo | $47 one-time (third-party reports) | No (cloud) | Older-generation voice quality; upsell funnel |
| Raw Chatterbox engine | Free, MIT license (Resemble AI) | Yes | A Python library, not a product: no dialogue workflow, no studio UI, no installer, no support. Rhetoric's own engine — see §6.1 |

The 2026-09-11 finding still holds in refreshed form: **paid + fully local
+ voice cloning + commercially clean licensing remains nearly empty.**
VoiceStudio is free but its default voices cannot legally be sold;
FineVoice is one-time but phones home. Rhetoric's whitespace is the
intersection: paid, local, offline, commercially licensed output,
dialogue-first.

### 1.4 What a sale actually nets (merchant-of-record math)

At a $0 budget the storefront must have no monthly fee and must handle
sales tax/VAT — that rules out plain Stripe (cheapest headline fee, but
the seller becomes the tax collector worldwide; the hidden cost is
compliance risk and time). Merchant-of-record options:

| Channel | Fee structure | Net on $39 | Net on $49 | Notes |
|---|---|---|---|---|
| Lemon Squeezy | 5% + $0.50, all-in (processing + tax remittance included), no monthly fee | **$36.55** | **$46.05** | Also generates license keys natively — maps directly onto Rhetoric's serial model. Caveat: owner Stripe is steering MoR sellers toward Stripe Managed Payments (3.5% on top of processing); monitor, don't block on it |
| Gumroad (direct link) | 10% + $0.50 + Stripe 2.9% + $0.30 | $33.17 | $41.88 | Merchant of record for tax since Jan 2025 |
| Gumroad Discover | 30% flat, processing included | $27.30 | $34.30 | Only worth it for buyers Gumroad itself finds; never drive owned traffic there |
| Stripe direct | 2.9% + $0.30 | $37.57 | $47.58 | Highest net, but **you** owe VAT/sales-tax compliance in every buyer's jurisdiction — not a $0-safe default |

**Recommendation: Lemon Squeezy as the primary store**, Gumroad as a
secondary listing for Discover reach later. Difference at $39 is ~$3.38
per sale in Rhetoric's favor vs Gumroad direct.

---

## 2. Launch price recommendation

### 2.1 The recommendation

- **List price: $49** one-time.
- **Early-adopter price: $39** one-time for the first 500 licenses (or
  until the volume trigger in §2.3 fires, whichever comes first) —
  this is Dyther's 2026-09-11 anchor, kept, but positioned as a launch
  price under a $49 list instead of as the permanent price.
- **$59 step:** when the volume trigger fires (§2.3), list rises to $59
  and the early-adopter tier is already closed.

### 2.2 Why the data supports it

Cost-of-alternative math (the only comparison that matters to a buyer):

- One year of ElevenLabs Creator on monthly billing: **$264**. On annual
  billing: **$220**. Rhetoric at $39 pays for itself in **under two
  months** of Creator; at $49 list, in about 2.2 months. Every month
  after that, the buyer is $22/mo ahead — forever, because the Rhetoric
  license does not expire and covers the current major version.
- One year of ElevenLabs Pro: **$990–$1,188**. Rhetoric at $49 is roughly
  **two weeks** of Pro.
- One 10-hour audiobook is ~550k characters — about **five months** of
  ElevenLabs Creator's entire monthly allowance. A single book project
  forces a Creator subscriber into overage or a Pro upgrade; on Rhetoric
  it is a non-event because there is no meter.
- Murf Creator ($228/yr) does not include voice cloning at any
  self-serve tier; Rhetoric's voice building is in the box at $39–$49,
  once.
- One-time anchors agree: FineVoice perpetual sells at $49.99 and
  Speechelo at $47, both cloud-dependent or older tech. A $49 list for a
  fully local product is at market, not above it; $39 early-adopter is a
  genuine, defensible discount rather than a fake strikethrough.

### 2.3 The $39 → $59 trigger (Dyther's rule, made measurable)

Dyther's 2026-09-11 rule: raise by $20 if sales reach hundreds per month.
Operationalized:

1. Early-adopter $39 ends at **500 total licenses sold** *or* **100+
   sales in each of two consecutive months**, whichever first → price
   becomes the $49 list.
2. List rises $49 → $59 when sales sustain **300+ per month for two
   consecutive months** (i.e., "hundreds per month" demonstrated, not
   spiked by a single launch day).
3. Existing licensees are never re-charged for the current major
   version (per the product model); the price steps apply to new buyers
   only. A future major version is the legitimate second revenue event.

### 2.4 Sensitivity — what each price says

| Price | Positioning effect |
|---|---|
| **$29** | Signals "cheap utility," invites feature-by-feature comparison against free VoiceStudio, and anchors expectations so low that doubling later reads as a betrayal. Net $27.05 on Lemon Squeezy. Use **only** as a scoped promo code (e.g., Product Hunt launch day), never as list. |
| **$39** | The impulse-buy ceiling for creator tools; the payback math (<2 months of ElevenLabs Creator) is irresistible at this number. Correct as the early-adopter price; leaving it as permanent list donates $10/sale of demonstrated willingness-to-pay (FineVoice gets $49.99 for less). |
| **$49** | Matches the one-time competitor anchors, reads as "professional tool," still a rounding error against one year of any cloud subscription. Correct list price. |
| **$59** | Premium against every one-time anchor. Justified after social proof (reviews, testimonials, volume) exists — which is exactly Dyther's trigger. Launching here cold, with zero reviews, suppresses the first cohort that generates the proof. Correct step-3 price. |

---

## 3. Positioning (one paragraph, for reuse in all copy)

Rhetoric renders two-speaker dialogue — audiobook scenes, podcast
banter, game lines, narrator-plus-host explainers — into FLAC on your own
machine, with voices you build yourself. No subscription, no character
meter, no upload, no cloud that can be acquired and shut down. One
payment, your disk, your voices, output you can sell. (The underlying
Chatterbox engine was preferred over ElevenLabs by 63.75% of listeners in
a Podonos blind test — commissioned by Resemble AI, so cite it as a
vendor-commissioned result, never as neutral science.)

---

## 4. The $0 marketing strategy

Principle: at $0, distribution is borrowed — other people's audiences
(communities, directories, search results for dead/expensive competitors)
and owned assets built once and reused (demos, comparison pages, the
GitHub repo itself).

### 4.1 Owned channels

1. **GitHub repo as storefront.** The README is the landing page most
   buyers will see first. Top of README: what it does in one line, a
   playable demo link, the cost-comparison table from §1.1/§1.4
   condensed, "one-time $49 — no subscription" and the purchase link.
   Use GitHub Releases for distribution artifacts; keep repo topics
   accurate (`text-to-speech`, `voice-cloning`, `audiobooks`,
   `offline`, `linux`) for GitHub search.
2. **GitHub Pages site (free on the public repo).** Three comparison
   pages targeting existing search demand: *Rhetoric vs ElevenLabs*,
   *Rhetoric vs VoiceStudio*, *Play.ht alternatives*. Use the
   `*.github.io` subdomain — a custom domain is a flagged cost (§7).
3. **Demo library as the sales force.** There is no trial edition (by
   product design), so demos carry the entire evaluation burden. Five
   canonical scenes, each shipped as audio + a captioned short video
   (made with Rhetoric itself plus free tools — OBS/ffmpeg already on
   the production machine):
   - two-character audiobook scene (the flagship);
   - podcast co-host banter;
   - game NPC dialogue exchange;
   - narrator + host explainer (the Seismic Daily format);
   - same scene rendered by a cloud subscription vs Rhetoric (A/B).
4. **Seismic Daily crossover (honest scope).** Dyther's YouTube Shorts
   channel is an earthquake audience, not a TTS-buyer audience — its
   value is (a) proof-by-existence: a channel voiced by a local
   pipeline, published daily; (b) a community-post and pinned-comment
   announcement at launch; (c) one Short showing how a day's narration
   is made. Do not build the plan on this audience converting; treat
   anything it sends as a bonus.
5. **Waitlist capture.** Lemon Squeezy product page (pre-launch) or a
   free-tier email tool; the link goes in the README, Pages site, and
   every community bio. Verify the free tier's current subscriber cap
   at signup — caps on free tiers change.

### 4.2 Earned / community channels

**Reddit** (participate first, link second; several of these subs ban
drive-by promotion — read each sub's self-promotion rule before posting):

- Audiobook money audience: r/audiobooks, r/ACX, r/selfpublish
  (indie authors are the buyers; narrators are the channel's other
  half — a narrator who can offer AI-assisted drafts is a repeat
  recommender).
- Creators: r/VoiceActing, r/podcasting, r/NewTubers, r/youtubers.
- Local/privacy audience: r/selfhosted, r/LocalLLaMA, r/opensource.
- Launch boards: r/SideProject.
- Games: r/IndieDev / r/gamedev classifieds-adjacent threads for the
  dialogue angle.

**Launch platforms (all free):**

- **Product Hunt** — genuinely free; no paid launch tier exists.
  Rules that shape the plan: personal account at least **one week old**
  (create it in step 1 of §5, not launch week); self-hunting is
  encouraged; asking for upvotes is against the rules (ask for
  feedback); ads cost $5,000+ and are banned during your own launch, so
  organic is the only route anyway; only ~10% of launches get featured
  now, so treat it as one spike among several, not the plan. Ship the
  $29 promo code here (§2.4).
- **Hacker News — Show HN.** Angle: local-first, the Play.ht shutdown,
  one-time pricing as an anti-subscription statement, technical
  packaging story. Expect — and answer well — the "Chatterbox is free
  and MIT, why pay?" question (§6.1).
- **AlternativeTo** — list Rhetoric as an alternative to ElevenLabs,
  Murf, LOVO, VoiceStudio, and above all **Play.ht**: the dead
  product's page is where displaced users land.
- **SaaSHub** and similar free directories — same listing copy, an hour
  of form-filling, permanent search presence.

**Communities (free to join, slow to earn):**

- Discord servers for TTS/AI-voice, indie authors, and audiobook
  production; Facebook groups for indie-author audiobook production
  (where that buyer demographic actually congregates). Join, answer
  questions for weeks, post the launch once, in the promo-allowed
  channel, when it exists.
- **Play.ht refugee thread-watching:** every "Play.ht shut down, what
  now?" thread on Reddit and AlternativeTo is a warm lead. Answer
  helpfully, disclose authorship, mention Rhetoric once. Murf spent a
  6-month free offer on these users; Rhetoric's answer is permanence.

### 4.3 Content engine (one asset, five surfaces)

Each demo scene is rendered once, then cut into: a YouTube Short, a
Reddit post (in the matching sub), a Pages-site embed, a Product Hunt
gallery item, and a GitHub release note. Recurring post formats:

- **Cost-math posts:** "One audiobook = five months of ElevenLabs
  Creator credits" (§2.2). Concrete, checkable, shareable.
- **Permanence posts:** "Play.ht is gone. Your Rhetoric install cannot
  be." The shutdown essay is the launch announcement's backbone.
- **Craft posts:** how a two-speaker scene is staged, voice-building
  walkthroughs — these sell the studio angle competitors don't have.
- **Build-in-public:** GitHub Discussions changelog notes per release;
  each release is a new excuse to post everywhere above.

### 4.4 Metrics that matter

- Waitlist signups and store-page visits → sales conversion.
- Sales/week and net revenue after fees (target the §2.3 triggers).
- Refunds/chargebacks and support-hours per sale (a solo operation
  dies of support load before it dies of low traffic; the no-refund
  policy makes dispute rate the number to watch).
- Demo plays → store click-through (which scene sells).
- GitHub stars/issues as a free proxy for discovery and support load.

---

## 5. Launch sequence (dependency order, not calendar)

1. **Accounts first (clocks are running):** create the Product Hunt
   personal account (starts the one-week minimum-age clock), the Lemon
   Squeezy store, and the waitlist. Nothing here needs the release gate.
2. **Store plumbing tested:** Lemon Squeezy product configured ($49 list,
   license keys on), a test-mode purchase completes, and the issued key
   activates Rhetoric offline. A store that fails on launch day is the
   one unforced error this plan can fully prevent.
3. **Assets built:** the five demo scenes (§4.1.3), README storefront
   rewrite, Pages comparison pages live.
4. **Listings submitted:** AlternativeTo and SaaSHub (review lag is
   theirs, so submit before announcing anywhere).
5. **Community warm-up:** genuine participation in the §4.2 subreddits
   and Discords; the Play.ht essay posted to GitHub Discussions and the
   Seismic Daily community tab; waitlist announced to owned audiences.
6. **Release gate check:** `scripts/soft_launch.py --check` must clear
   (EULA finalized + counsel lane, LGPL obligations documented) before
   any sale. Steps 1–5 proceed in parallel; this step gates only step 7.
7. **Launch stack:** early-adopter $39 goes live → Product Hunt launch
   (midweek, 12:01 AM Pacific, $29 PH-day promo code) → Show HN two to
   three days later, recycling launch-day questions and testimonials.
8. **Proof loop:** testimonials and first reviews into the README;
   weekly demo drop; monthly cost-math post; every software release is
   a news beat across the same channels.
9. **Price-step watch:** when a §2.3 trigger fires, execute the price
   change and announce it *before* it takes effect — a announced future
   increase is itself a (free, honest) sales event.

---

## 6. Objections, answered before they're asked

### 6.1 "The engine is free and MIT-licensed. Why pay?"

True, and the FAQ should say so proudly. What the $39–$49 buys is the
product around the engine: the two-speaker dialogue workflow, the voice-building studio, a tested installer with pinned dependencies, offline
serial activation, packaged updates for the major version, and a human
who answers issues. This is the standard open-core-adjacent bargain
(people pay for exactly this packaging across the local-AI ecosystem),
and hiding the engine's license would detonate trust on Hacker News —
the channel where this product most needs credibility. Rhetoric's own
output is commercially clean because the engine is MIT — unlike
VoiceStudio's default CC-BY-NC voices, which cannot be sold at any
price. Turn the objection into the pitch.

### 6.2 "No trial?"

By design (the product model has no trial edition). The mitigation is
evidentiary: extensive demos, the full manual and system requirements
public in the repo, and a launch price below the two-month subscription
payback line. Do not quietly add a trial later without revisiting
`PRODUCT_OFFER.md`.

### 6.3 "Linux only?"

True at launch and stated plainly in all copy. Windows interest is
captured on the waitlist as a measured segment — that list is the demand
evidence for prioritizing Windows qualification later, and it costs
nothing to keep.

---

## 7. Hidden-cost audit (the $0 promise, checked)

| Tempting spend | Real cost | $0 alternative used in this plan |
|---|---|---|
| Custom domain | ~$10–15/yr | `*.github.io` subdomain; buy the domain out of first revenue, not before launch |
| Product Hunt promotion | Ads start ~$5,000 and are banned during your own launch; paid upvotes risk a permanent ban | Organic launch only — it is also the only legal route |
| Gumroad Discover traffic | 30% of the sale | Drive owned traffic to Lemon Squeezy (5% + $0.50); accept Discover sales only as found money |
| Stripe direct checkout | Lowest fee, but seller carries worldwide VAT/sales-tax compliance | Merchant-of-record platforms (Lemon Squeezy / Gumroad) — compliance is what the 5% buys |
| Deal sites (AppSumo-type) | Deep discount expectations + revenue share + support surge | Deferred. FineVoice's $49.99 deal presence proves the channel works for a later push, but it is a pricing event, not a free launch channel |
| Email marketing platform | Free tiers cap subscribers and features | Free tier at launch scale; verify the cap at signup; Lemon Squeezy's own buyer emails cover purchasers |
| Paid subreddit / influencer posts | Cash, and usually disclosure obligations | Participation and demos; the product rendering its own marketing assets is the whole point of a TTS demo |

---

## 8. First 10 actions (ready to execute, all $0)

1. Create the Lemon Squeezy store; configure Rhetoric at $49 list with
   license-key generation enabled; run a test-mode purchase and confirm
   the key activates the app offline.
2. Create the Product Hunt personal account today (starts the one-week
   clock) and draft the launch page: tagline, gallery (demo scenes),
   maker first-comment, $29 launch-day promo code.
3. Render Demo Scene #1 with Rhetoric — the two-character audiobook
   scene — and cut the 45-second captioned video version.
4. Rewrite the top of the GitHub README into the storefront (§4.1.1)
   and open it as a change on the release branch for owner review.
5. Publish the GitHub Pages site with the three comparison pages
   (§4.1.2).
6. Submit the AlternativeTo listing (alternatives: ElevenLabs, Murf,
   Play.ht, VoiceStudio).
7. Submit the SaaSHub listing with the same copy.
8. Publish the Play.ht-shutdown essay ("your cloud TTS can die; local
   software can't") to GitHub Discussions; cross-post to the Seismic
   Daily community tab.
9. Join r/audiobooks, r/ACX, r/selfpublish, r/selfhosted and answer five
   real TTS questions helpfully, no links. (Repeat weekly; this is the
   compounding asset.)
10. Point the waitlist signup at the README, Pages site, and community
    bios; announce it once to existing repo watchers via a Discussion
    post.

---

## 9. Sources (accessed 2026-11-08)

ElevenLabs pricing (multiple independent Oct 2026 checks of the vendor
pricing page, consistent figures):

- https://www.toolbistro.com/radar/elevenlabs-pricing
- https://www.blurstudio.ai/knowledge/elevenlabs-pricing
- https://toolchase.com/blog/elevenlabs-pricing-2026/
- https://quickveed.com/blogs/elevenlabs-pricing

Murf pricing (Studio restructure; Creator $19 annual / $29 monthly,
Business $66 / $99, cloning Enterprise-only):

- https://javisreview.com/review/murf-ai-review-2026/
- https://youraisoft.com/murf-ai-review/
- https://aialleyway.com/murf-pricing/

Play.ht shutdown and archived pricing:

- https://www.aiinsiders.net/tools/reviews/playht
- https://litmustools.com/review/playht/
- (Murf's 6-month refugee offer for Play.ht users is reported in the
  Murf coupon roundup at https://grabon.com/murf-ai-coupons/ — treat the
  offer detail as reported, not primary-verified.)

LOVO pricing (primary page not server-rendered; figures are third-party
and labeled unverified in §1.1):

- https://clipjury.com/reviews/lovo/
- https://www.fahimai.com/lovo-ai-vs-podcastle

Typecast pricing (two conflicting 2026 models; ranged in §1.1):

- https://www.anygen.io/showcase/typecast-ai/index.html
- https://cliploft.com/tools/typecast-ai-voice-generator

Resemble AI pricing (Flex pay-as-you-go; detection pivot):

- https://costbench.com/software/ai-voice-tools/resemble-ai/
- https://news.ssbcrack.com/best-ai-voice-cloning-tools/

VoiceStudio (free, AGPL-3.0, default OmniVoice weights CC-BY-NC, beta):

- https://www.nextriva.net/2026/10/voicestudio.html
- https://www.codebasehub.pro/blog/voicestudio-open-source-voice-cloning
- https://www.explainx.ai/blog/voicestudio-open-source-local-elevenlabs-alternative-2026

FineVoice perpetual pricing ($49.99 deal listing in stock at check):

- https://www.stacksocial.com/sales/finevoice-ai-basic-plan-lifetime-subscription
- https://www.techrepublic.com/article/finevoice-ai-lifetime-subscription/
- https://www.dealfuel.com/seller/finevoice-ai-voice-changer/

Chatterbox engine (MIT license, Podonos blind test, PerTh watermark):

- https://localaimaster.com/blog/elevenlabs-open-source-alternatives
- https://localaimaster.com/blog/kokoro-vs-xtts-vs-chatterbox

Marketplace fees:

- Gumroad (10% + $0.50 direct, 30% Discover, merchant of record):
  https://checkoutpage.com/blog/gumroad-fees?srsltid=AfmBOornS1AA4wkY9Axu8s-RGUsdYOb_0DEzSk24QQUEHhXxIFHJg4mR
  and https://gumkit.app/blog/gumroad-fees-explained/
- Lemon Squeezy (5% + $0.50 all-in, merchant of record, license keys):
  https://whatpayment.com/en/reviews/lemonsqueezy-review/
  and https://craftomorrow.com/lemon-squeezy-vs-gumroad-vs-etsy/
- Stripe headline processing (2.9% + $0.30) as reported in the two fee
  comparisons above.

Product Hunt launch rules (free; account age; no paid tier; ads banned
during own launch):

- http://help.producthunt.com/en/articles/17734646-8-launch-faq-and-myths
- https://letslaunch.today/blog/product-hunt-launch-rules

Internal references: `docs/release/PRODUCT_OFFER.md` (product model),
`docs/SOFT_LAUNCH.md` (release gate), and the owner's 2026-09-11 pricing
anchor ($39, +$20 at hundreds/month) preserved in project records.

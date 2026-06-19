# Here by Headout — PARTNER Trailer · FAL Image-to-Video Prompts

Image-to-video companion to `flow-trailer-prompts-partner.md`. Same 8-scene
partner arc (confident open → proof → peak → CTA), reformatted for **FAL i2v**.

> **Read this first — the i2v reframe:** in image-to-video the **start frame
> owns the scene** (composition, palette, Headout purple, typography, faces, the
> QR prop). The text prompt should describe **only what moves** — action, camera,
> timing. Re-describing the static set fights the input image and causes drift.

---

## How consistency actually works in FAL (read before generating)

**FAL i2v is stateless.** Each scene is a separate API call — one image, one
prompt, some params. There is **no conversation memory**, so you *cannot* send a
master prompt once and have later scenes inherit it. Consistency comes from three
levers instead, in order of impact:

### Lever 1 — The start frames (most important)
The look lives in the **images**, not the text. Generate all 8 stills as **one
batch** with:
- the **same Master Style Block below as the style reference** (paste it into your
  image model — nano-banana / Midjourney `--sref` / Flux style ref),
- your **Headout city screenshots** seeded in for palette + the purple accent,
- a **character reference** for the recurring owner so the same face/wardrobe
  appears in Scenes 1, 2, 3, 5, 6,
- the **same Headout-purple QR table-tent** as a prop reference in Scenes 4, 5, 7.

Get the stills consistent and the clips are already 80% consistent.

### Lever 2 — The Master Style Block (your "master prompt")
This is the master prompt you wanted — but you **prepend it to every scene's
motion prompt**, since FAL won't remember it between calls. It locks the camera
grammar, grade, and pace so all 8 clips feel like one film.

```
MASTER STYLE — Here by Headout partner brand film. Premium modern travel-tech
look: bright editorial photography, warm natural light, shallow depth of field,
soft filmic grade, gentle film grain. Headout-purple accent present in every
shot. Composed, confident, high production value, photoreal, 4K. Camera moves are
slow, smooth and deliberate (push-ins, lateral glides, pull-backs) — never
shaky or frantic. Real, candid human warmth in faces and gestures.
```

### Lever 3 — Locked params (set once, reuse for every scene)
- **Model:** keep the *same* model across the film (don't mix Kling and Seedance
  in one cut — their motion/grade differ). Default: `fal-ai/kling-video/v2.5-turbo/pro/image-to-video`.
- **Aspect ratio:** `16:9` for the launch film. Re-render heroes at `9:16` for social.
- **fps / duration:** same fps everywhere; render 5s and trim on the beat.
- **Seed family:** lock one base seed; nudge ±1 per scene. Same seed = consistent motion character.
- **CFG / prompt strength:** mid (~0.5) — high follows text but drifts from the frame.

### The final prompt you actually send to FAL, per scene:
```
[Master Style Block]  +  [that scene's Motion prompt]
negative prompt: [Global negative, below]
```

**Global negative prompt** (every scene):
```
text, captions, subtitles, watermark, logo, fake UI text, distorted hands,
extra fingers, warping, morphing faces, flicker, jitter, shaky camera, low
quality, blurry, oversaturated, deformed, duplicated people, plastic skin
```

---

## Recommended models by shot type
| Use | Model | Why |
|---|---|---|
| **Live-action (1, 2, 5, 7, 8)** | `fal-ai/kling-video/v2.5-turbo/pro/image-to-video` | Best controllable, premium motion from a brand still. |
| **Native audio baked in** | `fal-ai/veo3/image-to-video` | Adds ambient/VO; pricier. Else add VO+music in CapCut. |
| **Snappy Scene 7 cuts** | `fal-ai/bytedance/seedance/v1/pro/image-to-video` | Fast 0.5–0.8s beat cuts. *Grade-match in edit if mixing.* |
| **UI scenes (3, 4, 6)** | *Prefer Screen Studio capture of the real build;* i2v = fallback. |

---

## Pacing arc — confident open → fast proof → strong close

Partner trailers sell **trust, not tension**. Open confident and aspirational
(not "lost"), accelerate through the proof (setup → live → earnings), peak on the
"any place" montage, land on a clear CTA. Render each i2v clip at 5s and **trim on
the beat** to the cut lengths below; match the camera move so the film feels of a
piece.

| Phase | Scenes | Feel | Cut length | Camera (i2v move) |
|---|---|---|---|---|
| **Confident open** | 1–2 | Busy, thriving place; the missed moment reframed as opportunity | 3–4s | slow push-in / lateral glide |
| **The proof** | 3–6 | Setup → QR → guests book → you earn; momentum builds | 1.5–2.5s | locked or slow push-in, snappy |
| **Fast peak** | 7 | Every kind of place, all earning | 0.5–0.8s | brisk push-in, hard cuts on the beat |
| **Land + CTA** | 8 + banner | Release, scale, "become a partner" | 4–5s | slow aerial pull-back, settle |

Music + VO are unchanged from `flow-trailer-prompts-partner.md` — reuse its cue
sheet and hit points (Scene 3 "Generate" tap = first downbeat; Scene 6 commission
tick = accent chime; Scene 7 cuts on the kick; Scene 8 pull-back = biggest hit).

---

## Scene 1 — The missed moment · ~4s · CONFIDENT OPEN

**Beat & depth:** the everyday lost booking, framed as *opportunity, not failure*.
A guest leans in at the counter, hopeful — "what should we do today?" The owner
genuinely *wants* to help but has nothing to hand them: a warm, slightly
apologetic shrug, a vague gesture toward the street. The guest's face softens
from anticipation to mild disappointment as they drift off. The space around them
is beautiful and thriving — which is the point: the only thing missing is the
answer. We feel the value quietly leaking out the door.

**Start frame:** warm boutique-hotel lobby (or stylish café) at mid-morning;
recurring owner behind a counter, a guest standing across mid-question. Mid-shot,
shallow DoF, soft window light, a small Headout-purple detail in frame (a coaster,
a sign). Generate with the Master Style Block + owner character ref.

**Motion prompt:**
```
The owner gives a small, warm, apologetic shrug and a soft open-handed gesture
toward the street; their helpful smile fades slightly. The guest's hopeful
expression softens to mild disappointment, and they nod politely and slowly turn
to drift out of frame. Quiet ambient life continues softly in the background.
Camera: very slow, gentle push-in toward the counter.
```
*Intent: warmth + a missed beat, never embarrassment.*

---

## Scene 2 — The reframe (footfall + trust) · ~4s · CONFIDENT OPEN

**Beat & depth:** reveal the asset the owner already owns — **footfall and
trust** — the two things Headout can't buy. This is the "you're sitting on a
distribution channel" beat. Layer the life: a guest checking in and being greeted
by name, two friends laughing over coffee, the owner pointing a regular toward a
table, easy eye contact and familiarity everywhere. The room should feel *trusted
and full* — a steady, valuable flow of people who already believe in this place.

**Start frame:** the same space, busy and alive — guests checking in, coffee
being poured, the owner greeting someone warmly at the door. Wider than Scene 1
so the flow of people reads. Same grade, same owner.

**Motion prompt:**
```
Guests move naturally and happily through the space — one checks in and is
greeted warmly by the owner, two friends laugh over coffee, a regular is waved
toward a table. A steady, optimistic flow of people who clearly trust this place.
Secondary motion: steam off coffee, a door easing open, soft light shifting.
Camera: smooth, slightly slowed lateral glide across the room.
```
*Intent: untapped potential, abundance — not busy chaos.*

---

## Scene 3 — Sign up in 60 seconds · ~2.5s · THE PROOF
*(Prefer a Screen Studio capture of the real setup form. i2v fallback below.)*

**Beat & depth:** kill the "this is a big integration" fear in one shot. No
engineers, no contract, no inventory to source — just three quick fields (**place
name, place type, commission**) and a button. Sixty seconds. The owner's hands
move with easy confidence; the punchline is their face: a quick glance up with a
hopeful, almost disbelieving *"…that's it?"* The purple **"Generate Here by
Headout"** button is the hero — it should feel alive and inviting under the finger.

**Start frame:** close-up of the owner's hands on a tablet at the counter showing
a clean, short setup form with a few filled fields; finger hovering near a large
glowing purple **"Generate Here by Headout"** button. Warm counter surface, soft
light, purple screen-glow.

**Motion prompt:**
```
The finger taps the glowing purple Generate button; the button pulses and reacts
warmly on tap, a soft purple glow blooming. The owner glances up from the tablet
with a hopeful, slightly disbelieving "that's it?" expression. Only tiny, premium
UI micro-motion otherwise. Camera: locked, steady, faint settle.
```
*Keep UI motion minimal so fake text doesn't warp; the tap + glance is the beat.*

---

## Scene 4 — Branded QR + storefront + dashboard drop out · ~2.5s · THE PROOF
*(Prefer a Screen Studio capture. i2v fallback below.)*

**Beat & depth:** the 60-second payoff. One button press and a whole business
materialises — a branded **purple QR table-tent**, a co-branded mobile storefront,
and a live dashboard — assembling with a satisfying, premium animation. They built
nothing; they *have a storefront*. End on the tactile proof: the printed purple QR
stand being set down and squared up on the counter, adjusted with quiet pride.

**Start frame:** tablet screen mid-assembly — purple QR table-tent, co-branded
storefront preview, and live dashboard appearing together, soft purple glow.

**Motion prompt:**
```
The three elements bloom and settle into place together with a smooth, premium
assembly animation, a soft purple glow rippling outward as they lock in. Hold on
the finished layout. Camera: locked, steady, a slight satisfying settle.
```
*Hard-cut in edit to a separate ~1s clip — hands setting the freshly printed
purple QR table-tent on the counter and squaring it up proudly (animate that from
its own counter still, same Master Style Block).*

---

## Scene 5 — Guests scan & book — on Headout's rails · ~2.5s · THE PROOF

**Beat & depth:** the owner does *nothing* — Headout owns inventory, checkout,
payments, fulfillment, support. Foreground: a guest happily raises their phone to
the purple QR, taps, and books, a small delighted nod when it works. Background,
soft-focus: the owner carries on warmly serving the next guest, completely
hands-off. A subtle purple glow ties the phone, the QR, and the storefront into
one system. The whole experience runs itself.

**Start frame:** a guest at the counter lifting a phone toward the purple QR
table-tent; owner soft-focus in the background mid-service. Same QR prop as Scene 4.

**Motion prompt:**
```
The guest lifts their phone to the purple QR table-tent, taps the screen to book,
and gives a small delighted nod as it confirms; a subtle purple glow links the
phone and the QR. In the soft-focus background the owner keeps warmly serving the
next guest, completely hands-off and relaxed. Camera: slow, smooth, gentle drift.
```
*Intent: effortless income — keep the owner unbothered in the background.*

---

## Scene 6 — You earn (the partner dashboard) · ~2.5s · THE PROOF
*(Prefer a Screen Studio capture of the live dashboard. i2v fallback below.)*

**Beat & depth:** the money beat — the whole pitch in one reaction. A booking
lands *live* on the dashboard: impressions, conversions, and **commission** tick
upward, a chart rising, a subtle purple progress accent. The owner watches it
happen and breaks into a genuine, delighted smile — *they just got paid for a
question they used to answer for free.* Sell it with the face and the purple
screen-glow, not the numbers.

**Start frame:** close-up of the owner watching a tablet dashboard on the counter
— three metric tiles (impressions, conversions, commission) + a rising chart,
purple screen-glow on their face.

**Motion prompt:**
```
A booking lands live: the three metric tiles pulse and tick upward and the chart
rises, with a subtle purple progress accent sweeping across. The owner watches,
then breaks into a genuine, delighted, slightly surprised smile, purple
screen-glow warming their face. Camera: slow push-in toward the reaction.
```
*Intent: the emotional + financial high — land it on the smile.*

---

## Scene 7 — Any place becomes a partner (montage) · ~6s total · FAST PEAK

**Beat & depth:** prove the model is *place-agnostic* from the partner angle —
every kind of venue setting up the same purple QR and watching it earn. One
constant object (the QR), many proud owners. This is the energy peak: hardest
cuts, building light, a partner network igniting across a city. Each owner's
gesture should read as quiet pride — *this is mine now, and it works.*

**Build as separate short i2v clips, one per place, cut on the beat (0.5–0.8s
each), same purple QR table-tent prop in every still.**

**Start frames:** hotel front desk · café bar · hostel reception · airport lounge
desk · theatre box office · tourist info desk · rooftop bar. Grade each a step
later in the day (afternoon → golden dusk → glowing night) so energy climbs.

**Motion prompt (reuse per clip):**
```
A proud owner/manager sets the Headout-purple QR table-tent down on the counter
and squares it into place with a satisfied, quietly proud smile; the QR pulses
softly in purple. Brisk, confident, single clean action. Camera: a brisk, slight
push-in.
```
**Place lockups — snap a "{Place} × Headout" label onto each cut in CapCut on the
beat (identical lockup styling = the repeating co-brand motif). NOT in FAL.**

| Cut | Location still | Headout-style label |
|---|---|---|
| 1 | Hotel front desk | **Casa Aurelia × Headout** |
| 2 | Café bar | **Caffè Prati × Headout** |
| 3 | Hostel reception | **Trastevere Social × Headout** |
| 4 | Airport lounge desk | **Fiumicino SkyLounge × Headout** |
| 5 | Theatre box office | **Teatro Argentina × Headout** |
| 6 | Tourist info desk | **Prati Visitor Desk × Headout** |
| 7 | Rooftop bar | **Terrazza Borghese × Headout** |

*Casa Aurelia, Caffè Prati, and Prati Visitor Desk are real §9 seed places — keep
exact; the rest are believable Rome stand-ins. Cut every clip on the kick.*

---

## Scene 8 — Scale + call to action · ~5s · LAND + CTA

**Beat & depth:** release the built-up energy and turn it into an ask. Pull back
over a city of glowing purple pins — the partner network coming alive — the glow
rippling outward toward other cities on the horizon. The frantic montage energy
decelerates into a wide, calm, aspirational hold, leaving clean dark negative
space up top for the banner. End on the invitation: *become a partner.*

**Start frame:** stylized night map of the city (Rome) with a few Headout-purple
location pins lit; clean dark negative space in the upper center for the banner.

**Motion prompt:**
```
More glowing Headout-purple location pins ignite one after another across the
city until it shimmers like a live network, the glow rippling outward toward the
horizon and other cities. Motion decelerates into a calm, wide, aspirational
hold. Camera: slow aerial pull-back, leaving the upper-center negative space clear.
```
*Animate banner + "Become a partner →" CTA over the negative space in CapCut/
Canva (same lockup as the guest trailer). Tagline: "Your guests explore. You earn."*

---

## Carried over from the Flow sheet
- Same Headout-purple QR, same "Here · by Headout" lockup, same Rome world, same
  screenshot palette refs → both trailers feel like one brand.
- VO script, VO sync map, and music cue sheet are unchanged — reuse
  `flow-trailer-prompts-partner.md` §VO and §Music as-is over these clips.
- Partner end-card tagline options (pick one): **"Your guests explore. You earn."**
  · "Turn foot traffic into income." · "Turn any trusted place into a Headout storefront."

# Here by Headout — PARTNER Trailer · FAL Image-to-Video Prompts

Image-to-video companion to `flow-trailer-prompts-partner.md`. Same 8-scene
partner arc (confident open → proof → peak → CTA), reformatted for **FAL i2v**.

> **The core difference vs. the Flow/Veo3 text-to-video sheet:** in
> image-to-video the **start frame owns the scene** — composition, palette,
> Headout purple, typography, who's in shot. The text prompt should describe
> **only what moves**: the action, the camera move, and the timing. Re-describing
> the static set fights the input image and causes drift/morphing. Keep prompts
> short and motion-led.

---

## Recommended FAL setup

| Use | Model | Why |
|---|---|---|
| **Live-action scenes (1, 2, 5, 7, 8)** | `fal-ai/kling-video/v2.5-turbo/pro/image-to-video` | Best controllable motion from a brand still; clean, premium camera moves. |
| **If you want native audio baked in** | `fal-ai/veo3/image-to-video` | Adds ambient/VO; pricier. Otherwise add VO+music in CapCut per your existing workflow. |
| **Snappy montage cuts (Scene 7 alt)** | `fal-ai/bytedance/seedance/v1/pro/image-to-video` | Fast, good for 0.5–0.8s beat-synced cuts. |
| **UI scenes (3, 4, 6)** | *Prefer Screen Studio capture of the real build.* i2v fallback = animate a real screenshot. |

**Global params**
- **Aspect ratio:** `16:9` for the launch film. Re-render hero scenes at `9:16` for Reels/Shorts.
- **Duration:** match the cut lengths below (Kling supports 5s/10s — render 5s and trim on the beat).
- **CFG / prompt strength:** mid (~0.5). Higher = follows text harder but drifts from the frame; lower = stays truer to the still.
- **Seed:** lock a seed per scene once you like a take, so re-renders stay consistent.

**Global negative prompt** (paste into every scene):
```
text, captions, subtitles, watermark, logo, fake UI text, distorted hands,
extra fingers, warping, morphing faces, flicker, jitter, low quality, blurry,
oversaturated, deformed, duplicated people
```

**Start-frame sources**
- **Live-action stills:** generate with nano-banana / Midjourney / Flux using the
  *scene description* from `flow-trailer-prompts-partner.md` as the image prompt,
  seeded with your Headout city screenshots for palette + the purple accent.
  Generate the still at the trailer aspect ratio so motion has room.
- **UI stills:** real screenshots of the build (preferred) or the Claude Design
  partner-flow screens in `design/`.
- **The constant prop:** keep the **same Headout-purple QR table-tent** visible
  across stills 4, 5, 7 so the i2v clips share the repeating motif.

---

## Scene 1 — The missed moment · ~4s · CONFIDENT OPEN

**Start frame:** warm boutique-hotel lobby / café; friendly owner behind the
counter, a guest standing across asking a question. Mid-shot, shallow DoF,
Headout-purple accent somewhere in frame.

**Motion prompt:**
```
The owner gives a small, warm, helpless shrug and a soft gesture toward the
street; the guest nods politely and slowly turns to drift away out of frame.
Subtle ambient life in the background. Camera holds with a very slow, gentle
push-in. Soft natural light, cinematic, calm observational pace.
```
*Camera: slow push-in. Keep it warm, not awkward — opportunity, not failure.*

---

## Scene 2 — The reframe (footfall + trust) · ~4s · CONFIDENT OPEN

**Start frame:** the same space, full of life — guests checking in, sipping
coffee, the owner greeting someone warmly by the door.

**Motion prompt:**
```
Guests move naturally through the space — checking in, sipping coffee, chatting;
the owner greets a guest warmly by the door. A steady, optimistic flow of happy
footfall. Camera drifts in a smooth, slightly slowed lateral glide across the
room. Warm natural light, aspirational, full of life.
```
*Camera: smooth lateral drift. Sense of "untapped channel," not busy chaos.*

---

## Scene 3 — Sign up in 60 seconds · ~2.5s · THE PROOF
*(Prefer a Screen Studio capture of the real setup form. i2v fallback below.)*

**Start frame:** close-up of owner's hands on a tablet showing the clean setup
form, finger near a large glowing purple **Generate** button.

**Motion prompt:**
```
The finger taps the glowing purple button; the button pulses and reacts on tap.
The owner glances up with a hopeful "that's it?" expression. Tiny, premium UI
micro-motion only. Camera locked, steady. Soft light.
```
*Keep motion minimal so the fake UI doesn't warp; the tap + glance is the beat.*

---

## Scene 4 — Branded QR + storefront + dashboard drop out · ~2.5s · THE PROOF
*(Prefer a Screen Studio capture. i2v fallback below.)*

**Start frame:** tablet screen mid-assembly — purple QR table-tent, co-branded
storefront preview, and live dashboard appearing together.

**Motion prompt:**
```
The three elements bloom and settle into place with a smooth, premium assembly
animation, a soft purple glow blooming outward. Hold on the finished layout.
Camera locked, steady, slight settle. Bright, branded, satisfying.
```
*Hard-cut in edit to a separate clip of hands placing the printed QR on the
counter (animate that as its own short i2v from a counter still).*

---

## Scene 5 — Guests scan & book — on Headout's rails · ~2.5s · THE PROOF

**Start frame:** a guest at the counter raising a phone to the purple QR
table-tent; owner soft-focus in the background serving the next guest.

**Motion prompt:**
```
The guest lifts their phone to the purple QR table-tent and taps the screen to
book, smiling; in the soft-focus background the owner keeps serving the next
guest, completely hands-off. A subtle purple glow links the phone and the QR.
Camera slow, smooth, warm natural light.
```
*The point is the owner does nothing — keep them relaxed in the background.*

---

## Scene 6 — You earn (the partner dashboard) · ~2.5s · THE PROOF
*(Prefer a Screen Studio capture of the live dashboard. i2v fallback below.)*

**Start frame:** close-up of owner watching a tablet dashboard on the counter —
three metric tiles (impressions, conversions, commission) + a rising chart,
purple screen-glow on their face.

**Motion prompt:**
```
A booking lands live: the three metric tiles pulse and tick upward and the chart
rises, with a subtle purple progress accent. The owner breaks into a genuine,
delighted smile, purple screen-glow on their face. Camera slow push-in. Premium,
bright, data-product feel.
```
*This is the money beat — sell it with the reaction, not the numbers.*

---

## Scene 7 — Any place becomes a partner (montage) · ~6s total · FAST PEAK

**Build as several short i2v clips, one per place, cut on the beat (0.5–0.8s
each).** One start frame per location, **same purple QR table-tent in each.**

**Start frames:** hotel front desk · café bar · hostel reception · airport lounge
desk · theatre box office · tourist info desk · rooftop bar.

**Motion prompt (reuse per clip):**
```
A proud owner/manager sets the Headout-purple QR table-tent down on the counter
and adjusts it into place with a satisfied smile; the QR pulses softly in purple.
Quick, confident motion. Camera a brisk, slight push-in. Energetic.
```
*Shift each clip's grade afternoon → golden dusk → glowing night so energy
builds across the montage. Add the **"{Place} × Headout"** labels in CapCut
(table in the Flow sheet), not in FAL.*

---

## Scene 8 — Scale + call to action · ~5s · LAND + CTA

**Start frame:** stylized night map of Rome with a few Headout-purple location
pins lit, clean dark negative space in the upper center for the banner.

**Motion prompt:**
```
More glowing purple location pins ignite one after another across the city until
it shimmers like a live network, the glow rippling outward toward the horizon.
Motion decelerates into a calm, wide, aspirational hold. Camera slow aerial
pull-back. Premium, confident, leaving the upper-center negative space clear.
```
*Animate banner + "Become a partner →" CTA over the negative space in CapCut/
Canva (same lockup as the guest trailer). Tagline: "Your guests explore. You earn."*

---

## Notes carried over from the Flow sheet
- Same Headout-purple QR, same "Here · by Headout" lockup, same Rome world,
  same screenshot palette references → both trailers feel like one brand.
- VO script, VO sync map, and music cue sheet are unchanged — reuse
  `flow-trailer-prompts-partner.md` §VO and §Music as-is over these clips.
- Partner end-card tagline options (pick one): **"Your guests explore. You earn."**
  · "Turn foot traffic into income." · "Turn any trusted place into a Headout storefront."

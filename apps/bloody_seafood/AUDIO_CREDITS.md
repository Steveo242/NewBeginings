# Bloody Seafood - music and sound credits and licences

| Sprite key | Source | Licence |
| --- | --- | --- |
| `bgm_freespin` (free spins and super free spins) | Original composition (2026-10-31): a D-minor sea-shanty rocker at 152 BPM, A/B/A' over 24 bars, seamless 37.9 s loop - fiddle hook, oom-pah accordion, strings, brass, bass and drums. Composed as MIDI by `tools/compose_fs_music.py`, rendered with fluidsynth through the FluidR3_GM soundfont and mixed by `tools/render_fs_music.py` (loudness matched to the base music, true peak -3.5 dBTP, no clipping). | Composition: original work owned by the game's publisher (Steel Gaming). Soundfont: FluidR3_GM, (c) 2000-2002, 2008 Frank Wen, 2008 Toby Smithe, MIT licence (`/usr/share/doc/fluid-soundfont-gm/copyright`). |
| `sfx_cluster_hit_1..3` (a cluster wins) | Original (2026-10-31): timpani, brass-section stab on D minor and glockenspiel sparkle, MIDI rendered through FluidR3_GM, plus a synthesised wet slap - `tools/make_cluster_fx_v2.py`. | Original work (Steel Gaming); soundfont FluidR3_GM, MIT. |
| `sfx_cluster_burst_1..3` (winning symbols burst), `sfx_btn_spin` (spin button: iron clank) | Original sound design, synthesised from scratch by `tools/make_cluster_fx_v2.py` (no samples). | Original work owned by the game's publisher (Steel Gaming); no third-party rights. |
| `bgm_main` (base game) | "Campfire Guitar" by ImmergoMedia, Freesound #670001, edited into a 59 s crossfaded loop. | CC0 1.0 (public domain) |

To regenerate: `python3 tools/compose_fs_music.py <dir>` then
`python3 tools/render_fs_music.py <dir> out.wav <base-music.wav>` (needs fluidsynth and
fluid-soundfont-gm), and `python3 tools/make_cluster_fx_v2.py <dir>`; splice the results into
`static/assets/audio/sounds.*` under the same keys.

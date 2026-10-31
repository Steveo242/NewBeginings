# Bloody Seafood - music and sound credits and licences

| Sprite key | Source | Licence |
| --- | --- | --- |
| `bgm_freespin` (free spins and super free spins) | Original composition (2026-10-31, v3): dark, storm-driven and building - D minor with the Phrygian flat second, 144 BPM, A/B/C/D over 32 bars, seamless 53.3 s loop: staccato low-string ostinato, taiko and timpani, a choir wind pad, the hook on horns then full brass + choir, palm-muted overdriven guitar and double kick in the heavy half, and a synthesised low-passed thunder strike at the section changes. Composed as MIDI by `tools/compose_fs_music_v3.py`, rendered with fluidsynth through the FluidR3_GM soundfont and mixed by `tools/render_fs_music.py` (loudness matched to the base music, true peak -4 dBTP, no clipping). | Composition: original work owned by the game's publisher (Steel Gaming). Soundfont: FluidR3_GM, (c) 2000-2002, 2008 Frank Wen, 2008 Toby Smithe, MIT licence (`/usr/share/doc/fluid-soundfont-gm/copyright`). |
| `amb_storm` (harbour ambience under every mode) | Original sound design (2026-10-31): breaking waves, water lapping the pier and a distant rumble, synthesised from scratch by `tools/make_surf_amb.py` (no samples), seamless 48 s loop. | Original work owned by the game's publisher (Steel Gaming); no third-party rights. |
| `sfx_mult_up_1..6` (global multiplier steps up), `sfx_mult_down` (multiplier back to x1) | Original (2026-10-31): synthesised ship's bell and chain ratchet with a brass-section stab rendered through FluidR3_GM, a semitone higher per step; the reset is a synthesised hull thud, gong and timber groan - `tools/make_multiplier_fx.py`. | Original work (Steel Gaming); soundfont FluidR3_GM, MIT. |
| `sfx_cluster_hit_1..3` (a cluster wins) | Original (2026-10-31): timpani, brass-section stab on D minor and glockenspiel sparkle, MIDI rendered through FluidR3_GM, plus a synthesised wet slap - `tools/make_cluster_fx_v2.py`. | Original work (Steel Gaming); soundfont FluidR3_GM, MIT. |
| `sfx_cluster_burst_1..3` (winning symbols burst), `sfx_btn_spin` (spin button: iron clank) | Original sound design, synthesised from scratch by `tools/make_cluster_fx_v2.py` (no samples). | Original work owned by the game's publisher (Steel Gaming); no third-party rights. |
| `bgm_main` (base game) | "Campfire Guitar" by ImmergoMedia, Freesound #670001, edited into a 59 s crossfaded loop. | CC0 1.0 (public domain) |

To regenerate: `python3 tools/compose_fs_music_v3.py <dir>` then
`python3 tools/render_fs_music.py <dir> out.wav <base-music.wav>` (needs fluidsynth and
fluid-soundfont-gm), `python3 tools/make_cluster_fx_v2.py <dir>`, `python3 tools/make_surf_amb.py <out.wav>` and
`python3 tools/make_multiplier_fx.py <dir>`; splice the results into
`static/assets/audio/sounds.*` under the same keys.

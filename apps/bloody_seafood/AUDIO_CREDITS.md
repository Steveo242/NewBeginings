# Bloody Seafood - music credits and licences

| Sprite key | Source | Licence |
| --- | --- | --- |
| `bgm_freespin` (free spins and super free spins) | Original composition, synthesised from scratch by `tools/make_fs_music.py` (no samples, no soundfonts): 160 BPM, D minor, 48 s seamless loop. Written for this game on 2026-10-31. | Original work owned by the game's publisher (Steel Gaming); no third-party rights. |
| `sfx_cluster_hit_1..3` (a cluster wins), `sfx_cluster_burst_1..3` (winning symbols burst), `sfx_btn_spin` (spin button: heavy ship-metal clank) | Original sound design, synthesised from scratch by `tools/make_cluster_fx.py` on 2026-10-31 (no samples). | Original work owned by the game's publisher (Steel Gaming); no third-party rights. |
| `bgm_main` (base game) | "Campfire Guitar" by ImmergoMedia, Freesound #670001, edited into a 59 s crossfaded loop | CC0 1.0 (public domain) |

Regenerate the free-spins track with `python3 tools/make_fs_music.py out.wav 0.13`
(the second argument is the target RMS; 0.13 sits with the base music), then splice it
into `static/assets/audio/sounds.*` under `bgm_freespin` as a looping entry.

import 'pixi.js/basis';
import { setBasisTranscoderPath } from 'pixi.js';

// Basis Universal sheets (bs-render basis_pack.py: UASTC, transcoded on the device to
// ASTC / BC7 / ETC2 - a quarter of the GPU memory of RGBA - or RGBA where none exists).
// The transcoder ships with the game: nothing loads from a CDN.
setBasisTranscoderPath({
	jsUrl: new URL('../../assets/basis/basis_transcoder.js', import.meta.url).href,
	wasmUrl: new URL('../../assets/basis/basis_transcoder.wasm', import.meta.url).href,
});

export default {
	daySky: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/day_sky.webp', import.meta.url).href,
		preload: true,
	},
	daySea: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/day_sea.webp', import.meta.url).href,
		preload: true,
	},
	dayHeadland: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/day_headland.webp', import.meta.url).href,
		preload: true,
	},
	dayTrawler: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/day_trawler.webp', import.meta.url).href,
		preload: true,
	},
	dayDock: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/day_dock.webp', import.meta.url).href,
		preload: true,
	},
	stormSky: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/bg_sky.webp', import.meta.url).href,
		preload: true,
	},
	stormSea: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/bg_sea.webp', import.meta.url).href,
		preload: true,
	},
	stormHeadland: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/bg_headland.webp', import.meta.url).href,
		preload: true,
	},
	stormTrawler: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/bg_trawler.webp', import.meta.url).href,
		preload: true,
	},
	stormDock: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/bg_dock.webp', import.meta.url).href,
		preload: true,
	},
	fxNoise: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/fx_noise.png', import.meta.url).href,
		preload: true,
	},
	fxRain: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/fx_rain.webp', import.meta.url).href,
		preload: true,
	},
	fxFog: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/fx_fog.webp', import.meta.url).href,
		preload: true,
	},
	fxGlow: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/fx_glow.webp', import.meta.url).href,
		preload: true,
	},
	fxSharkBreach: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/fx_shark_breach.webp', import.meta.url).href,
		preload: true,
	},
	fxBeam: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/fx_beam.webp', import.meta.url).href,
		preload: true,
	},
	// a seamless 3D-rendered hawser (bs-render build_rope3d.py), bent along a MeshRope by
	// Anticipation.svelte
	fxRope: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/fx_rope.webp', import.meta.url).href,
		preload: true,
	},
	fxCaustics: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/fx_caustics.png', import.meta.url).href,
		preload: true,
	},
	tankBack: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/tank_back.webp', import.meta.url).href,
		preload: true,
	},
	tankGlass: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/tank_glass.webp', import.meta.url).href,
		preload: true,
	},
	tankFront: {
		type: 'sprite',
		src: new URL('../../assets/sprites/storm/tank_front.webp', import.meta.url).href,
		preload: true,
	},
	// Rendered 3D win titles (build_win_titles.py -> pack_win_titles.py): BIG WIN .. MAX WIN,
	// FREE SPINS, SUPER FREE SPINS, TOTAL HAUL - frames named <tier key>.png.
	winTitles: {
		type: 'sprites',
		src: new URL('../../assets/sprites/winTitles/winTitles.json', import.meta.url).href,
		preload: true,
	},
	// The 3D bet bar (build_ui3d.py -> pack_ui3d.py): every control's idle/hover/pressed
	// frame, the spin porthole + its turning glyph, and the 9-slice panel and plates.
	ui3d: {
		type: 'sprites',
		src: new URL('../../assets/sprites/ui3d/ui3d.json', import.meta.url).href,
		preload: true,
	},
	betUp: {
		type: 'sprite',
		src: new URL('../../assets/sprites/ui/bet_up.png', import.meta.url).href,
		preload: true,
	},
	betDown: {
		type: 'sprite',
		src: new URL('../../assets/sprites/ui/bet_down.png', import.meta.url).href,
		preload: true,
	},
	btnInfo: {
		type: 'sprite',
		src: new URL('../../assets/sprites/ui/btn_info.png', import.meta.url).href,
		preload: true,
	},
	btnPayTable: {
		type: 'sprite',
		src: new URL('../../assets/sprites/ui/btn_paytable.png', import.meta.url).href,
		preload: true,
	},
	bet: {
		type: 'sprite',
		src: new URL('../../assets/sprites/ui/spin_bs.png', import.meta.url).href,
		preload: true,
	},
	buyBonus: {
		type: 'sprite',
		src: new URL('../../assets/sprites/ui/mode_kiss.png', import.meta.url).href,
		preload: true,
	},
	titlePlaque: {
		type: 'sprite',
		src: new URL('../../assets/sprites/bgLayers/logo3d.webp', import.meta.url).href,
		preload: true,
	},
	logoBlood: {
		type: 'sprite',
		src: new URL('../../assets/sprites/bgLayers/logo3d_blood.webp', import.meta.url).href,
		preload: true,
	},
	titlePlaqueBoard: {
		type: 'sprite',
		src: new URL('../../assets/sprites/bgLayers/logo3d.webp', import.meta.url).href,
		preload: true,
	},
	progressBar: {
		type: 'sprites',
		src: new URL('../../assets/sprites/progressBar/progressBar.json', import.meta.url).href,
		preload: true,
	},
	symbolsStatic: {
		type: 'sprites',
		src: new URL('../../assets/sprites/symbolsStatic/symbolsStatic.json', import.meta.url).href,
		basis: true,
	},
	mBackgroundLow: {
		type: 'sprite',
		src: new URL('../../assets/sprites/mBackground/m_bg_low.png', import.meta.url).href,
	},
	mBackgroundMid: {
		type: 'sprite',
		src: new URL('../../assets/sprites/mBackground/m_bg_mid.png', import.meta.url).href,
	},
	mBackgroundHigh: {
		type: 'sprite',
		src: new URL('../../assets/sprites/mBackground/m_bg_high.png', import.meta.url).href,
	},
	symbolExplode: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/symbol_explode.json', import.meta.url).href,
		basis: true,
	},
	H1_win: {
		type: 'spriteSheet',
		lazy: true, // game/lazyWins.ts
		src: new URL('../../assets/sprites/symbolsAnim/H1_win.json', import.meta.url).href,
		basis: true,
	},
	H2_win: {
		type: 'spriteSheet',
		lazy: true, // game/lazyWins.ts
		src: new URL('../../assets/sprites/symbolsAnim/H2_win.json', import.meta.url).href,
		basis: true,
	},
	H3_win: {
		type: 'spriteSheet',
		lazy: true, // game/lazyWins.ts
		src: new URL('../../assets/sprites/symbolsAnim/H3_win.json', import.meta.url).href,
		basis: true,
	},
	H4_win: {
		type: 'spriteSheet',
		lazy: true, // game/lazyWins.ts
		src: new URL('../../assets/sprites/symbolsAnim/H4_win.json', import.meta.url).href,
		basis: true,
	},
	L1_win: {
		type: 'spriteSheet',
		lazy: true, // game/lazyWins.ts
		src: new URL('../../assets/sprites/symbolsAnim/L1_win.json', import.meta.url).href,
		basis: true,
	},
	L2_win: {
		type: 'spriteSheet',
		lazy: true, // game/lazyWins.ts
		src: new URL('../../assets/sprites/symbolsAnim/L2_win.json', import.meta.url).href,
		basis: true,
	},
	L3_win: {
		type: 'spriteSheet',
		lazy: true, // game/lazyWins.ts
		src: new URL('../../assets/sprites/symbolsAnim/L3_win.json', import.meta.url).href,
		basis: true,
	},
	S_win: {
		type: 'spriteSheet',
		lazy: true, // game/lazyWins.ts
		src: new URL('../../assets/sprites/symbolsAnim/S_win.json', import.meta.url).href,
		basis: true,
	},
	W_win: {
		type: 'spriteSheet',
		lazy: true, // game/lazyWins.ts
		src: new URL('../../assets/sprites/symbolsAnim/W_win.json', import.meta.url).href,
		basis: true,
	},
	// v5 rendered landings and idle loops (pack_symbol3d.py STATE=land|idle)
	H1_land: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H1_land.json', import.meta.url).href,
		basis: true,
	},
	H2_land: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H2_land.json', import.meta.url).href,
		basis: true,
	},
	H3_land: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H3_land.json', import.meta.url).href,
		basis: true,
	},
	H4_land: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H4_land.json', import.meta.url).href,
		basis: true,
	},
	L1_land: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/L1_land.json', import.meta.url).href,
		basis: true,
	},
	L2_land: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/L2_land.json', import.meta.url).href,
		basis: true,
	},
	L3_land: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/L3_land.json', import.meta.url).href,
		basis: true,
	},
	W_land: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/W_land.json', import.meta.url).href,
		basis: true,
	},
	S_land: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/S_land.json', import.meta.url).href,
		basis: true,
	},
	H1_idle: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H1_idle.json', import.meta.url).href,
		basis: true,
	},
	H2_idle: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H2_idle.json', import.meta.url).href,
		basis: true,
	},
	H3_idle: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H3_idle.json', import.meta.url).href,
		basis: true,
	},
	H4_idle: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H4_idle.json', import.meta.url).href,
		basis: true,
	},
	L1_idle: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/L1_idle.json', import.meta.url).href,
		basis: true,
	},
	L2_idle: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/L2_idle.json', import.meta.url).href,
		basis: true,
	},
	L3_idle: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/L3_idle.json', import.meta.url).href,
		basis: true,
	},
	W_idle: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/W_idle.json', import.meta.url).href,
		basis: true,
	},
	S_idle: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/S_idle.json', import.meta.url).href,
		basis: true,
	},
	sound: {
		type: 'audio',
		src: new URL('../../assets/audio/sounds.json', import.meta.url).href,
		preload: true,
	},
} as const;

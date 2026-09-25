<script lang="ts" module>
	// Painted storm-harbour plate, split into depth layers (source space 2752x1536).
	const SRC_W = 2752;
	const SRC_H = 1536;
	const LAYERS = {
		sky: { y: 0 },
		sea: { y: 930 },
		headland: { x: 0, y: 338 },
		trawler: { x: 1891, y: 98 },
		dock: { x: 0, y: 1062 },
	};
	const HORIZON_Y = 985;
	const PLANK_TOP_Y = 1258; // front edge of the dock planks
	const TANK_PLINTH_BELOW_CENTRE = 514; // game units from board centre to the tank's feet
	const TOWER_X = 620; // lighthouse tower centre, headland-local
	const LAMP = { x: 612, y: 80 }; // lighthouse lamp, headland-local
	const TRAWLER_PIVOT = { x: 409, y: 952 }; // waterline centre, trawler-local

	const KEYS = [
		'stormSky', 'stormSea', 'stormHeadland', 'stormTrawler', 'stormDock',
		'fxNoise', 'fxRain', 'fxFog', 'fxGlow', 'fxBeam',
	] as const;
</script>

<script lang="ts">
	import * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { getContextParent } from 'pixi-svelte';

	import { getContext } from '../game/context';

	const context = getContext();
	const parent = getContextParent();

	const root = new PIXI.Container();
	root.zIndex = -9;
	parent.addToParent(root);

	let built = false;
	let tick: ((t: PIXI.Ticker) => void) | undefined;

	const rand = (a: number, b: number) => a + Math.random() * (b - a);

	/** Jagged bolt from a to b by midpoint displacement, with a few forks. */
	function boltPaths(ax: number, ay: number, bx: number, by: number, rough: number) {
		const split = (p: number[][], d: number): number[][] => {
			if (d < 6) return p;
			const out: number[][] = [p[0]];
			for (let i = 1; i < p.length; i++) {
				const [x0, y0] = p[i - 1];
				const [x1, y1] = p[i];
				const len = Math.hypot(x1 - x0, y1 - y0);
				const nx = -(y1 - y0) / len;
				const ny = (x1 - x0) / len;
				const off = (Math.random() - 0.5) * d;
				out.push([(x0 + x1) / 2 + nx * off, (y0 + y1) / 2 + ny * off], [x1, y1]);
			}
			return split(out, d * 0.55);
		};
		const main = split([[ax, ay], [bx, by]], rough);
		const paths = [main];
		for (let f = 0; f < 3; f++) {
			const i = Math.floor(rand(0.15, 0.7) * main.length);
			const [sx, sy] = main[i];
			const len = Math.hypot(bx - ax, by - ay) * rand(0.2, 0.4);
			const ang = Math.atan2(by - ay, bx - ax) + rand(-0.9, 0.9);
			paths.push(split([[sx, sy], [sx + Math.cos(ang) * len, sy + Math.sin(ang) * len]], rough * 0.5));
		}
		return paths;
	}

	function build() {
		const tex = (k: (typeof KEYS)[number]) => context.stateApp.loadedAssets[k] as PIXI.Texture;
		const noiseTex = tex('fxNoise');
		noiseTex.source.addressMode = 'repeat';

		const black = new PIXI.Graphics();
		root.addChild(black);

		// sky: slow billowing through a large, drifting displacement map
		const skyWrap = new PIXI.Container();
		const sky = new PIXI.Sprite(tex('stormSky'));
		const skyNoise = new PIXI.Sprite(noiseTex);
		skyNoise.renderable = false;
		skyNoise.scale.set(6);
		const skyDisp = new PIXI.DisplacementFilter({ sprite: skyNoise, scale: 26 });
		skyWrap.addChild(sky, skyNoise);
		skyWrap.filters = [skyDisp];
		root.addChild(skyWrap);

		// lightning lives between the clouds and everything on the water
		const boltLayer = new PIXI.Container();
		root.addChild(boltLayer);

		// sea: faster, finer ripple
		const seaWrap = new PIXI.Container();
		const sea = new PIXI.Sprite(tex('stormSea'));
		const seaNoise = new PIXI.Sprite(noiseTex);
		seaNoise.renderable = false;
		seaNoise.scale.set(2.2, 1.1);
		const seaDisp = new PIXI.DisplacementFilter({ sprite: seaNoise, scale: { x: 10, y: 16 } });
		seaWrap.addChild(sea, seaNoise);
		seaWrap.filters = [seaDisp];
		root.addChild(seaWrap);

		// drifting fog banks along the horizon
		const fog = new PIXI.TilingSprite({ texture: tex('fxFog'), width: 10, height: 10 });
		fog.alpha = 0.22;
		root.addChild(fog);

		// headland + lighthouse lamp and rotating beam
		const headWrap = new PIXI.Container();
		const headland = new PIXI.Sprite(tex('stormHeadland'));
		const beam = new PIXI.Sprite(tex('fxBeam'));
		beam.anchor.set(0, 0.5);
		beam.blendMode = 'add';
		beam.tint = 0xffe2a8;
		const lampGlow = new PIXI.Sprite(tex('fxGlow'));
		lampGlow.anchor.set(0.5);
		lampGlow.blendMode = 'add';
		lampGlow.tint = 0xffc870;
		headWrap.addChild(headland, beam, lampGlow);
		root.addChild(headWrap);

		// trawler pitching and heaving on the swell
		const trawlerWrap = new PIXI.Container();
		const trawler = new PIXI.Sprite(tex('stormTrawler'));
		trawler.pivot.set(TRAWLER_PIVOT.x, TRAWLER_PIVOT.y);
		trawlerWrap.addChild(trawler);
		root.addChild(trawlerWrap);

		const dock = new PIXI.Sprite(tex('stormDock'));
		root.addChild(dock);

		// two rain sheets at different depths, slanted by the wind
		const rainWrap = new PIXI.Container();
		rainWrap.rotation = 0.2;
		const rainFar = new PIXI.TilingSprite({ texture: tex('fxRain'), width: 10, height: 10 });
		const rainNear = new PIXI.TilingSprite({ texture: tex('fxRain'), width: 10, height: 10 });
		rainFar.alpha = 0.18;
		rainNear.alpha = 0.3;
		rainFar.tileScale.set(0.6);
		rainNear.tileScale.set(1.3);
		rainWrap.addChild(rainFar, rainNear);
		root.addChild(rainWrap);

		// lightning flash: sky brightness spike plus a cold wash over the whole scene
		const flashMatrix = new PIXI.ColorMatrixFilter();
		const flashWash = new PIXI.Graphics();
		flashWash.blendMode = 'add';
		root.addChild(flashWash);

		let t = 0;
		let nextStrike = 2500;
		let strike: { age: number; g: PIXI.Graphics; pulses: number[] } | null = null;
		let lastW = 0;
		let lastH = 0;
		let k = 1;

		const layout = (W: number, H: number) => {
			k = Math.max(W / SRC_W, H / SRC_H);
			const ox = (W - SRC_W * k) / 2;
			const oy = (H - SRC_H * k) / 2;
			const main = context.stateLayoutDerived.mainLayout();
			const side = Math.max(0, (W - 880 * main.scale) / 2);
			const narrow = side < W * 0.12;

			black.clear().rect(0, 0, W, H).fill(0x05090c);
			// oversize the displaced layers a touch so the displacement never pulls
			// transparent pixels in at the screen edges
			sky.scale.set(k * 1.03);
			sky.position.set(ox - SRC_W * k * 0.015, oy + LAYERS.sky.y * k - 10);
			sea.scale.set(k * 1.03, k);
			sea.position.set(ox - SRC_W * k * 0.015, oy + LAYERS.sea.y * k);
			// The tank's plinth must stand on the planks. Where the board sits high
			// (stacked layouts) lift the dock to meet it, scaling so it still
			// reaches the bottom of the screen.
			const board = context.stateGameDerived.boardLayout();
			const plinth = H / 2 + (board.y + TANK_PLINTH_BELOW_CENTRE - main.height / 2) * main.scale;
			const plankTop = oy + PLANK_TOP_Y * k;
			if (plinth < plankTop + 12 * k) {
				const d = Math.max(k, (H - plinth) / (SRC_H - PLANK_TOP_Y));
				dock.scale.set(d);
				dock.position.set(W / 2 - (SRC_W * d) / 2, plinth - (PLANK_TOP_Y - LAYERS.dock.y) * d - 6 * d);
			} else {
				dock.scale.set(k);
				dock.position.set(ox, oy + LAYERS.dock.y * k);
			}

			fog.width = W;
			fog.height = 240 * k * 2.2;
			fog.tileScale.set(k * 2.2);
			fog.y = oy + HORIZON_Y * k - fog.height * 0.6;

			if (narrow) {
				// stacked layouts: the board spans the width, so lift the tower and
				// masts into the band above it
				const hk = k * 0.75;
				headland.scale.set(hk);
				headWrap.position.set(W * 0.15 - TOWER_X * hk, H * 0.12 - LAMP.y * hk);
				const tk = k * 0.62;
				trawler.scale.set(tk);
				trawlerWrap.position.set(W * 0.85, H * 0.04 + TRAWLER_PIVOT.y * tk);
			} else {
				headland.scale.set(k);
				const towerX = Math.min(ox + TOWER_X * k, side * 0.78);
				headWrap.position.set(towerX - TOWER_X * k, oy + LAYERS.headland.y * k);
				trawler.scale.set(k);
				const cx = Math.max(ox + (LAYERS.trawler.x + TRAWLER_PIVOT.x) * k, W - side * 0.62);
				trawlerWrap.position.set(cx, oy + (LAYERS.trawler.y + TRAWLER_PIVOT.y) * k);
			}
			const hs = headland.scale.x;
			lampGlow.position.set(LAMP.x * hs, LAMP.y * hs);
			beam.position.copyFrom(lampGlow.position);

			const diag = Math.hypot(W, H) * 1.15;
			rainWrap.position.set(W / 2, H / 2);
			for (const r of [rainFar, rainNear]) {
				r.width = r.height = diag;
				r.position.set(-diag / 2, -diag / 2);
			}
			flashWash.clear().rect(0, 0, W, H).fill(0xbfe6ff);
			flashWash.alpha = 0;
		};

		const startStrike = (W: number, H: number) => {
			const leftSide = Math.random() < 0.5;
			const x = leftSide ? rand(0.06, 0.34) * W : rand(0.66, 0.94) * W;
			const horizon = (H - SRC_H * k) / 2 + HORIZON_Y * k;
			const g = new PIXI.Graphics();
			g.blendMode = 'add';
			for (const [i, p] of boltPaths(x + rand(-80, 80), -20, x + rand(-120, 120), horizon - rand(0, 40), 140 * k * 1.4).entries()) {
				const w = i === 0 ? 1 : 0.55;
				const draw = (width: number, color: number, alpha: number) => {
					g.moveTo(p[0][0], p[0][1]);
					for (const [px, py] of p.slice(1)) g.lineTo(px, py);
					g.stroke({ width: width * w, color, alpha, cap: 'round', join: 'round' });
				};
				draw(26 * k * 2, 0x5fb4ff, 0.12);
				draw(9 * k * 2, 0x9fd6ff, 0.45);
				draw(3 * k * 2, 0xffffff, 1);
			}
			boltLayer.addChild(g);
			// flicker: a few bright pulses in the first ~400ms
			strike = { age: 0, g, pulses: [0, rand(70, 110), rand(170, 260)] };
			// thunder follows the flash; the one-shot player won't restart a clip
			// that's still rolling, so a double strike doesn't stack
			const name = Math.random() < 0.7 ? 'sfx_thunder_close' : 'sfx_thunder_far';
			setTimeout(() => context.eventEmitter.broadcast({ type: 'soundOnce', name }), rand(120, 420));
		};

		tick = (ticker: PIXI.Ticker) => {
			const dt = ticker.deltaMS;
			t += dt;
			const { width: W, height: H } = context.stateLayoutDerived.canvasSizes();
			if (W !== lastW || H !== lastH) {
				layout(W, H);
				lastW = W;
				lastH = H;
			}

			skyNoise.x = -(t * 0.006) % (256 * 6);
			skyNoise.y = -(t * 0.002) % (256 * 6);
			seaNoise.x = -(t * 0.03) % (256 * 2.2);
			seaNoise.y = -(t * 0.018) % (256 * 1.1);
			sea.y = (H - SRC_H * k) / 2 + LAYERS.sea.y * k + Math.sin(t / 1700) * 3 * k;

			fog.tilePosition.x = -t * 0.012;

			// ship: pitch and heave slightly out of phase, like riding a swell
			trawler.rotation = Math.sin(t / 1100) * 0.032 + Math.sin(t / 2900) * 0.012;
			trawler.y = Math.sin(t / 1400 + 0.8) * 10 * k;

			// lighthouse beam turning about the vertical axis: its projected
			// length follows sin, and it flares toward us as it passes the viewer
			const a = (t / 7000) * Math.PI * 2;
			const s = Math.sin(a);
			const c = Math.cos(a);
			const hs = headland.scale.x;
			beam.scale.set(s * 1.5 * hs * 2, 0.55 * hs * 2);
			beam.alpha = 0.3 * Math.abs(s) ** 0.6 * (c < 0 ? 0.55 : 1);
			const flare = Math.max(0, c) ** 10;
			lampGlow.scale.set((0.9 + flare * 2.2 + Math.sin(t / 90) * 0.03) * hs * 2);
			lampGlow.alpha = 0.55 + flare * 0.45;

			rainFar.tilePosition.y = t * 0.55;
			rainNear.tilePosition.y = t * 1.1;

			// lightning
			nextStrike -= dt;
			if (!strike && nextStrike <= 0) {
				startStrike(W, H);
				nextStrike = rand(6000, 14000);
				if (Math.random() < 0.25) nextStrike = rand(500, 900); // double strike
			}
			if (strike) {
				strike.age += dt;
				const pulse = strike.pulses.reduce((m, p) => Math.max(m, Math.exp(-Math.max(0, strike!.age - p) / 60) * (strike!.age >= p ? 1 : 0)), 0);
				const tail = Math.exp(-strike.age / 260);
				strike.g.alpha = Math.min(1, pulse + tail * 0.4);
				flashWash.alpha = pulse * 0.16;
				flashMatrix.brightness(1 + pulse * 0.9, false);
				skyWrap.filters = pulse > 0.02 ? [skyDisp, flashMatrix] : [skyDisp];
				if (strike.age > 900) {
					strike.g.destroy();
					strike = null;
					flashWash.alpha = 0;
					skyWrap.filters = [skyDisp];
				}
			}
		};
		context.stateApp.pixiApplication?.ticker.add(tick);
	}

	$effect(() => {
		const loaded = context.stateApp.loadedAssets;
		if (built || !loaded || !KEYS.every((k) => loaded[k])) return;
		built = true;
		build();
	});

	onDestroy(() => {
		if (tick) context.stateApp.pixiApplication?.ticker.remove(tick);
	});
</script>

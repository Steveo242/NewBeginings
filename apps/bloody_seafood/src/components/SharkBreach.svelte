<script lang="ts">
	import * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { getContextParent } from 'pixi-svelte';
	import { stateBetDerived } from 'state-shared';

	import { getContext } from '../game/context';

	// MAX WIN: the great white (the H1 hero render) breaches out of the top of the tank,
	// jaws first, hangs at the top of its leap and drops back in, throwing a spray of
	// blood-tinged water where it breaks the surface. Board-local (the Win layer's board
	// container), drawn under the plaque. ~1.9 s, faster in turbo.
	const context = getContext();
	const parent = getContextParent();
	const root = new PIXI.Container();
	parent.addToParent(root);
	const app = context.stateApp.pixiApplication;
	const speed = Math.max(1, stateBetDerived.timeScale());
	const rand = (a: number, b: number) => a + Math.random() * (b - a);

	const board = context.stateGameDerived.boardLayout();
	const B = board.height;
	const surface = -B * 0.5; // the tank's waterline: the top of the board
	const shark = new PIXI.Sprite((context.stateApp.loadedAssets?.fxSharkBreach as PIXI.Texture) ?? PIXI.Texture.EMPTY);
	shark.anchor.set(0.5, 0.35);
	const sh = B * 0.9;
	shark.scale.set(sh / Math.max(1, shark.texture.height));
	shark.visible = false;
	root.addChild(shark);

	const spray = Array.from({ length: 70 }, () => {
		const blood = Math.random() < 0.35;
		const g = new PIXI.Graphics()
			.poly([1, 0, 0.7, 0.62, 0, 0.8, -0.8, 0.45, -3.2, 0, -0.8, -0.45, 0, -0.8, 0.7, -0.62])
			.fill({ color: blood ? 0x7a080c : 0xd8efff, alpha: blood ? 0.9 : 0.6 });
		g.visible = false;
		root.addChild(g);
		return { g, x: rand(-0.25, 0.25) * B, vx: rand(-0.7, 0.7) * B, vy: -rand(0.6, 1.5) * B, size: rand(0.008, 0.02) * B, delay: rand(0, 120) };
	});

	const easeOut = (x: number) => 1 - (1 - x) ** 3;
	const easeIn = (x: number) => x ** 2.2;
	const START = 250; // after the plaque pops
	const UP = 650;
	const HANG = 350;
	const DOWN = 600;
	let t = 0;
	const tick = (ticker: PIXI.Ticker) => {
		t += ticker.deltaMS * speed;
		const a = t - START;
		const low = surface + sh * 0.9; // fully under the waterline, inside the tank
		// the top of the leap: the jaws ~0.12 board above the tank (desktop's board fills the
		// screen height, so a higher leap went off the top)
		const high = surface - B * 0.12 + sh * 0.35;
		if (a < 0) return;
		shark.visible = a < UP + HANG + DOWN;
		if (a < UP) {
			const u = easeOut(a / UP);
			shark.y = low + (high - low) * u;
			shark.rotation = -0.22 + 0.12 * u;
			shark.alpha = Math.min(1, a / 120);
		} else if (a < UP + HANG) {
			const u = (a - UP) / HANG;
			shark.y = high - Math.sin(Math.PI * u) * B * 0.02;
			shark.rotation = -0.1 + 0.18 * u;
		} else {
			const u = easeIn(Math.min(1, (a - UP - HANG) / DOWN));
			shark.y = high + (low - high) * u;
			shark.rotation = 0.08 + 0.3 * u;
			shark.alpha = 1 - Math.max(0, u - 0.7) / 0.3;
		}
		// the spray where it breaks the surface, thrown up and falling back
		for (const d of spray) {
			const s = (a - 120 - d.delay) / 1000;
			const life = 1.1;
			d.g.visible = s > 0 && s < life;
			if (!d.g.visible) continue;
			d.g.position.set(d.x + d.vx * s, surface + d.vy * s + 1.6 * B * s * s);
			d.g.scale.set(d.size, d.size);
			d.g.rotation = Math.atan2(d.vy + 3.2 * B * s, d.vx);
			d.g.alpha = Math.min(1, (life - s) * 3);
		}
		if (a > UP + HANG + DOWN + 600) app?.ticker.remove(tick);
	};
	app?.ticker.add(tick);
	onDestroy(() => {
		app?.ticker.remove(tick);
		root.destroy({ children: true });
	});
</script>

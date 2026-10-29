<script lang="ts">
	// The game opens by smashing the tank's front glass: a strike, cracks racing out from
	// it, then the pane bursts into shards that fly at the camera and fall away. With the
	// pane gone the reels are seen directly - the glass's reflections were a film of added
	// light over every symbol (BoardFront drew it at half strength and it still hazed them).
	import * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { getContextParent } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { glass } from '../game/glass.svelte';

	const context = getContext();
	const parent = getContextParent();

	const root = new PIXI.Container();
	parent.addToParent(root);

	/** the glass opening, as a share of the board width (BoardFrame's OPENING_RATIO) */
	const OPENING_RATIO = 720 / 700;
	const DELAY_MS = 900;
	const CRACK_MS = 160;
	const FLY_MS = 1300;

	type Pt = [number, number];
	const rand = (a: number, b: number) => a + Math.random() * (b - a);

	/** Sutherland-Hodgman: clip a polygon to the box [0, w] x [0, h]. */
	const clip = (poly: Pt[], w: number, h: number) => {
		const edges: [(p: Pt) => boolean, (a: Pt, b: Pt) => Pt][] = [
			[(p) => p[0] >= 0, (a, b) => [0, a[1] + ((b[1] - a[1]) * (0 - a[0])) / (b[0] - a[0])]],
			[(p) => p[0] <= w, (a, b) => [w, a[1] + ((b[1] - a[1]) * (w - a[0])) / (b[0] - a[0])]],
			[(p) => p[1] >= 0, (a, b) => [a[0] + ((b[0] - a[0]) * (0 - a[1])) / (b[1] - a[1]), 0]],
			[(p) => p[1] <= h, (a, b) => [a[0] + ((b[0] - a[0]) * (h - a[1])) / (b[1] - a[1]), h]],
		];
		let out = poly;
		for (const [inside, cut] of edges) {
			const input = out;
			out = [];
			for (let i = 0; i < input.length; i++) {
				const a = input[(i + input.length - 1) % input.length];
				const b = input[i];
				if (inside(b)) {
					if (!inside(a)) out.push(cut(a, b));
					out.push(b);
				} else if (inside(a)) out.push(cut(a, b));
			}
			if (!out.length) break;
		}
		return out;
	};

	type Shard = { g: PIXI.Graphics; x0: number; y0: number; vx: number; vy: number; vr: number; grow: number; delay: number };

	let tick: (() => void) | undefined;

	const smash = () => {
		const layout = context.stateGameDerived.boardLayout();
		const size = layout.width * OPENING_RATIO;
		root.position.set(layout.x - size / 2, layout.y - size / 2);

		// strike a little off centre, like a fist or a fin hit it
		const P: Pt = [size * rand(0.4, 0.6), size * rand(0.38, 0.55)];
		const RAYS = 16;
		const angles = Array.from({ length: RAYS }, (_, i) => ((i + rand(-0.3, 0.3)) / RAYS) * Math.PI * 2);
		const radii = [0, size * rand(0.06, 0.09), size * rand(0.17, 0.22), size * rand(0.3, 0.36), size * 0.52, size * 1.5];
		// each ray wanders a little per ring so the cells aren't a perfect web
		const at = (ray: number, ring: number): Pt => {
			const a = angles[ray % RAYS] + (ring ? Math.sin(ray * 7.1 + ring * 3.3) * 0.08 : 0);
			const r = radii[ring] * (ring ? 1 + Math.sin(ray * 4.7 + ring) * 0.12 : 1);
			return [P[0] + Math.cos(a) * r, P[1] + Math.sin(a) * r];
		};

		// cracks: the ray lines and ring segments, drawn growing out from the strike
		const cracks = new PIXI.Graphics();
		cracks.blendMode = 'add';
		const flash = new PIXI.Graphics().circle(P[0], P[1], size * 0.12).fill({ color: 0xffffff, alpha: 0.9 });
		flash.blendMode = 'add';
		const maskG = new PIXI.Graphics().rect(0, 0, size, size).fill(0xffffff);
		const crackLayer = new PIXI.Container();
		crackLayer.addChild(cracks, flash, maskG);
		crackLayer.mask = maskG;
		root.addChild(crackLayer);
		const drawCracks = (u: number) => {
			cracks.clear();
			const reach = u * size * 0.75;
			for (let i = 0; i < RAYS; i++) {
				cracks.moveTo(P[0], P[1]);
				for (let k = 1; k < radii.length; k++) {
					const [x, y] = at(i, k);
					const d = Math.hypot(x - P[0], y - P[1]);
					if (d > reach) {
						const [px, py] = at(i, k - 1);
						const pd = Math.hypot(px - P[0], py - P[1]);
						const f = Math.max(0, (reach - pd) / (d - pd));
						cracks.lineTo(px + (x - px) * f, py + (y - py) * f);
						break;
					}
					cracks.lineTo(x, y);
				}
			}
			for (let k = 1; k < radii.length - 1; k++) {
				if (radii[k] > reach) break;
				for (let i = 0; i < RAYS; i++) {
					const a = at(i, k);
					const b = at(i + 1, k);
					cracks.moveTo(a[0], a[1]).lineTo(b[0], b[1]);
				}
			}
			cracks.stroke({ width: 3, color: 0xffffff, alpha: 0.9 });
		};

		// shards: one per cell, clipped to the pane
		const shards: Shard[] = [];
		const shardLayer = new PIXI.Container();
		for (let i = 0; i < RAYS; i++) {
			for (let k = 0; k < radii.length - 1; k++) {
				const poly = clip(k === 0 ? [at(i, 0), at(i, 1), at(i + 1, 1)] : [at(i, k), at(i, k + 1), at(i + 1, k + 1), at(i + 1, k)], size, size);
				if (poly.length < 3) continue;
				const cx = poly.reduce((s, p) => s + p[0], 0) / poly.length;
				const cy = poly.reduce((s, p) => s + p[1], 0) / poly.length;
				const local = poly.flatMap(([x, y]) => [x - cx, y - cy]);
				const g = new PIXI.Graphics()
					.poly(local)
					.fill({ color: 0xd8f4ff, alpha: 0.2 })
					.poly(local)
					.stroke({ width: 3, color: 0xffffff, alpha: 0.85 });
				g.position.set(cx, cy);
				g.visible = false;
				const dx = cx - P[0];
				const dy = cy - P[1];
				const dist = Math.hypot(dx, dy) || 1;
				// near the strike they go fast; the outer pane mostly drops
				const speed = size * rand(0.5, 1.1) * Math.max(0.3, 1 - dist / size);
				shards.push({
					g,
					x0: cx,
					y0: cy,
					vx: (dx / dist) * speed,
					vy: (dy / dist) * speed - size * rand(0.1, 0.35),
					vr: rand(-5, 5),
					grow: rand(0.5, 1.4) * Math.max(0.3, 1 - dist / size),
					delay: (dist / size) * 120,
				});
				shardLayer.addChild(g);
			}
		}
		root.addChild(shardLayer);

		context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_glass_shatter' });
		// wall clock, not the ticker's capped deltas: a slow device still finishes on time
		const start = performance.now();
		tick = () => {
			const age = performance.now() - start;
			if (age < CRACK_MS) {
				drawCracks(age / CRACK_MS);
				flash.alpha = 1 - age / CRACK_MS;
				return;
			}
			if (glass.intact) {
				glass.intact = false;
				crackLayer.destroy({ children: true });
			}
			const ft = age - CRACK_MS;
			for (const s of shards) {
				const tt = Math.max(0, ft - s.delay) / 1000;
				s.g.visible = true;
				s.g.position.set(s.x0 + s.vx * tt, s.y0 + s.vy * tt + size * 1.2 * tt * tt);
				s.g.rotation = s.vr * tt;
				s.g.scale.set(1 + s.grow * tt * 1.6);
				s.g.alpha = Math.max(0, 1 - tt / (FLY_MS / 1000));
			}
			if (ft > FLY_MS + 150) {
				context.stateApp.pixiApplication?.ticker.remove(tick!);
				tick = undefined;
				root.destroy({ children: true });
			}
		};
		context.stateApp.pixiApplication?.ticker.add(tick);
	};

	const timer = setTimeout(() => {
		if (glass.intact) smash();
	}, DELAY_MS);

	onDestroy(() => {
		clearTimeout(timer);
		if (tick) context.stateApp.pixiApplication?.ticker.remove(tick);
	});
</script>

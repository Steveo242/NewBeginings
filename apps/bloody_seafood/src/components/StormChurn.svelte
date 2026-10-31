<script lang="ts">
	import * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { getContextParent } from 'pixi-svelte';

	import { getContext } from '../game/context';

	// The tank water churning as the storm hits (StormCinematic): a rush of bubbles boiling
	// up from the gravel in turbulent swirls, inside the tank's opening, board-local.
	type Props = { duration: number };
	const props: Props = $props();

	const context = getContext();
	const parent = getContextParent();
	const root = new PIXI.Container();
	parent.addToParent(root);
	const app = context.stateApp.pixiApplication;
	const rand = (a: number, b: number) => a + Math.random() * (b - a);

	const B = context.stateGameDerived.boardLayout().height;
	const half = B * 0.5;
	const mask = new PIXI.Graphics().rect(-half * 1.02, -half * 1.02, B * 1.04, B * 1.04).fill(0xffffff);
	root.addChild(mask);
	root.mask = mask;

	const bubbles = Array.from({ length: 80 }, () => {
		const g = new PIXI.Graphics().circle(0, 0, 1).fill({ color: 0xdff3ff, alpha: 0.18 }).stroke({ color: 0xffffff, width: 0.14, alpha: 0.7 });
		g.visible = false;
		root.addChild(g);
		return {
			g,
			x: rand(-0.48, 0.48) * B,
			delay: rand(0, 0.6),
			rise: rand(0.7, 1.4),
			size: rand(0.006, 0.02) * B,
			swirl: rand(0.02, 0.07) * B,
			freq: rand(4, 9),
			phase: Math.random() * Math.PI * 2,
		};
	});

	// wall-clock, so the churn always spans the cinematic even when frames drop
	const t0 = performance.now();
	const tick = () => {
		const t = (performance.now() - t0) / props.duration; // 0..1 over the cinematic
		for (const b of bubbles) {
			const u = (t - b.delay * 0.7) * b.rise * 1.6;
			b.g.visible = u > 0 && u < 1;
			if (!b.g.visible) continue;
			b.g.scale.set(b.size * (1 + u * 0.5));
			b.g.position.set(b.x + Math.sin(u * b.freq + b.phase) * b.swirl, half - u * B * 1.05);
			b.g.alpha = Math.min(1, u * 6) * Math.min(1, (1 - u) * 4);
		}
	};
	app?.ticker.add(tick);
	onDestroy(() => {
		app?.ticker.remove(tick);
		root.destroy({ children: true });
	});
</script>

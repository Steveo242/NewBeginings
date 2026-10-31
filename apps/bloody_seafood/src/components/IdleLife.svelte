<script lang="ts">
	import * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { getContextParent } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { BOARD_DIMENSIONS, SYMBOL_SIZE } from '../game/constants';
	import { idleLife } from '../game/idleLife.svelte';

	// Between spins the tank keeps living, quietly: now and then a stream of bubbles rises
	// from the gravel, a small fish drifts past far behind the symbols, a slow ripple of
	// light runs through the caustics (Caustics reads idleLife.ripple) and one resting
	// symbol takes a breath or (a fish) twitches (SymbolSprite reads idleLife.breath*). All of it is drawn under
	// the symbols, nothing glows, and it stops - fading out - the moment a round starts.
	// Cheap on phones: a pool of 10 circles and one sprite, no filters.
	type Props = { x: number; y: number; width: number; height: number };
	const props: Props = $props();

	const context = getContext();
	const parent = getContextParent();
	const root = new PIXI.Container();
	parent.addToParent(root);

	const rand = (a: number, b: number) => a + Math.random() * (b - a);

	// ------------------------------------------------------------- bubble stream
	const STREAM = 10;
	const bubbles = Array.from({ length: STREAM }, () => {
		const g = new PIXI.Graphics().circle(0, 0, 1).fill({ color: 0xdff3ff, alpha: 0.22 }).stroke({ color: 0xffffff, width: 0.16, alpha: 0.75 });
		g.visible = false;
		root.addChild(g);
		return { g, delay: 0, size: 1, wob: 0, phase: 0 };
	});
	let stream: { x: number; age: number } | null = null;

	// ------------------------------------------------------------- distant fish
	const fish = new PIXI.Sprite();
	fish.anchor.set(0.5);
	fish.visible = false;
	fish.tint = 0x2c4a66; // far back in the blue: a silhouette, not a symbol
	root.addChildAt(fish, 0);
	let swim: { age: number; dur: number; y: number } | null = null;

	// ------------------------------------------------------------- schedule
	let nextStream = rand(2500, 5000);
	let nextFish = rand(4000, 8000);
	let nextRipple = rand(3000, 6000);
	let nextBreath = rand(2000, 4000);
	let ripple = -1;
	let breath = -1;
	let quiet = 1; // 1 = idle, eases to 0 while a round plays

	const tick = (ticker: PIXI.Ticker) => {
		const dt = ticker.deltaMS;
		const idle = context.stateXstateDerived.isIdle();
		quiet += ((idle ? 1 : 0) - quiet) * Math.min(1, dt / 250);
		root.alpha = quiet;
		const W = props.width;
		const H = props.height;

		if (idle) {
			nextStream -= dt;
			nextFish -= dt;
			nextRipple -= dt;
			nextBreath -= dt;
		}
		// a stream of 6-10 bubbles from one spot on the gravel
		if (!stream && nextStream <= 0) {
			stream = { x: rand(0.08, 0.92) * W, age: 0 };
			const n = 6 + Math.floor(Math.random() * 5);
			bubbles.forEach((b, i) => {
				b.delay = i < n ? i * rand(110, 190) : Infinity;
				b.size = rand(0.006, 0.014) * H;
				b.wob = rand(0.004, 0.012) * W;
				b.phase = Math.random() * Math.PI * 2;
			});
			nextStream = rand(7000, 14000);
		}
		if (stream) {
			stream.age += dt;
			let alive = false;
			for (const b of bubbles) {
				const a = stream.age - b.delay;
				const u = a / 2600; // ~2.6 s to the surface
				b.g.visible = u > 0 && u < 1;
				if (!b.g.visible) {
					if (u <= 0) alive = true;
					continue;
				}
				alive = true;
				b.g.scale.set(b.size * (1 + u * 0.6));
				b.g.position.set(stream.x + Math.sin(a / 260 + b.phase) * b.wob, H * (1.02 - u * 1.04));
				b.g.alpha = Math.min(1, u * 8) * Math.min(1, (1 - u) * 5);
			}
			if (!alive) stream = null;
		}

		// a small fish crossing far behind the symbols, right to left (they face left)
		if (!swim && nextFish <= 0) {
			const key = ['h3.webp', 'h2.webp', 'h4.webp'][Math.floor(Math.random() * 3)];
			const t = context.stateApp.loadedAssets?.[key] as PIXI.Texture | undefined;
			if (t) {
				fish.texture = t;
				const s = (SYMBOL_SIZE * rand(0.48, 0.62)) / t.width;
				fish.scale.set(s);
				swim = { age: 0, dur: rand(9000, 13000), y: rand(0.2, 0.8) * H };
				fish.visible = true;
			}
			nextFish = rand(10000, 18000);
		}
		if (swim) {
			swim.age += dt;
			const u = swim.age / swim.dur;
			const span = W + SYMBOL_SIZE;
			fish.position.set(W + SYMBOL_SIZE * 0.5 - u * span, swim.y + Math.sin(swim.age / 900) * SYMBOL_SIZE * 0.06);
			fish.rotation = Math.sin(swim.age / 900 + 1.2) * 0.05;
			fish.alpha = 0.42 * Math.min(1, u * 6) * Math.min(1, (1 - u) * 6);
			if (u >= 1) {
				swim = null;
				fish.visible = false;
			}
		}

		// light ripple through the caustics: a 3 s swell
		if (ripple < 0 && nextRipple <= 0) {
			ripple = 0;
			nextRipple = rand(8000, 14000);
		}
		if (ripple >= 0) {
			ripple += dt / 3000;
			idleLife.ripple = ripple < 1 ? Math.sin(Math.PI * ripple) ** 2 * quiet : 0;
			if (ripple >= 1) ripple = -1;
		}

		// one resting symbol takes a breath (1.4 s) or twitches (0.5 s)
		if (breath < 0 && nextBreath <= 0) {
			breath = 0;
			idleLife.breathCell = `${Math.floor(Math.random() * BOARD_DIMENSIONS.x)}:${Math.floor(Math.random() * BOARD_DIMENSIONS.y)}`;
			// half are twitches: a quick flick (only the fish do it - SymbolSprite)
			idleLife.kind = Math.random() < 0.5 ? 'twitch' : 'breath';
			nextBreath = rand(2500, 5500);
		}
		if (breath >= 0) {
			breath += dt / (idleLife.kind === 'twitch' ? 520 : 1400);
			idleLife.breath = breath < 1 && idle ? breath : 0;
			if (breath >= 1 || !idle) {
				breath = -1;
				idleLife.breathCell = '';
				idleLife.breath = 0;
			}
		}
	};

	$effect(() => {
		root.position.set(props.x, props.y);
	});
	context.stateApp.pixiApplication?.ticker.add(tick);
	onDestroy(() => {
		context.stateApp.pixiApplication?.ticker.remove(tick);
		root.destroy({ children: true });
	});
</script>

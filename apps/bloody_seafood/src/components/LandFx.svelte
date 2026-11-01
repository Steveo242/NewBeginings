<script lang="ts" module>
	import type { RawSymbol } from '../game/types';

	export type EmitterEventLandFx = {
		type: 'landFx';
		name: 'S' | 'W';
		reelIndex: number;
		rawSymbol: RawSymbol;
		/** which anchor of the spin this is (1st, 2nd, 3rd+): the impact grows with it */
		n: number;
	};
</script>

<script lang="ts">
	import { Circle, Container, Rectangle, Sprite } from 'pixi-svelte';

	import BoardContainer from './BoardContainer.svelte';
	import { getContext } from '../game/context';
	import { BOARD_DIMENSIONS, BOARD_SIZES, SYMBOL_SIZE } from '../game/constants';
	import { getSymbolInfo, getSymbolX, getSymbolY } from '../game/utils';
	import { BEAT_MS } from '../game/tempo';

	// The special landings, drawn over the board (no halos: every glow is the symbol's own
	// silhouette added back on top of itself).
	// - SCATTER anchor: a gold shimmer across the mirror gold, a water ripple and a burst of
	//   bubbles, and a short board shake - all bigger for the 2nd and 3rd anchor of a spin.
	// - WILD: a red pulse through the blood letters and a burst of blood drops.
	// - While a reel anticipates: the settled reels dim a little, except their anchors,
	//   which beat with a soft gold heartbeat on the rope's pulse (Anticipations has the
	//   matching low heartbeat sound). The rope effect itself is Anticipation.svelte.
	// Nothing here holds up the spin: the effects run alongside the reels.
	const context = getContext();
	const app = context.stateApp.pixiApplication;

	type Drop = { dx: number; dy: number; vx: number; vy: number; r: number };
	type Burst = { id: number; name: 'S' | 'W'; x: number; y: number; n: number; t0: number; drops: Drop[] };

	let bursts = $state<Burst[]>([]);
	let now = $state(performance.now());
	let id = 0;
	const rand = (a: number, b: number) => a + Math.random() * (b - a);
	const S_MS = 900;
	const W_MS = 750;

	// while an anticipating reel is still dropping (its glow's out-animation lingers after)
	const anticipating = $derived(
		context.stateGame.board.some((reel) => reel.reelState.anticipating && reel.reelState.motion !== 'stopped'),
	);

	// one rAF clock while anything is on screen
	let raf = 0;
	const tick = () => {
		now = performance.now();
		bursts = bursts.filter((b) => now - b.t0 < (b.name === 'S' ? S_MS : W_MS));
		raf = bursts.length || anticipating ? requestAnimationFrame(tick) : 0;
	};
	const run = () => {
		if (!raf) raf = requestAnimationFrame(tick);
	};
	$effect(() => {
		if (anticipating) run();
	});
	$effect(() => () => cancelAnimationFrame(raf));

	// a short, decaying board shake (the stage, as BigWinFx does)
	const shake = (amp: number, ms: number) => {
		const stage = app?.stage;
		if (!stage) return;
		const home = { x: stage.x, y: stage.y };
		const k = context.stateLayoutDerived.canvasSizes().height / 1080;
		const t0 = performance.now();
		const step = () => {
			const u = (performance.now() - t0) / ms;
			if (u >= 1) return stage.position.set(home.x, home.y);
			const a = amp * k * (1 - u) ** 2;
			stage.position.set(home.x + rand(-a, a), home.y + rand(-a, a));
			requestAnimationFrame(step);
		};
		step();
	};

	context.eventEmitter.subscribeOnMount({
		landFx: (e) => {
			const reel = context.stateGame.board[e.reelIndex];
			const sym = reel?.reelState.symbols.find((s) => s.rawSymbol === e.rawSymbol);
			if (!sym) return;
			const x = getSymbolX(e.reelIndex);
			const y = getSymbolY(sym.symbolIndexOfBoard);
			const drops: Drop[] =
				e.name === 'W'
					? Array.from({ length: 12 }, () => {
							const a = rand(-Math.PI * 0.95, -Math.PI * 0.05);
							const v = rand(0.9, 1.9) * SYMBOL_SIZE;
							return { dx: rand(-0.15, 0.15), dy: rand(-0.1, 0.1), vx: Math.cos(a) * v, vy: Math.sin(a) * v, r: rand(0.035, 0.07) };
						})
					: Array.from({ length: 6 + 3 * e.n }, () => ({
							dx: rand(-0.3, 0.3),
							dy: rand(0.0, 0.35),
							vx: rand(-0.1, 0.1) * SYMBOL_SIZE,
							vy: -rand(0.5, 1.0) * SYMBOL_SIZE,
							r: rand(0.025, 0.06),
						}));
			bursts = [...bursts, { id: id++, name: e.name, x, y, n: e.n, t0: performance.now(), drops }];
			if (e.name === 'S') shake([2.5, 4.5, 7][Math.min(3, e.n) - 1], 160 + 60 * e.n);
			else shake(2.5, 150);
			run();
		},
	});

	const sInfo = getSymbolInfo({ rawSymbol: { name: 'S' } as RawSymbol, state: 'static' });
	const wInfo = getSymbolInfo({ rawSymbol: { name: 'W' } as RawSymbol, state: 'static' });
	const size = (info: typeof sInfo) => ({
		width: SYMBOL_SIZE * info.sizeRatios.width,
		height: SYMBOL_SIZE * info.sizeRatios.height,
	});

	/** a soft heartbeat: lub-dub on every beat of the rope's pulse */
	const heart = (t: number) => {
		const u = (t % BEAT_MS) / BEAT_MS;
		const thump = (c: number, w: number) => Math.exp(-(((u - c) / w) ** 2));
		return Math.min(1, thump(0.08, 0.06) + 0.6 * thump(0.3, 0.06));
	};

	// the anchors already on settled reels, for the anticipation heartbeat
	const settledAnchors = $derived(
		anticipating
			? context.stateGame.board.flatMap((reel, reelIndex) =>
					reel.reelState.motion === 'stopped' && !reel.reelState.anticipating
						? reel.reelState.symbols
								.filter((s) => s.rawSymbol.name === 'S' && s.symbolIndexOfBoard >= 0 && s.symbolIndexOfBoard < BOARD_DIMENSIONS.y)
								.map((s) => ({ x: getSymbolX(reelIndex), y: getSymbolY(s.symbolIndexOfBoard) }))
						: [],
				)
			: [],
	);
	const dimReels = $derived(
		anticipating
			? context.stateGame.board
					.map((reel, reelIndex) => ({ reel, reelIndex }))
					.filter(({ reel }) => reel.reelState.motion === 'stopped' && !reel.reelState.anticipating)
					.map(({ reelIndex }) => getSymbolX(reelIndex))
			: [],
	);
</script>

<BoardContainer>
	<!-- anticipation: dim the settled reels, then the anchors on them, undimmed and beating -->
	{#each dimReels as x (x)}
		<Rectangle {x} y={BOARD_SIZES.height * 0.5} anchor={0.5} width={SYMBOL_SIZE} height={BOARD_SIZES.height} backgroundColor={0x000000} backgroundAlpha={0.3} />
	{/each}
	{#each settledAnchors as a (`${a.x}:${a.y}`)}
		<Sprite x={a.x} y={a.y} anchor={0.5} key={sInfo.assetKey} {...size(sInfo)} />
		<Container x={a.x} y={a.y} scale={1 + 0.06 * heart(now)}>
			<Sprite anchor={0.5} key={sInfo.assetKey} {...size(sInfo)} tint={0xffc860} blendMode="add" alpha={0.55 * heart(now)} />
		</Container>
	{/each}

	{#each bursts as b (b.id)}
		{@const age = now - b.t0}
		{#if b.name === 'S'}
			{@const u = age / S_MS}
			{@const k = 0.8 + 0.2 * b.n}
			<!-- the shimmer: gold light running up through the anchor's own silhouette -->
			<Sprite x={b.x} y={b.y} anchor={0.5} key={sInfo.assetKey} {...size(sInfo)} tint={0xffe0a0} blendMode="add"
				alpha={Math.max(0, Math.sin(Math.min(1, age / 380) * Math.PI)) * 0.7 * k} />
			<!-- water ripple: two thin rings spreading from the impact -->
			{#each [0, 0.18] as lag}
				{@const v = Math.max(0, (u - lag) / (1 - lag))}
				{#if v > 0 && v < 1}
					<Circle x={b.x} y={b.y + SYMBOL_SIZE * 0.3} anchor={0.5} diameter={SYMBOL_SIZE * (0.4 + 0.9 * k * v)}
						borderColor={0xd8f4ff} borderWidth={3} borderAlpha={(1 - v) * 0.55} backgroundAlpha={0} />
				{/if}
			{/each}
			<!-- bubbles rising off it -->
			{#each b.drops as d, i (i)}
				{@const s = age / 1000}
				{#if u < 1}
					<Circle x={b.x + d.dx * SYMBOL_SIZE + d.vx * s + Math.sin(age / 90 + i) * SYMBOL_SIZE * 0.03}
						y={b.y + d.dy * SYMBOL_SIZE + d.vy * s} anchor={0.5} diameter={SYMBOL_SIZE * d.r * 2}
						borderColor={0xe8fbff} borderWidth={1.5} borderAlpha={0.7 * (1 - u)} backgroundColor={0xbfe9ff} backgroundAlpha={0.15 * (1 - u)} />
				{/if}
			{/each}
		{:else}
			{@const u = age / W_MS}
			<!-- a quick red pulse through the blood letters -->
			<Sprite x={b.x} y={b.y} anchor={0.5} key={wInfo.assetKey} {...size(wInfo)} tint={0xff2a20} blendMode="add"
				alpha={Math.max(0, Math.sin(Math.min(1, age / 300) * Math.PI)) * 0.6} />
			<!-- blood drops flung out of it, falling back under gravity -->
			{#each b.drops as d, i (i)}
				{@const s = age / 1000}
				<Circle x={b.x + d.dx * SYMBOL_SIZE + d.vx * s} y={b.y + d.dy * SYMBOL_SIZE + d.vy * s + 2.6 * SYMBOL_SIZE * s * s}
					anchor={0.5} diameter={SYMBOL_SIZE * d.r * 2 * (1 - u * 0.4)} backgroundColor={0x7a0509} backgroundAlpha={Math.min(1, (1 - u) * 2.5)} />
			{/each}
		{/if}
	{/each}
</BoardContainer>

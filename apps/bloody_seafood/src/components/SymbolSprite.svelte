<script lang="ts">
	import * as PIXI from 'pixi.js';
	import { BaseSprite, Container, Sprite } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';
	import { elasticOut } from 'svelte/easing';

	import { getSymbolInfo } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';
	import { getContext } from '../game/context';
	import { BEAT_MS, pulse as beatPulse } from '../game/tempo';
	import { shineBandTexture, sparkleTexture } from '../game/fxTextures';

	type Props = {
		x?: number;
		y?: number;
		symbolInfo: ReturnType<typeof getSymbolInfo>;
		oncomplete?: () => void;
		bounce?: boolean;
		/** Symbol is at rest (static/postWinStatic) - eligible for the idle bob. */
		idle?: boolean;
		/** Symbol is mid-tumble - eligible for the fall motion blur. */
		spinning?: boolean;
		/** Breathe in and out with the music (scatters and wilds, always). */
		pulse?: boolean;
		/** Polished metal: a light sweep across it and sparkling glints (the wild). */
		shine?: boolean;
	};

	const props: Props = $props();
	const context = getContext();

	// A tiny always-on bob + sway so a settled board never reads as a frozen
	// picture - reviewers flagged static symbols as looking like "flattened
	// high-res pictures" rather than integrated game elements. Deliberately
	// subtle (a couple of px, well under a degree of rotation): this has to
	// read as "alive" at a glance, not as visible jitter competing with the
	// land bounce or a win.  Phase is derived from this symbol's own board
	// position so neighbouring cells don't bob in lockstep, which would read
	// as a mechanical grid pulse rather than organic life.
	let t = $state(0);
	const tick = () => {
		t += context.stateApp.pixiApplication!.ticker.deltaMS;
	};
	if (context.stateApp.pixiApplication) {
		context.stateApp.pixiApplication.ticker.add(tick);
	}
	$effect(() => () => context.stateApp.pixiApplication?.ticker.remove(tick));

	const phase = $derived(((props.x ?? 0) * 0.37 + (props.y ?? 0) * 0.53) % (Math.PI * 2));
	const idleY = $derived(props.idle ? Math.sin(t / 1400 + phase) * SYMBOL_SIZE * 0.012 : 0);
	const idleRotation = $derived(
		props.idle ? Math.sin(t / 2100 + phase * 1.3) * 0.018 : 0,
	);
	const idleScale = $derived(props.idle ? 1 + Math.sin(t / 1700 + phase * 0.7) * 0.01 : 1);
	// scatters swell and settle every two beats, all in step: the phase comes from the
	// shared wall clock (read each tick - `t` only makes it reactive), not this symbol's t
	const beat = $derived.by(() => {
		void t;
		return props.pulse ? beatPulse(performance.now()) : 0;
	});
	const pulseScale = $derived(1 + 0.085 * beat);
	const pulseY = $derived(-SYMBOL_SIZE * 0.035 * beat);

	// Shine, on the shared clock like the pulse so every wild on the board flashes together.
	// A 4-beat cycle: the light sweeps across on the swell (u 0.17-0.33), glints follow round it.
	const SHINE_CYCLE = BEAT_MS * 4;
	const u = $derived.by(() => {
		void t;
		return props.shine ? (performance.now() % SHINE_CYCLE) / SHINE_CYCLE : 0;
	});
	const sweep = $derived(Math.min(1, Math.max(0, (u - 0.17) / 0.16)));
	const sweepOn = $derived(u > 0.17 && u < 0.33);
	// ring, stock ends, fluke tips, crown - as fractions of the drawn symbol, from its centre
	const GLINTS = [
		[0, -0.42, 0.36],
		[-0.3, -0.25, 0.5],
		[0.3, -0.25, 0.62],
		[-0.32, 0.22, 0.78],
		[0.32, 0.22, 0.9],
		[0, 0.43, 0.02],
	] as const;
	const glint = (at: number) => {
		const d = (u - at + 1) % 1;
		return d < 0.09 ? Math.sin((d / 0.09) * Math.PI) : 0;
	};

	const drawnW = $derived(
		SYMBOL_SIZE * props.symbolInfo.sizeRatios.width * scale.current * idleScale * pulseScale,
	);
	const drawnH = $derived(
		SYMBOL_SIZE * props.symbolInfo.sizeRatios.height * scale.current * idleScale * pulseScale,
	);
	const drawnY = $derived((props.y ?? 0) + idleY + pulseY);
	const drawnRotation = $derived(rotation.current + idleRotation);

	// Fall blur: a vertical-only streak while tumbling, cheap (one Pixi
	// BlurFilter, already a dependency) and removed the instant the symbol
	// isn't spinning so it never blurs a settled or landing frame.
	const spinFilters = $derived(
		props.spinning ? [new PIXI.BlurFilter({ strengthX: 0, strengthY: 6, quality: 2 })] : [],
	);

	// A quick squash-and-release on landing, not a full animation state -
	// every symbol just settles into place with a little life instead of
	// popping in dead-still. Starts pre-squashed and springs out to 1, so
	// the "impact" reads as instant rather than a delayed grow-in.
	// one beat: the landings were snappier than the music's pulse
	const BOUNCE_DURATION = Math.round(BEAT_MS);
	const scale = new Tween(1, { duration: BOUNCE_DURATION, easing: elasticOut });
	const rotation = new Tween(0, { duration: BOUNCE_DURATION, easing: elasticOut });

	// This component instance is reused across every state a symbol passes
	// through (static/land/win/...) rather than remounted, since the parent
	// {#if isSprite} branch never changes - so onMount only ever fires once,
	// long before a real 'land' transition happens. The trigger has to live
	// in an $effect, which reruns every time `bounce` flips, not just once.
	$effect(() => {
		props.symbolInfo;
		if (props.bounce) {
			scale.set(0.82, { duration: 0 });
			rotation.set(Math.random() < 0.5 ? -0.07 : 0.07, { duration: 0 });
			scale.set(1);
			rotation.set(0);
			const timeout = setTimeout(() => props.oncomplete?.(), BOUNCE_DURATION);
			return () => clearTimeout(timeout);
		}
		props.oncomplete?.();
	});
</script>

<Sprite
	x={props.x}
	y={drawnY}
	anchor={0.5}
	key={props.symbolInfo.assetKey}
	width={drawnW}
	height={drawnH}
	rotation={drawnRotation}
	filters={spinFilters}
/>

{#if props.shine}
	<!-- gleam: the gold itself brightens on the swell -->
	<Sprite
		x={props.x}
		y={drawnY}
		anchor={0.5}
		key={props.symbolInfo.assetKey}
		width={drawnW}
		height={drawnH}
		rotation={drawnRotation}
		blendMode="add"
		alpha={0.1 + 0.3 * beat}
	/>
	<!-- the sweep, clipped to the symbol's own silhouette -->
	{#if sweepOn}
		<Container x={props.x} y={drawnY} rotation={drawnRotation}>
			<Sprite isMask key={props.symbolInfo.assetKey} anchor={0.5} width={drawnW} height={drawnH} />
			<BaseSprite
				texture={shineBandTexture()}
				anchor={0.5}
				x={(sweep - 0.5) * drawnW * 1.6}
				width={drawnW * 0.34}
				height={drawnH * 2}
				rotation={0.45}
				blendMode="add"
				tint={0xfff2cc}
				alpha={0.95}
			/>
		</Container>
	{/if}
	{#each GLINTS as [gx, gy, at]}
		{@const g = glint(at)}
		{#if g > 0}
			<BaseSprite
				texture={sparkleTexture()}
				anchor={0.5}
				x={(props.x ?? 0) + gx * drawnW}
				y={drawnY + gy * drawnH}
				width={SYMBOL_SIZE * 0.32 * g}
				height={SYMBOL_SIZE * 0.32 * g}
				rotation={g * 0.6}
				blendMode="add"
				tint={0xfff6dc}
			/>
		{/if}
	{/each}
{/if}

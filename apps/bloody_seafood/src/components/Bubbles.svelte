<script lang="ts" module>
	export type Props = {
		/** How many bubbles in this layer. */
		count?: number;
		/** Drawing order relative to the rest of the scene. */
		zIndex?: number;
		/** Overall opacity multiplier - foreground layers want this low. */
		opacity?: number;
		/** Bubble diameter as a fraction of canvas height, min/max. */
		sizeRange?: [number, number];
		/** Rise speed in canvas-heights per second, min/max. */
		speedRange?: [number, number];
	};
</script>

<script lang="ts">
	import { Circle, Container } from 'pixi-svelte';
	import { onDestroy } from 'svelte';

	import { getContext } from '../game/context';

	const {
		count = 26,
		zIndex = -1,
		opacity = 1,
		sizeRange = [0.012, 0.045],
		speedRange = [0.05, 0.14],
	}: Props = $props();

	const context = getContext();
	const sizes = $derived(context.stateLayoutDerived.canvasSizes());

	let t = $state(0);
	const tick = () => {
		t += context.stateApp.pixiApplication!.ticker.deltaMS;
	};
	if (context.stateApp.pixiApplication) {
		context.stateApp.pixiApplication.ticker.add(tick);
	}
	onDestroy(() => {
		context.stateApp.pixiApplication?.ticker.remove(tick);
	});

	// Per-bubble constants, drawn once. Positions are derived from the shared
	// clock rather than mutated per frame, so this stays declarative like
	// Background.svelte and survives resizes (everything is a fraction of
	// canvas size, resolved at render time).
	const lerp = (a: number, b: number, v: number) => a + (b - a) * v;
	const bubbles = Array.from({ length: count }, () => {
		const r = Math.random();
		return {
			xFrac: Math.random(),
			sizeFrac: lerp(sizeRange[0], sizeRange[1], r),
			// Bigger bubbles rise faster, as they do in water.
			speed: lerp(speedRange[0], speedRange[1], r) / 1000,
			wobbleFrac: lerp(0.004, 0.022, Math.random()),
			wobblePeriod: lerp(1400, 3600, Math.random()),
			phase: Math.random() * Math.PI * 2,
			offset: Math.random(),
			alpha: lerp(0.18, 0.5, Math.random()),
		};
	});
</script>

<Container {zIndex}>
	{#each bubbles as bubble, i (i)}
		{@const diameter = bubble.sizeFrac * sizes.height}
		{@const travel = sizes.height + diameter * 2}
		{@const progress = (bubble.offset + t * bubble.speed) % 1}
		{@const y = sizes.height + diameter - progress * travel}
		{@const x =
			bubble.xFrac * sizes.width +
			Math.sin(t / bubble.wobblePeriod + bubble.phase) * bubble.wobbleFrac * sizes.width}
		<Circle
			{x}
			{y}
			{diameter}
			anchor={{ x: 0.5, y: 0.5 }}
			backgroundColor={0xdff3ff}
			backgroundAlpha={bubble.alpha * 0.28 * opacity}
			borderColor={0xffffff}
			borderWidth={Math.max(1, diameter * 0.07)}
			borderAlpha={bubble.alpha * opacity}
		/>
	{/each}
</Container>

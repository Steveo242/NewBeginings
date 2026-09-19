<script lang="ts" module>
	export type Props = {
		/** Area the bubbles fill, in the parent container's coordinates. */
		width: number;
		height: number;
		x?: number;
		y?: number;
		/** How many bubbles in this layer. */
		count?: number;
		/** Overall opacity multiplier. */
		opacity?: number;
		/** Bubble diameter as a fraction of `height`, min/max. */
		sizeRange?: [number, number];
		/** Rise speed in heights per second, min/max. */
		speedRange?: [number, number];
	};
</script>

<script lang="ts">
	import { Circle, Container } from 'pixi-svelte';
	import { onDestroy } from 'svelte';

	import { getContext } from '../game/context';

	const {
		width,
		height,
		x = 0,
		y = 0,
		count = 22,
		opacity = 1,
		sizeRange = [0.03, 0.1],
		speedRange = [0.06, 0.16],
	}: Props = $props();

	const context = getContext();

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

	// Per-bubble constants, drawn once. Positions derive from the shared
	// clock rather than being mutated per frame, so this stays declarative
	// and survives resizes - every value is a fraction of the area passed
	// in, resolved at render time.
	const lerp = (a: number, b: number, v: number) => a + (b - a) * v;
	const bubbles = Array.from({ length: count }, () => {
		const r = Math.random();
		return {
			xFrac: Math.random(),
			sizeFrac: lerp(sizeRange[0], sizeRange[1], r),
			// Bigger bubbles rise faster, as they do in water.
			speed: lerp(speedRange[0], speedRange[1], r) / 1000,
			wobbleFrac: lerp(0.01, 0.05, Math.random()),
			wobblePeriod: lerp(1400, 3600, Math.random()),
			phase: Math.random() * Math.PI * 2,
			offset: Math.random(),
			alpha: lerp(0.2, 0.55, Math.random()),
		};
	});
</script>

<Container {x} {y}>
	{#each bubbles as bubble, i (i)}
		{@const diameter = bubble.sizeFrac * height}
		{@const travel = height + diameter * 2}
		{@const progress = (bubble.offset + t * bubble.speed) % 1}
		{@const by = height + diameter - progress * travel}
		{@const bx =
			bubble.xFrac * width +
			Math.sin(t / bubble.wobblePeriod + bubble.phase) * bubble.wobbleFrac * width}
		<Circle
			x={bx}
			y={by}
			{diameter}
			anchor={{ x: 0.5, y: 0.5 }}
			backgroundColor={0xdff3ff}
			backgroundAlpha={bubble.alpha * 0.26 * opacity}
			borderColor={0xffffff}
			borderWidth={Math.max(1, diameter * 0.08)}
			borderAlpha={bubble.alpha * opacity}
		/>
	{/each}
</Container>

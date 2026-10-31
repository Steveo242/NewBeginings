<script lang="ts">
	import { Container, Sprite } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	import { SYMBOL_SIZE } from '../game/constants';
	import { solidFilter } from '../game/fxTextures';
	import { SYMBOL_BOLT, storm } from '../game/lightning';
	import { getContext } from '../game/context';

	// A winning symbol's outline: a thin gold rim traced round its silhouette (colour from
	// game/lightning.ts), under the symbol, flaring a little as it wins and with the storm's
	// lightning. Never a light behind or round the symbol - an additive glow with a white
	// core read as a washed-out halo on every symbol.
	type Props = {
		x?: number;
		y?: number;
		name: string;
		/** the symbol's resting art, whose silhouette is traced */
		assetKey: string;
		sizeRatios: { width: number; height: number };
	};
	const props: Props = $props();
	const context = getContext();

	const hit = new Tween(0, { easing: cubicOut });
	$effect(() => {
		hit.set(1, { duration: 60 }).then(() => hit.set(0, { duration: 650 }));
	});

	let now = $state(performance.now());
	const tick = () => (now = performance.now());
	$effect(() => {
		const ticker = context.stateApp.pixiApplication?.ticker;
		if (!ticker) return;
		ticker.add(tick);
		return () => ticker.remove(tick);
	});

	// storm.pulse is a plain object written by Background: re-read it every tick
	const surge = $derived.by(() => {
		void now;
		return storm.pulse;
	});
	const bolt = $derived(SYMBOL_BOLT[props.name] ?? SYMBOL_BOLT.L1);
	/** the rim's width, in board units: thin, and only a touch wider on the storm's flash */
	const RIM_R = $derived(1.6 + 0.6 * surge);
	const DIRS = Array.from({ length: 12 }, (_, i) => [Math.cos((i / 12) * Math.PI * 2), Math.sin((i / 12) * Math.PI * 2)]);
	const w = $derived(SYMBOL_SIZE * props.sizeRatios.width);
	const h = $derived(SYMBOL_SIZE * props.sizeRatios.height);
</script>

<!-- A thin, crisp gold rim hugging the silhouette, drawn UNDER the symbol in normal blend:
	 the old version (12 additive gold copies 4-5 units out + a white-hot core) read as a
	 faded white halo round every winning symbol. No glow layer, no white, nothing spills. -->
<Container x={props.x} y={props.y} filters={[solidFilter(bolt.glow)]} alpha={Math.min(1, 0.55 + 0.35 * hit.current)}>
	{#each DIRS as [dx, dy]}
		<Sprite key={props.assetKey} anchor={0.5} x={dx * RIM_R} y={dy * RIM_R} width={w} height={h} />
	{/each}
</Container>

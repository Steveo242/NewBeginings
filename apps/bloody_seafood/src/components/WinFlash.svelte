<script lang="ts">
	import { Container, Sprite } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	import { SYMBOL_SIZE } from '../game/constants';
	import { solidFilter } from '../game/fxTextures';
	import { SYMBOL_BOLT, isHighValue, storm } from '../game/lightning';
	import { getContext } from '../game/context';

	// A winning symbol's own lightning: its silhouette traced in that symbol's colour
	// (game/lightning.ts) - a thin coloured glow round a bright core, flickering like an
	// arc. It is the only win indicator, and deliberately restrained: an outline, never a
	// light behind the symbol (the old bloom and cell boxes washed the art out - the gold
	// anchor became unreadable). It flares as the symbol wins and surges with the storm.
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

	const high = $derived(isHighValue(props.name));
	const bolt = $derived(SYMBOL_BOLT[props.name] ?? SYMBOL_BOLT.L1);
	/** a new random arc state ~20 times a second: the flicker and the jitter */
	const frame = $derived(Math.floor(now / 50));
	const rnd = (k: number) => {
		const v = Math.sin(frame * 12.9898 + k * 78.233) * 43758.5453;
		return v - Math.floor(v);
	};
	const flicker = $derived(0.7 + 0.3 * rnd(1));
	// storm.pulse is a plain object written by Background: re-read it every tick
	const surge = $derived.by(() => {
		void now;
		return storm.pulse;
	});
	const level = $derived(Math.min(1, 0.55 * ((high ? 1 : 0.85) * flicker + 0.6 * hit.current + surge * 0.5)));
	/** glow and core radii, in board units */
	const GLOW_R = $derived((high ? 5 : 4.2) * (1 + 0.2 * surge) + rnd(2));
	const CORE_R = $derived((high ? 2 : 1.7) + 0.5 * rnd(3));
	const DIRS = Array.from({ length: 12 }, (_, i) => [Math.cos((i / 12) * Math.PI * 2), Math.sin((i / 12) * Math.PI * 2)]);
	const w = $derived(SYMBOL_SIZE * props.sizeRatios.width);
	const h = $derived(SYMBOL_SIZE * props.sizeRatios.height);
</script>

<!-- the arc: a wide coloured glow, then a white-hot core hugging the silhouette -->
<Container x={props.x} y={props.y} filters={[solidFilter(bolt.glow)]} alpha={0.55 * level} blendMode="add">
	{#each DIRS as [dx, dy], i}
		<Sprite key={props.assetKey} anchor={0.5} x={dx * GLOW_R * (0.8 + 0.4 * rnd(10 + i))} y={dy * GLOW_R * (0.8 + 0.4 * rnd(30 + i))} width={w} height={h} />
	{/each}
</Container>
<Container x={props.x} y={props.y} filters={[solidFilter(bolt.mid)]} alpha={0.75 * level} blendMode="add">
	{#each DIRS as [dx, dy]}
		<Sprite key={props.assetKey} anchor={0.5} x={dx * CORE_R} y={dy * CORE_R} width={w} height={h} />
	{/each}
</Container>

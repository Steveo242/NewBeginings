<script lang="ts">
	import { Container, Rectangle, Sprite } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	import { SYMBOL_SIZE } from '../game/constants';
	import { solidFilter } from '../game/fxTextures';
	import { pulse } from '../game/tempo';
	import { getContext } from '../game/context';

	// The light on a winning symbol, in two colours so the eye reads both at once: the
	// symbol's own silhouette traced in a glowing outline (crimson on the fish and the
	// wild, electric cyan on the lows) and its reel square boxed in hot gold. Both punch
	// in white-hot the instant the symbol wins, then hold, breathing with the music,
	// until the winning cluster explodes.
	type Props = {
		x?: number;
		y?: number;
		premium: boolean;
		/** the symbol's resting art, whose silhouette gets the outline */
		assetKey: string;
		sizeRatios: { width: number; height: number };
	};
	const props: Props = $props();
	const context = getContext();

	const flash = new Tween(0, { easing: cubicOut });
	$effect(() => {
		flash.set(1, { duration: 70 }).then(() => flash.set(0, { duration: 560 }));
	});

	let now = $state(performance.now());
	const tick = () => (now = performance.now());
	$effect(() => {
		const ticker = context.stateApp.pixiApplication?.ticker;
		if (!ticker) return;
		ticker.add(tick);
		return () => ticker.remove(tick);
	});
	const beat = $derived(pulse(now, 1));
	const hold = $derived(Math.max(flash.current, 0.55 + 0.45 * beat));

	const OUTLINE = $derived(props.premium ? 0xff2d55 : 0x3ff0ff);
	const SQUARE = 0xffc93a;
	/** outline thickness, in board units: the silhouette drawn this far out all round */
	const R = 6;
	const DIRS = Array.from({ length: 12 }, (_, i) => [Math.cos((i / 12) * Math.PI * 2), Math.sin((i / 12) * Math.PI * 2)]);
	const w = $derived(SYMBOL_SIZE * props.sizeRatios.width);
	const h = $derived(SYMBOL_SIZE * props.sizeRatios.height);
	const grow = $derived(1 + 0.3 * (1 - flash.current) * (flash.current > 0.01 ? 1 : 0));
	const CELL = SYMBOL_SIZE * 0.96;
</script>

<!-- the square: a hot gold box round the reel cell, with a soft bloom -->
<Sprite
	key="fxGlow"
	anchor={0.5}
	x={props.x}
	y={props.y}
	width={SYMBOL_SIZE * (props.premium ? 2.4 : 1.9) * grow}
	height={SYMBOL_SIZE * (props.premium ? 2.4 : 1.9) * grow}
	tint={SQUARE}
	alpha={0.35 * hold + 0.6 * flash.current}
	blendMode="add"
/>
<Rectangle
	anchor={0.5}
	x={props.x}
	y={props.y}
	width={CELL}
	height={CELL}
	borderRadius={CELL * 0.12}
	backgroundAlpha={0}
	borderColor={flash.current > 0.5 ? 0xffffff : SQUARE}
	borderWidth={4 + 3 * flash.current}
	alpha={hold}
/>

<!-- the outline: the symbol's silhouette, painted flat and drawn offset all round it -->
<Container x={props.x} y={props.y} filters={[solidFilter(OUTLINE)]} alpha={hold} blendMode="add">
	{#each DIRS as [dx, dy]}
		<Sprite key={props.assetKey} anchor={0.5} x={dx * R} y={dy * R} width={w} height={h} />
	{/each}
</Container>

<!-- the white-hot hit -->
{#if flash.current > 0.01}
	<Sprite
		key="fxGlow"
		anchor={0.5}
		x={props.x}
		y={props.y}
		width={SYMBOL_SIZE * 1.1 * grow}
		height={SYMBOL_SIZE * 1.1 * grow}
		tint={0xffffff}
		alpha={flash.current * 0.75}
		blendMode="add"
	/>
{/if}

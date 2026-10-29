<script lang="ts">
	import { Sprite } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	import { SYMBOL_SIZE } from '../game/constants';

	// The hit of light the instant a symbol wins: a hot white core and a coloured bloom
	// that punch in within a frame or two and decay over half a second, under the win
	// animation itself. Premiums flash bigger and in gold, lows smaller in sea-glass cyan,
	// so the eye reads the size of a win before it reads the numbers.
	type Props = { x?: number; y?: number; premium: boolean };
	const props: Props = $props();

	const flash = new Tween(0, { easing: cubicOut });
	$effect(() => {
		flash.set(1, { duration: 70 }).then(() => flash.set(0, { duration: 560 }));
	});

	const BLOOM = $derived(props.premium ? 0xffc23a : 0x5ff2ff);
	const reach = $derived(props.premium ? 2.5 : 1.9);
	const grow = $derived(1 + 0.35 * (1 - flash.current));
</script>

{#if flash.current > 0.01}
	<Sprite
		key="fxGlow"
		anchor={0.5}
		x={props.x}
		y={props.y}
		width={SYMBOL_SIZE * reach * grow}
		height={SYMBOL_SIZE * reach * grow}
		tint={BLOOM}
		alpha={flash.current}
		blendMode="add"
	/>
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

<script lang="ts">
	import { Sprite } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	import { getSymbolInfo } from '../game/utils';
	import { GAME_SPEED, SYMBOL_SIZE } from '../game/constants';

	// The symbol itself bursting, under the explode sheet, in its own full colours: it swells and is
	// gone in the first third of the burst - without it the symbol just blinked out and
	// the splash played over an empty cell.
	type Props = {
		x?: number;
		y?: number;
		symbolInfo: ReturnType<typeof getSymbolInfo>;
	};

	const props: Props = $props();

	const POP_MS = Math.round(220 / GAME_SPEED);
	const progress = new Tween(0, { duration: POP_MS, easing: cubicOut });
	progress.set(1);

	const p = $derived(progress.current);
	const w = $derived(SYMBOL_SIZE * props.symbolInfo.sizeRatios.width * (1 + 0.3 * p));
	const h = $derived(SYMBOL_SIZE * props.symbolInfo.sizeRatios.height * (1 + 0.3 * p));
	const alpha = $derived(Math.max(0, 1 - Math.max(0, p - 0.25) / 0.75));
</script>

{#if alpha > 0}
	<Sprite x={props.x} y={props.y} anchor={0.5} key={props.symbolInfo.assetKey} width={w} height={h} {alpha} />
{/if}

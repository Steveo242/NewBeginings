<script lang="ts">
	import { Rectangle } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	import { getContext } from '../game/context';

	// While a reel anticipates a scatter the tank behind the symbols sinks into shadow, so
	// the anchors already down, glowing on top of it, are what the eye goes to. Drawn under
	// the symbols and exactly over the board, so nothing outside the frame darkens.
	const context = getContext();
	const board = $derived(context.stateGameDerived.boardLayout());
	const straining = $derived(
		context.stateGame.board.some(
			(reel) => reel.reelState.anticipating && reel.reelState.motion !== 'stopped',
		),
	);
	const dim = new Tween(0, { duration: 450, easing: cubicOut });
	$effect(() => {
		dim.set(straining ? 1 : 0, { duration: straining ? 700 : 350 });
	});
</script>

{#if dim.current > 0.01}
	<Rectangle
		x={board.x}
		y={board.y}
		anchor={0.5}
		width={board.width}
		height={board.height}
		backgroundColor={0x02060a}
		backgroundAlpha={0.32 * dim.current}
	/>
{/if}

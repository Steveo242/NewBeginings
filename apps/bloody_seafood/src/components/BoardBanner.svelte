<script lang="ts">
	import { Container, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { BOARD_SIZES } from '../game/constants';

	const context = getContext();

	const main = $derived(context.stateLayoutDerived.mainLayout());
	const board = $derived(context.stateGameDerived.boardLayout());

	/** Content aspect of title_plaque.png, measured off its alpha bounds. */
	const BANNER_ASPECT = 1.826;
	const MARGIN = 10;
	/** Never let the banner crowd the reels by outgrowing the board itself. */
	const MAX_WIDTH_RATIO = 0.92;

	// The board sits above centre, so the band over it is what is left between
	// the top of the design space and the board's own top edge. Fit the banner
	// to that band rather than to a fixed size, so it can never ride down over
	// the reels on a short canvas - it just gets smaller.
	const boardTop = $derived(board.y - BOARD_SIZES.height * 0.5);
	const available = $derived(Math.max(boardTop - MARGIN * 2, 0));

	const height = $derived(
		Math.min(available, (BOARD_SIZES.width * MAX_WIDTH_RATIO) / BANNER_ASPECT),
	);
	const width = $derived(height * BANNER_ASPECT);
	const centerY = $derived(boardTop - MARGIN - height * 0.5);
</script>

{#if height > 1}
	<Container x={board.x} y={centerY}>
		<Sprite key="titlePlaque" anchor={0.5} {width} {height} />
	</Container>
{/if}

<script lang="ts">
	import type { Graphics } from 'pixi.js';
	import { Container, Graphics as GraphicsNode, Rectangle, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { BOARD_DIMENSIONS, BOARD_SIZES, SYMBOL_SIZE } from '../game/constants';
	import Bubbles from './Bubbles.svelte';
	import Caustics from './Caustics.svelte';

	const context = getContext();
	// Faint solid separators, drawn into one Graphics rather than a Rectangle
	// per line so the grid costs a single display object.
	const GRID_LINE_WIDTH = 2;
	const GRID_LINE_ALPHA = 0.16;

	const drawGrid = (graphics: Graphics) => {
		for (let column = 1; column < BOARD_DIMENSIONS.x; column += 1) {
			graphics.rect(column * SYMBOL_SIZE - GRID_LINE_WIDTH * 0.5, 0, GRID_LINE_WIDTH, BOARD_SIZES.height);
		}
		for (let row = 1; row < BOARD_DIMENSIONS.y; row += 1) {
			graphics.rect(0, row * SYMBOL_SIZE - GRID_LINE_WIDTH * 0.5, BOARD_SIZES.width, GRID_LINE_WIDTH);
		}
		graphics.fill({ color: 0x000000, alpha: GRID_LINE_ALPHA });
	};
	// The tank renders cover 11.2 x 11.2 units (frame, lid handle and plinth) round the 7 x 7 grid, with a 7.2-unit opening.
	const FRAME_RATIO = 1120 / 700;
	const OPENING_RATIO = 720 / 700;
</script>

<!--
	Everything inside the aquarium, drawn UNDER the symbols: the rendered tank
	interior (back wall and side walls running into depth), drifting caustics and
	rising bubbles, masked to the frame opening. The frame itself and the glass
	are drawn over the symbols by BoardFront.
-->
{#if true}
	{@const layout = context.stateGameDerived.boardLayout()}
	{@const size = layout.width * FRAME_RATIO}
	{@const open = layout.width * OPENING_RATIO}
	{@const left = layout.x - open * 0.5}
	{@const top = layout.y - open * 0.5}
	<Sprite key="tankBack" anchor={0.5} x={layout.x} y={layout.y} width={size} height={size} />
	<Container>
		<Rectangle isMask x={left} y={top} width={open} height={open} />
		<Caustics x={left} y={top} width={open} height={open} />
		<Bubbles x={left} y={top} width={open} height={open} count={22} opacity={0.5} sizeRange={[0.018, 0.055]} />
		<GraphicsNode x={layout.x - BOARD_SIZES.width * 0.5} y={layout.y - BOARD_SIZES.height * 0.5} draw={drawGrid} />
	</Container>
{/if}

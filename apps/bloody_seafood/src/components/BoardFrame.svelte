<script lang="ts" module>
	export type EmitterEventBoardFrame =
		| { type: 'boardFrameGlowShow' }
		| { type: 'boardFrameGlowHide' };
</script>

<script lang="ts">
	import { Container, Rectangle, Sprite, SpineProvider, SpineTrack } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { BOARD_DIMENSIONS, BOARD_SIZES, SYMBOL_SIZE } from '../game/constants';
	import Bubbles from './Bubbles.svelte';

	const context = getContext();
	const GRID_LINE_WIDTH = 2;
	const GRID_LINE_ALPHA = 0.22;
	const SPINE_SCALE = { width: 0.59, height: 0.62 };
	const SPRITE_SCALE = { width: 880 / 700, height: 880 / 700 };
	const BG_RATIO = 1;
	const POSITION_ADJUSTMENT = 1;
	// Keeps the water inside the frame's border rather than under it.
	const WATER_INSET = 0.9;

	type AnimationName = 'reelhouse_glow_start' | 'reelhouse_glow_idle' | 'reelhouse_glow_exit';

	let animationName = $state<AnimationName | undefined>(undefined);
	let loop = $state(false);

	context.eventEmitter.subscribeOnMount({
		boardFrameGlowShow: () => {
			animationName = 'reelhouse_glow_start';
			loop = false;
		},
		boardFrameGlowHide: () => {
			if (animationName) animationName = 'reelhouse_glow_exit';
		},
	});
</script>

{#if animationName}
	<SpineProvider
		zIndex={-1}
		key="reelhouse"
		x={context.stateGameDerived.boardLayout().x * POSITION_ADJUSTMENT}
		y={context.stateGameDerived.boardLayout().y * POSITION_ADJUSTMENT}
		width={context.stateGameDerived.boardLayout().width * SPINE_SCALE.width}
		height={context.stateGameDerived.boardLayout().height * SPINE_SCALE.height}
	>
		<SpineTrack
			trackIndex={0}
			{animationName}
			{loop}
			listener={{
				complete: (entry) => {
					if (entry.animation) {
						if (entry.animation.name === 'reelhouse_glow_start') {
							animationName = 'reelhouse_glow_idle';
							loop = true;
						}

						if (entry.animation.name === 'reelhouse_glow_exit') {
							animationName = undefined;
							loop = false;
						}
					}
				},
			}}
		/>
	</SpineProvider>
{/if}

<Sprite
	key="frame_bg.png"
	anchor={0.5}
	x={context.stateGameDerived.boardLayout().x * POSITION_ADJUSTMENT}
	y={context.stateGameDerived.boardLayout().y * POSITION_ADJUSTMENT}
	width={context.stateGameDerived.boardLayout().width * BG_RATIO * SPRITE_SCALE.width}
	height={context.stateGameDerived.boardLayout().width * SPRITE_SCALE.height}
/>

<!--
	The reel window itself is water: the lit gradient plus a bubble field,
	sandwiched between the board's backing and its frame edge so the frame
	still draws over the top. Inset slightly so it fills the opening rather
	than running under the frame's border, and masked to that opening so no
	bubble escapes into the harbour scene behind.
-->
{#if true}
	{@const layout = context.stateGameDerived.boardLayout()}
	{@const w = layout.width * BG_RATIO * SPRITE_SCALE.width * WATER_INSET}
	{@const h = layout.width * SPRITE_SCALE.height * WATER_INSET}
	{@const left = layout.x * POSITION_ADJUSTMENT - w * 0.5}
	{@const top = layout.y * POSITION_ADJUSTMENT - h * 0.5}
	<Container>
		<Rectangle isMask x={left} y={top} width={w} height={h} />
		<Sprite key="boardWater" x={left} y={top} width={w} height={h} alpha={0.92} />
		<Bubbles
			x={left}
			y={top}
			width={w}
			height={h}
			count={22}
			opacity={0.55}
			sizeRange={[0.018, 0.055]}
		/>

		<!--
			Faint cell separators over the water, aligned to the symbol grid
			rather than the frame opening, so the reels read as a grid instead
			of symbols floating loose. Masked with the water, so the frame's
			border still covers the ends.
		-->
		{@const gridLeft = layout.x * POSITION_ADJUSTMENT - BOARD_SIZES.width * 0.5}
		{@const gridTop = layout.y * POSITION_ADJUSTMENT - BOARD_SIZES.height * 0.5}
		{#each Array.from({ length: BOARD_DIMENSIONS.x - 1 }) as _, index}
			<Rectangle
				x={gridLeft + (index + 1) * SYMBOL_SIZE - GRID_LINE_WIDTH * 0.5}
				y={gridTop}
				width={GRID_LINE_WIDTH}
				height={BOARD_SIZES.height}
				backgroundColor={0x000000}
				backgroundAlpha={GRID_LINE_ALPHA}
			/>
		{/each}
		{#each Array.from({ length: BOARD_DIMENSIONS.y - 1 }) as _, index}
			<Rectangle
				x={gridLeft}
				y={gridTop + (index + 1) * SYMBOL_SIZE - GRID_LINE_WIDTH * 0.5}
				width={BOARD_SIZES.width}
				height={GRID_LINE_WIDTH}
				backgroundColor={0x000000}
				backgroundAlpha={GRID_LINE_ALPHA}
			/>
		{/each}
	</Container>
{/if}

<Sprite
	key="frame_edge.png"
	anchor={0.5}
	x={context.stateGameDerived.boardLayout().x * POSITION_ADJUSTMENT}
	y={context.stateGameDerived.boardLayout().y * POSITION_ADJUSTMENT}
	width={context.stateGameDerived.boardLayout().width * BG_RATIO * SPRITE_SCALE.width}
	height={context.stateGameDerived.boardLayout().width * SPRITE_SCALE.height}
/>

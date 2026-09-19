<script lang="ts">
	import { Container, Rectangle } from 'pixi-svelte';
	import { stateUi } from 'state-shared';
	import type { LayoutUiProps } from 'components-ui-pixi/src/types';

	import { getContext } from '../game/context';
	import { BOARD_SIZES } from '../game/constants';

	const props: LayoutUiProps = $props();
	const context = getContext();

	const canvas = $derived(context.stateLayoutDerived.canvasSizes());
	const main = $derived(context.stateLayoutDerived.mainLayout());

	// One flat strip across the bottom, sized off the canvas so a single
	// layout serves every orientation - the shared Layout* components exist
	// to drive very different arrangements (side columns, a fold-out
	// drawer), which this deliberately replaces with a single row.
	const BAR_HEIGHT_RATIO = 0.13;
	const barHeight = $derived(Math.min(canvas.height * BAR_HEIGHT_RATIO, 190));
	const barTop = $derived(canvas.height - barHeight);
	const midY = $derived(barTop + barHeight * 0.5);

	// The controls track the board's on-screen width rather than the
	// canvas's, so they sit under the board instead of being flung out to
	// the screen edges. 880/700 is BoardFrame's frame sprite scale - the
	// frame is wider than the board grid itself - and OVERHANG lets the row
	// run slightly wider than the frame, but only slightly.
	const FRAME_SCALE = 880 / 700;
	const OVERHANG = 1.1;
	const boardScreenWidth = $derived(BOARD_SIZES.width * FRAME_SCALE * main.scale);
	const clusterWidth = $derived(
		Math.min(canvas.width * 0.96, boardScreenWidth * OVERHANG),
	);
	const clusterLeft = $derived(canvas.width * 0.5 - clusterWidth * 0.5);
	/** Position within the control cluster, 0 = left end, 1 = right end. */
	const at = (fraction: number) => clusterLeft + clusterWidth * fraction;

	// Controls are authored at UI_BASE_SIZE (150px); everything scales off
	// the bar height so the row stays proportional on any canvas.
	const unit = $derived(barHeight / 150);
	const iconScale = $derived(unit * 0.42);
	const smallScale = $derived(unit * 0.5);
	const spinScale = $derived(unit * 0.95);
	const labelScale = $derived(unit * 0.62);
</script>

<Container zIndex={60}>
	<!-- The strip spans the control cluster rather than the whole canvas, so
	     it reads as a bar under the board. Dark and semi-transparent so the
	     harbour behind it still shows. -->
	<Rectangle
		x={clusterLeft - barHeight * 0.2}
		y={barTop}
		width={clusterWidth + barHeight * 0.4}
		height={barHeight}
		borderRadius={barHeight * 0.18}
		backgroundColor={0x0a1a24}
		backgroundAlpha={0.82}
	/>

	<!-- Left: the incidental controls, smallest things in the row. -->
	<Container y={midY}>
		<Container x={at(0.02)} scale={iconScale}>
			{@render props.buttonGameRules({ anchor: 0.5 })}
		</Container>
		<Container x={at(0.075)} scale={iconScale}>
			{@render props.buttonPayTable({ anchor: 0.5 })}
		</Container>
		<Container x={at(0.13)} scale={iconScale}>
			{@render props.buttonSettings({ anchor: 0.5 })}
		</Container>
		<Container x={at(0.185)} scale={iconScale}>
			{@render props.buttonSoundSwitch({ anchor: 0.5 })}
		</Container>
	</Container>

	{#if !stateUi.freeSpinCounterShow}
		<Container x={at(0.27)} y={midY} scale={smallScale}>
			{@render props.buttonBuyBonus({ anchor: 0.5 })}
		</Container>
	{/if}

	<Container x={at(0.39)} y={midY} scale={labelScale}>
		{@render props.amountBalance({ stacked: true })}
	</Container>

	<Container x={at(0.52)} y={midY} scale={labelScale}>
		{@render props.amountWin({ stacked: true })}
	</Container>

	<!-- Right: play amount with its steppers, then the spin button. -->
	<Container x={at(0.65)} y={midY} scale={labelScale}>
		{@render props.amountBet({ stacked: true })}
	</Container>

	<Container x={at(0.745)} y={midY}>
		<Container y={-barHeight * 0.21} scale={iconScale}>
			{@render props.buttonIncrease({ anchor: 0.5 })}
		</Container>
		<Container y={barHeight * 0.21} scale={iconScale}>
			{@render props.buttonDecrease({ anchor: 0.5 })}
		</Container>
	</Container>

	<Container x={at(0.865)} y={midY} scale={spinScale}>
		{@render props.buttonBet({ anchor: 0.5 })}
	</Container>

	<Container x={at(0.97)} y={midY}>
		<Container y={-barHeight * 0.21} scale={iconScale}>
			{@render props.buttonAutoSpin({ anchor: 0.5 })}
		</Container>
		<Container y={barHeight * 0.21} scale={iconScale}>
			{@render props.buttonTurbo({ anchor: 0.5 })}
		</Container>
	</Container>
</Container>

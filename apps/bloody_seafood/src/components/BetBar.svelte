<script lang="ts">
	import { Container, Rectangle } from 'pixi-svelte';
	import { stateUi } from 'state-shared';
	import type { LayoutUiProps } from 'components-ui-pixi/src/types';

	import { getContext } from '../game/context';

	const props: LayoutUiProps = $props();
	const context = getContext();

	const canvas = $derived(context.stateLayoutDerived.canvasSizes());

	// One flat strip across the bottom of the canvas, sized off the canvas
	// itself so the same layout serves every orientation - the shared
	// LayoutDesktop/Portrait/Landscape split exists to drive very different
	// arrangements (side columns, a fold-out drawer), which this deliberately
	// replaces with a single row.
	const BAR_HEIGHT_RATIO = 0.13;
	const barHeight = $derived(Math.min(canvas.height * BAR_HEIGHT_RATIO, 190));
	const barTop = $derived(canvas.height - barHeight);
	const midY = $derived(barTop + barHeight * 0.5);

	// Controls are authored at UI_BASE_SIZE (150px); everything below scales
	// off the bar height so the row stays proportional on any canvas.
	const unit = $derived(barHeight / 150);
	const iconScale = $derived(unit * 0.42);
	const smallScale = $derived(unit * 0.5);
	const spinScale = $derived(unit * 0.95);
	const labelScale = $derived(unit * 0.62);

	const pad = $derived(barHeight * 0.55);
	const iconGap = $derived(barHeight * 0.52);
</script>

<Container zIndex={60}>
	<!-- The strip itself. Kept dark and semi-transparent so the water and
	     bubbles behind it still read, rather than a solid panel. -->
	<Rectangle
		x={0}
		y={barTop}
		width={canvas.width}
		height={barHeight}
		backgroundColor={0x0a1a24}
		backgroundAlpha={0.82}
	/>
	<Rectangle
		x={0}
		y={barTop}
		width={canvas.width}
		height={Math.max(2, barHeight * 0.018)}
		backgroundColor={0xc4601f}
		backgroundAlpha={0.9}
	/>

	<!-- Left: the incidental controls, smallest things in the row. -->
	<Container x={pad} y={midY}>
		<Container scale={iconScale}>
			{@render props.buttonGameRules({ anchor: 0.5 })}
		</Container>
		<Container x={iconGap} scale={iconScale}>
			{@render props.buttonPayTable({ anchor: 0.5 })}
		</Container>
		<Container x={iconGap * 2} scale={iconScale}>
			{@render props.buttonSettings({ anchor: 0.5 })}
		</Container>
		<Container x={iconGap * 3} scale={iconScale}>
			{@render props.buttonSoundSwitch({ anchor: 0.5 })}
		</Container>
	</Container>

	<!-- Buy bonus, then the two read-only amounts. -->
	{#if !stateUi.freeSpinCounterShow}
		<Container x={pad + iconGap * 4.5} y={midY} scale={smallScale}>
			{@render props.buttonBuyBonus({ anchor: 0.5 })}
		</Container>
	{/if}

	<Container x={canvas.width * 0.34} y={midY} scale={labelScale}>
		{@render props.amountBalance({ stacked: true })}
	</Container>

	<Container x={canvas.width * 0.5} y={midY} scale={labelScale}>
		{@render props.amountWin({ stacked: true })}
	</Container>

	<!-- Right: play amount with its steppers, then the spin button. -->
	<Container x={canvas.width * 0.66} y={midY} scale={labelScale}>
		{@render props.amountBet({ stacked: true })}
	</Container>

	<Container x={canvas.width * 0.755} y={midY}>
		<Container y={-barHeight * 0.21} scale={iconScale}>
			{@render props.buttonIncrease({ anchor: 0.5 })}
		</Container>
		<Container y={barHeight * 0.21} scale={iconScale}>
			{@render props.buttonDecrease({ anchor: 0.5 })}
		</Container>
	</Container>

	<Container x={canvas.width - pad - barHeight * 1.5} y={midY} scale={spinScale}>
		{@render props.buttonBet({ anchor: 0.5 })}
	</Container>

	<Container x={canvas.width - pad} y={midY}>
		<Container y={-barHeight * 0.21} scale={iconScale}>
			{@render props.buttonAutoSpin({ anchor: 0.5 })}
		</Container>
		<Container y={barHeight * 0.21} scale={iconScale}>
			{@render props.buttonTurbo({ anchor: 0.5 })}
		</Container>
	</Container>
</Container>

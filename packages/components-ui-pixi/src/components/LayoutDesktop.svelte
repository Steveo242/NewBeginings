<script lang="ts">
	import { stateUi } from 'state-shared';
	import { BLACK } from 'constants-shared/colors';
	import { MainContainer } from 'components-layout';
	import { Container, Rectangle, anchorToPivot } from 'pixi-svelte';

	import { DESKTOP_BASE_SIZE, DESKTOP_BACKGROUND_WIDTH_LIST } from '../constants';
	import { getContext } from '../context';
	import type { LayoutUiProps } from '../types';

	const props: LayoutUiProps = $props();
	const context = getContext();
</script>

<Container x={20}>
	{@render props.gameName()}
</Container>

<Container x={context.stateLayoutDerived.canvasSizes().width - 20}>
	{@render props.logo()}
</Container>

<MainContainer standard>
	<Container x={200} y={context.stateLayoutDerived.mainLayoutStandard().height * 0.5}>
		<Container y={-170} scale={0.8}>
			{@render props.buttonMenu({ anchor: 0.5 })}
		</Container>

		<Container y={0} scale={0.8}>
			{#if !stateUi.freeSpinCounterShow}{@render props.buttonBuyBonus({ anchor: 0.5 })}{/if}
		</Container>

		<Container y={170} scale={0.8}>
			{@render props.buttonAutoSpin({ anchor: 0.5 })}
		</Container>
	</Container>

	<Container
		x={context.stateLayoutDerived.mainLayoutStandard().width - 200}
		y={context.stateLayoutDerived.mainLayoutStandard().height * 0.5}
	>
		<Container y={-330} scale={0.72}>
			{@render props.amountBalance({ stacked: true })}
		</Container>

		<Container y={-250} scale={0.72}>
			{@render props.amountWin({ stacked: true })}
		</Container>

		<Container y={-170} scale={0.72}>
			{@render props.amountBet({ stacked: true })}
		</Container>

		<Container y={-40} scale={0.7}>
			{@render props.buttonIncrease({ anchor: 0.5 })}
		</Container>

		<Container y={110} scale={0.7}>
			{@render props.buttonBet({ anchor: 0.5 })}
		</Container>

		<Container y={260} scale={0.7}>
			{@render props.buttonDecrease({ anchor: 0.5 })}
		</Container>

		<Container y={410} scale={0.7}>
			{@render props.buttonTurbo({ anchor: 0.5 })}
		</Container>
	</Container>
</MainContainer>

{#if stateUi.menuOpen}
	<Rectangle
		eventMode="static"
		cursor="pointer"
		alpha={0.5}
		anchor={0.5}
		backgroundColor={BLACK}
		width={context.stateLayoutDerived.canvasSizes().width}
		height={context.stateLayoutDerived.canvasSizes().height}
		x={context.stateLayoutDerived.canvasSizes().width * 0.5}
		y={context.stateLayoutDerived.canvasSizes().height * 0.5}
		onpointerup={() => (stateUi.menuOpen = false)}
	/>

	<MainContainer standard alignVertical="bottom">
		<Container
			x={298}
			y={context.stateLayoutDerived.mainLayoutStandard().height - DESKTOP_BASE_SIZE - 10}
		>
			<Container scale={0.8} y={DESKTOP_BASE_SIZE * 0.5 - 150 - 170 * 3}>
				{@render props.buttonPayTable({ anchor: 0.5 })}
			</Container>

			<Container scale={0.8} y={DESKTOP_BASE_SIZE * 0.5 - 150 - 170 * 2}>
				{@render props.buttonGameRules({ anchor: 0.5 })}
			</Container>

			<Container scale={0.8} y={DESKTOP_BASE_SIZE * 0.5 - 150 - 170 * 1}>
				{@render props.buttonSettings({ anchor: 0.5 })}
			</Container>

			<Container scale={0.8} y={DESKTOP_BASE_SIZE * 0.5 - 150}>
				{@render props.buttonSoundSwitch({ anchor: 0.5 })}
			</Container>

			<Container scale={0.8} y={DESKTOP_BASE_SIZE * 0.5}>
				{@render props.buttonMenuClose({ anchor: 0.5 })}
			</Container>
		</Container>
	</MainContainer>
{/if}

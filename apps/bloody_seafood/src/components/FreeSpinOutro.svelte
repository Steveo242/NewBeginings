<script lang="ts" module>
	import type { WinLevelData } from '../game/winLevelMap';

	export type EmitterEventFreeSpinOutro =
		| { type: 'freeSpinOutroShow' }
		| { type: 'freeSpinOutroHide' }
		| { type: 'freeSpinOutroCountUp'; amount: number; winLevelData: WinLevelData };
</script>

<script lang="ts">
 import { Container } from "pixi-svelte";
 import { MainContainer } from "components-layout";
 import WinBanner from "./WinBanner.svelte";
 import WinAmountText from "./WinAmountText.svelte";
	import { Sprite, SpineProvider, SpineTrack, SpineSlot } from 'pixi-svelte';
	import { FadeContainer, WinCountUpProvider, ResponsiveBitmapText } from 'components-pixi';
	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';
	import { waitForResolve } from 'utils-shared/wait';
	import { CanvasSizeRectangle } from 'components-layout';
	import { OnMount } from 'components-shared';
	import { stateUrlDerived } from 'state-shared';

	import { getContext } from '../game/context';
	import { WIN_LEVEL_APPLAUSE_SFX } from '../game/bookEventHandlerMap';
	import FreeSpinAnimation from './FreeSpinAnimation.svelte';
	import PressToContinue from './PressToContinue.svelte';
	import WinCoins from './WinCoins.svelte';

	type AnimationName = 'intro' | 'idle';

	const context = getContext();

	let show = $state(true);
	let animationName = $state<AnimationName>('intro');
	let amount = $state(0);
	let winLevelData = $state<WinLevelData>();
	let oncomplete = $state(() => {});
	let onCountUpComplete = $state(() => {});

	context.eventEmitter.subscribeOnMount({
		freeSpinOutroShow: () => (show = true),
		freeSpinOutroHide: async () => (show = false),
		freeSpinOutroCountUp: async (emitterEvent) => {
			amount = emitterEvent.amount;
			winLevelData = emitterEvent.winLevelData;
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});
</script>

<FadeContainer {show}>
	{#if winLevelData}
		{@const duration = winLevelData.presentDuration}
		{@const isBigWin = winLevelData.type === 'big'}
		<WinCountUpProvider {amount} {duration} oncomplete={() => onCountUpComplete()}>
			{#snippet children({ countUpAmount, startCountUp, finishCountUp, countUpCompleted })}
				<OnMount
					onmount={async () => {
						await startCountUp();
						const applauseSfx = winLevelData
							? (WIN_LEVEL_APPLAUSE_SFX[winLevelData.alias] ?? 'sfx_applause')
							: 'sfx_applause';
						context.eventEmitter.broadcast({ type: 'soundStop', name: applauseSfx });
					}}
				/>

				<CanvasSizeRectangle backgroundColor={0x000000} backgroundAlpha={0.5} />

				<MainContainer>
  <Container x={context.stateGameDerived.boardLayout().x} y={context.stateGameDerived.boardLayout().y}>
    <WinBanner text="TOTAL HAUL" alias="big">
      <WinAmountText anchor={0.5} text={bookEventAmountToCurrencyString(countUpAmount)} style={{ fontSize: 100 }} />
    </WinBanner>
  </Container>
</MainContainer>

				{#if false}<WinCoins emit={!countUpCompleted} levelAlias={winLevelData?.alias} />{/if}

				<PressToContinue onpress={() => (countUpCompleted ? oncomplete() : finishCountUp())} />
			{/snippet}
		</WinCountUpProvider>
	{/if}
</FadeContainer>

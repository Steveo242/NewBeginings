<script lang="ts">
	import { onMount } from 'svelte';

	import { EnablePixiExtension } from 'components-pixi';
	import { EnableHotkey } from 'components-shared';
	import { MainContainer } from 'components-layout';
	import { App, Text, REM } from 'pixi-svelte';
	import { stateModal } from 'state-shared';

	import { UiGameName } from 'components-ui-pixi';
	import BetBarUI from './BetBarUI.svelte';
	import { GameVersion, Modals } from 'components-ui-html';
	import GameRules from './GameRules.svelte';
	import PayTable from './PayTable.svelte';

	import { getContext } from '../game/context';
	import { applyBetModeMeta } from '../game/betModeMeta';
	import EnableSound from './EnableSound.svelte';
	import EnableGameActor from './EnableGameActor.svelte';
	import ResumeBet from './ResumeBet.svelte';
	import Sound from './Sound.svelte';
	import Background from './Background.svelte';
	import LoadingScreen from './LoadingScreen.svelte';
	import BoardFrame from './BoardFrame.svelte';
	import BoardBanner from './BoardBanner.svelte';
	import Board from './Board.svelte';
	import Anticipations from './Anticipations.svelte';
	import ClusterWinAmounts from './ClusterWinAmounts.svelte';
	import TumbleBoard from './TumbleBoard.svelte';
	import TumbleWinAmount from './TumbleWinAmount.svelte';
	import GlobalMultiplier from './GlobalMultiplier.svelte';
	import MultiplierBoard from './MultiplierBoard.svelte';
	import MultiplierTotal from './MultiplierTotal.svelte';
	import Win from './Win.svelte';
	import FreeSpinIntro from './FreeSpinIntro.svelte';
	import FreeSpinCounter from './FreeSpinCounter.svelte';
	import FreeSpinOutro from './FreeSpinOutro.svelte';
	import Transition from './Transition.svelte';
	
	const context = getContext();

	applyBetModeMeta();

	onMount(() => (context.stateLayout.showLoadingScreen = true));

	context.eventEmitter.subscribeOnMount({
		buyBonusConfirm: () => {
			stateModal.modal = { name: 'buyBonusConfirm' };
		},
	});
</script>

<App>
	<EnableSound />
	<EnableHotkey />
	<EnableGameActor />
	<EnablePixiExtension />

	<Background />

	{#if context.stateLayout.showLoadingScreen}
		<LoadingScreen onloaded={() => (context.stateLayout.showLoadingScreen = false)} />
	{:else}
		<ResumeBet />
		<!--
			The reason why <Sound /> is rendered after clicking the loading screen:
			"Autoplay with sound is allowed if: The user has interacted with the domain (click, tap, etc.)."
			Ref: https://developer.chrome.com/blog/autoplay
		-->
		<Sound />

		<MainContainer>
			<BoardFrame />
			<BoardBanner />
		</MainContainer>

		<MainContainer>
			<Board />
			<Anticipations />
			<TumbleWinAmount />
			
		</MainContainer>

		<MainContainer>
			<TumbleBoard />
			<!-- <TumbleAnticipations /> -->
			<ClusterWinAmounts />
		</MainContainer>

		<MainContainer>
			<MultiplierBoard />
			<MultiplierTotal />
		</MainContainer>

		<BetBarUI>
			{#snippet gameName()}
				<UiGameName name="Bloody Seafood" />
			{/snippet}
			{#snippet logo()}
				<Text
					anchor={{ x: 1, y: 0 }}
					text="STEEL GAMING"
					style={{
						fontFamily: 'proxima-nova',
						fontSize: REM * 1.5,
						fontWeight: '600',
						lineHeight: REM * 2,
						fill: 0xffffff,
					}}
				/>
			{/snippet}
		</BetBarUI>
		<MainContainer><GlobalMultiplier /></MainContainer>
		<Win />
		<FreeSpinIntro />
		{#if ['desktop', 'landscape'].includes(context.stateLayoutDerived.layoutType())}
			<FreeSpinCounter />
		{/if}
		<FreeSpinOutro />
		<Transition />

			{/if}
</App>

<Modals>
	{#snippet version()}
		<GameVersion version="1.0.0" />
	{/snippet}
	{#snippet gameRules()}
		<GameRules />
	{/snippet}
	{#snippet payTable()}
		<PayTable />
	{/snippet}
</Modals>

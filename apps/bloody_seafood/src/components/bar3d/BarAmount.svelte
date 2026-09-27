<script lang="ts">
	import { Tween } from 'svelte/motion';

	import { Container } from 'pixi-svelte';
	import { stateBet, stateBetDerived, stateModal } from 'state-shared';
	import { bookEventAmountToCurrencyString, numberToCurrencyString } from 'utils-shared/amount';
	import { getContext } from 'components-ui-pixi/src/context';
	import { i18nDerived } from 'components-ui-pixi/src/i18n/i18nDerived';

	import BarLabel from './BarLabel.svelte';

	// The shared LabelBalance / LabelWin / LabelBet, logic unchanged, drawn with
	// BarLabel so the bar's amounts use the game's display face.
	type Props = { kind: 'balance' | 'win' | 'bet'; stacked?: boolean };

	const props: Props = $props();
	const context = getContext();

	const balanceTween = new Tween(stateBet.balanceAmount);
	const winTween = new Tween(stateBet.winBookEventAmount);

	$effect(() => {
		balanceTween.set(stateBet.balanceAmount);
	});
	$effect(() => {
		winTween.set(stateBet.winBookEventAmount);
	});

	const label = $derived(
		props.kind === 'balance'
			? i18nDerived.balance()
			: props.kind === 'win'
				? i18nDerived.win()
				: stateBetDerived.activeBetMode()?.text.betAmountLabel || i18nDerived.bet(),
	);
	const value = $derived(
		props.kind === 'balance'
			? numberToCurrencyString(balanceTween.current)
			: props.kind === 'win'
				? bookEventAmountToCurrencyString(winTween.current)
				: numberToCurrencyString(stateBetDerived.betCost()),
	);

	const betDisabled = $derived(!context.stateXstateDerived.isIdle());
	const onBetPress = () => {
		if (betDisabled) return;
		context.eventEmitter.broadcast({ type: 'soundPressGeneral' });
		stateModal.modal = { name: 'betAmountMenu' };
	};
</script>

{#if props.kind === 'bet'}
	<Container eventMode="static" cursor={betDisabled ? 'not-allowed' : 'pointer'} onpointerup={onBetPress}>
		<BarLabel {label} {value} />
	</Container>
{:else}
	<BarLabel {label} {value} />
{/if}

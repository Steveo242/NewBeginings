<script lang="ts" module>
	export type EmitterEventMultiplierTotal =
		| { type: 'multiplierTotalShow' }
		| { type: 'multiplierTotalHide' }
		| { type: 'multiplierTotalUpdate'; totalMultiplier: number }
		| { type: 'multiplierTotalAnimate' };
</script>

<script lang="ts">
	import WinAmountText from './WinAmountText.svelte';
	import { Container } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';
	import { backOut } from 'svelte/easing';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import BoardContainer from './BoardContainer.svelte';

	// The board multiplier total (only reached by boardMultiplierInfo, which the current
	// math never emits). Drawn in code - it used to ride the sample game's
	// tumble_multiplier spine: the number slams in and settles.
	const context = getContext();

	let show = $state(false);
	let totalMultiplier = $state(0);
	const slam = new Tween(1, { duration: 520, easing: backOut });

	context.eventEmitter.subscribeOnMount({
		multiplierTotalShow: () => (show = true),
		multiplierTotalHide: () => (show = false),
		multiplierTotalUpdate: (emitterEvent) => (totalMultiplier = emitterEvent.totalMultiplier),
		multiplierTotalAnimate: async () => {
			slam.set(2.2, { duration: 0 });
			await slam.set(1);
		},
	});
</script>

{#snippet multiplierSnippet()}
	<WinAmountText
		scale={3}
		anchor={0.5}
		text={`${totalMultiplier} X`}
		style={{
			fontFamily: 'gold',
			fontSize: SYMBOL_SIZE,
			letterSpacing: -5,
		}}
	/>
{/snippet}

{#if show}
	<BoardContainer>
		<Container
			x={context.stateGameDerived.boardLayout().width * 0.5}
			y={context.stateGameDerived.boardLayout().height * 0.5}
			scale={slam.current}
		>
			{@render multiplierSnippet()}
		</Container>
	</BoardContainer>
{/if}

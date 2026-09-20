<script lang="ts">
	import { Container, Rectangle, SpineProvider, SpineTrack } from 'pixi-svelte';
	import { stateBetDerived } from 'state-shared';

	import { getContext } from '../game/context';
	import type { Reel } from '../game/stateGame.svelte';
	import { REEL_PADDING, SYMBOL_SIZE } from '../game/constants';

	type Props = {
		reel: Reel;
		oncomplete: () => void;
	};

	const props: Props = $props();
	const context = getContext();

	type AnimationName = 'anticipation_intro' | 'anticipation_loop' | 'anticipation_out';

	let animationName = $state<AnimationName>('anticipation_intro');

	$effect(() => {
		if (props.reel.reelState.motion === 'stopped') {
			animationName = 'anticipation_out';
		}
	});

	// Clamps the glow to exactly this reel's column, from the top of the
	// board to the bottom - regardless of where the rig's own internal
	// anchor sits, it can never bleed above the board or into a neighbour
	// reel. Sizing/positioning the spine itself to land perfectly inside
	// this window took several tries and disagreed with what actually
	// rendered each time; the mask makes that unnecessary to get exactly
	// right.
	const reelLeft = $derived(
		context.stateGameDerived.boardLayout().x -
			context.stateGameDerived.boardLayout().width * 0.5 +
			(props.reel.reelIndex + REEL_PADDING) * SYMBOL_SIZE,
	);
	const boardTop = $derived(
		context.stateGameDerived.boardLayout().y -
			context.stateGameDerived.boardLayout().height * 0.5,
	);
</script>

<Container>
	<Rectangle
		isMask
		x={reelLeft}
		y={boardTop}
		width={SYMBOL_SIZE}
		height={context.stateGameDerived.boardLayout().height}
	/>
	<SpineProvider
		key="anticipation"
		width={SYMBOL_SIZE * 0.56}
		height={context.stateGameDerived.boardLayout().height}
		x={reelLeft}
		y={context.stateGameDerived.boardLayout().y}
	>
		<SpineTrack
			trackIndex={0}
			{animationName}
			loop={animationName === 'anticipation_loop'}
			timeScale={stateBetDerived.timeScale()}
			listener={{
				complete: () => {
					if (animationName === 'anticipation_intro') {
						animationName = 'anticipation_loop';
					}

					if (animationName === 'anticipation_out') {
						props.oncomplete();
					}
				},
			}}
		/>
	</SpineProvider>
</Container>

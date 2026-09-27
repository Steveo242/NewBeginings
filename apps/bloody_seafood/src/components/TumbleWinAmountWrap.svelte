<script lang="ts">
	import type { Snippet } from 'svelte';

	import { Container } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import BoardContainer from './BoardContainer.svelte';

	type Props = {
		show: boolean;
		children: Snippet;
	};

	const props: Props = $props();
	const context = getContext();

	// Mounted on the tank's bottom beam (the strip of iron between the last row
	// and the bet bar). It used to sit above the top row, under the front frame
	// and the logo - drawn first, so the frame painted straight over it.
	const beamY = $derived(context.stateGameDerived.boardLayout().height + SYMBOL_SIZE * 0.4);

	const desktopPosition = $derived({
		x: context.stateGameDerived.boardLayout().width * 0.5,
		y: beamY,
	});

	const portraitPosition = $derived({
		x:
			context.stateGameDerived.boardLayout().width *
			(context.stateGame.gameType === 'basegame' ? 0.5 : 0.37),
		y: beamY,
	});

	const position = $derived(
		context.stateLayoutDerived.isStacked() ? portraitPosition : desktopPosition,
	);

	const scale = 1;
</script>

<FadeContainer show={props.show}>
	<BoardContainer>
		<Container {...position} {scale}>
			{@render props.children()}
		</Container>
	</BoardContainer>
</FadeContainer>

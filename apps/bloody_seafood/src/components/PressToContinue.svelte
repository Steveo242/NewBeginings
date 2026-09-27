<script lang="ts">
	import { MainContainer, OnPressFullScreen } from 'components-layout';
	import { OnHotkey } from 'components-shared';
	import { Text } from 'pixi-svelte';
	import { onMount } from 'svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { displayTextStyle } from '../game/fonts';

	type Props = {
		onpress: () => void;
	};

	const props: Props = $props();
	const context = getContext();

	// Sits inside the bottom of the tank rather than at the foot of the screen,
	// where the bet bar lives - there it printed straight over BALANCE / WIN.
	const y = $derived(
		context.stateGameDerived.boardLayout().y +
			context.stateGameDerived.boardLayout().height * 0.5 -
			SYMBOL_SIZE * 0.3,
	);

	// A slow breathe so it reads as a prompt, not a caption.
	let alpha = $state(1);
	onMount(() => {
		let frame = 0;
		const start = performance.now();
		const tick = () => {
			alpha = 0.7 + 0.3 * Math.cos(((performance.now() - start) / 1400) * Math.PI * 2);
			frame = requestAnimationFrame(tick);
		};
		frame = requestAnimationFrame(tick);
		return () => cancelAnimationFrame(frame);
	});
</script>

<MainContainer>
	<Text
		text="TAP TO CONTINUE"
		style={displayTextStyle(48)}
		anchor={{ x: 0.5, y: 1 }}
		x={context.stateGameDerived.boardLayout().x}
		{y}
		{alpha}
	/>
</MainContainer>
<OnHotkey hotkey="Space" onpress={() => props.onpress()} />
<OnPressFullScreen onpress={() => props.onpress()} />

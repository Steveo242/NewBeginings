<script lang="ts" module>
	export type EmitterEventFreeSpinIntro =
		| { type: 'freeSpinIntroShow' }
		| { type: 'freeSpinIntroHide' }
		| { type: 'freeSpinIntroUpdate'; totalFreeSpins: number };
</script>

<script lang="ts">
 import { Container } from "pixi-svelte";
 import { MainContainer } from "components-layout";
 import WinBanner from "./WinBanner.svelte";
 import WinAmountText from "./WinAmountText.svelte";
	import { CanvasSizeRectangle } from 'components-layout';
	import { stateUrlDerived, stateBet } from 'state-shared';
	import { FadeContainer } from 'components-pixi';
	import { waitForResolve } from 'utils-shared/wait';
	import { BitmapText, SpineProvider, SpineSlot, SpineTrack, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { isSuperBetMode } from '../game/constants';
	import PressToContinue from './PressToContinue.svelte';
	import FreeSpinAnimation from './FreeSpinAnimation.svelte';

	type AnimationName = 'intro' | 'idle';

	const context = getContext();

	let show = $state(false);
	let animationName = $state<AnimationName>('intro');
	let freeSpinsFromEvent = $state(0);
	let oncomplete = $state(() => {});

	// The book events don't say which feature this is, so the active bet mode
	// is the signal - the same one the math uses to decide whether wilds carry.
	const bannerText = $derived(
		isSuperBetMode(stateBet.activeBetModeKey) ? 'SUPER FREE SPINS' : 'FREE SPINS',
	);

	context.eventEmitter.subscribeOnMount({
		freeSpinIntroShow: () => (show = true),
		freeSpinIntroHide: () => (show = false),
		freeSpinIntroUpdate: async (emitterEvent) => {
			// if (emitterEvent.extraSpins) {
			// 	context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_fs_respins' });
			// }
			// freeSpinsFromEvent = emitterEvent.extraSpins ?? emitterEvent.totalFreeSpins;
			freeSpinsFromEvent = emitterEvent.totalFreeSpins;
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});
</script>

<FadeContainer {show}>
	<CanvasSizeRectangle backgroundColor={0x000000} backgroundAlpha={0.5} />

	<MainContainer>
 <Container x={context.stateGameDerived.boardLayout().x} y={context.stateGameDerived.boardLayout().y}>
 <WinBanner text={bannerText} alias="big">
 <WinAmountText anchor={0.5} text={freeSpinsFromEvent} style={{ fontSize: 120 }} />
 </WinBanner>
 </Container>
</MainContainer>

	<PressToContinue onpress={() => oncomplete()} />
</FadeContainer>

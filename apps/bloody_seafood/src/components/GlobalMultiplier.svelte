<script lang="ts" module>
	export type EmitterEventGlobalMultiplier =
		| { type: 'globalMultiplierShow' }
		| { type: 'globalMultiplierHide' }
		| { type: 'globalMultiplierUpdate'; multiplier: number };
</script>

<script lang="ts">
 import WinAmountText from "./WinAmountText.svelte";
	import { Tween } from 'svelte/motion';

	import {
		BitmapText,
		Container,
		SpineEventEmitterProvider,
		SpineProvider,
		SpineSlot,
		SpineTrack,
	} from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { stateBetDerived } from 'state-shared';
	import { waitForResolve, waitForTimeout } from 'utils-shared/wait';

	import BoardContainer from './BoardContainer.svelte';
	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';

	type AnimationName = 'static' | 'win' | 'reset' | 'increment';

	const PANEL_WIDTH = SYMBOL_SIZE * 0.641;
	const context = getContext();
	const scale = $derived(context.stateLayoutDerived.isStacked() ? 1.28 : 1);
	const desktopPosition = $derived({
		x: context.stateGameDerived.boardLayout().width - PANEL_WIDTH * 1.3,
		y: -SYMBOL_SIZE * 1.1,
	});
	const portraitPosition = $derived({
		x: context.stateGameDerived.boardLayout().width - PANEL_WIDTH * 1.5,
		y: -SYMBOL_SIZE * 0.55,
	});
	const position = $derived(
		context.stateLayoutDerived.isStacked() ? portraitPosition : desktopPosition,
	);

	let show = $state(false);
	let animationName = $state<AnimationName>('static');
	let multiplier = $state(1);
	let previousMultiplier = new Tween(1);
	let oncomplete = $state(() => {});

	context.eventEmitter.subscribeOnMount({
		globalMultiplierShow: () => (show = true),
		globalMultiplierHide: () => {
			show = false;
			// Clear the panel's state here rather than leaving it to the reset
			// animation. Once hidden, FadeContainer drops its children at alpha 0,
			// which unmounts the SpineTrack - so the 'complete' event the update
			// handler awaits can never arrive. Without this, animationName sticks
			// on 'reset' forever, the closing previousMultiplier sync never runs,
			// and the next feature reopens the panel still reading the old value.
			// Releasing oncomplete frees any update still waiting on that event.
			animationName = 'static';
			multiplier = 1;
			previousMultiplier.set(1, { duration: 0 });
			oncomplete();
		},
		globalMultiplierUpdate: async (emitterEvent) => {
			if (emitterEvent.multiplier === 1 && multiplier !== 1) {
				animationName = 'reset';
				await waitForTimeout(300);
				context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_reset' });
				previousMultiplier.set(emitterEvent.multiplier);
			}

			if (emitterEvent.multiplier > multiplier) {
				context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_update' });
				animationName = 'increment';
			}

			if (animationName !== 'static') {
				multiplier = emitterEvent.multiplier;
				await waitForResolve((resolve) => (oncomplete = resolve));
				animationName = 'static';
				previousMultiplier.set(multiplier, { duration: 0 });
			}
		},
	});
</script>

<FadeContainer {show}>
	<BoardContainer>
		<Container x={position.x} y={position.y} {scale}>
			<SpineProvider key="globalMultiplier" width={PANEL_WIDTH}>
				<SpineTrack
					trackIndex={0}
					{animationName}
					timeScale={stateBetDerived.timeScale()}
					listener={{
						complete: () => {
							oncomplete();
						},
					}}
				/>
				<SpineEventEmitterProvider>
					<SpineSlot slotName="slot_multi">
						<WinAmountText
							anchor={0.5}
							text={`${Math.round(previousMultiplier.current)}×`}
							style={{
								fontFamily: 'gold',
								fontSize: SYMBOL_SIZE * 5.2,
							}}
						/>
					</SpineSlot>
					<SpineSlot slotName="slot_multi_next">
						<WinAmountText
							anchor={0.5}
							text={`${multiplier}×`}
							style={{
								fontFamily: 'gold',
								fontSize: SYMBOL_SIZE * 5.2,
							}}
						/>
					</SpineSlot>
				</SpineEventEmitterProvider>
			</SpineProvider>
		</Container>
	</BoardContainer>
</FadeContainer>

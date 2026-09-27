<script lang="ts" module>
	export type EmitterEventFreeSpinIntro =
		| { type: 'freeSpinIntroShow' }
		| { type: 'freeSpinIntroHide' }
		| { type: 'freeSpinIntroUpdate'; totalFreeSpins: number };
</script>

<script lang="ts">
	import { Tween } from 'svelte/motion';
	import { Container, Text } from 'pixi-svelte';
	import { MainContainer } from 'components-layout';
	import WinBanner from './WinBanner.svelte';
	import { SYMBOL_SIZE } from '../game/constants';
	import { DISPLAY_FONT, displayTextStyle } from '../game/fonts';
	import { CanvasSizeRectangle } from 'components-layout';
	import { stateUrlDerived, stateBet } from 'state-shared';
	import { FadeContainer } from 'components-pixi';
	import { waitForResolve } from 'utils-shared/wait';

	import { getContext } from '../game/context';
	import { isSuperBetMode } from '../game/constants';
	import PressToContinue from './PressToContinue.svelte';

	type AnimationName = 'intro' | 'idle';

	const context = getContext();

	let show = $state(false);
	let animationName = $state<AnimationName>('intro');
	let freeSpinsFromEvent = $state(0);
	let oncomplete = $state(() => {});

	// The book events don't say which feature this is, so the active bet mode
	// is the signal - the same one the math uses to decide whether wilds carry.
	const isSuper = $derived(isSuperBetMode(stateBet.activeBetModeKey));
	const bannerText = $derived(isSuper ? 'SUPER FREE SPINS' : 'FREE SPINS');

	// The feature in three lines (matches the math: +1 per winning cluster holding a
	// wild, never reset during the feature; super carries every landed wild, max 6).
	const lines = $derived([
		'EACH WINNING CLUSTER WITH A WILD: MULTIPLIER +1',
		'THE MULTIPLIER NEVER RESETS DURING THE FEATURE',
		isSuper ? 'LANDED WILDS CARRY INTO EVERY NEXT SPIN (MAX 6)' : '3+ CHESTS AWARD EXTRA SPINS',
	]);
	/** WinBanner's plaque height (W 0.86 x board, H = 0.34 W) */
	const BANNER_H = $derived(context.stateGameDerived.boardLayout().width * 0.86 * 0.34);
	const linesAlpha = new Tween(0);
	$effect(() => {
		if (show) {
			linesAlpha.set(0, { duration: 0 });
			setTimeout(() => linesAlpha.set(1, { duration: 400 }), 450);
		}
	});
	const captionStyle = {
		fontFamily: DISPLAY_FONT,
		fontWeight: 'bold',
		fontSize: SYMBOL_SIZE * 0.2,
		fill: 0xe9dcc0,
		letterSpacing: SYMBOL_SIZE * 0.06,
	} as const;
	const lineStyle = {
		fontFamily: DISPLAY_FONT,
		fontWeight: 'bold',
		fontSize: SYMBOL_SIZE * 0.2,
		fill: 0xe9dcc0,
		align: 'center',
		letterSpacing: SYMBOL_SIZE * 0.01,
		dropShadow: { color: 0x000000, alpha: 0.9, blur: 3, distance: 2, angle: Math.PI / 2 },
		wordWrap: true,
		wordWrapWidth: SYMBOL_SIZE * 7.2,
	} as const;

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
	<!-- dark enough that the plaque owns the screen -->
	<CanvasSizeRectangle backgroundColor={0x000000} backgroundAlpha={0.75} />

	<MainContainer>
		<Container x={context.stateGameDerived.boardLayout().x} y={context.stateGameDerived.boardLayout().y}>
			<WinBanner text={bannerText} alias={isSuper ? 'epic' : 'superwin'}>
				<Container y={-SYMBOL_SIZE * 0.12}>
					<Text anchor={0.5} text={`${freeSpinsFromEvent}`} style={displayTextStyle(SYMBOL_SIZE * 1.25)} />
				</Container>
				<Text anchor={0.5} y={SYMBOL_SIZE * 0.62} text="AWARDED" style={captionStyle} />
			</WinBanner>
			<!-- what the feature does, in one glance -->
			<Container y={BANNER_H * 0.5 + SYMBOL_SIZE * 0.55} alpha={linesAlpha.current}>
				{#each lines as line, i}
					<Text anchor={0.5} y={i * SYMBOL_SIZE * 0.36} text={line} style={lineStyle} />
				{/each}
			</Container>
		</Container>
	</MainContainer>

	<PressToContinue onpress={() => oncomplete()} />
</FadeContainer>

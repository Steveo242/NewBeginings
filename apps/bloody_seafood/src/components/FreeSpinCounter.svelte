<script lang="ts" module>
	export type EmitterEventFreeSpinCounter =
		| { type: 'freeSpinCounterShow' }
		| { type: 'freeSpinCounterHide' }
		| { type: 'freeSpinCounterUpdate'; current?: number; total?: number };
</script>

<script lang="ts">
	import { stateUi } from 'state-shared';
	import { FadeContainer } from 'components-pixi';
	import { Container, Text } from 'pixi-svelte';

	import BoardContainer from './BoardContainer.svelte';
	import NineSlice from './bar3d/NineSlice.svelte';
	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { DISPLAY_FONT, displayTextStyle } from '../game/fonts';
	import { HUD_PANEL_W, hudColumn } from '../game/hud';

	// "FREE SPINS 5 / 8" on an iron plaque at the top of the free-spins HUD column
	// (the multiplier meter hangs below it). Its panel sprite, Frame_FSCounter.png,
	// never shipped with this game - the count floated as bare text over the sky.
	const context = getContext();
	const H = SYMBOL_SIZE * 1.15;
	const PANEL_SCALE = 0.45;
	const PANEL_BORDER = 80;
	const position = $derived(hudColumn(context, 'counter'));

	const captionStyle = {
		fontFamily: DISPLAY_FONT,
		fontWeight: 'bold',
		fontSize: SYMBOL_SIZE * 0.19,
		fill: 0xe9dcc0,
		letterSpacing: SYMBOL_SIZE * 0.035,
		dropShadow: { color: 0x000000, alpha: 0.8, blur: 2, distance: 2, angle: Math.PI / 2 },
	} as const;

	let show = $state(false);
	let current = $state(0);
	let total = $state(0);

	context.eventEmitter.subscribeOnMount({
		freeSpinCounterShow: () => (show = stateUi.freeSpinCounterShow = true),
		freeSpinCounterHide: () => (show = stateUi.freeSpinCounterShow = false),
		freeSpinCounterUpdate: (emitterEvent) => {
			if (emitterEvent.current !== undefined) current = stateUi.freeSpinCounterCurrent = emitterEvent.current;
			if (emitterEvent.total !== undefined) total = stateUi.freeSpinCounterTotal = emitterEvent.total;
		},
	});

	// Mounted on every layout: it owns stateUi's counter state, which the bet bar reads to
	// swap its play-amount label for the spin count on stacked (phone) layouts. The plaque
	// itself only has room beside the tank on wide layouts. (Mounting the whole component
	// only on wide layouts left phones with no spin count at all.)
	const wide = $derived(['desktop', 'landscape'].includes(context.stateLayoutDerived.layoutType()));
</script>

<FadeContainer show={show && wide}>
	<BoardContainer>
		<Container x={position.x} y={position.y}>
			<Container scale={PANEL_SCALE}>
				<NineSlice key="panel.png" width={HUD_PANEL_W / PANEL_SCALE} height={H / PANEL_SCALE} border={PANEL_BORDER} />
			</Container>
			<Text anchor={0.5} y={-H * 0.24} text="FREE SPINS" style={captionStyle} />
			<Text anchor={0.5} y={H * 0.14} text={`${current} / ${total}`} style={displayTextStyle(SYMBOL_SIZE * 0.5)} />
		</Container>
	</BoardContainer>
</FadeContainer>

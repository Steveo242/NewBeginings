<script lang="ts" module>
	export type EmitterEventGlobalMultiplier =
		| { type: 'globalMultiplierShow' }
		| { type: 'globalMultiplierHide' }
		| { type: 'globalMultiplierUpdate'; multiplier: number };
</script>

<script lang="ts">
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	import { Container, Sprite, Text } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { stateBetDerived } from 'state-shared';
	import { waitForTimeout } from 'utils-shared/wait';

	import BoardContainer from './BoardContainer.svelte';
	import NineSlice from './bar3d/NineSlice.svelte';
	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { DISPLAY_FONT, displayTextStyle } from '../game/fonts';
	import { HUD_PANEL_W, hudColumn } from '../game/hud';

	// The free-spin multiplier is the bonus's whole story (+1 for every winning cluster
	// with a wild in it, kept for the entire feature), so it gets a real meter: an iron
	// plaque with a big brass number that slams in on every increase. It used to be a
	// tiny badge tucked beside the logo on the tank's top-right corner.
	const context = getContext();

	const H = SYMBOL_SIZE * 1.8;
	const PANEL_SCALE = 0.45;
	const PANEL_BORDER = 80;
	const position = $derived(hudColumn(context, 'multiplier'));

	let show = $state(false);
	let multiplier = $state(1);
	const pop = new Tween(1, { easing: cubicOut });
	const flash = new Tween(0, { easing: cubicOut });

	const captionStyle = {
		fontFamily: DISPLAY_FONT,
		fontWeight: 'bold',
		fontSize: SYMBOL_SIZE * 0.21,
		fill: 0xe9dcc0,
		letterSpacing: SYMBOL_SIZE * 0.035,
		dropShadow: { color: 0x000000, alpha: 0.8, blur: 2, distance: 2, angle: Math.PI / 2 },
	} as const;

	context.eventEmitter.subscribeOnMount({
		globalMultiplierShow: () => (show = true),
		globalMultiplierHide: () => {
			show = false;
			multiplier = 1;
			pop.set(1, { duration: 0 });
			flash.set(0, { duration: 0 });
		},
		globalMultiplierUpdate: async (emitterEvent) => {
			const speed = stateBetDerived.timeScale();
			if (emitterEvent.multiplier === 1 && multiplier !== 1) {
				context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_reset' });
				await pop.set(0.6, { duration: 180 / speed });
				multiplier = 1;
				await pop.set(1, { duration: 220 / speed });
				return;
			}
			if (emitterEvent.multiplier > multiplier) {
				context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_update' });
				multiplier = emitterEvent.multiplier;
				// slam: big and bright, then settle with a flash behind the number
				pop.set(1.9, { duration: 0 });
				flash.set(1, { duration: 0 });
				flash.set(0, { duration: 700 / speed });
				await pop.set(1, { duration: 380 / speed });
				await waitForTimeout(120 / speed);
			}
		},
	});
</script>

<FadeContainer {show}>
	<BoardContainer>
		<Container x={position.x} y={position.y}>
			<Container scale={PANEL_SCALE}>
				<NineSlice
					key="panel.png"
					width={HUD_PANEL_W / PANEL_SCALE}
					height={H / PANEL_SCALE}
					border={PANEL_BORDER}
				/>
			</Container>
			<Text anchor={0.5} y={-H * 0.3} text="MULTIPLIER" style={captionStyle} />
			<Sprite
				key="fxGlow"
				anchor={0.5}
				y={H * 0.1}
				width={HUD_PANEL_W * 1.6}
				height={H * 1.6}
				tint={0xffc870}
				alpha={flash.current}
				blendMode="add"
			/>
			<Container y={H * 0.12} scale={pop.current}>
				<Text anchor={0.5} text={`${multiplier}×`} style={displayTextStyle(SYMBOL_SIZE * 1.02)} />
			</Container>
		</Container>
	</BoardContainer>
</FadeContainer>

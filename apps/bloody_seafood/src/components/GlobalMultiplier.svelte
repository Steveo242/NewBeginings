<script lang="ts" module>
	export type EmitterEventGlobalMultiplier =
		| { type: 'globalMultiplierShow' }
		| { type: 'globalMultiplierHide' }
		| { type: 'globalMultiplierUpdate'; multiplier: number };
</script>

<script lang="ts">
	import { Tween } from 'svelte/motion';
	import { backOut, cubicOut, elasticOut } from 'svelte/easing';

	import { Container, Sprite, Text } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { stateBetDerived } from 'state-shared';

	import BoardContainer from './BoardContainer.svelte';
	import NineSlice from './bar3d/NineSlice.svelte';
	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { DISPLAY_FONT, displayTextStyle } from '../game/fonts';
	import { HUD_PANEL_H, HUD_PANEL_W, hudColumn } from '../game/hud';
	import type { SoundEffectName } from '../game/sound';

	// The free-spin multiplier is the bonus's whole story (+1 for every winning cluster
	// with a wild in it, kept for the entire feature), so it gets a real meter: an iron
	// plaque with a big brass number that slams in on every increase. It used to be a
	// tiny badge tucked beside the logo on the tank's top-right corner.
	const context = getContext();

	const H = HUD_PANEL_H;
	const PANEL_SCALE = 0.45;
	const PANEL_BORDER = 80;
	const position = $derived(hudColumn(context, 'multiplier'));

	let show = $state(false);
	let multiplier = $state(1);
	// steps up since the last reset: each one's bell/brass stinger is a semitone higher,
	// capped at the 6th (make_multiplier_fx.py)
	let steps = 0;
	const UP_STEPS = 6;
	const pop = new Tween(1, { easing: cubicOut });
	const flash = new Tween(0, { easing: cubicOut });
	const glint = new Tween(0, { easing: cubicOut });
	// the number on the plaque: ticks through the values between the old and the new one
	let shown = $state(1);
	const tickTo = (from: number, to: number, ms: number) => {
		const n = Math.max(1, to - from);
		for (let i = 1; i <= n; i++) setTimeout(() => (shown = from + i), (ms * i) / n);
	};

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
			// the feature ends with the multiplier dropping back to x1
			if (multiplier > 1) context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_mult_down' });
			steps = 0;
			show = false;
			multiplier = 1;
			shown = 1;
			pop.set(1, { duration: 0 });
			flash.set(0, { duration: 0 });
		},
		globalMultiplierUpdate: async (emitterEvent) => {
			const speed = stateBetDerived.timeScale();
			if (emitterEvent.multiplier === 1 && multiplier !== 1) {
				context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_mult_down' });
				steps = 0;
				// reset: a small dip and a soft settle back
				await pop.set(0.85, { duration: 160 / speed });
				multiplier = 1;
				shown = 1;
				await pop.set(1, { duration: 320 / speed, easing: backOut });
				return;
			}
			if (emitterEvent.multiplier > multiplier) {
				steps = Math.min(steps + 1, UP_STEPS);
				context.eventEmitter.broadcast({ type: 'soundOnce', name: `sfx_mult_up_${steps}` as SoundEffectName });
				const from = multiplier;
				multiplier = emitterEvent.multiplier;
				// POP: a fast punch up to 1.35x and an elastic overshoot back, a gold flash and
				// a glint sweeping across, and the number ticking up to its new value
				flash.set(1, { duration: 0 });
				flash.set(0, { duration: 650 / speed });
				glint.set(0, { duration: 0 });
				glint.set(1, { duration: 420 / speed });
				tickTo(from, multiplier, 240 / speed);
				await pop.set(1.35, { duration: 90 / speed, easing: cubicOut });
				await pop.set(1, { duration: 520 / speed, easing: elasticOut });
			}
		},
	});
</script>

<FadeContainer {show}>
	<BoardContainer>
		<Container x={position.x} y={position.y} scale={position.scale ?? 1}>
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
				<Text anchor={0.5} text={`${shown}×`} style={displayTextStyle(SYMBOL_SIZE * 1.02)} />
			</Container>
			<!-- the glint: a narrow bright bar wiping across the number on each step up -->
			{#if glint.current > 0 && glint.current < 1}
				<Sprite
					key="fxGlow"
					anchor={0.5}
					x={(glint.current - 0.5) * HUD_PANEL_W * 0.9}
					y={H * 0.12}
					width={HUD_PANEL_W * 0.16}
					height={H * 0.62}
					tint={0xfff1c8}
					alpha={Math.sin(glint.current * Math.PI) * 0.8}
					blendMode="add"
				/>
			{/if}
		</Container>
	</BoardContainer>
</FadeContainer>

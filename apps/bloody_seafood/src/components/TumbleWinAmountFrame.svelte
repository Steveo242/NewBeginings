<script lang="ts">
	import type { Snippet } from 'svelte';

	import { Container, Text, type Sizes } from 'pixi-svelte';

	import NineSlice from './bar3d/NineSlice.svelte';
	import { SYMBOL_SIZE } from '../game/constants';
	import { DISPLAY_FONT } from '../game/fonts';

	type Props = {
		children: Snippet<[{ frameSizes: Sizes }]>;
	};

	const props: Props = $props();

	// The running cascade total, on a plaque cut from the bet bar's riveted iron
	// strap (ui3d panel.png) so it reads as part of the tank. The old Frame_Tumble
	// sprites were never shipped with this game - the total floated on nothing.
	const PANEL_SIZES = { width: SYMBOL_SIZE * 3.6, height: SYMBOL_SIZE * 1.12 };
	// panel.png's corners are 80 texture px; drawn at this scale they stay rivet-sized
	const PANEL_SCALE = 0.4;
	const PANEL_BORDER = 80;

	const AMOUNT_SIZES = { width: SYMBOL_SIZE * 3.1, height: SYMBOL_SIZE * 0.7 };

	const captionStyle = {
		fontFamily: DISPLAY_FONT,
		fontWeight: 'bold',
		fontSize: SYMBOL_SIZE * 0.2,
		fill: 0xe9dcc0,
		letterSpacing: SYMBOL_SIZE * 0.03,
		dropShadow: { color: 0x000000, alpha: 0.8, blur: 2, distance: 2, angle: Math.PI / 2 },
	} as const;
</script>

<Container scale={PANEL_SCALE}>
	<NineSlice
		key="panel.png"
		width={PANEL_SIZES.width / PANEL_SCALE}
		height={PANEL_SIZES.height / PANEL_SCALE}
		border={PANEL_BORDER}
	/>
</Container>

<Text anchor={0.5} y={-PANEL_SIZES.height * 0.28} text="TUMBLE WIN" style={captionStyle} />

<Container y={PANEL_SIZES.height * 0.12}>
	{@render props.children({ frameSizes: AMOUNT_SIZES })}
</Container>

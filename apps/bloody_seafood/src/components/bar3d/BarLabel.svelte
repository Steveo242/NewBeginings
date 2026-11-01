<script lang="ts">
	import { CanvasTextMetrics, TextStyle } from 'pixi.js';
	import { Text } from 'pixi-svelte';

	import { UI_BASE_FONT_SIZE } from 'components-ui-pixi/src/constants';

	import { DISPLAY_FONT } from '../../game/fonts';

	// The shared UiLabel's layout (stacked: caption over value) in the game's display
	// face: a small brass caption over a large bright value, read off a dark LabelPlate.
	// (Navy on cream enamel read as a form field and was the weakest part of the bar.)
	// maxWidth: the caption and value shrink to fit it (the plate never grows), so a long
	// amount like 1,234,567.89 or a counting-up win cannot jump or overrun its plate.
	type Props = { label: string; value: string; maxWidth?: number };

	const props: Props = $props();

	const LABEL_SIZE = UI_BASE_FONT_SIZE * 0.66;
	const VALUE_SIZE = UI_BASE_FONT_SIZE * 1.3;
	/** caption, a small gap, value: their combined height, by font size */
	const STACK = LABEL_SIZE + UI_BASE_FONT_SIZE * 0.14 + VALUE_SIZE;

	const labelStyle = {
		fontFamily: DISPLAY_FONT,
		fontWeight: 'bold',
		fontSize: LABEL_SIZE,
		fill: 0xd9b56c,
		letterSpacing: UI_BASE_FONT_SIZE * 0.08,
	} as const;

	const valueStyle = {
		fontFamily: DISPLAY_FONT,
		fontWeight: 'bold',
		fontSize: VALUE_SIZE,
		fill: 0xfff6e4,
		dropShadow: { color: 0x000000, alpha: 0.75, blur: 3, distance: 2, angle: Math.PI / 2 },
	} as const;

	const labelMetrics = new TextStyle(labelStyle);
	const valueMetrics = new TextStyle(valueStyle);
	const fit = (text: string, style: TextStyle) =>
		props.maxWidth ? Math.min(1, props.maxWidth / Math.max(1, CanvasTextMetrics.measureText(text, style).width)) : 1;
	const labelScale = $derived(fit(props.label, labelMetrics));
	const valueScale = $derived(fit(props.value, valueMetrics));
</script>

<!-- the caption-and-value pair is centred on its origin, so whatever plate or button it
     sits in, it sits in the middle of it -->
<Text anchor={0.5} text={props.label} style={labelStyle} scale={labelScale} y={-STACK * 0.5 + LABEL_SIZE * 0.5} />
<Text anchor={0.5} text={props.value} style={valueStyle} scale={valueScale} y={STACK * 0.5 - VALUE_SIZE * 0.5} />

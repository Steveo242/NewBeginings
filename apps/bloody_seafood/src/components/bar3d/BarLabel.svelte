<script lang="ts">
	import { Text } from 'pixi-svelte';

	import { UI_BASE_FONT_SIZE } from 'components-ui-pixi/src/constants';

	import { DISPLAY_FONT } from '../../game/fonts';

	// The shared UiLabel's layout (stacked: caption over value) in the game's display
	// face: a small brass caption over a large bright value, read off a dark LabelPlate.
	// (Navy on cream enamel read as a form field and was the weakest part of the bar.)
	type Props = { label: string; value: string };

	const props: Props = $props();

	const labelStyle = {
		fontFamily: DISPLAY_FONT,
		fontWeight: 'bold',
		fontSize: UI_BASE_FONT_SIZE * 0.66,
		fill: 0xd9b56c,
		letterSpacing: UI_BASE_FONT_SIZE * 0.08,
	} as const;

	const valueStyle = {
		fontFamily: DISPLAY_FONT,
		fontWeight: 'bold',
		fontSize: UI_BASE_FONT_SIZE * 1.3,
		fill: 0xfff6e4,
		dropShadow: { color: 0x000000, alpha: 0.75, blur: 3, distance: 2, angle: Math.PI / 2 },
	} as const;
</script>

<Text anchor={{ x: 0.5, y: 0 }} text={props.label} style={labelStyle} />
<Text anchor={{ x: 0.5, y: 0 }} text={props.value} style={valueStyle} y={UI_BASE_FONT_SIZE * 0.9} />

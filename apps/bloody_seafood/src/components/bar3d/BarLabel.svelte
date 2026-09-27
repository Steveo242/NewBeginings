<script lang="ts">
	import { Text } from 'pixi-svelte';

	import { UI_BASE_FONT_SIZE } from 'components-ui-pixi/src/constants';

	import { DISPLAY_FONT } from '../../game/fonts';

	// The shared UiLabel's layout (stacked: caption over value) in the game's
	// display face. Its `tiled` plate is an asset this game never shipped - the
	// bar draws its own enamel plate behind every label instead.
	type Props = { label: string; value: string };

	const props: Props = $props();

	const labelStyle = {
		fontFamily: DISPLAY_FONT,
		fontWeight: 'bold',
		fontSize: UI_BASE_FONT_SIZE * 0.72,
		fill: 0xa80d26,
		letterSpacing: UI_BASE_FONT_SIZE * 0.06,
	} as const;

	const valueStyle = {
		fontFamily: DISPLAY_FONT,
		fontWeight: 'bold',
		fontSize: UI_BASE_FONT_SIZE * 1.25,
		fill: 0x14375e,
	} as const;
</script>

<Text anchor={{ x: 0.5, y: 0 }} text={props.label} style={labelStyle} />
<Text anchor={{ x: 0.5, y: 0 }} text={props.value} style={valueStyle} y={UI_BASE_FONT_SIZE} />

<script lang="ts">
	import { Rectangle } from 'pixi-svelte';

	// The dark, brass-rimmed well an amount sits in: blackened iron like the tank frame,
	// so the bright value carries the contrast rather than a light plate.
	type Props = { width: number; height: number };

	const props: Props = $props();
</script>

<Rectangle
	anchor={0.5}
	width={props.width}
	height={props.height}
	borderRadius={props.height * 0.24}
	backgroundColor={0x0a1114}
	backgroundAlpha={0.78}
	borderColor={0xb89150}
	borderWidth={5}
/>
<Rectangle
	anchor={0.5}
	width={props.width - 22}
	height={props.height - 22}
	borderRadius={props.height * 0.2}
	backgroundAlpha={0}
	borderColor={0x000000}
	borderAlpha={0.55}
	borderWidth={3}
/>

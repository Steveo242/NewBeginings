<script lang="ts" module>
	import { Rectangle, type RectangleProps } from 'pixi-svelte';

	export type Props = RectangleProps & { key?: string };
</script>

<script lang="ts">
	import { Sprite } from 'pixi-svelte';

	const { key, backgroundColor, borderWidth, borderColor, ...rest }: Props = $props();
</script>

{#if key}
	<Sprite {key} {...rest} tint={backgroundColor ?? 0xffffff} />
{:else}
	<Rectangle borderRadius={50} {backgroundColor} {borderWidth} {borderColor} {...rest} />
{/if}

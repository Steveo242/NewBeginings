<script lang="ts">
	// One rendered 3D control (build_ui3d.py): atlas frames <icon>_idle / _hover / _pressed.
	// Hover and "active" (turbo on, autoplay running) share the lit-brass frame; disabled
	// greys the idle frame. Frames include the drop shadow, so they're drawn a little
	// larger than the hit area.
	import type { Snippet } from 'svelte';
	import { Container, Sprite } from 'pixi-svelte';
	import { Button } from 'components-pixi';

	type Props = {
		icon: string;
		/** hit-area width in bar units; height = width * aspect */
		size: number;
		aspect?: number;
		onpress: () => void;
		disabled?: boolean;
		active?: boolean;
		children?: Snippet;
	};

	const props: Props = $props();
	const w = $derived(props.size);
	const h = $derived(props.size * (props.aspect ?? 1));
	/** rendered frame / button body: the frame carries shadow and margin round the body */
	const ART = 1.3;
</script>

<Button anchor={0.5} sizes={{ width: w, height: h }} onpress={props.onpress} disabled={props.disabled}>
	{#snippet children({ center, hovered, pressed })}
		{@const state = props.disabled
			? 'idle'
			: pressed
				? 'pressed'
				: hovered || props.active
					? 'hover'
					: 'idle'}
		<Sprite
			key={`${props.icon}_${state}.png`}
			{...center}
			anchor={0.5}
			width={w * ART}
			height={h * ART}
			tint={props.disabled ? 0x8a8a8a : 0xffffff}
			alpha={props.disabled ? 0.6 : 1}
		/>
		{#if props.children}
			<Container {...center}>{@render props.children()}</Container>
		{/if}
	{/snippet}
</Button>

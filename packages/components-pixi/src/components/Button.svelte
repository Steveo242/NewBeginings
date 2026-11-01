<script lang="ts" module>
	import type { Snippet } from 'svelte';

	import {
		Container,
		Rectangle,
		anchorToPivot,
		type ContainerProps,
		type Sizes,
		type PixiPoint,
	} from 'pixi-svelte';

	type ContainerPropsToOmit =
		| 'eventMode'
		| 'cursor'
		| 'pivot'
		| 'children'
		| 'onpointerover'
		| 'onpointerout'
		| 'onpointerdown'
		| 'onpointerup'
		| 'onpointerupoutside';

	export type Props = Omit<ContainerProps, ContainerPropsToOmit> & {
		sizes: Sizes;
		onpress: () => void;
		disabled?: boolean;
		anchor?: PixiPoint;
		children: Snippet<
			[
				{
					center: { x: number; y: number };
					hovered: boolean;
					pressed: boolean;
				},
			]
		>;
		debug?: boolean;
	};
</script>

<script lang="ts">
	const { children, sizes, anchor, disabled, onpress, debug, ...containerProps }: Props = $props();
	const center = $derived({
		x: sizes.width * 0.5,
		y: sizes.height * 0.5,
	});

	let hovered = $state(false);
	let pressed = $state(false);

	$effect(() => {
		if (disabled) {
			hovered = false;
			pressed = false;
		}
	});
</script>

<Container
	{...containerProps}
	eventMode="static"
	cursor={disabled ? 'not-allowed' : 'pointer'}
	pivot={anchorToPivot({ sizes, anchor })}
	onpointerover={() => {
		if (disabled) return;
		hovered = true;
	}}
	onpointerout={() => {
		// sliding off cancels the press, like a native button
		hovered = false;
		pressed = false;
	}}
	onpointerdown={(event) => {
		event.stopPropagation();
		if (disabled) return;
		pressed = true;
	}}
	onpointerup={(event) => {
		event.stopPropagation();
		if (disabled) return;
		// Only a press that started on this button counts. Pixi fires pointerup on whatever
		// is under the pointer at release, so a tap that began on a neighbour (play -/+ next
		// to the spin) and drifted a few px onto this one used to fire it.
		const wasPressed = pressed;
		pressed = false;
		if (wasPressed) onpress();
	}}
	onpointerupoutside={() => {
		pressed = false;
	}}
>
	{#if debug}
		<Rectangle
			width={sizes.width}
			height={sizes.height}
			alpha={0.5}
			borderWidth={2}
			borderColor={0xffffff}
		/>
	{/if}
	{@render children({ center, hovered, pressed })}
</Container>

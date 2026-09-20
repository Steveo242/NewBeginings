<script lang="ts">
	import { Sprite, type SpriteProps } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';
	import { elasticOut } from 'svelte/easing';
	import { onMount } from 'svelte';

	import { getSymbolInfo } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';

	type Props = {
		x?: number;
		y?: number;
		symbolInfo: ReturnType<typeof getSymbolInfo>;
		oncomplete?: () => void;
		bounce?: boolean;
	};

	const props: Props = $props();

	// A quick squash-and-release on landing, not a full animation state -
	// every symbol just settles into place with a little life instead of
	// popping in dead-still. Starts pre-squashed and springs out to 1, so
	// the "impact" reads as instant rather than a delayed grow-in.
	const BOUNCE_DURATION = 420;
	const scale = new Tween(props.bounce ? 0.82 : 1, {
		duration: BOUNCE_DURATION,
		easing: elasticOut,
	});
	const rotation = new Tween(props.bounce ? (Math.random() < 0.5 ? -0.07 : 0.07) : 0, {
		duration: BOUNCE_DURATION,
		easing: elasticOut,
	});

	onMount(() => {
		if (props.bounce) {
			scale.set(1);
			rotation.set(0);
			setTimeout(() => props.oncomplete?.(), BOUNCE_DURATION);
		} else {
			props.oncomplete?.();
		}
	});

	$effect(() => {
		props.symbolInfo;
		if (!props.bounce) props.oncomplete?.();
	});
</script>

<Sprite
	x={props.x}
	y={props.y}
	anchor={0.5}
	key={props.symbolInfo.assetKey}
	width={SYMBOL_SIZE * props.symbolInfo.sizeRatios.width * scale.current}
	height={SYMBOL_SIZE * props.symbolInfo.sizeRatios.height * scale.current}
	rotation={rotation.current}
/>

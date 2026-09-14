<script lang="ts">
	import { SpriteSheet } from 'pixi-svelte';

	import { getSymbolInfo } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';

	type Props = {
		x?: number;
		y?: number;
		symbolInfo: ReturnType<typeof getSymbolInfo>;
		oncomplete?: () => void;
		onFrameChange?: (frame: number) => void;
		loop?: boolean;
	};

	const props: Props = $props();
</script>

<SpriteSheet
	x={props.x}
	y={props.y}
	anchor={0.5}
	key={props.symbolInfo.assetKey}
	width={SYMBOL_SIZE * props.symbolInfo.sizeRatios.width}
	height={SYMBOL_SIZE * props.symbolInfo.sizeRatios.height}
	loop={props.loop ?? false}
	play={true}
	onComplete={props.oncomplete}
	onFrameChange={props.onFrameChange}
/>

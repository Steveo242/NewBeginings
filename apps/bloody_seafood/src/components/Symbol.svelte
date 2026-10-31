<script lang="ts">
	import SymbolSprite from './SymbolSprite.svelte';
	import SymbolAnimatedSprite from './SymbolAnimatedSprite.svelte';
	import SymbolPop from './SymbolPop.svelte';
	import WinFlash from './WinFlash.svelte';
	import { getSymbolInfo } from '../game/utils';
	import type { SymbolState, RawSymbol } from '../game/types';
	import { getContext } from '../game/context';
	import { HIGH_SYMBOLS, SYMBOL_SIZE } from '../game/constants';

	type Props = {
		x?: number;
		y?: number;
		state: SymbolState;
		rawSymbol: RawSymbol;
		oncomplete?: () => void;
		loop?: boolean;
	};

	const props: Props = $props();
	const context = getContext();
	const symbolInfo = $derived(getSymbolInfo({ rawSymbol: props.rawSymbol, state: props.state }));
	const staticInfo = $derived(getSymbolInfo({ rawSymbol: props.rawSymbol, state: 'static' }));
	const isSprite = $derived(symbolInfo.type === 'sprite');
	const isSpriteSheet = $derived(symbolInfo.type === 'spriteSheet');
	// Only the fish (the high symbols) swim gently at rest; the chum pails, crate,
	// anchor, BS wild and multipliers sit still until their own land/win animations.
	const idle = $derived(
		(props.state === 'static' || props.state === 'postWinStatic') &&
			HIGH_SYMBOLS.includes(props.rawSymbol.name),
	);
</script>

<!-- under the symbol, so the silhouette copies only show as a rim round it. Not during
	 'win': the outline traces the RESTING art, so while the 3D win jumps out of its cell it
	 was left behind as a gold silhouette backing - it shows once the symbol is back. -->
{#if props.state === 'postWinStatic' && (props.rawSymbol.name as string) !== 'M'}
	<WinFlash
		x={props.x}
		y={props.y}
		name={props.rawSymbol.name}
		assetKey={staticInfo.assetKey}
		sizeRatios={staticInfo.sizeRatios}
	/>
{/if}

{#if isSprite}
	<SymbolSprite
		{symbolInfo}
		x={props.x}
		y={props.y}
		oncomplete={props.oncomplete}
		bounce={props.state === 'land'}
		{idle}
		spinning={props.state === 'spin'}
	/>
{:else if isSpriteSheet}
	{#if props.state === 'explosion' && staticInfo.type === 'sprite'}
		<SymbolPop symbolInfo={staticInfo} x={props.x} y={props.y} />
	{/if}
	<SymbolAnimatedSprite
		{symbolInfo}
		x={props.x}
		y={props.y}
		oncomplete={props.oncomplete}
		loop={props.loop}
		onFrameChange={(frame) => {
			// The wild's explode sound. It used to hang off a 'wildExplode'
			// event on the old explosion spine,
			// but that skeleton declared no events at all, so the cue never
			// actually fired. Now that the explode is a spritesheet, it is
			// triggered off the frame instead - early, so it lands with the
			// burst rather than after it.
			if (frame === 1 && props.state === 'explosion' && props.rawSymbol.name === 'W') {
				context.eventEmitter?.broadcast({ type: 'soundOnce', name: 'sfx_wild_explode' });
			}
		}}
	/>
{/if}


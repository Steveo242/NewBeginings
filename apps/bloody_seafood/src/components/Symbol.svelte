<script lang="ts">
	import { SpineProvider, SpineTrack } from 'pixi-svelte';

	import SymbolSpine from './SymbolSpine.svelte';
	import SymbolSprite from './SymbolSprite.svelte';
	import SymbolAnimatedSprite from './SymbolAnimatedSprite.svelte';
	import SymbolGlow from './SymbolGlow.svelte';
	import { getSymbolBackgroundInfo, getSymbolInfo } from '../game/utils';
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
	const isSprite = $derived(symbolInfo.type === 'sprite');
	const isSpriteSheet = $derived(symbolInfo.type === 'spriteSheet');
	// Only the fish (the high symbols) swim gently at rest; the chum pails, crate,
	// chest, anchor and multipliers sit still until their own land/win animations.
	const idle = $derived(
		(props.state === 'static' || props.state === 'postWinStatic') &&
			HIGH_SYMBOLS.includes(props.rawSymbol.name),
	);
	// the light behind a symbol: scatters always (except while they win/burst - they
	// have their own show then), premiums only on their way down and landing
	const PREMIUMS = ['H1', 'H2', 'H3', 'H4'];
	// the wild is the power symbol: always lit in gold, like the scatter
	const glowKind = $derived(
		props.rawSymbol.name === 'S'
			? 'scatter'
			: props.rawSymbol.name === 'W'
				? 'wild'
				: PREMIUMS.includes(props.rawSymbol.name)
					? 'premium'
					: null,
	);
	const glowLit = $derived(
		glowKind === 'scatter' || glowKind === 'wild'
			? !['win', 'explosion'].includes(props.state)
			: props.state === 'spin' || props.state === 'land',
	);
	const showWinFrame = $derived(
		props.state === 'win' && !['S', 'M'].includes(props.rawSymbol.name),
	);
</script>

{#if glowKind}
	<SymbolGlow x={props.x} y={props.y} kind={glowKind} lit={glowLit} />
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
		pulse={(glowKind === 'scatter' || glowKind === 'wild') && glowLit}
		shine={glowKind === 'wild' && glowLit}
	/>
{:else if isSpriteSheet}
	<SymbolAnimatedSprite
		{symbolInfo}
		x={props.x}
		y={props.y}
		oncomplete={props.oncomplete}
		loop={props.loop}
		onFrameChange={(frame) => {
			// The wild's explode sound. It used to hang off a 'wildExplode'
			// event on the old explosion spine (see the spine branch below),
			// but that skeleton declared no events at all, so the cue never
			// actually fired. Now that the explode is a spritesheet, it is
			// triggered off the frame instead - early, so it lands with the
			// burst rather than after it.
			if (frame === 1 && props.state === 'explosion' && props.rawSymbol.name === 'W') {
				context.eventEmitter?.broadcast({ type: 'soundOnce', name: 'sfx_wild_explode' });
			}
		}}
	/>
	{#if showWinFrame}
		<SpineProvider x={props.x} y={props.y} key="anticipation" width={SYMBOL_SIZE * 0.19}>
			<SpineTrack trackIndex={0} animationName={'payframe'} loop />
		</SpineProvider>
	{/if}
{:else}
	{@const symbolBackgroundInfo = getSymbolBackgroundInfo({
		rawSymbol: props.rawSymbol,
		state: props.state,
	})}
	<SymbolSpine
		loop={props.loop}
		{symbolInfo}
		{symbolBackgroundInfo}
		x={props.x}
		y={props.y}
		showWinFrame={props.state === 'win' && !['S', 'M'].includes(props.rawSymbol.name)}
		listener={{
			complete: props.oncomplete,
			event: (_, event) => {
				if (event.data?.name === 'wildExplode') {
					context.eventEmitter?.broadcast({ type: 'soundOnce', name: 'sfx_wild_explode' });
				}
			},
		}}
	/>
{/if}

<script lang="ts">
	import SymbolSprite from './SymbolSprite.svelte';
	import SymbolAnimatedSprite from './SymbolAnimatedSprite.svelte';
	import SymbolPop from './SymbolPop.svelte';
	import { getSymbolIdleInfo, getSymbolInfo } from '../game/utils';
	import type { SymbolState, RawSymbol } from '../game/types';
	import { getContext } from '../game/context';
	import { HIGH_SYMBOLS, SYMBOL_SIZE } from '../game/constants';
	import { Container, Sprite } from 'pixi-svelte';
	import { pulse } from '../game/tempo';

	type Props = {
		x?: number;
		y?: number;
		state: SymbolState;
		rawSymbol: RawSymbol;
		oncomplete?: () => void;
		loop?: boolean;
		/** `${reel}:${row}` on the board (idle phase, the occasional breath) */
		cell?: string;
	};

	const props: Props = $props();
	const context = getContext();
	const symbolInfo = $derived(getSymbolInfo({ rawSymbol: props.rawSymbol, state: props.state }));
	const staticInfo = $derived(getSymbolInfo({ rawSymbol: props.rawSymbol, state: 'static' }));
	// at rest, a symbol with a rendered idle loop plays it (frame 0 is the static pose, so
	// the hand-over from the land / the static is seamless) - once its sheet is loaded
	const idleInfo = $derived(getSymbolIdleInfo({ rawSymbol: props.rawSymbol }));
	const idleLoop = $derived(
		(props.state === 'static' || props.state === 'postWinStatic') &&
			idleInfo !== undefined &&
			!!context.stateApp.loadedAssets?.[idleInfo.assetKey],
	);
	// a sheet that isn't loaded (yet) must never hold a state open: its oncomplete would
	// never fire and the tumble waits on it. The static sprite (with its bounce) stands in.
	const sheetMissing = $derived(
		symbolInfo.type === 'spriteSheet' && !context.stateApp.loadedAssets?.[symbolInfo.assetKey],
	);
	const isSprite = $derived((symbolInfo.type === 'sprite' || sheetMissing) && !idleLoop);
	const isSpriteSheet = $derived(symbolInfo.type === 'spriteSheet' && !sheetMissing);
	// Only the fish (the high symbols) swim gently at rest; the chum pails, crate,
	// anchor, BS wild and multipliers sit still until their own land/win animations.
	const idle = $derived(
		(props.state === 'static' || props.state === 'postWinStatic') &&
			HIGH_SYMBOLS.includes(props.rawSymbol.name),
	);

	// One shared clock for the win pulse and the scatter tremble (ticker-driven, so both
	// stop costing anything the moment neither is showing).
	let now = $state(0);
	const isWin = $derived(props.state === 'win' && isSpriteSheet);
	// a scatter already down while another reel is still dropping in anticipation
	const scatterTense = $derived(
		props.rawSymbol.name === 'S' &&
			(props.state === 'static' || props.state === 'land') &&
			context.stateGame.board.some(
				(reel) => reel.reelState.anticipating && reel.reelState.motion !== 'stopped',
			),
	);
	let since = 0;
	$effect(() => {
		const app = context.stateApp.pixiApplication;
		if (!app || !(isWin || scatterTense)) return;
		since = performance.now();
		const tick = () => (now = performance.now() - since);
		app.ticker.add(tick);
		return () => app.ticker.remove(tick);
	});

	// Win: a hard punch-in (1.22 -> 1 over ~180 ms) then a beat-locked swell, with a warm
	// halo behind - highs get the biggest punch and the hottest halo.
	const high = $derived(HIGH_SYMBOLS.includes(props.rawSymbol.name) || props.rawSymbol.name === 'W');
	const punch = $derived(Math.max(0, 1 - now / 180));
	const winScale = $derived(
		isWin ? 1 + (high ? 0.22 : 0.15) * punch * punch + (high ? 0.06 : 0.04) * pulse(now, 1) : 1,
	);
	const glowAlpha = $derived(isWin ? Math.min(1, now / 90) * (0.55 + 0.35 * pulse(now, 1)) : 0);
	const glowTint = $derived(
		props.rawSymbol.name === 'W' || props.rawSymbol.name === 'S'
			? 0xffc04a
			: high
				? 0xff5a3c
				: 0xffd9a0,
	);
	// Scatter tension: a nervous tremble that quickens, and a gold glow throbbing on the beat
	const shake = $derived(scatterTense ? Math.sin(now / 28) * (0.035 + Math.min(0.03, now / 60000)) : 0);
	const shakeX = $derived(scatterTense ? Math.sin(now / 19) * SYMBOL_SIZE * 0.025 : 0);
	const tenseScale = $derived(scatterTense ? 1.06 + 0.05 * pulse(now, 0.5) : 1);
	const tenseGlow = $derived(scatterTense ? Math.min(1, now / 150) * (0.6 + 0.4 * pulse(now, 0.5)) : 0);
</script>

{#if glowAlpha > 0 || tenseGlow > 0}
	<Sprite
		key="fxGlow"
		anchor={0.5}
		x={props.x}
		y={props.y}
		width={SYMBOL_SIZE * (scatterTense ? 1.9 : high ? 1.8 : 1.5) * (scatterTense ? tenseScale : winScale)}
		height={SYMBOL_SIZE * (scatterTense ? 1.9 : high ? 1.8 : 1.5) * (scatterTense ? tenseScale : winScale)}
		tint={scatterTense ? 0xffc04a : glowTint}
		alpha={Math.max(glowAlpha, tenseGlow)}
		blendMode="add"
	/>
{/if}

<!-- No outline, tint or colour boost on a win (the old gold WinFlash rim and the animate
	 layer's saturation filter left fish looking flat once they dropped back): symbols keep
	 their true rendered colours throughout; the pop-out alone marks the win. -->
<Container
	x={(props.x ?? 0) + shakeX}
	y={props.y ?? 0}
	scale={scatterTense ? tenseScale : winScale}
	rotation={shake}
>
{#if idleLoop && idleInfo}
	<SymbolAnimatedSprite symbolInfo={idleInfo} loop={true} />
{:else if isSprite}
	<SymbolSprite
		symbolInfo={sheetMissing ? staticInfo : symbolInfo}
		oncomplete={props.oncomplete}
		bounce={props.state === 'land'}
		{idle}
		resting={props.state === 'static' || props.state === 'postWinStatic'}
		cell={props.cell}
		spinning={props.state === 'spin'}
	/>
{:else if isSpriteSheet}
	{#if props.state === 'explosion' && staticInfo.type === 'sprite'}
		<SymbolPop symbolInfo={staticInfo} />
	{/if}
	<SymbolAnimatedSprite
		{symbolInfo}
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
</Container>

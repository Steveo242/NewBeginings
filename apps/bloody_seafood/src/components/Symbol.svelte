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
	const idleJitter = $derived.by(() => {
		const [r, c] = (props.cell ?? '0:0').split(':').map(Number);
		return 0.88 + 0.24 * (((r * 7 + c) * 0.618034) % 1);
	});
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

	// Win: a barely-there punch-in (1.04 -> 1, eased out over ~320 ms) and NO glow. The baked
	// win animation carries all the motion and light. (v5.4: a 1.8-cell additive warm glow
	// sat behind every winner; in a cluster the winners are neighbours on the animate layer,
	// so each one's glow was added over the next fish - washing them white - and the old
	// 1.18-1.22 punch-in upscaled the 512 px frames, softening them, until they settled.)
	const high = $derived(HIGH_SYMBOLS.includes(props.rawSymbol.name) || props.rawSymbol.name === 'W');
	const punch = $derived(Math.max(0, 1 - now / 320));
	const winScale = $derived(isWin ? 1 + (high ? 0.04 : 0.03) * punch * punch * punch : 1);
	// Scatter tension: a slow, straining rock (~1.5 Hz, the rope's pull - a fast tremble read
	// as jitter), and a gold glow throbbing on the beat
	const shake = $derived(scatterTense ? Math.sin(now / 105) * (0.03 + Math.min(0.02, now / 60000)) : 0);
	const shakeX = $derived(scatterTense ? Math.sin(now / 105 + 0.6) * SYMBOL_SIZE * 0.012 : 0);
	const tenseScale = $derived(scatterTense ? 1.06 + 0.05 * pulse(now, 0.5) : 1);
	const tenseGlow = $derived(scatterTense ? Math.min(1, now / 150) * (0.6 + 0.4 * pulse(now, 0.5)) : 0);
</script>

{#if tenseGlow > 0}
	<Sprite
		key="fxGlow"
		anchor={0.5}
		x={props.x}
		y={props.y}
		width={SYMBOL_SIZE * 1.9 * tenseScale}
		height={SYMBOL_SIZE * 1.9 * tenseScale}
		tint={0xffc04a}
		alpha={tenseGlow}
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
	<!-- each cell breathes at its own pace (+-12%), so a settled board never pulses in step -->
	<SymbolAnimatedSprite
		symbolInfo={{ ...idleInfo, animationSpeed: idleInfo.animationSpeed * idleJitter }}
		loop={true}
	/>
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

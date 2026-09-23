<script lang="ts">
	import * as PIXI from 'pixi.js';
	import { Sprite, type SpriteProps } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';
	import { elasticOut } from 'svelte/easing';

	import { getSymbolInfo } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';
	import { getContext } from '../game/context';

	type Props = {
		x?: number;
		y?: number;
		symbolInfo: ReturnType<typeof getSymbolInfo>;
		oncomplete?: () => void;
		bounce?: boolean;
		/** Symbol is at rest (static/postWinStatic) - eligible for the idle bob. */
		idle?: boolean;
		/** Symbol is mid-tumble - eligible for the fall motion blur. */
		spinning?: boolean;
	};

	const props: Props = $props();
	const context = getContext();

	// A tiny always-on bob + sway so a settled board never reads as a frozen
	// picture - reviewers flagged static symbols as looking like "flattened
	// high-res pictures" rather than integrated game elements. Deliberately
	// subtle (a couple of px, well under a degree of rotation): this has to
	// read as "alive" at a glance, not as visible jitter competing with the
	// land bounce or a win.  Phase is derived from this symbol's own board
	// position so neighbouring cells don't bob in lockstep, which would read
	// as a mechanical grid pulse rather than organic life.
	let t = $state(0);
	const tick = () => {
		t += context.stateApp.pixiApplication!.ticker.deltaMS;
	};
	if (context.stateApp.pixiApplication) {
		context.stateApp.pixiApplication.ticker.add(tick);
	}
	$effect(() => () => context.stateApp.pixiApplication?.ticker.remove(tick));

	const phase = $derived(((props.x ?? 0) * 0.37 + (props.y ?? 0) * 0.53) % (Math.PI * 2));
	const idleY = $derived(props.idle ? Math.sin(t / 1400 + phase) * SYMBOL_SIZE * 0.012 : 0);
	const idleRotation = $derived(
		props.idle ? Math.sin(t / 2100 + phase * 1.3) * 0.018 : 0,
	);
	const idleScale = $derived(props.idle ? 1 + Math.sin(t / 1700 + phase * 0.7) * 0.01 : 1);

	// Fall blur: a vertical-only streak while tumbling, cheap (one Pixi
	// BlurFilter, already a dependency) and removed the instant the symbol
	// isn't spinning so it never blurs a settled or landing frame.
	const spinFilters = $derived(
		props.spinning ? [new PIXI.BlurFilter({ strengthX: 0, strengthY: 6, quality: 2 })] : [],
	);

	// A quick squash-and-release on landing, not a full animation state -
	// every symbol just settles into place with a little life instead of
	// popping in dead-still. Starts pre-squashed and springs out to 1, so
	// the "impact" reads as instant rather than a delayed grow-in.
	const BOUNCE_DURATION = 420;
	const scale = new Tween(1, { duration: BOUNCE_DURATION, easing: elasticOut });
	const rotation = new Tween(0, { duration: BOUNCE_DURATION, easing: elasticOut });

	// This component instance is reused across every state a symbol passes
	// through (static/land/win/...) rather than remounted, since the parent
	// {#if isSprite} branch never changes - so onMount only ever fires once,
	// long before a real 'land' transition happens. The trigger has to live
	// in an $effect, which reruns every time `bounce` flips, not just once.
	$effect(() => {
		props.symbolInfo;
		if (props.bounce) {
			scale.set(0.82, { duration: 0 });
			rotation.set(Math.random() < 0.5 ? -0.07 : 0.07, { duration: 0 });
			scale.set(1);
			rotation.set(0);
			const timeout = setTimeout(() => props.oncomplete?.(), BOUNCE_DURATION);
			return () => clearTimeout(timeout);
		}
		props.oncomplete?.();
	});
</script>

<Sprite
	x={props.x}
	y={(props.y ?? 0) + idleY}
	anchor={0.5}
	key={props.symbolInfo.assetKey}
	width={SYMBOL_SIZE * props.symbolInfo.sizeRatios.width * scale.current * idleScale}
	height={SYMBOL_SIZE * props.symbolInfo.sizeRatios.height * scale.current * idleScale}
	rotation={rotation.current + idleRotation}
	filters={spinFilters}
/>

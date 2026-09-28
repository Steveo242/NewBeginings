<script lang="ts">
	import { Sprite } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { BEAT_MS, pulse } from '../game/tempo';

	// A soft light behind a symbol. Scatters are always lit and breathe with the music;
	// premiums light up while they drop and land, then fade back as the reel settles.
	type Props = { x?: number; y?: number; kind: 'scatter' | 'wild' | 'premium'; lit: boolean };
	const props: Props = $props();
	const context = getContext();

	const TINT = { scatter: 0xffc45a, wild: 0xffd23c, premium: 0xfff0d6 } as const;
	const PEAK = { scatter: 0.85, wild: 1, premium: 0.6 } as const;

	// fade in fast on the way down, out over a beat once settled
	const level = new Tween(0, { easing: cubicOut });
	$effect(() => {
		level.set(props.lit ? 1 : 0, { duration: props.lit ? 120 : BEAT_MS });
	});

	let now = $state(performance.now());
	const tick = () => (now = performance.now());
	$effect(() => {
		const ticker = context.stateApp.pixiApplication?.ticker;
		if (props.kind === 'premium' || !ticker) return;
		ticker.add(tick);
		return () => ticker.remove(tick);
	});

	const breathes = $derived(props.kind !== 'premium');
	const breathe = $derived(breathes ? pulse(now) : 0.5);
	const size = $derived(SYMBOL_SIZE * (breathes ? 1.55 + 0.3 * breathe : 1.45));
	const alpha = $derived(level.current * PEAK[props.kind] * (breathes ? 0.55 + 0.45 * breathe : 1));
</script>

{#if level.current > 0.01}
	<Sprite
		key="fxGlow"
		anchor={0.5}
		x={props.x}
		y={props.y}
		width={size}
		height={size}
		tint={TINT[props.kind]}
		{alpha}
		blendMode="add"
	/>
{/if}

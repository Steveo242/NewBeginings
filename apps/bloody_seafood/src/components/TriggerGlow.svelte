<script lang="ts" module>
	export type EmitterEventTriggerGlow = {
		type: 'scatterTriggerGlow';
		positions: { reel: number; row: number }[];
	};
</script>

<script lang="ts">
	import { Sprite } from 'pixi-svelte';

	import BoardContainer from './BoardContainer.svelte';
	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';

	// When the chests that trigger free spins burst open, each gets a pulsing gold glow
	// around it - three chests animating among 46 other symbols otherwise
	// don't pull the eye. Over the resting symbols (the tank's water layers are opaque),
	// under the 3D win, which plays in the unmasked animate layer.
	const DURATION = 2.2;
	const context = getContext();

	let positions: { reel: number; row: number }[] = $state([]);
	let t = $state(0);
	let raf = 0;

	context.eventEmitter.subscribeOnMount({
		scatterTriggerGlow: (emitterEvent) => {
			positions = emitterEvent.positions;
			const start = performance.now();
			cancelAnimationFrame(raf);
			const loop = (now: number) => {
				t = (now - start) / 1000;
				if (t < DURATION) raf = requestAnimationFrame(loop);
				else positions = [];
			};
			raf = requestAnimationFrame(loop);
		},
	});

	// swell in, pulse twice, fade out
	const alpha = $derived(
		Math.min(1, t * 4) * Math.min(1, (DURATION - t) * 2) * (0.75 + 0.25 * Math.cos(t * Math.PI * 2.4)),
	);
	const size = $derived(SYMBOL_SIZE * (2.6 + 0.3 * Math.sin(t * Math.PI * 2.4)));
</script>

<BoardContainer>
	{#each positions as p}
		<Sprite
			key="fxGlow"
			anchor={0.5}
			x={SYMBOL_SIZE * (p.reel + 0.5)}
			y={SYMBOL_SIZE * (p.row - 0.5)}
			width={size}
			height={size}
			tint={0xffc060}
			{alpha}
			blendMode="add"
		/>
	{/each}
</BoardContainer>

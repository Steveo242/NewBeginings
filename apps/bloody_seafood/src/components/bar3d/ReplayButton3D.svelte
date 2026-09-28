<script lang="ts">
	// The play button's brass porthole in replay mode: it never sends a play request.
	// While the replayed round runs the glyph turns and the button is greyed; once the
	// round has finished, pressing it (or Space) plays the same round again.
	import { Sprite } from 'pixi-svelte';
	import { Button } from 'components-pixi';
	import { OnHotkey } from 'components-shared';

	import { getContext } from '../../game/context';
	import { restoreReplayRound } from '../../game/replay';

	const { size }: { size: number } = $props();
	const context = getContext();
	const running = $derived(!context.stateXstateDerived.isIdle());
	const ART = 1.3;

	let angle = $state(0);

	$effect(() => {
		if (!running) return;
		let raf = 0;
		let last = performance.now();
		const tick = (now: number) => {
			angle = (angle + ((now - last) / 1000) * 1.6 * Math.PI * 2) % (Math.PI * 2);
			last = now;
			raf = requestAnimationFrame(tick);
		};
		raf = requestAnimationFrame(tick);
		return () => cancelAnimationFrame(raf);
	});

	const onpress = () => {
		if (running || !restoreReplayRound()) return;
		context.eventEmitter.broadcast({ type: 'soundPressGeneral' });
		context.eventEmitter.broadcast({ type: 'resumeBet' });
	};
</script>

<OnHotkey hotkey="Space" disabled={running} {onpress} />
<Button anchor={0.5} sizes={{ width: size, height: size }} {onpress} disabled={running}>
	{#snippet children({ center, hovered, pressed })}
		{@const state = running ? 'idle' : pressed ? 'pressed' : hovered ? 'hover' : 'idle'}
		<Sprite
			key={`spin_${state}.png`}
			{...center}
			anchor={0.5}
			width={size * ART}
			height={size * ART}
			tint={running ? 0x8a8a8a : 0xffffff}
		/>
		<Sprite
			key="spin_glyph.png"
			{...center}
			anchor={0.5}
			width={size * ART * (pressed ? 0.975 : 1)}
			height={size * ART * (pressed ? 0.975 : 1)}
			rotation={angle}
			alpha={running ? 0.5 : 1}
		/>
	{/snippet}
</Button>

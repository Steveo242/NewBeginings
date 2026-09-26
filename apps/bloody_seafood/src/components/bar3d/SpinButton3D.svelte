<script lang="ts">
	// The play button as a rendered brass porthole (build_ui3d.py "spin"): the body has
	// idle/hover/pressed frames, and the arrow glyph is its own layer so it can turn
	// while the reels run. Bet/stop behaviour and the Space hotkey
	// are the shared ButtonBet's, via the shared ButtonBetProvider.
	import { Sprite } from 'pixi-svelte';
	import { Button } from 'components-pixi';
	import { OnHotkey } from 'components-shared';
	import { stateBetDerived } from 'state-shared';
	import ButtonBetProvider from 'components-ui-pixi/src/components/ButtonBetProvider.svelte';

	import { getContext } from '../../game/context';

	const { size }: { size: number } = $props();
	const context = getContext();
	const disabled = $derived(!stateBetDerived.isBetCostAvailable());
	const spinning = $derived(!context.stateXstateDerived.isIdle());
	const ART = 1.3;

	let angle = $state(0);
	const speed = $derived(spinning ? 1.6 : 0); // turns per second

	$effect(() => {
		if (!speed) return;
		let raf = 0;
		let last = performance.now();
		const tick = (now: number) => {
			angle = (angle + ((now - last) / 1000) * speed * Math.PI * 2) % (Math.PI * 2);
			last = now;
			raf = requestAnimationFrame(tick);
		};
		raf = requestAnimationFrame(tick);
		return () => cancelAnimationFrame(raf);
	});
</script>

<ButtonBetProvider>
	{#snippet children({ key, onpress })}
		{@const greyed = disabled || key === 'spin_disabled' || key === 'stop_disabled'}
		<OnHotkey hotkey="Space" {disabled} {onpress} />
		<Button anchor={0.5} sizes={{ width: size, height: size }} {onpress} {disabled}>
			{#snippet children({ center, hovered, pressed })}
				{@const state = greyed ? 'idle' : pressed ? 'pressed' : hovered ? 'hover' : 'idle'}
				<Sprite
					key={`spin_${state}.png`}
					{...center}
					anchor={0.5}
					width={size * ART}
					height={size * ART}
					tint={greyed ? 0x8a8a8a : 0xffffff}
				/>
				<Sprite
					key="spin_glyph.png"
					{...center}
					anchor={0.5}
					width={size * ART * (pressed ? 0.975 : 1)}
					height={size * ART * (pressed ? 0.975 : 1)}
					rotation={angle}
					alpha={greyed ? 0.5 : 1}
				/>
			{/snippet}
		</Button>
	{/snippet}
</ButtonBetProvider>

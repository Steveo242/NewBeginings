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
	import { pulse as tempoPulse } from '../../game/tempo';

	const { size }: { size: number } = $props();
	const context = getContext();
	const disabled = $derived(!stateBetDerived.isBetCostAvailable());
	const spinning = $derived(!context.stateXstateDerived.isIdle());
	const ART = 1.3;
	// The porthole's face sits up-left of its frame (the shadow falls down-right): the
	// body spans 30-335 of 384 px, and the arrow ring is centred at (182.8, 183.1). Each
	// is anchored on its own centre so the arrow turns in place on the face - turning it
	// round the frame's centre swung it in a circle half off the button.
	const BODY_ANCHOR = 182.5 / 384;
	const GLYPH_ANCHOR = { x: 182.8 / 384, y: 183.1 / 384 };
	/** the arrow ring is drawn small in its frame (r 45 of 384); bring it up to fill the face */
	const GLYPH_K = 1.45;

	let angle = $state(0);
	let pulse = $state(0);
	const speed = $derived(spinning ? 1.6 : 0); // turns per second

	$effect(() => {
		let raf = 0;
		let last = performance.now();
		const tick = (now: number) => {
			if (speed) angle = (angle + ((now - last) / 1000) * speed * Math.PI * 2) % (Math.PI * 2);
			pulse = tempoPulse(now);
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
				{#if !greyed}
					<!-- a warm halo that breathes while the game waits on a press, and flares
					     hot while the reels run -->
					<Sprite
						key="fxGlow"
						{...center}
						anchor={0.5}
						width={size * (1.9 + 0.25 * pulse)}
						height={size * (1.9 + 0.25 * pulse)}
						tint={spinning ? 0xffe08a : 0xffa63d}
						alpha={spinning ? 0.75 : 0.28 + 0.32 * pulse}
						blendMode="add"
					/>
				{/if}
				<Sprite
					key={`spin_${state}.png`}
					{...center}
					anchor={BODY_ANCHOR}
					width={size * ART}
					height={size * ART}
					tint={greyed ? 0x8a8a8a : 0xffffff}
				/>
				<Sprite
					key="spin_glyph.png"
					{...center}
					anchor={GLYPH_ANCHOR}
					width={size * ART * GLYPH_K * (pressed ? 0.95 : 1)}
					height={size * ART * GLYPH_K * (pressed ? 0.95 : 1)}
					rotation={angle}
					tint={greyed ? 0xffffff : 0xfff1c8}
					alpha={greyed ? 0.5 : 1}
				/>
			{/snippet}
		</Button>
	{/snippet}
</ButtonBetProvider>

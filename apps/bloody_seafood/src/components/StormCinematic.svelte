<script lang="ts" module>
	export type EmitterEventStormCinematic =
		| { type: 'stormCinematic' }
		// a lightning strike now, with a whiteout and close thunder (Background) - the bonus
		// music's voice -> crew switch
		| { type: 'stormStrike' };
</script>

<script lang="ts">
	import { Tween } from 'svelte/motion';
	import { onDestroy } from 'svelte';
	import { Container } from 'pixi-svelte';
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { stateBetDerived } from 'state-shared';
	import { waitForResolve } from 'utils-shared/wait';

	import { getContext } from '../game/context';
	import { idleLife } from '../game/idleLife.svelte';
	import StormChurn from './StormChurn.svelte';

	// The bonus trigger's storm, ~2.4 s between the scatter win and the free-spins intro:
	// the sky darkens and the rain comes in (Background, on this same event), a bolt
	// strikes with its thunder ~0.8 s in, the tank water churns with a rush of bubbles and
	// the caustics surge, and the screen sinks toward the intro's dark. Turbo shortens it;
	// a tap or Space skips straight to the intro.
	const context = getContext();
	const BASE_MS = 2400;

	let active = $state(false);
	let done = () => {};
	const dim = new Tween(0);
	let timer: ReturnType<typeof setTimeout> | undefined;
	let raf = 0;

	const finish = () => {
		if (!active) return;
		active = false;
		clearTimeout(timer);
		cancelAnimationFrame(raf);
		removeEventListener('pointerdown', finish, true);
		removeEventListener('keydown', onKey, true);
		idleLife.ripple = 0;
		dim.set(0, { duration: 0 });
		done();
	};
	const onKey = (e: KeyboardEvent) => {
		if (e.code === 'Space' || e.code === 'Enter') finish();
	};

	context.eventEmitter.subscribeOnMount({
		stormCinematic: async () => {
			const ms = BASE_MS / Math.max(1, stateBetDerived.timeScale());
			active = true;
			dim.set(0.38, { duration: ms * 0.75 });
			// the caustics surge while the water churns
			const t0 = performance.now();
			const loop = (now: number) => {
				const u = (now - t0) / ms;
				idleLife.ripple = u < 1 ? Math.sin(Math.PI * Math.min(1, u * 1.4)) : 0;
				if (u < 1) raf = requestAnimationFrame(loop);
			};
			raf = requestAnimationFrame(loop);
			addEventListener('pointerdown', finish, true);
			addEventListener('keydown', onKey, true);
			timer = setTimeout(finish, ms);
			await waitForResolve((resolve) => (done = resolve));
		},
	});

	onDestroy(finish);
</script>

{#if active}
	<CanvasSizeRectangle backgroundColor={0x02060a} backgroundAlpha={dim.current} />
	<MainContainer>
		<Container x={context.stateGameDerived.boardLayout().x} y={context.stateGameDerived.boardLayout().y}>
			<StormChurn duration={BASE_MS / Math.max(1, stateBetDerived.timeScale())} />
		</Container>
	</MainContainer>
{/if}

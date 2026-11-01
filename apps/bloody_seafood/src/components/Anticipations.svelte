<script lang="ts">
	import { OnMount } from 'components-shared';
	import { SECOND } from 'constants-shared/time';

	import { getContext } from '../game/context';
	import { rope } from '../game/stateGame.svelte';
	import Anticipation from './Anticipation.svelte';

	const context = getContext();
	const hasAnticipation = $derived(
		context.stateGame.board.some((reel) => reel.reelState.anticipating),
	);

	// The rope strains only while an anticipating reel is still dropping: tied to the reels,
	// not to the glow's out-animation, which lingers on well after they have stopped.
	const straining = $derived(
		context.stateGame.board.some(
			(reel) => reel.reelState.anticipating && reel.reelState.motion !== 'stopped',
		),
	);
	// On top of the rope (kept as it was): a low heartbeat that swells under it while a reel
	// anticipates and cuts dead on the last stop - then the anchor clang if one landed
	// (stateGame) or, if the reels came up short, a quick deflating trombone.
	let wasStraining = false;
	let strainStart = 0;
	$effect(() => {
		if (straining && !wasStraining) {
			strainStart = performance.now();
			context.eventEmitter.broadcast({ type: 'soundLoop', name: 'sfx_heartbeat' });
			context.eventEmitter.broadcast({ type: 'soundFade', name: 'sfx_heartbeat', from: 0.25, to: 1, duration: 2.5 * SECOND });
		}
		if (!straining && wasStraining) {
			context.eventEmitter.broadcast({ type: 'soundStop', name: 'sfx_heartbeat' });
			if (rope.snappedAt < strainStart) context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_antic_miss', forcePlay: true });
		}
		wasStraining = straining;
		if (!straining) context.eventEmitter.broadcast({ type: 'soundStop', name: 'sfx_rope_strain' });
	});

	// after a snap the rope hangs slack for a moment before the next reel takes up the strain
	const SNAP_SLACK_MS = 700;
	const takeUpStrain = () => {
		const wait = Math.max(0, rope.snappedAt + SNAP_SLACK_MS - performance.now());
		setTimeout(() => {
			if (!straining) return;
			// not forced: reels flagged together get one snatch, not a flam
			context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_rope_taut' });
			// 4 beats long, so it loops on the music's pulse
			context.eventEmitter.broadcast({ type: 'soundLoop', name: 'sfx_rope_strain' });
		}, wait);
	};
</script>

{#if hasAnticipation}
	<OnMount
		onmount={() => {
			context.eventEmitter.broadcast({ type: 'soundLoop', name: 'sfx_anticipation' });
			context.eventEmitter.broadcast({
				type: 'soundFade',
				name: 'sfx_anticipation',
				from: 0,
				to: 1,
				duration: SECOND,
			});

			return () => {
				context.eventEmitter.broadcast({ type: 'soundStop', name: 'sfx_anticipation' });
			};
		}}
	/>
{/if}

{#each context.stateGame.board as reel}
	{#if reel.reelState.anticipating}
		<OnMount onmount={takeUpStrain} />
		<Anticipation {reel} oncomplete={() => (reel.reelState.anticipating = false)} />
	{/if}
{/each}

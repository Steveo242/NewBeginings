<script lang="ts">
	import { Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { glass } from '../game/glass.svelte';

	const context = getContext();
	const FRAME_RATIO = 1120 / 700;
	const layout = $derived(context.stateGameDerived.boardLayout());
	const size = $derived(layout.width * FRAME_RATIO);
</script>

<!--
	Drawn OVER the symbols so they sit inside the tank: the glass pane's rendered
	reflections as pure added light (glints and polished edges, never a darkening
	film), then the riveted iron frame, lid handle and plinth.
-->
<!-- half strength: its two reflection streaks added up to 35/255 of light across the middle
     reels and washed out the symbols under them -->
<!-- gone for good once GlassBreak smashes it as the game opens; until then it shows at full
     strength so the player sees there IS a pane before it bursts (over the deep-blue water
     the half-strength reflections no longer read, and the smash looked like it came from
     nowhere) -->
{#if glass.intact}
	<Sprite key="tankGlass" anchor={0.5} x={layout.x} y={layout.y} width={size} height={size} blendMode="add" alpha={0.9} />
{/if}
<Sprite key="tankFront" anchor={0.5} x={layout.x} y={layout.y} width={size} height={size} />

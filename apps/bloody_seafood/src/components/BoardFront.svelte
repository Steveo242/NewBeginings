<script lang="ts">
	import { Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';

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
<Sprite key="tankGlass" anchor={0.5} x={layout.x} y={layout.y} width={size} height={size} blendMode="add" alpha={0.5} />
<Sprite key="tankFront" anchor={0.5} x={layout.x} y={layout.y} width={size} height={size} />

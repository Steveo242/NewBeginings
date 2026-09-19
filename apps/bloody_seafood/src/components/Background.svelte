<script lang="ts">
	import { Rectangle, Sprite, Container } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import Bubbles from './Bubbles.svelte';

	const context = getContext();
	const sizes = $derived(context.stateLayoutDerived.canvasSizes());
</script>

<!-- Base fill matches the gradient's deep end, so any sliver the stretched
     sprite doesn't cover on an extreme aspect ratio still reads as water. -->
<Rectangle {...sizes} backgroundColor={0x1b6ca0} zIndex={-9} />

<Container zIndex={-8}>
	<Sprite key="bgWater" x={0} y={0} width={sizes.width} height={sizes.height} />
</Container>

<!-- Behind the reels: the main body of bubbles. -->
<Bubbles zIndex={-7} count={26} />

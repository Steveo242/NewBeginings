<script lang="ts">
	import { Rectangle, Sprite, Container } from 'pixi-svelte';
	import { onDestroy } from 'svelte';

	import { getContext } from '../game/context';

	const context = getContext();
	const sizes = $derived(context.stateLayoutDerived.canvasSizes());

	let t = $state(0);
	const tick = () => { t += context.stateApp.pixiApplication!.ticker.deltaMS; };
	if (context.stateApp.pixiApplication) {
		context.stateApp.pixiApplication.ticker.add(tick);
	}
	onDestroy(() => {
		context.stateApp.pixiApplication?.ticker.remove(tick);
	});

	// drift + bob, all derived from one clock
	const boatX = $derived(-(t * 0.0035) % (sizes.width * 0.25));
	const gullX = $derived(sizes.width * 0.10 - ((t * 0.018) % (sizes.width * 1.6)));
	const waterY = $derived(Math.sin(t / 2600) * sizes.height * 0.004);
	const nearY = $derived(Math.sin(t / 1900 + 1.1) * sizes.height * 0.006);
</script>

<Rectangle {...sizes} backgroundColor={0x000000} zIndex={-9} />

<Container zIndex={-8}>
	<Sprite key="bgSky" x={0} y={0} width={sizes.width} height={sizes.height} />
</Container>

<Container zIndex={-7}>
	<Sprite key="bgBoats" x={boatX} y={0} width={sizes.width * 1.25} height={sizes.height} />
</Container>

<Container zIndex={-6}>
	<Sprite
		key="bgWater"
		x={0}
		y={sizes.height * 0.46 + waterY}
		width={sizes.width}
		height={sizes.height * 0.24}
	/>
</Container>

<Container zIndex={-5}>
	<Sprite
		key="bgNearBoats"
		x={0}
		y={sizes.height * 0.50 + nearY}
		width={sizes.width}
		height={sizes.height * 0.22}
	/>
</Container>

<Container zIndex={-4}>
	<Sprite
		key="bgDock"
		x={0}
		y={sizes.height * 0.64}
		width={sizes.width}
		height={sizes.height * 0.36}
	/>
</Container>

<Container zIndex={-3}>
	<Sprite key="bgGulls" x={gullX} y={sizes.height * 0.05} width={sizes.width * 1.6} height={sizes.height * 0.30} />
</Container>

<Container zIndex={-2}>
	<Sprite key="bgOverlay" x={0} y={0} width={sizes.width} height={sizes.height} alpha={0.3} />
</Container>

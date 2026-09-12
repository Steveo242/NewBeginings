<script lang="ts">
	import { stateGame } from '../game/stateGame.svelte';
	import type { Snippet } from 'svelte';

	import { Container, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';

	type Props = {
		children: Snippet;
	};

	const props: Props = $props();

	const context = getContext();

	let settleOffset = $state(0);
	let t = 0;
	let running = false;
	const DUR = 280;
	const tick = () => {
		if (!running) return;
		t += context.stateApp.pixiApplication!.ticker.deltaMS;
		const k = Math.min(t / DUR, 1);
		settleOffset = k >= 1 ? 0 : Math.sin(k * Math.PI) * 16;
			stateGame.boardBump = settleOffset;
		if (k >= 1) { running = false; context.stateApp.pixiApplication?.ticker.remove(tick); }
	};
	context.eventEmitter.subscribeOnMount({
		boardBump: () => {
			t = 0;
			if (!running) { running = true; context.stateApp.pixiApplication!.ticker.add(tick); }
		},
	});
</script>

<Container
	x={context.stateGameDerived.boardLayout().x}
	y={context.stateGameDerived.boardLayout().y + settleOffset}
	pivot={context.stateGameDerived.boardLayout().pivot}
>
	{@render props.children()}
</Container>

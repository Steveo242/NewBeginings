<script lang="ts">
	import type { Snippet } from 'svelte';

	import { Container } from 'pixi-svelte';

	import { getContext } from '../game/context';

	type Props = {
		children: Snippet;
	};

	const props: Props = $props();

	const context = getContext();

	let settleOffset = $state(0);
	let t = 0;
	let running = false;
	const DUR = 420;
	const tick = () => {
		if (!running) return;
		t += context.stateApp.pixiApplication!.ticker.deltaMS;
		const k = Math.min(t / DUR, 1);
		settleOffset = k >= 1 ? 0 : Math.sin(k * Math.PI * 3) * 26 * (1 - k) * (1 - k);
		if (k >= 1) { running = false; context.stateApp.pixiApplication?.ticker.remove(tick); }
	};
	context.eventEmitter.subscribeOnMount({
		boardSettle: () => {
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

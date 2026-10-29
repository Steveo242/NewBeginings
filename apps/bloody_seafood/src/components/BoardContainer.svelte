<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { Filter } from 'pixi.js';

	import { Container } from 'pixi-svelte';

	import { getContext } from '../game/context';

	type Props = {
		children: Snippet;
		filters?: Filter[];
	};

	const props: Props = $props();

	const context = getContext();
</script>

<Container
	x={context.stateGameDerived.boardLayout().x}
	y={context.stateGameDerived.boardLayout().y}
	pivot={context.stateGameDerived.boardLayout().pivot}
	filters={props.filters}
>
	{@render props.children()}
</Container>

<script lang="ts" module>
	export type EmitterEventScatterShine = { type: 'scatterShine' };
</script>

<script lang="ts">
	import { Container, Sprite } from 'pixi-svelte';
	import { onDestroy } from 'svelte';

	import { getContext } from '../game/context';
	import { getSymbolInfo, getSymbolX } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';

	const SWEEP_MS = 900;

	const context = getContext();

	let elapsed = $state<number | undefined>(undefined);

	const tick = () => {
		if (elapsed === undefined) return;
		elapsed += context.stateApp.pixiApplication!.ticker.deltaMS;
		if (elapsed >= SWEEP_MS) elapsed = undefined;
	};
	if (context.stateApp.pixiApplication) {
		context.stateApp.pixiApplication.ticker.add(tick);
	}
	onDestroy(() => {
		context.stateApp.pixiApplication?.ticker.remove(tick);
	});

	// One clock for every scatter, so they sweep together rather than each
	// running its own timer - "in unison" is the whole point of the effect.
	context.eventEmitter.subscribeOnMount({
		scatterShine: () => {
			elapsed = 0;
		},
	});

	const progress = $derived(elapsed === undefined ? undefined : elapsed / SWEEP_MS);

	// Ease out at both ends so the streak fades in and out rather than
	// popping on at the symbol's edge.
	const fade = $derived(
		progress === undefined ? 0 : Math.sin(Math.min(1, Math.max(0, progress)) * Math.PI),
	);

	const scatters = $derived(
		context.stateGame.board.flatMap((reel, reelIndex) =>
			reel.reelState.symbols
				.filter((reelSymbol) => reelSymbol.rawSymbol.name === 'S')
				.map((reelSymbol) => ({
					reelIndex,
					reelSymbol,
					x: getSymbolX(reelIndex),
					y: reelSymbol.symbolY.current,
					info: getSymbolInfo({ rawSymbol: reelSymbol.rawSymbol, state: 'static' }),
				})),
		),
	);
</script>

{#if progress !== undefined}
	{#each scatters as scatter (`${scatter.reelIndex}-${scatter.y}`)}
		{@const width = SYMBOL_SIZE * scatter.info.sizeRatios.width}
		{@const height = SYMBOL_SIZE * scatter.info.sizeRatios.height}
		<Container x={scatter.x} y={scatter.y}>
			<!--
				The scatter's own sprite masks the streak, so the shine only
				lands on the symbol's artwork - masking to the cell box instead
				would light up the transparent space around it as a glowing
				rectangle.
			-->
			<Sprite
				isMask
				key={scatter.info.assetKey}
				anchor={0.5}
				{width}
				{height}
			/>
			<Sprite
				key="shineBand"
				anchor={0.5}
				x={(progress - 0.5) * width * 1.9}
				width={width * 0.42}
				height={height * 1.5}
				rotation={0.32}
				alpha={fade * 0.85}
				blendMode="add"
			/>
		</Container>
	{/each}
{/if}

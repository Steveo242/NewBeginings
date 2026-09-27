<script lang="ts" module>
	import ClusterWinAmount, { type RawWin, type Win } from './ClusterWinAmount.svelte';

	export type EmitterEventClusterWinAmounts = {
		type: 'showClusterWinAmounts';
		wins: RawWin[];
	};
</script>

<script lang="ts">
	import { waitForResolve } from 'utils-shared/wait';
	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';

	import BoardContainer from './BoardContainer.svelte';
	import { getContext } from '../game/context';

	const context = getContext();

	let wins: Win[] = $state([]);

	// Labels sit on each cluster's anchor cell, so two clusters winning side by side
	// printed straight over each other ("$3.$10.00"). Estimate each label's box from
	// its longest text (in cells: ~0.26 per character at this font size) and push
	// colliding labels apart vertically, keeping every label on the board.
	const CHAR_W = 0.26;
	const LABEL_H = 0.62;
	const layout = (raw: RawWin[]) => {
		const placed: { x: number; y: number; w: number }[] = [];
		return raw.map((win) => {
			const longest = Math.max(
				bookEventAmountToCurrencyString(win.result).length,
				win.mult > 1 ? `${bookEventAmountToCurrencyString(win.win)} X ${win.mult}`.length : 0,
			);
			const w = longest * CHAR_W + 0.2;
			const x = Math.min(7 - w / 2, Math.max(w / 2, win.reel + 0.5));
			let y = win.row - 0.5;
			const hits = (cy: number) =>
				placed.some((p) => Math.abs(p.x - x) < (p.w + w) / 2 && Math.abs(p.y - cy) < LABEL_H);
			for (let step = 1; hits(y) && step < 12; step++) {
				const off = Math.ceil(step / 2) * LABEL_H * (step % 2 ? 1 : -1);
				const cy = win.row - 0.5 + off;
				if (cy > LABEL_H / 2 && cy < 7 - LABEL_H / 2) y = cy;
			}
			placed.push({ x, y, w });
			return { ...win, x, y };
		});
	};

	context.eventEmitter.subscribeOnMount({
		showClusterWinAmounts: async (emitterEvent) => {
			wins = layout(emitterEvent.wins).map((rawWin) => ({ ...rawWin, oncomplete: () => {} }));
			const gerPromises = () =>
				wins.map(async (win) => {
					await waitForResolve((resolve) => (win.oncomplete = resolve));
				});
			await Promise.all(gerPromises());
			wins = [];
		},
	});
</script>

<BoardContainer>
	{#each wins as win}
		<ClusterWinAmount {win} />
	{/each}
</BoardContainer>

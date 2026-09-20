<script lang="ts">
	import { Container, Rectangle } from 'pixi-svelte';
	import { stateUi } from 'state-shared';
	import { BLACK } from 'constants-shared/colors';
	import type { LayoutUiProps } from 'components-ui-pixi/src/types';
	import { UI_BASE_SIZE } from 'components-ui-pixi/src/constants';
	import LabelFreeSpinCounter from 'components-ui-pixi/src/components/LabelFreeSpinCounter.svelte';

	import { getContext } from '../game/context';

	const props: LayoutUiProps = $props();
	const context = getContext();

	const canvas = $derived(context.stateLayoutDerived.canvasSizes());
	const layoutType = $derived(context.stateLayoutDerived.layoutType());

	// The bar is authored once in the shared controls' own coordinate space
	// (a button is UI_BASE_SIZE across) and the whole thing is scaled by a
	// single factor to fit the canvas. Sizes and positions therefore always
	// scale together; the previous version scaled sizes off the canvas
	// height and positions off its width, which on any portrait canvas drove
	// them apart until every control overlapped its neighbour.
	const BTN = UI_BASE_SIZE;
	const SPIN = UI_BASE_SIZE * 1.35;
	const LABEL_W = 430;
	const LABEL_H = 132;
	const GAP = 34;
	const ROW_GAP = 26;
	/** Stacked labels draw downwards from their origin, so lift them to sit centred. */
	const LABEL_SHIFT_Y = -UI_BASE_SIZE * 0.37;

	const LABEL_KEYS = ['balance', 'win', 'bet'];

	type Slot = { key: string; width: number };
	type Row = { slots: Slot[]; height: number };

	const icon = (key: string): Slot => ({ key, width: BTN });
	const label = (key: string): Slot => ({ key, width: LABEL_W });

	/**
	 * Three arrangements of the same controls. Wide is the single strip;
	 * compact folds the readouts onto their own line; stacked splits again so
	 * a phone held upright still gets full-size controls.
	 */
	const arrangements = $derived({
		wide: {
			heightRatio: 0.18,
			rows: [
				{
					height: Math.max(SPIN, LABEL_H),
					slots: [
						...(canvas.width < 1200
							? [icon('menu')]
							: [icon('rules'), icon('pay'), icon('settings'), icon('sound')]),
						icon('buy'),
						label('balance'),
						label('win'),
						label('bet'),
						icon('dec'),
						{ key: 'spin', width: SPIN },
						icon('inc'),
						icon('auto'),
						icon('turbo'),
					],
				},
			] as Row[],
		},
		compact: {
			heightRatio: 0.3,
			rows: [
				{ height: LABEL_H, slots: [label('balance'), label('win'), label('bet')] },
				{
					height: SPIN,
					slots: [
						icon('menu'),
						icon('buy'),
						icon('dec'),
						{ key: 'spin', width: SPIN },
						icon('inc'),
						icon('auto'),
						icon('turbo'),
					],
				},
			] as Row[],
		},
		stacked: {
			heightRatio: 0.32,
			rows: [
				{ height: LABEL_H, slots: [label('balance'), label('win')] },
				{
					height: SPIN,
					slots: [
						icon('menu'),
						icon('auto'),
						{ key: 'spin', width: SPIN },
						icon('turbo'),
						icon('buy'),
					],
				},
				{ height: BTN, slots: [icon('dec'), label('bet'), icon('inc')] },
			] as Row[],
		},
	});

	const WIDTH_RATIO = 0.98;
	const MAX_SCALE = 0.62;
	/** Below this the controls get too small to tap comfortably. */
	const MIN_COMFORT = 0.34;

	const measure = (arrangement: { heightRatio: number; rows: Row[] }) => {
		const rows = arrangement.rows.map((row) => {
			const width = row.slots.reduce((sum, s) => sum + s.width, 0) + GAP * (row.slots.length - 1);
			const centers: Record<string, number> = {};
			let cursor = -width * 0.5;
			for (const slot of row.slots) {
				centers[slot.key] = cursor + slot.width * 0.5;
				cursor += slot.width + GAP;
			}
			return { ...row, width, centers };
		});

		const width = Math.max(...rows.map((row) => row.width));
		const height =
			rows.reduce((sum, row) => sum + row.height, 0) + ROW_GAP * (rows.length - 1);

		let cursor = -height * 0.5;
		const placed = rows.map((row) => {
			const y = cursor + row.height * 0.5;
			cursor += row.height + ROW_GAP;
			return { ...row, y };
		});

		const scale = Math.min(
			(canvas.width * WIDTH_RATIO) / width,
			(canvas.height * arrangement.heightRatio) / height,
			MAX_SCALE,
		);

		return { rows: placed, width, height, scale };
	};

	// A tall canvas always splits into three rows - a lone wide strip under a
	// tall board wastes the space and reads as a desktop bar on a phone.
	// Otherwise keep the widest arrangement that still tests comfortably, and
	// if none does, take whichever leaves the controls largest.
	const chosen = $derived.by(() => {
		if (['portrait', 'tablet'].includes(layoutType)) return measure(arrangements.stacked);

		const wide = measure(arrangements.wide);
		if (wide.scale >= MIN_COMFORT) return wide;

		const compact = measure(arrangements.compact);
		if (compact.scale >= MIN_COMFORT) return compact;

		return compact.scale > wide.scale ? compact : wide;
	});

	const useMenu = $derived(chosen.rows.some((row) => row.slots.some((s) => s.key === 'menu')));

	// Game.svelte only renders the side counter panel on wide layouts, so
	// everywhere else the play slot has to carry the count itself.
	const counterInBar = $derived(
		stateUi.freeSpinCounterShow && !['desktop', 'landscape'].includes(layoutType),
	);

	const barHeight = $derived(chosen.height * chosen.scale);
	const margin = $derived(Math.min(canvas.height * 0.015, 16));
	const centerX = $derived(canvas.width * 0.5);
	const centerY = $derived(canvas.height - barHeight * 0.5 - margin);

	const PANEL_PAD = 30;

	// Where the menu button ended up, so its fold-out stack can sit above it.
	const menuRow = $derived(chosen.rows.find((row) => row.centers.menu !== undefined));
	const menuX = $derived(centerX + (menuRow?.centers.menu ?? 0) * chosen.scale);
	const menuY = $derived(centerY + (menuRow?.y ?? 0) * chosen.scale);
</script>

<Container zIndex={60}>
	<!-- Dark and semi-transparent so the harbour behind it still shows. -->
	<Rectangle
		anchor={0.5}
		x={centerX}
		y={centerY}
		width={(chosen.width + PANEL_PAD * 2) * chosen.scale}
		height={(chosen.height + PANEL_PAD * 2) * chosen.scale}
		borderRadius={Math.min(chosen.height + PANEL_PAD * 2, chosen.width) * chosen.scale * 0.18}
		backgroundColor={0x0a1a24}
		backgroundAlpha={0.82}
	/>

	<Container x={centerX} y={centerY} scale={chosen.scale}>
		{#each chosen.rows as row (row.y)}
			{#each row.slots as slot (slot.key)}
				<Container
					x={row.centers[slot.key]}
					y={row.y + (LABEL_KEYS.includes(slot.key) ? LABEL_SHIFT_Y : 0)}
				>
					{#if slot.key === 'menu'}
						{@render props.buttonMenu({ anchor: 0.5 })}
					{:else if slot.key === 'rules'}
						{@render props.buttonGameRules({ anchor: 0.5 })}
					{:else if slot.key === 'pay'}
						{@render props.buttonPayTable({ anchor: 0.5 })}
					{:else if slot.key === 'settings'}
						{@render props.buttonSettings({ anchor: 0.5 })}
					{:else if slot.key === 'sound'}
						{@render props.buttonSoundSwitch({ anchor: 0.5 })}
					{:else if slot.key === 'buy'}
						{#if !stateUi.freeSpinCounterShow}
							{@render props.buttonBuyBonus({ anchor: 0.5 })}
						{/if}
					{:else if slot.key === 'balance'}
						{@render props.amountBalance({ stacked: true })}
					{:else if slot.key === 'win'}
						{@render props.amountWin({ stacked: true })}
					{:else if slot.key === 'bet'}
						{#if counterInBar}
							<LabelFreeSpinCounter stacked />
						{:else}
							{@render props.amountBet({ stacked: true })}
						{/if}
					{:else if slot.key === 'dec'}
						{#if !counterInBar}
							{@render props.buttonDecrease({ anchor: 0.5 })}
						{/if}
					{:else if slot.key === 'inc'}
						{#if !counterInBar}
							{@render props.buttonIncrease({ anchor: 0.5 })}
						{/if}
					{:else if slot.key === 'spin'}
						<Container scale={SPIN / BTN}>
							{@render props.buttonBet({ anchor: 0.5 })}
						</Container>
					{:else if slot.key === 'auto'}
						{@render props.buttonAutoSpin({ anchor: 0.5 })}
					{:else if slot.key === 'turbo'}
						{@render props.buttonTurbo({ anchor: 0.5 })}
					{/if}
				</Container>
			{/each}
		{/each}
	</Container>
</Container>

{#if useMenu && stateUi.menuOpen}
	<Container zIndex={61}>
		<Rectangle
			eventMode="static"
			cursor="pointer"
			anchor={0.5}
			alpha={0.5}
			backgroundColor={BLACK}
			x={canvas.width * 0.5}
			y={canvas.height * 0.5}
			width={canvas.width}
			height={canvas.height}
			onpointerup={() => (stateUi.menuOpen = false)}
		/>

		<Container x={menuX} y={menuY} scale={chosen.scale}>
			<Container y={-(BTN + GAP) * 4}>
				{@render props.buttonPayTable({ anchor: 0.5 })}
			</Container>
			<Container y={-(BTN + GAP) * 3}>
				{@render props.buttonGameRules({ anchor: 0.5 })}
			</Container>
			<Container y={-(BTN + GAP) * 2}>
				{@render props.buttonSettings({ anchor: 0.5 })}
			</Container>
			<Container y={-(BTN + GAP)}>
				{@render props.buttonSoundSwitch({ anchor: 0.5 })}
			</Container>
			<Container>
				{@render props.buttonMenuClose({ anchor: 0.5 })}
			</Container>
		</Container>
	</Container>
{/if}

import { createLayout } from 'utils-layout';

export const { stateLayout, stateLayoutDerived } = createLayout({
	backgroundRatio: {
		normal: 2039 / 1000,
		portrait: 1242 / 2208,
	},
	// The board is 700x800 and sits centred in this space, so on the old
	// desktop/landscape/tablet sizes it filled the full height and left the
	// bet bar nowhere to go but on top of the reels. The extra height is
	// headroom for the bar, not a bigger board.
	mainSizesMap: {
		desktop: { width: 1422, height: 1010 },
		tablet: { width: 1000, height: 1180 },
		landscape: { width: 1600, height: 1120 },
		portrait: { width: 800, height: 1422 },
	},
});

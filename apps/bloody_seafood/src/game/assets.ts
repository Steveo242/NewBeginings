export default {
	bgSky: {
		type: 'sprite',
		src: new URL('../../assets/sprites/bgLayers/bg_land_sky.png', import.meta.url).href,
		preload: true,
	},
	bgBoats: {
		type: 'sprite',
		src: new URL('../../assets/sprites/bgLayers/bg_land_boats.png', import.meta.url).href,
		preload: true,
	},
	bgWater: {
		type: 'sprite',
		src: new URL('../../assets/sprites/bgLayers/bg_land_water.png', import.meta.url).href,
		preload: true,
	},
	bgNearBoats: {
		type: 'sprite',
		src: new URL('../../assets/sprites/bgLayers/bg_land_nearboats.png', import.meta.url).href,
		preload: true,
	},
	bgDock: {
		type: 'sprite',
		src: new URL('../../assets/sprites/bgLayers/bg_land_dock.png', import.meta.url).href,
		preload: true,
	},
	bgGulls: {
		type: 'sprite',
		src: new URL('../../assets/sprites/bgLayers/bg_land_gulls.png', import.meta.url).href,
		preload: true,
	},
	bgOverlay: {
		type: 'sprite',
		src: new URL('../../assets/sprites/bgLayers/bg_land_overlay.png', import.meta.url).href,
		preload: true,
	},
	sortingTable: {
		type: 'sprite',
		src: new URL('../../assets/sprites/table/sorting_table.png', import.meta.url).href,
		preload: true,
	},
	betUp: {
		type: 'sprite',
		src: new URL('../../assets/sprites/ui/bet_up.png', import.meta.url).href,
		preload: true,
	},
	betDown: {
		type: 'sprite',
		src: new URL('../../assets/sprites/ui/bet_down.png', import.meta.url).href,
		preload: true,
	},
	btnInfo: {
		type: 'sprite',
		src: new URL('../../assets/sprites/ui/btn_info.png', import.meta.url).href,
		preload: true,
	},
	btnPayTable: {
		type: 'sprite',
		src: new URL('../../assets/sprites/ui/btn_paytable.png', import.meta.url).href,
		preload: true,
	},
	bet: {
		type: 'sprite',
		src: new URL('../../assets/sprites/ui/spin_bs.png', import.meta.url).href,
		preload: true,
	},
	buyBonus: {
		type: 'sprite',
		src: new URL('../../assets/sprites/ui/mode_kiss.png', import.meta.url).href,
		preload: true,
	},
	titlePlaque: {
		type: 'sprite',
		src: new URL('../../assets/sprites/bgLayers/title_plaque.png', import.meta.url).href,
		preload: true,
	},
	loader: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/loader/loader.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/loader/loader.json', import.meta.url).href,
			scale: 2,
		},
		preload: true,
	},
	H1: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols/symbols.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols/h1.json', import.meta.url).href,
			scale: 2,
		},
	},
	H2: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols/symbols.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols/h2.json', import.meta.url).href,
			scale: 2,
		},
	},
	H3: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols/symbols.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols/h3.json', import.meta.url).href,
			scale: 2,
		},
	},
	H4: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols/symbols.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols/h4.json', import.meta.url).href,
			scale: 2,
		},
	},
	H5: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols/symbols.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols/h5.json', import.meta.url).href,
			scale: 2,
		},
	},
	L1: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols/symbols.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols/l1.json', import.meta.url).href,
			scale: 2,
		},
	},
	L2: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols/symbols.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols/l2.json', import.meta.url).href,
			scale: 2,
		},
	},
	L3: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols/symbols.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols/l3.json', import.meta.url).href,
			scale: 2,
		},
	},
	L4: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols/symbols.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols/l4.json', import.meta.url).href,
			scale: 2,
		},
	},
	M: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols2/symbols2.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols2/M.json', import.meta.url).href,
			scale: 2,
		},
	},
	S: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols2/symbols2.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols2/S.json', import.meta.url).href,
			scale: 2,
		},
	},
	explosion: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols3/symbols3.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols3/explosion.json', import.meta.url).href,
			scale: 2,
		},
	},
	W: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/symbols3/symbols3.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/symbols3/W.json', import.meta.url).href,
			scale: 2,
		},
	},
	reelsFrame: {
		type: 'sprites',
		src: new URL('../../assets/sprites/reelsFrame/reels_frame.json', import.meta.url).href,
	},
	payFrame: {
		type: 'sprite',
		src: new URL('../../assets/sprites/payFrame/payFrame.png', import.meta.url).href,
	},
	anticipation: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/anticipation/anticipation.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/anticipation/anticipation.json', import.meta.url).href,
			scale: 2,
		},
	},
	goldFont: {
		type: 'font',
		src: new URL('../../assets/fonts/goldFont/bs_gold.xml', import.meta.url).href,
	},
	goldBlur: {
		type: 'font',
		src: new URL('../../assets/fonts/goldBlur/bs_gold_blur.xml', import.meta.url).href,
	},
	bigwin: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/bigwin/big_wins.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/bigwin/mm_bigwin.json', import.meta.url).href,
			scale: 2,
		},
	},
	globalMultiplier: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/globalMultiplier/multiframe.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/globalMultiplier/multiframe.json', import.meta.url).href,
			scale: 2,
		},
	},
	fsIntro: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/fsIntro/fs_screen.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/fsIntro/fs_screen.json', import.meta.url).href,
			scale: 2,
		},
	},
	fsIntroNumber: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/fsIntro/fs_screen.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/fsIntro/fs_screen_number.json', import.meta.url).href,
			scale: 2,
		},
	},
	fsOutroNumber: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/fsIntro/fs_screen.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/fsIntro/fs_total_number.json', import.meta.url).href,
			scale: 2,
		},
	},
	foregroundAnimation: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/foregroundAnimation/bs_bg.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/foregroundAnimation/bs_bg.json', import.meta.url).href,
			scale: 2,
		},
		preload: true,
	},
	foregroundFeatureAnimation: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/foregroundFeatureAnimation/bs_bg_feature.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/foregroundFeatureAnimation/bs_bg_feature.json', import.meta.url).href,
			scale: 2,
		},
		preload: true,
	},
	tumble_multiplier: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/tumbleWin/tumble_win.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/tumbleWin/tumble_multiplier.json', import.meta.url).href,
			scale: 2,
		},
	},
	tumble_win: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/tumbleWin/tumble_win.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/tumbleWin/tumble_win.json', import.meta.url).href,
			scale: 2,
		},
	},
	reelhouse: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/reelhouse/reelhouse_glow.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/reelhouse/reelhouse_glow.json', import.meta.url).href,
			scale: 2,
		},
	},
	progressBar: {
		type: 'sprites',
		src: new URL('../../assets/sprites/progressBar/progressBar.json', import.meta.url).href,
		preload: true,
	},
	freeSpins: {
		type: 'sprites',
		src: new URL('../../assets/sprites/freeSpins/freeSpins.json', import.meta.url).href,
	},
	clusterWin: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/clusterWin/clusterpay.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/clusterWin/clusterpay.json', import.meta.url).href,
			scale: 2,
		},
	},
	transition: {
		type: 'spine',
		src: {
			atlas: new URL('../../assets/spines/transition/transition.atlas', import.meta.url).href,
			skeleton: new URL('../../assets/spines/transition/transition.json', import.meta.url).href,
			scale: 2,
		},
	},
	symbolsStatic: {
		type: 'sprites',
		src: new URL('../../assets/sprites/symbolsStatic/symbolsStatic.json', import.meta.url).href,
	},
	mBackgroundLow: {
		type: 'sprite',
		src: new URL('../../assets/sprites/mBackground/m_bg_low.png', import.meta.url).href,
	},
	mBackgroundMid: {
		type: 'sprite',
		src: new URL('../../assets/sprites/mBackground/m_bg_mid.png', import.meta.url).href,
	},
	mBackgroundHigh: {
		type: 'sprite',
		src: new URL('../../assets/sprites/mBackground/m_bg_high.png', import.meta.url).href,
	},
	H1_win: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H1_win.json', import.meta.url).href,
	},
	H2_win: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H2_win.json', import.meta.url).href,
	},
	H3_win: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H3_win.json', import.meta.url).href,
	},
	H4_win: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H4_win.json', import.meta.url).href,
	},
	H5_win: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/H5_win.json', import.meta.url).href,
	},
	L1_win: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/L1_win.json', import.meta.url).href,
	},
	L2_win: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/L2_win.json', import.meta.url).href,
	},
	L3_win: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/L3_win.json', import.meta.url).href,
	},
	L4_win: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/L4_win.json', import.meta.url).href,
	},
	S_win: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/S_win.json', import.meta.url).href,
	},
	W_win: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/symbolsAnim/W_win.json', import.meta.url).href,
	},
	coins: {
		type: 'spriteSheet',
		src: new URL('../../assets/sprites/coin/SD2_Coin.json', import.meta.url).href,
	},
	sound: {
		type: 'audio',
		src: new URL('../../assets/audio/sounds.json', import.meta.url).href,
		preload: true,
	},
} as const;

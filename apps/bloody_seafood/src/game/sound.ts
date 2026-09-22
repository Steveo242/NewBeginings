import { createSound } from 'utils-sound';

export type MusicName = 'bgm_main' | 'bgm_freespin';

export type SoundEffectName =
	| 'jng_intro_fs'
	| 'sfx_anticipation'
	| 'sfx_applause'
	| 'sfx_applause_big'
	| 'sfx_applause_epic'
	| 'sfx_applause_mega'
	| 'sfx_bigwin_coinloop'
	| 'sfx_btn_general'
	| 'sfx_btn_spin'
	| 'sfx_fs_respins'
	| 'sfx_multiplier_combine_a'
	| 'sfx_multiplier_combine_b'
	| 'sfx_multiplier_explosion_a'
	| 'sfx_multiplier_explosion_b'
	| 'sfx_multiplier_explosion_c'
	| 'sfx_multiplier_landing'
	| 'sfx_multiplier_reset'
	| 'sfx_multiplier_up'
	| 'sfx_multiplier_update'
	| 'sfx_multiplier_win'
	| 'sfx_reel_stop_1'
	| 'sfx_reel_stop_2'
	| 'sfx_reel_stop_3'
	| 'sfx_reel_stop_4'
	| 'sfx_reel_stop_5'
	| 'sfx_royals_landing'
	| 'sfx_scatter_reveal'
	| 'sfx_scatter_toot'
	| 'sfx_scatter_win'
	| 'sfx_scatter_win_v2'
	| 'sfx_superfreespin'
	| 'sfx_symbols_landing'
	| 'sfx_wild_explode'
	| 'sfx_win_bell'
	| 'sfx_winlevel_end'
	| 'sfx_winlevel_small'
	| 'sfx_youwon_panel'
	| 'tumble_win_1'
	| 'tumble_win_2'
	| 'tumble_win_3'
	| 'tumble_win_4';

export type SoundName = MusicName | SoundEffectName;

const sound = createSound<SoundName>();

export { sound };

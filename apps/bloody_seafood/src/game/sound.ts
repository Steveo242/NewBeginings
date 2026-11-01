import { createSound } from 'utils-sound';

export type MusicName = 'bgm_main' | 'bgm_fs_intro' | 'bgm_freespin' | 'bgm_super_intro' | 'bgm_superspin';

/** The bonus music (Sound.svelte): the track's calm section loops until the first free
 *  spin, then the main loop drops in on its downbeat with a lightning strike. */
export const bonusMusic = { dropped: false };
export const BONUS_MUSIC: MusicName[] = ['bgm_fs_intro', 'bgm_freespin', 'bgm_super_intro', 'bgm_superspin'];
export const bonusMusicName = (superMode: boolean): MusicName =>
	superMode
		? bonusMusic.dropped ? 'bgm_superspin' : 'bgm_super_intro'
		: bonusMusic.dropped ? 'bgm_freespin' : 'bgm_fs_intro';

export const ALL_MUSIC: MusicName[] = ['bgm_main', ...BONUS_MUSIC];

/** big-win music, one per celebration tier (tools/make_bigwin_music.py): the base game's
 *  jig and the bonuses' shanty set (_fs). One-shots over the ducked music. */
export type WinMusicName = `bgm_win_${'big' | 'superwin' | 'mega' | 'epic' | 'max'}${'' | '_fs'}`;

export type SoundEffectName =
	| WinMusicName
	| 'amb_storm'
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
	| 'sfx_mult_up_1'
	| 'sfx_mult_up_2'
	| 'sfx_mult_up_3'
	| 'sfx_mult_up_4'
	| 'sfx_mult_up_5'
	| 'sfx_mult_up_6'
	| 'sfx_mult_down'
	| 'sfx_stinger_big'
	| 'sfx_stinger_superwin'
	| 'sfx_stinger_mega'
	| 'sfx_stinger_epic'
	| 'sfx_stinger_max'
	| 'sfx_premium_land'
	| 'sfx_anchor_land_1'
	| 'sfx_anchor_land_2'
	| 'sfx_anchor_land_3'
	| 'sfx_wild_land'
	| 'sfx_heartbeat'
	| 'sfx_antic_miss'
	| 'sfx_reel_stop_1'
	| 'sfx_reel_stop_2'
	| 'sfx_reel_stop_3'
	| 'sfx_reel_stop_4'
	| 'sfx_reel_stop_5'
	| 'sfx_rope_snap'
	| 'sfx_rope_strain'
	| 'sfx_rope_taut'
	| 'sfx_royals_landing'
	| 'sfx_scatter_reveal'
	| 'sfx_scatter_toot'
	| 'sfx_scatter_win'
	| 'sfx_scatter_win_v2'
	| 'sfx_superfreespin'
	| 'sfx_thunder_close'
	| 'sfx_thunder_far'
	| 'sfx_symbols_landing'
	| 'sfx_wild_explode'
	| 'sfx_glass_shatter'
	| 'sfx_win_bell'
	| 'sfx_winlevel_end'
	| 'sfx_winlevel_small'
	| 'sfx_youwon_panel'
	| 'tumble_win_1'
	| 'tumble_win_2'
	| 'tumble_win_3'
	| 'tumble_win_4'
	| 'sfx_cluster_hit_1'
	| 'sfx_cluster_hit_2'
	| 'sfx_cluster_hit_3'
	| 'sfx_cluster_burst_1'
	| 'sfx_cluster_burst_2'
	| 'sfx_cluster_burst_3';

/** one of the three takes, so a long cascade never repeats the same hit */
export const clusterSfx = (kind: 'hit' | 'burst') =>
	`sfx_cluster_${kind}_${1 + Math.floor(Math.random() * 3)}` as SoundEffectName;

export type SoundName = MusicName | SoundEffectName;

const sound = createSound<SoundName>();

export { sound };

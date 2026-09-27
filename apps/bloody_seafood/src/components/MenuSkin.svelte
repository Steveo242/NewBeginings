<script lang="ts">
	// The HTML menus (buy bonus + confirm, autoplay, settings, paytable, rules) in the same
	// rendered iron-and-brass kit as the 3D bet bar (bs-render build_ui3d.py). Those menus
	// are components-ui-html's, which is shared with every game and never edited, so this
	// only restyles them - by their class names, as 9-slice border-images - and leaves all
	// of their markup and behaviour alone. Text stays live and flat for legibility.
	//
	// border-image slices are measured off the renders: shadow margin + corner radius, in
	// image px. border-image-outset pushes the shadow margin back outside the element box
	// so the brass edge lands on the element's own edge.
	import frame from '../menus3d/frame.webp';
	import card from '../menus3d/card.webp';
	import btnIdle from '../menus3d/btn_idle.webp';
	import btnHover from '../menus3d/btn_hover.webp';
	import btnPressed from '../menus3d/btn_pressed.webp';
	import plusIdle from '../menus3d/plus_idle.webp';
	import plusHover from '../menus3d/plus_hover.webp';
	import minusIdle from '../menus3d/minus_idle.webp';
	import minusHover from '../menus3d/minus_hover.webp';
	import closeIdle from '../menus3d/close_idle.webp';
	import closeHover from '../menus3d/close_hover.webp';

	// vite hashes the image URLs, so the global rules below get them as custom properties
	// on the document root (the menus aren't inside this component, so it must be :root)
	const vars: Record<string, string> = {
		'--m3-frame': frame,
		'--m3-card': card,
		'--m3-btn': btnIdle,
		'--m3-btn-hover': btnHover,
		'--m3-btn-pressed': btnPressed,
		'--m3-plus': plusIdle,
		'--m3-plus-hover': plusHover,
		'--m3-minus': minusIdle,
		'--m3-minus-hover': minusHover,
		'--m3-close': closeIdle,
		'--m3-close-hover': closeHover,
	};

	$effect(() => {
		const root = document.documentElement.style;
		for (const [key, src] of Object.entries(vars)) root.setProperty(key, `url("${src}")`);
		return () => Object.keys(vars).forEach((key) => root.removeProperty(key));
	});
</script>

<style lang="scss">
	:global(:root) {
		--m3-bone: #f2ecde;
		--m3-brass: #e3b858;
		--m3-brass-dark: #8a6a2f;
		--m3-blood: #b3141c;
	}

	/* ---------------------------------------------------------------- the menu itself */
	:global(.pop-up-wrap) {
		color: var(--m3-bone) !important;
	}
	:global(.pop-up-wrap .blur-layer) {
		background-color: rgba(4, 12, 18, 0.62) !important;
	}
	/* (no position here: phone buy-bonus pins its play-amount stepper to the screen
	   bottom absolutely, and a positioned frame would capture it) */
	:global(.pop-up-wrap .ui-popup-standard-content-wrap) {
		max-width: min(var(--maxWidth), calc(100vw - 2.5rem)) !important;
		max-height: calc(100% - 3rem) !important;
		padding: 1.6rem 1.8rem 1.8rem;
		border-style: solid;
		border-width: 31px 38px 35px 34px;
		border-image: var(--m3-frame) 155 190 175 170 fill / 31px 38px 35px 34px / 6px 13px 10px 9px stretch;
		box-sizing: border-box;
	}
	/* Buy bonus: portrait and landscape centre their card rows absolutely, so the content
	   box collapses to nothing - frame the card rows (.bonuses) instead, in every layout.
	   (Never put a filter/transform on the content box: the phone play-amount stepper is
	   position: fixed, and either would trap it inside.) */
	:global(.pop-up-wrap .ui-popup-standard-content-wrap:has(.bonuses)) {
		border: 0 !important;
		border-image: none !important;
		padding: 0 !important;
	}
	:global(.pop-up-wrap .bonuses) {
		padding: 1.4rem 1.6rem;
		border-style: solid;
		border-width: 31px 38px 35px 34px;
		border-image: var(--m3-frame) 155 190 175 170 fill / 31px 38px 35px 34px / 6px 13px 10px 9px stretch;
	}
	/* phones: the card rows already fill the width, so the cards' own plates carry it */
	@media (max-width: 600px) {
		:global(.pop-up-wrap .bonuses) {
			padding: 0;
			border: 0;
			border-image: none;
		}
	}
	:global(.pop-up-wrap .ui-modal-title-wrap),
	:global(.pop-up-wrap .subtitle) {
		font-family: BloodySeafoodDisplay, Georgia, 'Times New Roman', serif;
		font-weight: bold;
		letter-spacing: 0.08em;
		color: var(--m3-brass);
		text-shadow:
			0 0.1rem 0 #000,
			0 0 0.6rem rgba(227, 184, 88, 0.35);
	}
	:global(.pop-up-wrap .ui-modal-title-wrap) {
		font-size: 1.5rem;
	}

	/* close: the round 3D close button from the bar kit */
	:global(.pop-up-wrap .close-button) {
		font-size: 0 !important;
		width: 3.4rem !important;
		height: 3.4rem !important;
		margin: 0.6rem;
		background: var(--m3-close) center / contain no-repeat !important;
		filter: drop-shadow(0 0.25rem 0.4rem rgba(0, 0, 0, 0.5));
	}
	:global(.pop-up-wrap .close-button:hover) {
		background-image: var(--m3-close-hover) !important;
	}
	:global(.pop-up-wrap .close-button:active) {
		transform: translateY(2px) scale(0.97);
	}

	/* ---------------------------------------------------------------- buttons */
	/* Every menu button is a shared Button wrapping a BaseIcon .rectangle (which sizes it)
	   and an absolutely-placed label: the rectangle becomes a brass-rimmed iron pill. */
	:global(.pop-up-wrap button.button .rectangle) {
		background: none !important;
		border-style: solid !important;
		border-color: transparent !important;
		border-width: 19px 33px 23px 29px !important;
		border-image: var(--m3-btn) 72 124 86 110 fill / 19px 33px 23px 29px / 3px 17px 7px 13px stretch !important;
		border-radius: 0 !important;
		box-sizing: border-box;
		min-height: 2.6rem;
		filter: drop-shadow(0 0.2rem 0.25rem rgba(0, 0, 0, 0.55));
	}
	:global(.pop-up-wrap button.button:hover:not(:disabled) .rectangle),
	/* a selected option (autoplay rounds) is the one the shared code draws white-bordered */
	:global(.pop-up-wrap button.button .rectangle[style*='white']) {
		border-image-source: var(--m3-btn-hover) !important;
	}
	:global(.pop-up-wrap button.button:active:not(:disabled) .rectangle) {
		border-image-source: var(--m3-btn-pressed) !important;
	}
	:global(.pop-up-wrap button.button:active:not(:disabled) .base-button-content) {
		transform: translateY(1px);
	}
	:global(.pop-up-wrap button.button .base-button-content) {
		color: var(--m3-bone) !important;
		font-family: BloodySeafoodDisplay, Georgia, 'Times New Roman', serif;
		font-weight: bold;
		letter-spacing: 0.06em;
		text-shadow: 0 0.08rem 0.15rem #000;
	}
	/* the selected option glows gold, clearly apart from the rest. The shared buy-bonus
	   cards draw their ACTIVATE/PLAY buttons with the same white border, so those glow
	   too - as the menu's calls to action, which suits them */
	:global(.pop-up-wrap button.button .rectangle[style*='white']) {
		filter: brightness(1.2) drop-shadow(0 0 0.45rem rgba(255, 200, 90, 0.85)) !important;
	}
	:global(.pop-up-wrap button.button .rectangle[style*='white'] + .base-button-content) {
		color: #ffe08a !important;
	}

	/* the play-amount - / + steppers: the bar's round 3D buttons */
	:global(.pop-up-wrap button[data-test='down-button'] .rectangle),
	:global(.pop-up-wrap button[data-test='up-button'] .rectangle) {
		border: 0 !important;
		border-image: none !important;
		min-height: 0;
		width: 3rem !important;
		height: 3rem !important;
		background: var(--m3-minus) center / contain no-repeat !important;
	}
	:global(.pop-up-wrap button[data-test='up-button'] .rectangle) {
		background-image: var(--m3-plus) !important;
	}
	:global(.pop-up-wrap button[data-test='down-button']:hover .rectangle) {
		background-image: var(--m3-minus-hover) !important;
	}
	:global(.pop-up-wrap button[data-test='up-button']:hover .rectangle) {
		background-image: var(--m3-plus-hover) !important;
	}
	:global(.pop-up-wrap button[data-test='down-button'] .base-button-content),
	:global(.pop-up-wrap button[data-test='up-button'] .base-button-content) {
		font-size: 0 !important;
	}
	:global(.pop-up-wrap button[data-test='down-button'] .base-button-content *),
	:global(.pop-up-wrap button[data-test='up-button'] .base-button-content *) {
		display: none;
	}

	/* ---------------------------------------------------------------- buy bonus */
	:global(.pop-up-wrap .bonus-card-wrap) {
		background: none !important;
		border-style: solid !important;
		border-width: 24px 25px 27px 22px !important;
		border-image: var(--m3-card) 137 142 153 126 fill / 24px 25px 27px 22px / 7px 7px 9px 5px stretch !important;
		border-radius: 0 !important;
		padding: 0.4rem 0.3rem 0.2rem !important;
		filter: drop-shadow(0 0.3rem 0.5rem rgba(0, 0, 0, 0.45));
	}
	:global(.pop-up-wrap .bonus-card-wrap .title) {
		font-family: BloodySeafoodDisplay, Georgia, 'Times New Roman', serif;
		font-weight: bold;
		letter-spacing: 0.05em;
		color: var(--m3-brass);
		text-shadow: 0 0.08rem 0 #000;
	}
	:global(.pop-up-wrap .bonus-card-wrap .description) {
		color: var(--m3-bone);
		opacity: 0.9;
	}
	:global(.pop-up-wrap .bonus-card-wrap .price) {
		font-family: BloodySeafoodDisplay, Georgia, 'Times New Roman', serif;
		font-weight: bold;
		font-size: 1.25rem;
		color: #fff4c8;
		text-shadow: 0 0 0.5rem rgba(227, 184, 88, 0.5);
	}
	:global(.pop-up-wrap .toggle-wrap .amount) {
		font-family: BloodySeafoodDisplay, Georgia, 'Times New Roman', serif;
		font-weight: bold;
		font-size: 1.4rem;
		color: #fff4c8;
		padding: 0 0.6rem;
	}

	/* ---------------------------------------------------------------- settings / autoplay */
	:global(.pop-up-wrap input.range) {
		-webkit-appearance: none;
		appearance: none;
		margin: 0.7rem 0 0.3rem;
		height: 0.6rem;
		border-radius: 0.35rem;
		background: linear-gradient(#1a120c, #3a2a1c);
		box-shadow:
			inset 0 0.12rem 0.25rem #000,
			0 0 0 0.12rem var(--m3-brass-dark);
	}
	:global(.pop-up-wrap input.range::-webkit-slider-thumb) {
		-webkit-appearance: none;
		width: 1.35rem;
		height: 1.35rem;
		border-radius: 50%;
		background: radial-gradient(circle at 35% 30%, #fff1b8, var(--m3-brass) 45%, var(--m3-brass-dark));
		box-shadow: 0 0.15rem 0.3rem rgba(0, 0, 0, 0.6);
		cursor: pointer;
	}
	:global(.pop-up-wrap input.range::-moz-range-thumb) {
		width: 1.35rem;
		height: 1.35rem;
		border: 0;
		border-radius: 50%;
		background: radial-gradient(circle at 35% 30%, #fff1b8, var(--m3-brass) 45%, var(--m3-brass-dark));
		box-shadow: 0 0.15rem 0.3rem rgba(0, 0, 0, 0.6);
	}
	/* settings labels, autoplay's ADVANCED toggle: the menus' serif, not the SDK sans */
	:global(.pop-up-wrap .col > span),
	:global(.pop-up-wrap .toggle),
	:global(.pop-up-wrap .full-width),
	:global(.pop-up-wrap .content-wrap) {
		font-family: BloodySeafoodDisplay, Georgia, 'Times New Roman', serif;
		letter-spacing: 0.04em;
		color: var(--m3-bone);
	}
	:global(.pop-up-wrap .value) {
		font-family: BloodySeafoodDisplay, Georgia, 'Times New Roman', serif;
		color: #fff4c8;
	}
	:global(.pop-up-wrap input.checkbox) {
		accent-color: var(--m3-brass);
	}
</style>

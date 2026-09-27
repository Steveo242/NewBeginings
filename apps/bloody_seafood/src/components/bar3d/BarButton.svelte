<script lang="ts" module>
	export type BarButtonKind =
		| 'dec'
		| 'inc'
		| 'auto'
		| 'turbo'
		| 'menu'
		| 'close'
		| 'rules'
		| 'pay'
		| 'settings'
		| 'sound'
		| 'buy';
</script>

<script lang="ts">
	// The bet bar's controls in the rendered 3D kit. Behaviour is copied line for line from
	// the shared components-ui-pixi buttons (ButtonDecrease, ButtonAutoSpin, ButtonTurbo,
	// ...), which can't be reskinned without editing the shared package: those draw flat
	// rectangles and text captions, not textures.
	import { stateBet, stateBetDerived, stateConfig, stateModal, stateSound, stateUi } from 'state-shared';
	import { Text } from 'pixi-svelte';
	import { UI_BASE_FONT_SIZE, UI_BASE_SIZE } from 'components-ui-pixi/src/constants';
	import { i18nDerived } from 'components-ui-pixi/src/i18n/i18nDerived';
	import ButtonBetAutoSpinsCounter from 'components-ui-pixi/src/components/ButtonBetAutoSpinsCounter.svelte';

	import Button3D from './Button3D.svelte';
	import { DISPLAY_FONT } from '../../game/fonts';
	import { getContext } from '../../game/context';

	const { kind }: { kind: BarButtonKind } = $props();
	const context = getContext();

	const idle = $derived(context.stateXstateDerived.isIdle());
	const click = () => context.eventEmitter.broadcast({ type: 'soundPressGeneral' });
	const smallest = $derived(stateConfig.betAmountOptions[0]);
	const biggest = $derived(stateConfig.betAmountOptions[stateConfig.betAmountOptions.length - 1]);

	type Spec = {
		icon: string;
		onpress: () => void;
		disabled?: boolean;
		active?: boolean;
		size?: number;
		aspect?: number;
	};

	const spec = $derived.by((): Spec => {
		switch (kind) {
			case 'dec':
				return {
					icon: 'minus',
					disabled: !idle || stateBet.betAmount === smallest,
					onpress: () => {
						click();
						const next = [...stateConfig.betAmountOptions]
							.sort((a, b) => b - a)
							.find((option) => option < stateBet.betAmount);
						stateBetDerived.setBetAmount(next || smallest);
					},
				};
			case 'inc':
				return {
					icon: 'plus',
					disabled: !idle || stateBet.betAmount === biggest,
					onpress: () => {
						click();
						const next = [...stateConfig.betAmountOptions]
							.sort((a, b) => a - b)
							.find((option) => option > stateBet.betAmount);
						stateBetDerived.setBetAmount(next || biggest);
					},
				};
			case 'auto':
				return {
					icon: 'auto',
					active: stateBetDerived.hasAutoBetCounter(),
					disabled:
						stateBet.isSpaceHold ||
						(!idle && !stateBetDerived.hasAutoBetCounter()) ||
						!stateBetDerived.isBetCostAvailable(),
					onpress: () => {
						click();
						if (stateBetDerived.hasAutoBetCounter()) stateBet.autoSpinsCounter = 0;
						else stateModal.modal = { name: 'autoSpin' };
					},
				};
			case 'turbo':
				return {
					icon: 'turbo',
					active: stateBet.isTurbo,
					disabled: stateBet.isSpaceHold,
					onpress: () => {
						click();
						stateBetDerived.updateIsTurbo(!stateBet.isTurbo, { persistent: true });
					},
				};
			case 'menu':
				return { icon: 'menu', onpress: () => (click(), (stateUi.menuOpen = true)) };
			case 'close':
				return { icon: 'close', onpress: () => (click(), (stateUi.menuOpen = false)) };
			case 'rules':
				return { icon: 'info', onpress: () => (click(), (stateModal.modal = { name: 'gameRules' })) };
			case 'pay':
				return { icon: 'paytable', onpress: () => (click(), (stateModal.modal = { name: 'payTable' })) };
			case 'settings':
				return { icon: 'settings', onpress: () => (click(), (stateModal.modal = { name: 'settings' })) };
			case 'sound':
				return {
					icon: stateSound.volumeValueMaster === 0 ? 'sound_off' : 'sound_on',
					onpress: () => {
						click();
						stateSound.volumeValueMaster = stateSound.volumeValueMaster === 0 ? 50 : 0;
					},
				};
			case 'buy': {
				const active = stateBetDerived.activeBetMode()?.type === 'activate';
				return {
					icon: 'buy',
					aspect: 1 / 2.8,
					size: UI_BASE_SIZE * 1.9,
					active,
					disabled: !idle,
					onpress: () => {
						click();
						if (active) stateBet.activeBetModeKey = 'BASE';
						else stateModal.modal = { name: 'buyBonus' };
					},
				};
			}
		}
	});

	// ButtonTurbo's own wiring: turbo follows the stop button for the rest of a spin
	if (kind === 'turbo') {
		context.eventEmitter.subscribeOnMount({
			stopButtonClick: () => stateBetDerived.updateIsTurbo(true, { persistent: false }),
			stopButtonEnable: () => stateBetDerived.updateIsTurbo(false, { persistent: false }),
		});
	}
</script>

<Button3D
	icon={spec.icon}
	size={spec.size ?? UI_BASE_SIZE}
	aspect={spec.aspect}
	onpress={spec.onpress}
	disabled={spec.disabled}
	active={spec.active}
>
	{#if kind === 'auto'}
		<ButtonBetAutoSpinsCounter />
	{:else if kind === 'buy'}
		<!-- live, never baked into the art: social=true swaps BUY BONUS -> PLAY BONUS -->
		<Text
			x={UI_BASE_SIZE * 0.26}
			anchor={0.5}
			text={spec.active ? i18nDerived.disable() : i18nDerived.buyBonus()}
			style={{
				align: 'center',
				wordWrap: true,
				wordWrapWidth: UI_BASE_SIZE * 1.0,
				lineHeight: UI_BASE_FONT_SIZE * 0.85,
				fontFamily: DISPLAY_FONT,
				fontWeight: 'bold',
				fontSize: UI_BASE_FONT_SIZE * 0.72,
				fill: 0xf2ecde,
				dropShadow: { color: 0x000000, alpha: 0.6, blur: 2, distance: 2, angle: Math.PI / 2 },
			}}
		/>
	{/if}
</Button3D>

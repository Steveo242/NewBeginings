<script lang="ts">
	import type { ButtonProps } from 'components-pixi';
	import { stateModal } from 'state-shared';
	import UiButton from 'components-ui-pixi/src/components/UiButton.svelte';

	import { getContext } from '../game/context';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const context = getContext();

	// The shared ButtonSettings fixes its plate at UI_BASE_SIZE * 1.3 (195)
	// while UiButton draws every caption at a fixed 40.5 units. "SETTINGS"
	// measures about 236 units and is a single word, so unlike "SOUND ON" or
	// "AUTO SPIN" it cannot wrap - it just spills out of its own button. Same
	// control and same modal, with a plate wide enough for the word.
	const sizes = { width: 270, height: 195 };

	const onpress = () => {
		context.eventEmitter.broadcast({ type: 'soundPressGeneral' });
		stateModal.modal = { name: 'settings' };
	};
</script>

<UiButton {...props} {sizes} {onpress} icon="settings" variant="light" />

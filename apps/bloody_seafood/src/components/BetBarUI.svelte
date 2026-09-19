<script lang="ts">
	import type { Snippet } from 'svelte';

	import { EnableSpaceHold } from 'components-shared';
	import UiFadeContainer from 'components-ui-pixi/src/components/UiFadeContainer.svelte';
	import LabelBalance from 'components-ui-pixi/src/components/LabelBalance.svelte';
	import LabelWin from 'components-ui-pixi/src/components/LabelWin.svelte';
	import LabelBet from 'components-ui-pixi/src/components/LabelBet.svelte';
	import ButtonPayTable from 'components-ui-pixi/src/components/ButtonPayTable.svelte';
	import ButtonGameRules from 'components-ui-pixi/src/components/ButtonGameRules.svelte';
	import ButtonSettings from 'components-ui-pixi/src/components/ButtonSettings.svelte';
	import ButtonBuyBonus from 'components-ui-pixi/src/components/ButtonBuyBonus.svelte';
	import ButtonBet from 'components-ui-pixi/src/components/ButtonBet.svelte';
	import ButtonTurbo from 'components-ui-pixi/src/components/ButtonTurbo.svelte';
	import ButtonAutoSpin from 'components-ui-pixi/src/components/ButtonAutoSpin.svelte';
	import ButtonIncrease from 'components-ui-pixi/src/components/ButtonIncrease.svelte';
	import ButtonDecrease from 'components-ui-pixi/src/components/ButtonDecrease.svelte';
	import ButtonMenu from 'components-ui-pixi/src/components/ButtonMenu.svelte';
	import ButtonMenuClose from 'components-ui-pixi/src/components/ButtonMenuClose.svelte';
	import ButtonSoundSwitch from 'components-ui-pixi/src/components/ButtonSoundSwitch.svelte';

	import BetBar from './BetBar.svelte';

	type Props = {
		gameName: Snippet;
		logo: Snippet;
	};

	const props: Props = $props();
</script>

<!--
	App-local stand-in for components-ui-pixi's <UI>. It reuses every shared
	control (so all bet/spin/autoplay logic and the HTML modals stay exactly
	as they are) but hands them to BetBar, a single bottom strip, instead of
	the shared per-device layouts that put controls in side columns and a
	fold-out drawer. Kept here rather than patched into the shared package
	because that package is shared with every other game in the monorepo.
-->
<EnableSpaceHold />

<UiFadeContainer>
	<BetBar>
		{#snippet gameName()}
			{@render props.gameName()}
		{/snippet}

		{#snippet logo()}
			{@render props.logo()}
		{/snippet}

		{#snippet amountBalance(labelProps)}
			<LabelBalance {...labelProps} />
		{/snippet}

		{#snippet amountWin(labelProps)}
			<LabelWin {...labelProps} />
		{/snippet}

		{#snippet amountBet(labelProps)}
			<LabelBet {...labelProps} />
		{/snippet}

		{#snippet buttonBuyBonus(buttonProps)}
			<ButtonBuyBonus {...buttonProps} />
		{/snippet}

		{#snippet buttonBet(buttonProps)}
			<ButtonBet {...buttonProps} />
		{/snippet}

		{#snippet buttonTurbo(buttonProps)}
			<ButtonTurbo {...buttonProps} />
		{/snippet}

		{#snippet buttonAutoSpin(buttonProps)}
			<ButtonAutoSpin {...buttonProps} />
		{/snippet}

		{#snippet buttonIncrease(buttonProps)}
			<ButtonIncrease {...buttonProps} />
		{/snippet}

		{#snippet buttonDecrease(buttonProps)}
			<ButtonDecrease {...buttonProps} />
		{/snippet}

		{#snippet buttonMenu(buttonProps)}
			<ButtonMenu {...buttonProps} />
		{/snippet}

		{#snippet buttonMenuClose(buttonProps)}
			<ButtonMenuClose {...buttonProps} />
		{/snippet}

		{#snippet buttonPayTable(buttonProps)}
			<ButtonPayTable {...buttonProps} />
		{/snippet}

		{#snippet buttonGameRules(buttonProps)}
			<ButtonGameRules {...buttonProps} />
		{/snippet}

		{#snippet buttonSettings(buttonProps)}
			<ButtonSettings {...buttonProps} />
		{/snippet}

		{#snippet buttonSoundSwitch(buttonProps)}
			<ButtonSoundSwitch {...buttonProps} />
		{/snippet}
	</BetBar>
</UiFadeContainer>

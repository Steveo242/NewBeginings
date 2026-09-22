<script lang="ts">
	import { type Snippet } from 'svelte';
	import { GlobalStyle } from 'components-ui-html';
	import { Authenticate, LoadI18n } from 'components-shared';
	import Game from '../components/Game.svelte';
	import PublisherIntro from '../components/PublisherIntro.svelte';
	import { setContext } from '../game/context';

	import messagesMap from '../i18n/messagesMap';

	type Props = { children: Snippet };

	const props: Props = $props();

	const introUrl = new URL('../../steel_gaming_intro.mp4', import.meta.url).href;

	setContext();
</script>

<GlobalStyle>
	<Authenticate>
		<LoadI18n {messagesMap}>
			<Game />
		</LoadI18n>
	</Authenticate>
</GlobalStyle>

<!-- The Steel Gaming publisher splash. It replaces the shared gif loader
     outright rather than stacking with it: the game already shows its own
     progress bar (LoadingScreen) while assets load, so a second spinner
     would only add dead time in front of the player. -->
<PublisherIntro src={introUrl} />

{@render props.children()}
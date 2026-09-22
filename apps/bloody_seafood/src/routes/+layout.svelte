<script lang="ts">
	import { type Snippet } from 'svelte';
	import { GlobalStyle } from 'components-ui-html';
	import { Authenticate, LoaderBase, LoadI18n } from 'components-shared';
	import Game from '../components/Game.svelte';
	import { setContext } from '../game/context';

	import messagesMap from '../i18n/messagesMap';

	type Props = { children: Snippet };

	const props: Props = $props();

	// The publisher splash. Swap static/loader.gif for the Steel Gaming file.
	const loaderUrl = new URL('../../loader.gif', import.meta.url).href;

	setContext();
</script>

<GlobalStyle>
	<Authenticate>
		<LoadI18n {messagesMap}>
			<Game />
		</LoadI18n>
	</Authenticate>
</GlobalStyle>

<!-- LoaderBase, not LoaderExample: the latter draws a literal "Add Your
     Loader" caption over the splash, which was shipping in the build. -->
<LoaderBase src={loaderUrl} maxWidth={400} backgroundColor="#0b1a26" timeout={2000} />

{@render props.children()}
<script lang="ts">
	// A 9-slice sprite (pixi-svelte has no wrapper): the rendered iron panel and enamel
	// plates keep their riveted corners at any width. Mounted the way pixi-svelte's own
	// sprites are (addToParent destroys it on unmount).
	import * as PIXI from 'pixi.js';
	import { getContextApp, getContextParent } from 'pixi-svelte';

	type Props = {
		key: string;
		x?: number;
		y?: number;
		width: number;
		height: number;
		/** corner size in texture px (left, top, right, bottom) */
		border: number;
		alpha?: number;
	};

	const props: Props = $props();
	const app = getContextApp();
	const parent = getContextParent();
	const texture = $derived((app.stateApp.loadedAssets?.[props.key] as PIXI.Texture) ?? PIXI.Texture.EMPTY);
	const sprite = new PIXI.NineSliceSprite({ texture: PIXI.Texture.EMPTY });

	$effect(() => {
		sprite.texture = texture;
		sprite.leftWidth = sprite.rightWidth = props.border;
		sprite.topHeight = sprite.bottomHeight = props.border;
		sprite.width = props.width;
		sprite.height = props.height;
		// (a NineSliceSprite's width/height resize it, scale stays 1, so this is centred)
		sprite.pivot.set(props.width / 2, props.height / 2);
		sprite.x = props.x ?? 0;
		sprite.y = props.y ?? 0;
		sprite.alpha = props.alpha ?? 1;
	});

	parent.addToParent(sprite);
</script>

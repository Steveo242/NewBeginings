<script lang="ts">
	import { Text } from 'pixi-svelte';
	import { Button, type ButtonProps } from 'components-pixi';

	import UiSprite from './UiSprite.svelte';
	import type { ButtonIcon } from '../types';
	import type { Snippet } from 'svelte';
	import { i18nDerived } from '../i18n/i18nDerived';
	import { UI_BASE_FONT_SIZE } from '../constants';

	const ICON_ASSET_MAP: Partial<Record<ButtonIcon, string>> = {
		increase: 'betUp',
		decrease: 'betDown',
		info: 'btnInfo',
		payTable: 'btnPayTable',
	};

	type Props = Omit<ButtonProps, 'children'> & {
		icon: ButtonIcon;
		sizes: { width: number; height: number };
		active?: boolean;
		children?: Snippet;
		variant?: 'dark' | 'light';
	};

	const {
		icon,
		active,
		bare = false,
		variant = 'dark',
		children: childrenFromParent,
		...buttonProps
	}: Props = $props();

	const assetKey = $derived(ICON_ASSET_MAP[icon]);
</script>

<Button {...buttonProps}>
	{#snippet children({ center, hovered, pressed })}
		{#if !bare}
		<UiSprite
			key={assetKey}
			{...center}
			anchor={0.5}
			width={buttonProps.sizes.width}
			height={buttonProps.sizes.height}
			backgroundColor={assetKey ? undefined : variant === 'dark' ? 0x000000 : 0xffffff}
			{...buttonProps.disabled ? { backgroundColor: 0xaaaaaa } : {}}
			{...active && !assetKey
				? { borderWidth: 10, borderColor: variant === 'dark' ? 0xffffff : 0x000000 }
				: {}}
		/>
		{/if}

		{#if !assetKey}
			<Text
				{...center}
				anchor={0.5}
				text={i18nDerived[icon]()}
				style={{
					align: 'center',
					wordWrap: true,
					wordWrapWidth: 200,
					fontFamily: 'proxima-nova',
					fontWeight: '600',
					fontSize: UI_BASE_FONT_SIZE * 0.9,
					fill: bare ? 0x14375E : variant === 'dark' ? 0xffffff : 0x000000,
				}}
			/>
		{/if}

		{@render childrenFromParent?.()}
	{/snippet}
</Button>

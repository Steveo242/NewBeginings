<script lang="ts">
  import { Container, Text } from "pixi-svelte";
  let { text = "", anchor = 0.5, maxWidth = 0, style = {}, ...rest }: any = $props();
  let w = $state(0);
  const fit = $derived(maxWidth && w > maxWidth ? maxWidth / w : 1);
  const size = $derived((style?.fontSize ?? 100) * 0.9);
</script>

<Container {...rest} scale={fit}>
  <Text
    {anchor}
    text={String(text)}
    onresize={(r: { width: number }) => (w = r.width)}
    style={{
      fontFamily: "Georgia, serif",
      fontSize: size,
      fontWeight: "bold",
      align: "center",
      fill: 0xffd27a,
      stroke: { color: 0x3a0008, width: 8 },
      dropShadow: { color: 0x000000, alpha: 0.6, blur: 4, distance: 4, angle: 1.57 },
    }}
  />
</Container>

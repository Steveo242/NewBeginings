<script lang="ts">
  import { Container, Text } from "pixi-svelte";

  let {
    text = "",
    /**
     * The widest string this label will ever show - normally the final win
     * amount. The fit scale is measured against this instead of the live
     * value, so it stays constant for the whole count-up.
     */
    measureText = "",
    anchor = 0.5,
    maxWidth = 0,
    style = {},
    ...rest
  }: any = $props();

  let w = $state(0);
  // Measured off `measureText`, which doesn't change while the counter
  // runs. Measuring the live text instead made the label pulse: the count
  // rolls digits every frame and the font is proportional, so the measured
  // width - and therefore the scale - jittered up and down continuously.
  const fit = $derived(maxWidth && w > maxWidth ? maxWidth / w : 1);
  const size = $derived((style?.fontSize ?? 100) * 0.9);
  const textStyle = $derived({
    fontFamily: "Georgia, serif",
    fontSize: size,
    fontWeight: "bold",
    align: "center",
    fill: 0xffd27a,
    stroke: { color: 0x3a0008, width: 8 },
    dropShadow: { color: 0x000000, alpha: 0.6, blur: 4, distance: 4, angle: 1.57 },
  });
</script>

<Container {...rest} scale={fit}>
  <Text {anchor} text={String(text)} style={textStyle} />
</Container>

<!-- Invisible sizing probe. Pixi has no way to measure a string without a
     display object, and this has to be measured separately from the label
     above, whose text changes every frame. Only rendered when a maxWidth
     is set - most callers don't fit, and this would be a wasted Text. -->
{#if maxWidth}
  <Container alpha={0}>
    <Text
      anchor={anchor}
      text={String(measureText || text)}
      onresize={(r: { width: number }) => (w = r.width)}
      style={textStyle}
    />
  </Container>
{/if}

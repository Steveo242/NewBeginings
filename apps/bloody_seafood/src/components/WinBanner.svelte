<script lang="ts">
  import type { Snippet } from "svelte";
  import { Container, Graphics, Sprite, Text } from "pixi-svelte";
  import { getContext } from "../game/context";

  type Props = { text?: string | null; alias?: string; children: Snippet };
  const props: Props = $props();
  const context = getContext();

  const TIERS: Record<string, { fill: number; band: number }> = {
    big: { fill: 0xffd27a, band: 0xa30d24 },
    superwin: { fill: 0xffb347, band: 0xb3121f },
    mega: { fill: 0xff7a7a, band: 0x8b0000 },
    epic: { fill: 0xff3b3b, band: 0x5c0011 },
    max: { fill: 0xffffff, band: 0xc8102e },
  };
  const tier = $derived(TIERS[props.alias ?? "big"] ?? TIERS.big);
  const W = $derived(context.stateGameDerived.boardLayout().width * 0.85);

  /** Content aspect of title_plaque_board.png, measured off its alpha bounds. */
  const LOGO_ASPECT = 2.573;
  /** Wider than the plaque so the logo overhangs it on both sides. */
  const LOGO_WIDTH_RATIO = 1.32;
  /**
   * Bottom edge sits just inside the ribbon band's top (-125), so the logo
   * crowns the plaque and its blood drips dangle over the band rather than
   * floating clear of it. The wordmark below is at -75 and stays uncovered.
   */
  const LOGO_BOTTOM = -120;
  const logoWidth = $derived(W * LOGO_WIDTH_RATIO);
  const logoHeight = $derived(logoWidth / LOGO_ASPECT);

  // The whole banner is drawn at its original dimensions and then scaled
  // down as a unit, so the plaque, wordmark and amount keep their
  // proportions. At 1x the plaque measures 755px against a 700px board -
  // wider than the reels it sits over - which is why it read so large.
  const BANNER_SCALE = 0.5;

  let t = $state(0);
  $effect(() => {
    const start = performance.now();
    let raf = 0;
    const loop = (now: number) => {
      t = (now - start) / 1000;
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  });

  const easeOutBack = (x: number) => 1 + 2.70158 * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2);
  const pop = $derived(t < 0.4 ? easeOutBack(t / 0.4) : 1);

  const DRIPS = [[-0.38, 26], [-0.21, 38], [-0.05, 22], [0.12, 34], [0.29, 28], [0.4, 18]];

  const draw = (g: any) => {
    const w = W;
    const h = 290;
    const top = -125;
    const bh = 100;
    const tail = 60;
    const L = -w / 2 - 20;
    const R = w / 2 + 20;
    g.clear();
    g.roundRect(-w / 2, -h / 2, w, h, 24).fill({ color: 0x0b1a26, alpha: 0.9 }).stroke({ width: 6, color: 0xd4a44a });
    g.poly([L, top, L - tail, top, L - tail * 0.55, top + bh / 2, L - tail, top + bh, L, top + bh]).fill({ color: tier.band, alpha: 0.8 });
    g.poly([R, top, R + tail, top, R + tail * 0.55, top + bh / 2, R + tail, top + bh, R, top + bh]).fill({ color: tier.band, alpha: 0.8 });
    g.rect(L, top, R - L, bh).fill({ color: tier.band });
    g.rect(L, top + 6, R - L, 4).fill({ color: 0xd4a44a });
    g.rect(L, top + bh - 10, R - L, 4).fill({ color: 0xd4a44a });
    for (const [fx, len] of DRIPS) {
      const x = fx * w;
      g.roundRect(x - 5, top + bh - 4, 10, len, 5).fill({ color: tier.band });
      g.circle(x, top + bh - 4 + len, 8).fill({ color: tier.band });
    }
  };
</script>

<Container scale={pop * BANNER_SCALE}>
  <Graphics {draw} />
  <Sprite
    key="titlePlaqueBoard"
    anchor={0.5}
    width={logoWidth}
    height={logoHeight}
    y={LOGO_BOTTOM - logoHeight * 0.5}
  />
  <!-- y is the ribbon band's exact centre (band runs -125..-25), and the
       text is anchor-centred, so the wordmark sits dead centre in the band.
       It used to carry a permanent 4% sine pulse; that is gone - the size
       is static once the intro pop settles. -->
  <Container y={-75}>
    <Text
      anchor={0.5}
      text={props.text ?? ""}
      style={{
        fontFamily: "Impact, 'Arial Black', 'Trebuchet MS', sans-serif",
        fontSize: 76,
        fontWeight: "bold",
        letterSpacing: 3,
        fill: tier.fill,
        stroke: { color: 0x1a0004, width: 9 },
        dropShadow: { color: 0x000000, alpha: 0.7, blur: 6, distance: 5, angle: 1.57 },
      }}
    />
  </Container>
  <Container y={60}>
    {@render props.children()}
  </Container>
</Container>

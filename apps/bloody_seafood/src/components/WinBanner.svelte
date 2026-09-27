<script lang="ts">
  import type { Snippet } from "svelte";
  import { Container, Graphics, Sprite, Text } from "pixi-svelte";

  import NineSlice from "./bar3d/NineSlice.svelte";
  import WinBurst from "./WinBurst.svelte";
  import { getContext } from "../game/context";
  import { displayTextStyle } from "../game/fonts";

  // The celebration plaque behind every big win, the free-spins intro and TOTAL HAUL.
  // Built from the same 3D kit as the tank and the bet bar: a riveted iron 9-slice with
  // a brass rim (ui3d panel.png), crowned by a rendered 3D title (winTitles atlas, real
  // extruded lettering: bone -> gold -> blood as the tiers climb) that breaks over the
  // plaque's top edge. It replaces a code-drawn navy box with Impact lettering.
  type Props = { text?: string | null; alias?: string; children: Snippet };
  const props: Props = $props();
  const context = getContext();

  const TITLE_FRAMES: Record<string, string> = {
    "BIG WIN": "wintitle_big.png",
    "SUPER WIN": "wintitle_superwin.png",
    "MEGA WIN": "wintitle_mega.png",
    "EPIC WIN!": "wintitle_epic.png",
    "MAX WIN": "wintitle_max.png",
    "FREE SPINS": "wintitle_freespins.png",
    "SUPER FREE SPINS": "wintitle_superfreespins.png",
    "TOTAL HAUL": "wintitle_totalhaul.png",
  };
  // halo + burst grow with the tier
  // halo is always warm gold (additive red over the teal board just greys out); the
  // rays carry the tier's colour and get stronger as the tiers climb
  const TIER_FX: Record<string, { glow: number; rays: number; rayTint: number; burst: number }> = {
    big: { glow: 0.55, rays: 0.3, rayTint: 0xffe2a8, burst: 0.8 },
    superwin: { glow: 0.65, rays: 0.38, rayTint: 0xffc861, burst: 1 },
    mega: { glow: 0.75, rays: 0.46, rayTint: 0xff7a5a, burst: 1.15 },
    epic: { glow: 0.85, rays: 0.55, rayTint: 0xff4a3a, burst: 1.3 },
    max: { glow: 1, rays: 0.65, rayTint: 0xffd060, burst: 1.5 },
  };
  const RAYS = 14;
  // each ray fades out along its length (fine bands of falling alpha) - flat hard-edged
  // wedges read as clip art. (No blur filter: filtering drops the additive blend.)
  const BANDS = Array.from({ length: 10 }, (_, b) => Math.pow(1 - b / 10, 1.6));
  const drawRays = (g: any) => {
    g.clear();
    const r = W * 1.1;
    const spin = t * 0.22;
    const fade = fx.rays * Math.min(1, t * 2.5);
    for (let i = 0; i < RAYS; i++) {
      const a = spin + (i / RAYS) * Math.PI * 2;
      const half = (Math.PI / RAYS) * 0.42;
      const cA = Math.cos(a - half), sA = Math.sin(a - half) * 0.7;
      const cB = Math.cos(a + half), sB = Math.sin(a + half) * 0.7;
      BANDS.forEach((k, b) => {
        const r0 = (b / BANDS.length) * r, r1 = ((b + 1) / BANDS.length) * r;
        g.poly([cA * r0, sA * r0, cA * r1, sA * r1, cB * r1, sB * r1, cB * r0, sB * r0])
          .fill({ color: fx.rayTint, alpha: fade * k * (i % 2 ? 0.55 : 1) });
      });
    }
  };

  const fx = $derived(TIER_FX[props.alias ?? "big"] ?? TIER_FX.big);
  const titleFrame = $derived(TITLE_FRAMES[props.text ?? ""]);
  const titleTexture = $derived(
    titleFrame ? (context.stateApp.loadedAssets?.[titleFrame] as { width: number; height: number } | undefined) : undefined,
  );

  // sized off the board so it scales with every layout
  const W = $derived(context.stateGameDerived.boardLayout().width * 0.86);
  const H = $derived(W * 0.34);
  // panel.png's corners are 80 texture px; drawn at this scale they stay rivet-sized
  const PANEL_SCALE = 0.55;
  const PANEL_BORDER = 80;

  // the title: as tall as ~62% of the plaque, never wider than the plaque + overhang
  const titleH = $derived(H * 0.62);
  const titleW = $derived(
    titleTexture ? Math.min(W * 1.06, (titleTexture.width / titleTexture.height) * titleH) : 0,
  );
  const titleHFit = $derived(titleTexture ? titleW * (titleTexture.height / titleTexture.width) : 0);

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
  // plaque pops in; the title slams down onto it a beat later, overshooting
  const pop = $derived(t < 0.35 ? easeOutBack(t / 0.35) : 1);
  const slamT = $derived(Math.max(0, Math.min(1, (t - 0.12) / 0.28)));
  const slam = $derived(1 + (1 - easeOutBack(slamT)) * 0.9);
  const titleAlpha = $derived(Math.min(1, slamT * 3));
  // a slow breathe on the halo once it has landed
  const glowPulse = $derived(1 + Math.sin(t * 2.4) * 0.06);
</script>

<Container scale={pop}>
  <!-- light rays + halo behind the plaque -->
  <Graphics draw={drawRays} blendMode="add" />
  <Sprite
    key="fxGlow"
    anchor={0.5}
    width={W * 1.7 * glowPulse}
    height={W * 1.05 * glowPulse}
    tint={0xffc870}
    alpha={fx.glow * Math.min(1, t * 3)}
    blendMode="add"
  />
  {#if t < 1.6}
    <WinBurst radius={W * 0.5} strength={fx.burst} count={Math.round(56 * fx.burst)} />
  {/if}

  <!-- the plaque -->
  <Container scale={PANEL_SCALE}>
    <NineSlice key="panel.png" width={W / PANEL_SCALE} height={H / PANEL_SCALE} border={PANEL_BORDER} />
  </Container>

  <!-- the amount / spin count, centred in the plaque below the title -->
  <Container y={H * 0.1}>
    {@render props.children()}
  </Container>

  <!-- the 3D title, breaking over the top edge -->
  <Container y={-H * 0.5} scale={slam} alpha={titleAlpha}>
    {#if titleTexture}
      <Sprite key={titleFrame} anchor={0.5} width={titleW} height={titleHFit} />
    {:else if props.text}
      <Text anchor={0.5} text={props.text} style={displayTextStyle(H * 0.4)} />
    {/if}
  </Container>
</Container>

/** Whether the tank's front glass is still in one piece. GlassBreak smashes it as the game
 *  opens; BoardFront stops drawing the pane once it's gone. */
export const glass = $state({ intact: true });

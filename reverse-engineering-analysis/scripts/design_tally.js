// Read-only design measurement for DESIGN.md. Paste the function body into
// chrome-devtools `evaluate_script` (function: ...), Claude browser `javascript_tool`, or cua_repl.
// Returns VALUES ONLY (no selectors, ids, class names or markup) — consistent with rule 1.
//
// 1) Page tally — run once per main screen, at a desktop viewport (emulate 1440x900 first):
() => {
  const tally = {};
  const add = (k, v) => {
    if (!v || v === 'none' || v === '0px' || v === 'rgba(0, 0, 0, 0)') return;
    (tally[k] ??= {})[v] = (tally[k][v] || 0) + 1;
  };
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const s = getComputedStyle(el);
    const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (hasText) {
      add('color', s.color);
      add('font', `${s.fontFamily.split(',')[0].trim()}|${s.fontSize}|${s.fontWeight}|${s.lineHeight}|${s.letterSpacing}`);
    }
    add('background', s.backgroundColor);
    if (s.backgroundImage.includes('gradient')) add('gradient', s.backgroundImage);
    add('radius', s.borderRadius);
    add('shadow', s.boxShadow);
    add('padding', s.padding);
    add('gap', s.gap === 'normal' ? '' : s.gap);
    if (s.borderStyle !== 'none' && s.borderWidth !== '0px') add('border', `${s.borderWidth} ${s.borderStyle} ${s.borderColor}`);
    if (s.opacity !== '1') add('opacity', s.opacity);
    if (s.transitionDuration !== '0s') add('transition', `${s.transitionProperty} ${s.transitionDuration} ${s.transitionTimingFunction}`);
  }
  const top = o => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, 15);
  return {
    viewport: `${innerWidth}x${innerHeight}@${devicePixelRatio}x`,
    colorScheme: matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
    ...Object.fromEntries(Object.entries(tally).map(([k, v]) => [k, top(v)])),
  };
}

// 2) One element (chrome-devtools: pass the snapshot uid in `args`, the tool hands you the element).
//    Use for component specs and states: measure default, then hover/focus/press with REAL input,
//    wait ~300 ms for transitions, measure again.
// (el) => {
//   const s = getComputedStyle(el), r = el.getBoundingClientRect();
//   const pick = ['color','backgroundColor','backgroundImage','fontFamily','fontSize','fontWeight','lineHeight',
//                 'letterSpacing','padding','borderRadius','border','boxShadow','outline','outlineOffset','opacity',
//                 'transitionDuration'];
//   return { size: `${Math.round(r.width)}x${Math.round(r.height)}`,
//            ...Object.fromEntries(pick.map(k => [k, s[k]])) };
// }

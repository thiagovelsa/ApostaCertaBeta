# Frontend Design Guidelines

## Aesthetic Directions Quick Reference

### 1. Brutally Minimal
**Characteristics**: Maximum whitespace, single color or duotone, typography-focused, clarity above all
- **Colors**: One dominant color + white, or grayscale
- **Typography**: Large, bold display text; minimal body copy
- **Layout**: Left-aligned, generous whitespace, asymmetrical
- **Animations**: None or extremely subtle (fade, scale)
- **Decorative Details**: None; negative space is the decoration
- **Use when**: SaaS dashboards, technical documentation, luxury brands (Apple-style)

**Example CSS Pattern**:
```css
:root {
  --primary: #000;
  --bg: #fff;
  --text: #000;
}

body {
  font-family: 'Playfair Display', serif;
  font-size: 16px;
  line-height: 1.8;
  max-width: 600px;
  margin: 0 auto;
  padding: 4rem 2rem;
}
```

### 2. Maximalist Chaos (Organized)
**Characteristics**: Layered complexity, visual abundance, intricate details, controlled chaos
- **Colors**: Multiple bold colors, patterns, gradients layered
- **Typography**: Mixed weights, sizes, playful combinations
- **Layout**: Overlapping elements, diagonal flow, grid-breaking
- **Animations**: Multiple simultaneous animations, staggered reveals
- **Decorative Details**: Patterns, textures, SVG illustrations, decorative borders
- **Use when**: Creative portfolios, e-commerce, brand experiences, festivals

**Example CSS Pattern**:
```css
:root {
  --primary: #ff006e;
  --secondary: #00f5ff;
  --tertiary: #ffbe0b;
  --bg: #111;
}

@keyframes stagger {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.element {
  animation: stagger 0.6s ease-out forwards;
}

.element:nth-child(1) { animation-delay: 0.1s; }
.element:nth-child(2) { animation-delay: 0.2s; }
.element:nth-child(3) { animation-delay: 0.3s; }
```

### 3. Retro-Futuristic
**Characteristics**: 80s/90s nostalgia, neon colors, geometric shapes, synth vibes
- **Colors**: Neon pink, cyan, purple, against dark backgrounds
- **Typography**: Bold sans-serif, all-caps, pixelated or smooth retro fonts
- **Layout**: Grid-based, geometric shapes, bold borders, shadows
- **Animations**: Glow effects, scanlines, digital transitions
- **Decorative Details**: Grids, geometric patterns, glowing shadows, borders
- **Use when**: Gaming, tech startups, music apps, experimental art

**Example CSS Pattern**:
```css
:root {
  --neon-pink: #ff006e;
  --neon-cyan: #00f5ff;
  --bg: #0a0e27;
}

.neon-text {
  color: var(--neon-pink);
  text-shadow: 0 0 10px var(--neon-pink), 0 0 20px var(--neon-pink);
  font-family: 'Bebas Neue', sans-serif;
  letter-spacing: 0.1em;
}

.scanlines {
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.15),
    rgba(0, 0, 0, 0.15) 1px,
    transparent 1px,
    transparent 2px
  );
}
```

### 4. Organic/Natural
**Characteristics**: Flowing forms, natural materials, earthy tones, curves over angles
- **Colors**: Warm earth tones, muted greens, natural browns, terracotta
- **Typography**: Serif body font, flowing display font, human-scale sizing
- **Layout**: Curved shapes, organic borders, flowing composition
- **Animations**: Smooth transitions, gentle curves, natural movement
- **Decorative Details**: Leaf patterns, natural textures, watercolor effects
- **Use when**: Wellness apps, sustainable brands, nature-focused sites, health products

**Example CSS Pattern**:
```css
:root {
  --primary: #8b6f47;
  --accent: #c89666;
  --bg: #f5ede1;
}

.organic-shape {
  border-radius: 45% 55% 48% 52% / 48% 45% 55% 52%;
  background: linear-gradient(135deg, #c89666 0%, #8b6f47 100%);
}

.flowing-border {
  border-bottom: 3px solid var(--primary);
  border-radius: 45% 55% 52% 48% / 48% 52% 45% 55%;
}
```

### 5. Luxury/Refined
**Characteristics**: Elegant, sophisticated, high-end materials feel, attention to detail
- **Colors**: Deep jewel tones, gold accents, neutral backgrounds
- **Typography**: Serif display font, refined spacing, elegant body font
- **Layout**: Centered, generous whitespace, grid-based but refined
- **Animations**: Subtle, smooth, elegant transitions
- **Decorative Details**: Gold borders, subtle patterns, refined shadows
- **Use when**: High-end brands, luxury products, exclusive services, upscale experiences

**Example CSS Pattern**:
```css
:root {
  --primary: #1a1a1a;
  --accent: #d4af37;
  --bg: #f9f7f4;
}

.luxury-border {
  border-top: 2px solid var(--accent);
  border-bottom: 2px solid var(--accent);
  padding: 1rem 0;
}

.refined-shadow {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

h1 {
  font-family: 'Playfair Display', serif;
  font-weight: 700;
  letter-spacing: 0.05em;
}
```

### 6. Playful/Toy-like
**Characteristics**: Friendly, rounded forms, vibrant colors, approachable, fun
- **Colors**: Bright, saturated colors, rainbow combinations, cheerful palette
- **Typography**: Rounded sans-serif, playful display font, friendly feel
- **Layout**: Rounded corners, friendly spacing, playful asymmetry
- **Animations**: Bouncy, playful, delightful micro-interactions
- **Decorative Details**: Stickers, rounded shapes, playful illustrations
- **Use when**: Kids apps, playful brands, entertainment, edu-tech, startups

**Example CSS Pattern**:
```css
:root {
  --primary: #ff6b6b;
  --secondary: #4ecdc4;
  --tertiary: #ffd93d;
  --bg: #fffacd;
}

.bouncy {
  animation: bounce 0.6s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

button {
  border-radius: 50px;
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

button:hover {
  transform: scale(1.1);
  box-shadow: 0 5px 15px rgba(255, 107, 107, 0.3);
}
```

### 7. Editorial/Magazine
**Characteristics**: Typography-focused, hierarchical, narrative-driven, classic beauty
- **Colors**: Neutral with strategic accent colors, high contrast
- **Typography**: Beautiful serif + sans-serif pairing, varied hierarchy
- **Layout**: Column-based, asymmetrical but structured, generous margins
- **Animations**: Subtle, scene-based, tied to scroll or reveal
- **Decorative Details**: Drop caps, ornamental dividers, refined imagery
- **Use when**: Blog platforms, magazine sites, news portals, literary works

**Example CSS Pattern**:
```css
:root {
  --text: #2c2c2c;
  --accent: #c41e3a;
  --bg: #ffffff;
}

article {
  max-width: 700px;
  font-family: 'Crimson Text', serif;
  font-size: 1.1rem;
  line-height: 1.8;
  color: var(--text);
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: 3rem;
  line-height: 1.2;
  margin-bottom: 1rem;
}

.drop-cap::first-letter {
  font-size: 3em;
  font-weight: bold;
  color: var(--accent);
  float: left;
  line-height: 0.8;
  margin-right: 0.1em;
}

hr {
  border: none;
  height: 2px;
  background: linear-gradient(to right, transparent, var(--accent), transparent);
  margin: 2rem 0;
}
```

### 8. Brutalist/Raw
**Characteristics**: Exposed structure, raw materials, no-frills, honest design
- **Colors**: Grayscale, concrete greys, black and white
- **Typography**: Monospace or raw sans-serif, untreated feel
- **Layout**: Grid-based, visible structure, no hidden complexity
- **Animations**: Minimal, structural, no superfluous movement
- **Decorative Details**: None; raw materials and structure are the design
- **Use when**: Tech blogs, developer tools, architecture portfolios, artistic statements

**Example CSS Pattern**:
```css
:root {
  --text: #000;
  --border: #ccc;
  --bg: #f5f5f5;
}

* {
  border: 1px solid var(--border);
}

body {
  font-family: 'Courier Prime', monospace;
  background: var(--bg);
  padding: 2rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0;
  border: 2px solid var(--text);
}

.grid-item {
  border: 1px solid var(--border);
  padding: 1rem;
  background: white;
}
```

## Typography Pairing Examples

### Bold + Refined
- **Display**: Playfair Display (serif, elegant)
- **Body**: Lato (sans-serif, friendly)
- **Use for**: Luxury, editorial, upscale

### Retro + Modern
- **Display**: Bebas Neue (futuristic, bold)
- **Body**: IBM Plex Sans (clean, technical)
- **Use for**: Retro-futuristic, tech, modern

### Creative + Legible
- **Display**: Abril Fatface (distinctive, display)
- **Body**: Roboto (readable, clean)
- **Use for**: Creative portfolios, magazines

### Monospace + Display
- **Display**: Space Mono (monospace, unique)
- **Body**: Quicksand (friendly, rounded)
- **Use for**: Developer tools, tech blogs, playful

### Classic + Minimal
- **Display**: IBM Plex Serif (classic, serious)
- **Body**: IBM Plex Sans (matching, modern)
- **Use for**: Minimal design, professional, elegant

## Color Harmony Strategies

### Monochromatic + Neon
**Strategy**: Single hue with vibrant accent
```css
--primary: #1a1a1a;
--secondary: #2d2d2d;
--accent: #00ff88;  /* Neon green */
```

### Complementary Jewel Tones
**Strategy**: Deep, opposite colors
```css
--primary: #1e3a8a;  /* Deep blue */
--secondary: #b45309; /* Deep orange */
--accent: #f5f5f5;
```

### Analogous Warm
**Strategy**: Adjacent warm colors
```css
--primary: #d97706;   /* Orange */
--secondary: #f59e0b; /* Amber */
--tertiary: #dc2626;  /* Red */
--accent: #fffbeb;    /* Cream */
```

### High Contrast
**Strategy**: Black + vibrant color + white
```css
--primary: #000;
--accent: #ff006e;    /* Hot pink */
--bg: #fff;
```

## Animation Techniques

### Staggered Entrance
```css
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.item {
  animation: fadeInUp 0.6s ease-out forwards;
}

.item:nth-child(1) { animation-delay: 0.1s; }
.item:nth-child(2) { animation-delay: 0.2s; }
.item:nth-child(3) { animation-delay: 0.3s; }
```

### Smooth Hover Transform
```css
.button {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}
```

### Scroll-Triggered Reveal
```css
@keyframes slideIn {
  from { opacity: 0; transform: translateX(-30px); }
  to { opacity: 1; transform: translateX(0); }
}

.scroll-reveal {
  animation: slideIn 0.8s ease-out;
}
```

## Common Mistakes to Avoid

1. **Mixed aesthetic directions**: Choose ONE and commit
2. **Generic colors**: Avoid purple + white, grey + blue
3. **Over-animation**: 2-3 moments of delight beat constant motion
4. **Poor typography pairing**: Don't pair two similar fonts
5. **Centered everything**: Use asymmetry intentionally
6. **Weak contrast**: Text must be readable
7. **Ignoring negative space**: Space is an active design element
8. **Trend-chasing**: Design for your specific context, not for trends
9. **Cookie-cutter components**: Customize standard patterns
10. **No visual testing**: Always preview in browser before declaring done

## Accessibility Considerations

- **Color contrast**: Minimum WCAG AA (4.5:1 for text)
- **Typography**: Readable font sizes (16px minimum body)
- **Motion**: Respect `prefers-reduced-motion` media query
- **Interactive elements**: Clear focus states, keyboard navigation
- **Semantic HTML**: Proper heading hierarchy, meaningful alt text
- **Touch targets**: Buttons/links at least 44x44px

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Remember

- **Bold is beautiful**: Strong decisions outperform safe middle grounds
- **Context matters**: Every project is unique; avoid templates
- **Details count**: Refined spacing, line-height, letter-spacing elevate design
- **Movement serves purpose**: Animate for delight, not distraction
- **Typography is personality**: Font choices set the entire tone

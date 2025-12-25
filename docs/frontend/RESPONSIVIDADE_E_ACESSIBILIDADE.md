# Responsividade e Acessibilidade - Sistema de Análise de Estatísticas de Futebol

**Versão:** 1.0
**Data:** 24 de dezembro de 2025
**Padrões:** WCAG 2.1 AA, Mobile-First, PWA

Guia completo para garantir que o sistema funciona em todos os dispositivos (mobile, tablet, desktop) e é acessível para todos os usuários, incluindo aqueles com deficiências.

---

## 1. Design Responsivo (Mobile-First)

### 1.1 Breakpoints do TailwindCSS

```typescript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'sm': '640px',   // Mobile landscape / Small tablets
      'md': '768px',   // Tablets
      'lg': '1024px',  // Laptops / Desktops
      'xl': '1280px',  // Large desktops
      '2xl': '1536px', // Extra large desktops
    },
  },
};
```

**Viewport Sizes:**
- **Mobile:** 375px - 639px (iPhone SE, iPhone 12, etc)
- **Tablet:** 640px - 1023px (iPad, iPad Pro)
- **Desktop:** 1024px+ (Laptops, desktops, large monitors)

### 1.2 Mobile-First Strategy

**Padrão:** Escrever CSS mobile primeiro, depois adicionar media queries para telas maiores

```typescript
// ❌ ERRADO - Desktop first
function MatchCard() {
  return (
    <div className="grid-cols-3">
      {/* Desktop layout by default */}
      {/* then override with sm: md: lg: */}
    </div>
  );
}

// ✅ CERTO - Mobile first
function MatchCard() {
  return (
    <div className="grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      {/* Mobile (1 col) by default */}
      {/* Tablet (2 cols) at 768px and up */}
      {/* Desktop (3 cols) at 1024px and up */}
    </div>
  );
}
```

### 1.3 Layout Adaptações por Breakpoint

#### Mobile (375px - 639px)

```typescript
// src/components/layout/Grid.tsx
export function Grid({ children }: GridProps) {
  return (
    <div className="grid grid-cols-1 gap-4">
      {/* Single column, small gap (4 = 16px) */}
      {children}
    </div>
  );
}

// src/pages/HomePage.tsx
function HomePage() {
  return (
    <Container className="px-4 py-6">
      {/* Smaller padding on mobile */}
      <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">
        {/* Responsive text sizes */}
      </h1>
    </Container>
  );
}

// Drawer menu para navegação (não cabe header completo)
function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="flex items-center justify-between p-4">
      <Logo size="sm" /> {/* Smaller logo */}
      <button
        className="lg:hidden" {/* Hide on desktop */}
        onClick={() => setMenuOpen(!menuOpen)}
      >
        ☰ Menu {/* Hamburger menu */}
      </button>
    </header>
  );
}
```

**Features Específicas Mobile:**
- Single column layouts
- Full-width buttons/inputs
- Hamburger menu para navegação
- Drawer/modal navigation
- Increased touch target sizes (min 44x44px)
- Smaller fonts (text-sm, text-base)

#### Tablet (640px - 1023px)

```typescript
export function Grid({ children }: GridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* 2 columns on tablets */}
      {children}
    </div>
  );
}

function Header() {
  return (
    <header className="flex items-center justify-between p-6">
      <Logo size="md" />
      <nav className="hidden md:flex gap-6">
        {/* Show navigation on tablet+ */}
        <a href="/">Home</a>
        <a href="/stats">Estatísticas</a>
      </nav>
    </header>
  );
}
```

**Features Tablet:**
- 2-column grids
- Horizontal navigation bar visible
- Medium-sized elements
- Balanced spacing

#### Desktop (1024px+)

```typescript
export function Grid({ children }: GridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {/* 3 columns on desktop */}
      {children}
    </div>
  );
}

function StatsPanel() {
  return (
    <div className="grid lg:grid-cols-3 gap-8">
      {/* 3-column layout: mandante | info | visitante */}
      <section>{/* Mandante */}</section>
      <section>{/* Match Info */}</section>
      <section>{/* Visitante */}</section>
    </div>
  );
}
```

**Features Desktop:**
- 3-column grids
- Full navigation bar
- Expanded sidebars
- Larger spacing
- All features visible without scrolling

### 1.4 Responsive Text Sizes

```typescript
// DESIGN_SYSTEM.md definiu:
// text-xs: 0.75rem (12px)
// text-sm: 0.875rem (14px)
// text-base: 1rem (16px)
// text-lg: 1.125rem (18px)
// text-xl: 1.25rem (20px)
// text-2xl: 1.5rem (24px)
// text-3xl: 1.875rem (30px)
// text-4xl: 2.25rem (36px)

// Aplicar responsive:
<h1 className="text-xl md:text-2xl lg:text-3xl">
  {/* 20px mobile, 24px tablet, 30px desktop */}
</h1>

<p className="text-sm md:text-base lg:text-lg">
  {/* 14px mobile, 16px tablet, 18px desktop */}
</p>
```

### 1.5 Responsive Images

```typescript
// src/components/atoms/TeamBadge.tsx
export function TeamBadge({ src, alt, size = 'md' }: TeamBadgeProps) {
  const sizeClasses = {
    'sm': 'w-8 h-8',      // 32px mobile
    'md': 'w-12 h-12',    // 48px tablet
    'lg': 'w-16 h-16',    // 64px desktop
    'xl': 'w-24 h-24',    // 96px large desktop
  };

  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      decoding="async"
      className={cn(
        'rounded-full object-cover',
        sizeClasses[size],
        'sm:w-12 sm:h-12 md:w-16 md:h-16 lg:w-24 lg:h-24' // Responsive
      )}
      srcSet={`${src}?w=32 32w, ${src}?w=64 64w, ${src}?w=96 96w`}
    />
  );
}
```

### 1.6 Container Responsivo

```typescript
// src/components/layout/Container.tsx
export function Container({ children, maxWidth = 'xl' }: ContainerProps) {
  const maxWidthClasses = {
    'sm': 'max-w-sm',    // 640px
    'md': 'max-w-md',    // 768px
    'lg': 'max-w-lg',    // 1024px
    'xl': 'max-w-xl',    // 1280px
    '2xl': 'max-w-2xl',  // 1536px
    'full': 'w-full',    // 100%
  };

  return (
    <div className={cn(
      'mx-auto px-4 md:px-6 lg:px-8', // Responsive padding
      maxWidthClasses[maxWidth]
    )}>
      {children}
    </div>
  );
}
```

---

## 2. Acessibilidade (WCAG 2.1 AA)

### 2.1 Semantic HTML

```typescript
// ✅ CORRETO - Semantic HTML
<header role="banner">
  <nav aria-label="Navegação principal">
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/about">Sobre</a></li>
    </ul>
  </nav>
</header>

<main role="main">
  <article>
    <h1>Título da Página</h1>
    <section>
      <h2>Seção 1</h2>
      <p>Conteúdo...</p>
    </section>
  </article>
</main>

<footer role="contentinfo">
  <p>&copy; 2025 Palpite Mestre</p>
</footer>

// ❌ ERRADO - Divs genéricas
<div className="header">
  <div className="nav">
    <div>Home</div>
    <div>Sobre</div>
  </div>
</div>
```

**Elementos Semânticos Principais:**
- `<header>` - Cabeçalho do site
- `<nav>` - Navegação
- `<main>` - Conteúdo principal
- `<article>` - Artigo/conteúdo independente
- `<section>` - Seção de conteúdo
- `<aside>` - Barra lateral
- `<footer>` - Rodapé

### 2.2 Heading Hierarchy

```typescript
// ✅ CORRETO - Hierarquia lógica
<main>
  <h1>Análise de Partidas</h1>           {/* Apenas 1 h1 por página */}

  <section>
    <h2>Partidas de Hoje</h2>            {/* Seções com h2 */}

    <article>
      <h3>Arsenal vs Chelsea</h3>        {/* Itens com h3 */}
    </article>
  </section>

  <section>
    <h2>Estatísticas</h2>
    <h3>Gols</h3>
    <h3>Escanteios</h3>
  </section>
</main>

// ❌ ERRADO - Headings fora de ordem
<h1>Título</h1>
<h3>Pulou h2!</h3>  {/* Quebra hierarquia */}
<h2>Voltou para h2</h2>
```

### 2.3 ARIA Labels & Attributes

```typescript
// Labels para inputs
<label htmlFor="date-picker">Selecionar Data:</label>
<input
  id="date-picker"
  type="date"
  aria-describedby="date-help"
/>
<span id="date-help" className="text-sm text-gray-400">
  Formato: DD/MM/YYYY
</span>

// aria-label para ícones
<button aria-label="Fechar menu">
  <CloseIcon />
</button>

// aria-live para conteúdo dinâmico
<div role="status" aria-live="polite" aria-atomic="true">
  {isLoading && "Carregando partidas..."}
  {error && `Erro: ${error.message}`}
</div>

// aria-selected para abas/filters
<button
  role="tab"
  aria-selected={filtro === 'geral'}
  onClick={() => setFiltro('geral')}
>
  Geral
</button>

// aria-expanded para expandibles
<button
  aria-expanded={isOpen}
  aria-controls="menu"
  onClick={() => setIsOpen(!isOpen)}
>
  ☰ Menu
</button>

<div id="menu" hidden={!isOpen}>
  {/* Menu items */}
</div>

// aria-labelledby para seções
<section aria-labelledby="stats-title">
  <h2 id="stats-title">Estatísticas Detalhadas</h2>
  {/* Stats content */}
</section>
```

**ARIA Best Practices:**
- Usar labels `<label>` sempre que possível (melhor que aria-label)
- Use `aria-label` apenas para elementos sem texto visível (botões com ícones)
- Use `aria-describedby` para descrições longas
- Use `aria-live` para conteúdo que muda dinamicamente
- Use `aria-hidden="true"` para elementos decorativos

### 2.4 Keyboard Navigation

```typescript
// Botões devem ser focusáveis por padrão
<button className="focus:outline-lime-500 focus:ring-2 focus:ring-offset-2">
  Clique
</button>

// Inputs devem ser focusáveis
<input
  type="text"
  className="focus:outline-none focus:ring-2 focus:ring-lime-500"
/>

// Links devem ser focusáveis
<a href="/about" className="focus:outline-lime-500">
  Sobre
</a>

// Tab order (se necessário forçar ordem)
<button tabIndex={0}>Primeiro</button>
<button tabIndex={1}>Segundo</button>
<button tabIndex={2}>Terceiro</button>

// Evitar tabIndex positivo - muda ordem natural
// Usar tabIndex={-1} para elementos que não devem ser focados

// Handlers de teclado
<button
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Pressione Enter ou Espaço
</button>
```

**Keyboard Shortcuts Padrão:**
- `Tab` - Navega para próximo elemento focusável
- `Shift + Tab` - Navega para elemento anterior
- `Enter` - Ativa botões/links
- `Espaço` - Ativa checkboxes/buttons
- `Esc` - Fecha modals/menus

### 2.5 Contrast Ratios (WCAG AA)

```typescript
// Verificar contraste no DESIGN_SYSTEM.md

// Primária: Lime #84cc16 on Dark #0a0a0a = 8.5:1 ✅ (WCAG AAA)
// Requirements:
// - Normal text: min 4.5:1
// - Large text (18pt+): min 3:1
// - WCAG AAA: min 7:1 (normal), 4.5:1 (large)

// ✅ Bom contraste (dark theme)
<div className="text-lime-500 bg-slate-900">
  {/* 8.5:1 - Excelente */}
</div>

// ✅ Contraste aceitável
<div className="text-white bg-slate-900">
  {/* ~20:1 - Perfeito */}
</div>

// ❌ Contraste inadequado
<div className="text-gray-400 bg-slate-900">
  {/* ~4.2:1 - Abaixo de 4.5:1 */}
</div>

// Usar Lime para textos principais garante excelente contraste
```

**Ferramenta para Verificar:** https://webaim.org/resources/contrastchecker/

### 2.6 Focus Visible Styling

```typescript
// src/index.css
@layer components {
  @apply focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-lime-500;
}

/* Ou manual */
button {
  &:focus {
    outline: none;
    border: 2px solid #84cc16;
    box-shadow: 0 0 0 3px rgba(132, 204, 22, 0.1);
  }

  &:focus-visible {
    outline: 2px solid #84cc16;
  }
}

// Garantir focus ring é visível
<button className="ring-offset-2 focus:ring-2 focus:ring-lime-500">
  {/* ring-offset cria espaço entre elemento e ring */}
</button>
```

### 2.7 Form Accessibility

```typescript
// ✅ CORRETO - Labels sempre associadas
<div className="form-group">
  <label htmlFor="date-input">Data da Partida:</label>
  <input
    id="date-input"
    type="date"
    required
    aria-required="true"
    aria-describedby="date-error"
  />
  <span id="date-error" role="alert" hidden={!error}>
    {error}
  </span>
</div>

// ❌ ERRADO - Label flutuante sem htmlFor
<input type="date" placeholder="Selecione a data" />

// Radio buttons
<fieldset>
  <legend>Filtro de Partidas:</legend>
  <div>
    <input id="geral" type="radio" name="filtro" value="geral" />
    <label htmlFor="geral">Geral</label>
  </div>
  <div>
    <input id="5" type="radio" name="filtro" value="5" />
    <label htmlFor="5">Últimas 5</label>
  </div>
</fieldset>

// Checkboxes
<div>
  <input id="notify" type="checkbox" />
  <label htmlFor="notify">Notificar sobre novas partidas</label>
</div>

// Error messages
<div role="alert" className="text-red-500">
  {error && `Erro: ${error}`}
</div>

// Success messages
<div role="status" aria-live="polite" className="text-green-500">
  {success && "Operação realizada com sucesso!"}
</div>
```

### 2.8 Image Alt Text

```typescript
// ✅ CORRETO - Alt descritivo
<img
  src="/arsenal-logo.svg"
  alt="Logo do Arsenal Football Club"
/>

// ✅ Decorativo (sem contexto importante)
<img
  src="/decorative-line.svg"
  alt=""  {/* alt vazio para imagens puramente decorativas */}
  aria-hidden="true"
/>

// ✅ Com fallback
<img
  src={teamBadge}
  alt={`Escudo do ${teamName}`}
  onError={(e) => {
    (e.target as HTMLImageElement).src = '/default-badge.svg';
  }}
/>

// ❌ ERRADO - Alt genérico ou ausente
<img src="/logo.png" />  {/* Sem alt */}
<img src="/logo.png" alt="imagem" />  {/* Genérico demais */}
```

### 2.9 Skip Links

```typescript
// src/components/layout/Header.tsx
export function Header() {
  return (
    <>
      {/* Skip to main content link (hidden, focusável apenas por teclado) */}
      <a
        href="#main-content"
        className="absolute -top-full left-0 bg-lime-500 text-black px-4 py-2 focus:top-0 z-50"
      >
        Pular para conteúdo principal
      </a>

      <header>
        <nav>{/* Navigation items */}</nav>
      </header>

      <main id="main-content">
        {/* Page content */}
      </main>
    </>
  );
}
```

---

## 3. PWA (Progressive Web App)

### 3.1 manifest.json

```json
{
  "name": "Palpite Mestre - Análise de Estatísticas de Futebol",
  "short_name": "Palpite Mestre",
  "description": "Sistema web para análise detalhada de estatísticas de futebol",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "theme_color": "#84cc16",
  "background_color": "#0a0a0a",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-192x192-maskable.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    }
  ],
  "screenshots": [
    {
      "src": "/screenshots/screenshot1.png",
      "sizes": "540x720",
      "type": "image/png",
      "form_factor": "narrow"
    },
    {
      "src": "/screenshots/screenshot2.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide"
    }
  ],
  "categories": ["sports"],
  "shortcuts": [
    {
      "name": "Análise de Partidas",
      "short_name": "Partidas",
      "description": "Abra a página de análise de partidas",
      "url": "/",
      "icons": [{ "src": "/icons/shortcut-partidas.png", "sizes": "96x96" }]
    }
  ]
}
```

**index.html - Link manifest:**
```html
<link rel="manifest" href="/manifest.json" />
<meta name="theme-color" content="#84cc16" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<meta name="apple-mobile-web-app-title" content="Palpite Mestre" />
```

### 3.2 Service Worker

```typescript
// public/sw.js
const CACHE_NAME = 'palpitremestre-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/manifest.json',
];

// Install - Cache essentials
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('Caching essential assets');
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

// Activate - Clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch - Network first, fall back to cache
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Cache successful responses
        if (response.status === 200) {
          const clonedResponse = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clonedResponse);
          });
        }
        return response;
      })
      .catch(() => {
        // Fall back to cache on network error
        return caches.match(event.request);
      })
  );
});
```

**Registrar Service Worker (src/main.tsx):**
```typescript
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').then(
    (registration) => {
      console.log('Service Worker registered:', registration);
    },
    (error) => {
      console.log('Service Worker registration failed:', error);
    }
  );
}
```

### 3.3 App Install Prompt

```typescript
// src/hooks/useInstallPrompt.ts
import { useState, useEffect } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export function useInstallPrompt() {
  const [prompt, setPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setPrompt(e as BeforeInstallPromptEvent);
    };

    window.addEventListener('beforeinstallprompt', handler);

    // Check if app is already installed
    if ((window.navigator as any).standalone === true) {
      setIsInstalled(true);
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handler);
    };
  }, []);

  const handleInstall = async () => {
    if (!prompt) return;

    prompt.prompt();
    const { outcome } = await prompt.userChoice;

    if (outcome === 'accepted') {
      setIsInstalled(true);
    }
    setPrompt(null);
  };

  return { canInstall: !!prompt && !isInstalled, handleInstall };
}

// Usar em Header
function Header() {
  const { canInstall, handleInstall } = useInstallPrompt();

  return (
    <header>
      {canInstall && (
        <button onClick={handleInstall}>
          📱 Instalar App
        </button>
      )}
    </header>
  );
}
```

---

## 4. Testing Checklist

### 4.1 Lighthouse Audit (Google)

```bash
# Rodar Lighthouse
npm run build
npm run preview  # Servidor local

# Abrir DevTools (F12) → Lighthouse → Generate report
# Verificar scores:
# - Performance: >90
# - Accessibility: >90
# - Best Practices: >90
# - SEO: >90
# - PWA: Instalable
```

**Lighthouse Metrics:**
- **Largest Contentful Paint (LCP):** <2.5s
- **First Input Delay (FID):** <100ms
- **Cumulative Layout Shift (CLS):** <0.1
- **Accessibility:** Sem issues críticas
- **Best Practices:** HTTPS, valid HTML, etc

### 4.2 axe DevTools (Acessibilidade Automatizada)

```bash
# Instalar extensão: https://www.deque.com/axe/devtools/
# 1. Abrir DevTools
# 2. Aba "axe DevTools"
# 3. "Scan ALL of my page"
# 4. Verificar violations:
#    - Deve ter 0 críticas
#    - Deve ter ≤5 warnings
```

**Checar Automaticamente:**
- Color contrast
- ARIA attributes
- Heading hierarchy
- Button/link accessibility
- Form labels
- Image alt text

### 4.3 Keyboard Navigation Testing

**Teste Manual:**
```
1. Desabilitar mouse
2. Usar Tab para navegar
3. Verificar Tab order é lógico
4. Verificar focus outline visível
5. Testar Enter/Espaço em buttons
6. Testar Esc para fechar modals
7. Testar Ctrl+F para buscar
```

**Checklist:**
- [ ] Tab order faz sentido
- [ ] Focus outline sempre visível
- [ ] Botões ativam com Enter/Espaço
- [ ] Links abrem com Enter
- [ ] Esc fecha modals/menus
- [ ] Sem keyboard traps
- [ ] Skip links funcionam

### 4.4 Screen Reader Testing

**Ferramentas:**
- **Windows:** NVDA (gratuito)
- **macOS:** VoiceOver (built-in)
- **iOS:** VoiceOver (built-in)
- **Android:** TalkBack (built-in)

**Teste com NVDA:**
```
1. Baixar NVDA: https://www.nvaccess.org/
2. Instalar e abrir
3. Ativar (Ctrl + Alt + N)
4. Navegar página com Tab, setas
5. Verificar:
   - Headings announceds corretamente
   - Form labels lidos
   - Buttons com aria-label são claros
   - Status updates announceds (aria-live)
   - Images descriptions lidas (alt text)
```

### 4.5 Mobile Responsiveness Testing

**DevTools Mobile Emulation:**
```
DevTools (F12) → Toggle device toolbar (Ctrl+Shift+M)

Testar sizes:
- iPhone SE (375x667)
- iPhone 12 (390x844)
- iPad (768x1024)
- Desktop (1920x1080)

Verificar:
- [ ] Layout adapta bem
- [ ] Texto legível (não precisa zoom)
- [ ] Botões têm 44x44px min (touch targets)
- [ ] Sem scroll horizontal
- [ ] Images responsive (srcSet)
- [ ] Formulários fáceis de usar
```

### 4.6 Browser Compatibility

```bash
# Testar em:
# ✅ Chrome/Edge (Chromium based) - 95%+ users
# ✅ Firefox - 3% users
# ✅ Safari - 2% users
# ✅ Mobile browsers (iOS Safari, Chrome Mobile)

# React 18 suporta:
# - Chrome 51+
# - Firefox 54+
# - Safari 10+
# - Edge 15+
```

### 4.7 Automated Testing

```typescript
// src/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import { Button } from './Button';

describe('Button Accessibility', () => {
  test('button is keyboard accessible', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole('button', { name: /click me/i });

    expect(button).toHaveFocus();
    button.focus();
    expect(button).toHaveFocus();
  });

  test('button has aria-label for icon-only buttons', () => {
    render(
      <Button icon={<CloseIcon />} aria-label="Fechar">
        {/* No visible text */}
      </Button>
    );

    const button = screen.getByRole('button', { name: /fechar/i });
    expect(button).toBeInTheDocument();
  });

  test('has sufficient color contrast', () => {
    const { container } = render(
      <Button>Primary Button</Button>
    );

    const button = container.querySelector('button');
    // Use axe-core for automated contrast checking
    expect(button).toHaveClass('text-lime-500'); // Lime #84cc16
  });
});
```

---

## 5. Performance Checklist

- [ ] Lighthouse Performance score >90
- [ ] LCP (Largest Contentful Paint) <2.5s
- [ ] FID (First Input Delay) <100ms
- [ ] CLS (Cumulative Layout Shift) <0.1
- [ ] CSS file size <50KB (minified, gzipped)
- [ ] JavaScript bundle <100KB (minified, gzipped)
- [ ] Images otimizadas (WebP, srcSet)
- [ ] Fonts carregando via @font-face
- [ ] Service Worker cacheando assets
- [ ] React Query com staleTime correto
- [ ] No memory leaks (DevTools → Memory)
- [ ] No console errors/warnings

---

## 6. Acessibilidade Checklist Final

### WCAG 2.1 Level AA

- [ ] Sem color-only information (always use text/icons too)
- [ ] Contrast ratio ≥4.5:1 for normal text
- [ ] Contrast ratio ≥3:1 for large text (18pt+)
- [ ] All images have descriptive alt text
- [ ] All form inputs have associated labels
- [ ] Headings use proper h1-h6 hierarchy
- [ ] Links have descriptive text (avoid "click here")
- [ ] Buttons and links are focusable (Tab)
- [ ] Focus indicator is visible
- [ ] Keyboard shortcuts are available
- [ ] Content doesn't blink/flash >3x/sec
- [ ] Page is responsive (mobile-friendly)
- [ ] Text is resizable (default zoom 100%)
- [ ] Meaningful page titles (browser tab)
- [ ] Skip navigation links present
- [ ] Error messages are clear
- [ ] Status updates announced (aria-live)

---

## Ver Também

Para aprofundar na responsividade e acessibilidade:

- **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** - Tokens de design, colors com contrast ratios validados
- **[COMPONENTES_REACT.md](COMPONENTES_REACT.md)** - Componentes com ARIA labels em exemplos
- **[ARQUITETURA_FRONTEND.md](ARQUITETURA_FRONTEND.md)** - Estrutura de componentes acessíveis
- **[INTEGRACAO_API.md](INTEGRACAO_API.md)** - Error handling e loading states (acessibilidade)
- **[../LOCAL_SETUP.md](../LOCAL_SETUP.md)** - Setup de ferramentas de acessibilidade

**Referências Externas:**
- **WCAG 2.1 Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/
- **Web Accessibility by Niel de Wet:** https://www.deque.com/
- **A11y Project:** https://www.a11yproject.com/
- **MDN Web Docs - Accessibility:** https://developer.mozilla.org/en-US/docs/Web/Accessibility

**Próximos Passos Recomendados:**
1. Implementar componentes com ARIA labels conforme [COMPONENTES_REACT.md](COMPONENTES_REACT.md)
2. Configurar responsive breakpoints em tailwind.config.js
3. Instalar axe DevTools extensão (Chrome/Firefox)
4. Rodar Lighthouse audit após implementação
5. Testar keyboard navigation sem mouse
6. Testar com screen reader (NVDA ou VoiceOver)
7. Implementar Service Worker para PWA
8. Adicionar manifest.json para instalação

---

**[⬆ Voltar ao topo](#responsividade-e-acessibilidade---sistema-de-análise-de-estatísticas-de-futebol)**

---

**Status do Projeto:**
- ✅ Documentação técnica frontend (✓ 5 docs completas)
- 🔄 Backend (Em desenvolvimento)
- 🔄 Frontend (Pronto para implementação)

**Última atualização:** 24 de dezembro de 2025

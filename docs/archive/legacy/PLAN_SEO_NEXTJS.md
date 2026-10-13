# Plan: SEO Completo para Next.js (pinguinoseguro.cl)

**Objetivo:** Optimizar SEO técnico y on-page del sitio pinguinoseguro.cl para máxima visibilidad en buscadores.

**Stack actual:**
- Next.js 16.1.6
- Deployed en: https://www.pinguinoseguro.cl
- Ruta del proyecto: `~/Desarrollo/pinguinoseguro_web`

**Tiempo estimado:** 3-4 horas

---

## Checklist de SEO

- [ ] Metadata completa (title, description, keywords)
- [ ] Open Graph tags (Facebook, LinkedIn)
- [ ] Twitter Cards
- [ ] sitemap.xml dinámico
- [ ] robots.txt
- [ ] Schema.org structured data
- [ ] Canonical URLs
- [ ] Optimización de imágenes
- [ ] Core Web Vitals
- [ ] Google Analytics / Search Console

---

## Fase 1: Metadata y Tags Básicos

### 1.1 Crear archivo de metadata centralizado

**Archivo: `app/config/metadata.ts`**

```typescript
import { Metadata } from 'next';

export const siteConfig = {
  name: 'Pinguino Seguro',
  description: 'Infraestructura crítica y soberanía de datos para pymes. VPN empresarial, Active Directory, DNS redundante y almacenamiento seguro sin depender de terceros.',
  url: 'https://www.pinguinoseguro.cl',
  ogImage: 'https://www.pinguinoseguro.cl/og-image.jpg',
  keywords: [
    'VPN empresarial Chile',
    'Active Directory pymes',
    'DNS redundante',
    'soberanía de datos',
    'infraestructura crítica',
    'seguridad informática Chile',
    'almacenamiento seguro',
    'backup empresarial',
    'ISO 27001',
    'Curanilahue',
    'Bío Bío'
  ],
  author: 'Pinguino Seguro SpA',
  contact: {
    email: 'contacto@pinguinoseguro.cl',
    phone: '+56 9 XXXX XXXX', // Actualizar con número real
  },
  social: {
    twitter: '@PinguinoSeguro', // Si existe
    linkedin: 'https://linkedin.com/company/pinguinoseguro', // Si existe
  }
};

export const defaultMetadata: Metadata = {
  metadataBase: new URL(siteConfig.url),
  title: {
    default: siteConfig.name,
    template: `%s | ${siteConfig.name}`,
  },
  description: siteConfig.description,
  keywords: siteConfig.keywords,
  authors: [{ name: siteConfig.author }],
  creator: siteConfig.author,
  publisher: siteConfig.author,

  // Open Graph
  openGraph: {
    type: 'website',
    locale: 'es_CL',
    url: siteConfig.url,
    title: siteConfig.name,
    description: siteConfig.description,
    siteName: siteConfig.name,
    images: [
      {
        url: siteConfig.ogImage,
        width: 1200,
        height: 630,
        alt: siteConfig.name,
      },
    ],
  },

  // Twitter
  twitter: {
    card: 'summary_large_image',
    title: siteConfig.name,
    description: siteConfig.description,
    images: [siteConfig.ogImage],
    creator: siteConfig.social.twitter,
  },

  // Icons
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },

  // Manifest
  manifest: '/site.webmanifest',

  // Robots
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },

  // Verification
  verification: {
    google: 'GOOGLE_VERIFICATION_CODE', // Obtener de Google Search Console
    // yandex: 'YANDEX_CODE',
    // bing: 'BING_CODE',
  },
};
```

### 1.2 Aplicar metadata en layout principal

**Archivo: `app/layout.tsx`**

```typescript
import { defaultMetadata } from './config/metadata';
import type { Metadata } from 'next';

export const metadata: Metadata = defaultMetadata;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es-CL">
      <head>
        {/* Google Analytics */}
        <script
          async
          src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'G-XXXXXXXXXX', {
                page_path: window.location.pathname,
              });
            `,
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

### 1.3 Metadata específica por página

**Ejemplo: `app/servicios/page.tsx`**

```typescript
import { Metadata } from 'next';
import { siteConfig } from '../config/metadata';

export const metadata: Metadata = {
  title: 'Servicios de Infraestructura Crítica',
  description: 'VPN empresarial, Active Directory, DNS redundante, almacenamiento seguro y backup automatizado para pymes en Chile.',
  openGraph: {
    title: 'Servicios | Pinguino Seguro',
    description: 'Infraestructura crítica sin depender de terceros',
    url: `${siteConfig.url}/servicios`,
  },
};

export default function ServiciosPage() {
  return <main>...</main>;
}
```

---

## Fase 2: Structured Data (Schema.org)

### 2.1 JSON-LD para organización

**Archivo: `app/components/schema/OrganizationSchema.tsx`**

```typescript
export function OrganizationSchema() {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'Pinguino Seguro SpA',
    legalName: 'Pinguino Seguro SpA',
    url: 'https://www.pinguinoseguro.cl',
    logo: 'https://www.pinguinoseguro.cl/logo.png',
    foundingDate: '2026', // Actualizar con fecha real
    founders: [
      {
        '@type': 'Person',
        name: 'Jaime Novoa',
      },
    ],
    address: {
      '@type': 'PostalAddress',
      streetAddress: 'General Bonilla 205',
      addressLocality: 'Curanilahue',
      addressRegion: 'Bío Bío',
      postalCode: '8320000',
      addressCountry: 'CL',
    },
    contactPoint: {
      '@type': 'ContactPoint',
      telephone: '+56-9-XXXX-XXXX',
      contactType: 'Customer Service',
      areaServed: 'CL',
      availableLanguage: ['Spanish'],
    },
    sameAs: [
      // 'https://www.linkedin.com/company/pinguinoseguro',
      // 'https://twitter.com/pinguinoseguro',
    ],
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}
```

### 2.2 JSON-LD para servicios

**Archivo: `app/components/schema/ServiceSchema.tsx`**

```typescript
export function ServiceSchema() {
  const services = [
    {
      '@type': 'Service',
      serviceType: 'VPN Empresarial',
      provider: {
        '@type': 'Organization',
        name: 'Pinguino Seguro',
      },
      areaServed: 'Chile',
      description: 'Conectividad segura para equipos, sucursales y teletrabajadores sin contratar VPN empresarial cara.',
    },
    {
      '@type': 'Service',
      serviceType: 'Active Directory',
      provider: {
        '@type': 'Organization',
        name: 'Pinguino Seguro',
      },
      areaServed: 'Chile',
      description: 'Una sola contraseña para todos los sistemas de tu empresa. Gestión centralizada de usuarios.',
    },
    {
      '@type': 'Service',
      serviceType: 'DNS Redundante',
      provider: {
        '@type': 'Organization',
        name: 'Pinguino Seguro',
      },
      areaServed: 'Chile',
      description: 'DNS redundante con 99.95% SLO, anti-phishing y DNSSEC para que tu empresa nunca quede sin internet.',
    },
  ];

  const schema = {
    '@context': 'https://schema.org',
    '@graph': services,
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}
```

### 2.3 Agregar schemas al layout

**Actualizar `app/layout.tsx`:**

```typescript
import { OrganizationSchema } from './components/schema/OrganizationSchema';

export default function RootLayout({ children }) {
  return (
    <html lang="es-CL">
      <head>
        <OrganizationSchema />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

---

## Fase 3: Sitemap y Robots

### 3.1 Sitemap dinámico

**Archivo: `app/sitemap.ts`**

```typescript
import { MetadataRoute } from 'next';
import { siteConfig } from './config/metadata';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = siteConfig.url;
  const currentDate = new Date();

  // Páginas estáticas
  const routes = ['', '/servicios', '/contacto', '/portal'].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: currentDate,
    changeFrequency: 'weekly' as const,
    priority: route === '' ? 1.0 : 0.8,
  }));

  // Agregar páginas dinámicas si existen
  // Ejemplo: servicios individuales, blog posts, etc.

  return routes;
}
```

### 3.2 Robots.txt

**Archivo: `app/robots.ts`**

```typescript
import { MetadataRoute } from 'next';
import { siteConfig } from './config/metadata';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/portal/admin/', '/_next/'],
      },
    ],
    sitemap: `${siteConfig.url}/sitemap.xml`,
  };
}
```

---

## Fase 4: Optimización de Imágenes

### 4.1 Crear OG Image

**Crear imagen Open Graph (1200x630px):**

```bash
# Ubicación: public/og-image.jpg
# Debe contener:
# - Logo de Pinguino Seguro
# - Tagline: "Infraestructura crítica para pymes"
# - Fondo: Tema dark/cyan (coherente con el sitio)
```

**Herramientas recomendadas:**
- Figma: https://www.figma.com/
- Canva: https://www.canva.com/
- OG Image Generator: https://og-playground.vercel.app/

### 4.2 Optimizar imágenes existentes

**Script de optimización (si no se usa ya):**

```bash
# Instalar sharp para optimización
npm install sharp

# Crear script: scripts/optimize-images.js
```

**Archivo: `scripts/optimize-images.js`**

```javascript
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const publicDir = path.join(__dirname, '../public');

async function optimizeImages() {
  const files = fs.readdirSync(publicDir);

  for (const file of files) {
    if (/\.(jpg|jpeg|png)$/i.test(file)) {
      const inputPath = path.join(publicDir, file);
      const outputPath = path.join(publicDir, `optimized-${file}`);

      await sharp(inputPath)
        .resize(1920, null, { withoutEnlargement: true }) // Max width
        .webp({ quality: 85 })
        .toFile(outputPath.replace(/\.(jpg|jpeg|png)$/i, '.webp'));

      console.log(`✅ Optimized: ${file}`);
    }
  }
}

optimizeImages();
```

**Agregar a package.json:**

```json
{
  "scripts": {
    "optimize-images": "node scripts/optimize-images.js"
  }
}
```

### 4.3 Usar Next.js Image component

**Reemplazar `<img>` por `<Image>` en todos los componentes:**

```tsx
import Image from 'next/image';

// ❌ Antes
<img src="/logo.png" alt="Logo" width={48} height={48} />

// ✅ Después
<Image
  src="/logo.png"
  alt="Pinguino Seguro - Infraestructura crítica para pymes"
  width={48}
  height={48}
  priority // Si está above the fold
  loading="lazy" // Si está below the fold
/>
```

---

## Fase 5: Core Web Vitals

### 5.1 Lazy loading de componentes pesados

**Ejemplo: `app/page.tsx`**

```typescript
import dynamic from 'next/dynamic';

// Componentes que no son críticos para First Contentful Paint
const ServiceSection = dynamic(() => import('@/components/ui/ServiceSection'), {
  loading: () => <div className="animate-pulse h-96 bg-white/5" />,
});

const Testimonials = dynamic(() => import('@/components/ui/Testimonials'));

export default function HomePage() {
  return (
    <main>
      {/* Hero: carga inmediata */}
      <HeroSection />

      {/* Lazy load: servicios */}
      <ServiceSection />

      {/* Lazy load: testimonios */}
      <Testimonials />
    </main>
  );
}
```

### 5.2 Prefetch estratégico

**Configurar en `next.config.ts`:**

```typescript
const nextConfig: NextConfig = {
  output: 'standalone',

  // Experimental: optimizaciones de performance
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', 'framer-motion'],
  },

  // Compresión
  compress: true,

  // Headers de cache
  async headers() {
    return [
      {
        source: '/:all*(svg|jpg|png|webp|gif)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
};
```

### 5.3 Font optimization

**Usar `next/font` para cargar fuentes:**

```typescript
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export default function RootLayout({ children }) {
  return (
    <html lang="es-CL" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
```

---

## Fase 6: Analytics y Monitoreo

### 6.1 Google Analytics 4

**Crear cuenta en:** https://analytics.google.com

**Obtener ID:** `G-XXXXXXXXXX`

**Componente de Analytics:**

**Archivo: `app/components/analytics/GoogleAnalytics.tsx`**

```typescript
'use client';

import Script from 'next/script';

export function GoogleAnalytics({ gaId }: { gaId: string }) {
  return (
    <>
      <Script
        strategy="afterInteractive"
        src={`https://www.googletagmanager.com/gtag/js?id=${gaId}`}
      />
      <Script
        id="google-analytics"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${gaId}', {
              page_path: window.location.pathname,
            });
          `,
        }}
      />
    </>
  );
}
```

**Usar en layout:**

```typescript
import { GoogleAnalytics } from './components/analytics/GoogleAnalytics';

export default function RootLayout({ children }) {
  return (
    <html>
      <head>
        <GoogleAnalytics gaId="G-XXXXXXXXXX" />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

### 6.2 Google Search Console

**Configurar en:** https://search.google.com/search-console

1. Agregar propiedad: `www.pinguinoseguro.cl`
2. Verificar mediante:
   - **Opción A:** Meta tag (agregar a `metadata.verification.google`)
   - **Opción B:** Archivo HTML en `public/`
   - **Opción C:** DNS TXT record en PowerDNS

3. Enviar sitemap: `https://www.pinguinoseguro.cl/sitemap.xml`

### 6.3 Clarity (Microsoft - heatmaps gratuitos)

**Opcional pero útil para UX:**

```typescript
// app/components/analytics/MicrosoftClarity.tsx
'use client';

import Script from 'next/script';

export function MicrosoftClarity({ projectId }: { projectId: string }) {
  return (
    <Script
      id="microsoft-clarity"
      strategy="afterInteractive"
      dangerouslySetInnerHTML={{
        __html: `
          (function(c,l,a,r,i,t,y){
            c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
            t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
            y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
          })(window, document, "clarity", "script", "${projectId}");
        `,
      }}
    />
  );
}
```

---

## Fase 7: Local SEO (Chile)

### 7.1 Google Business Profile

**Crear perfil en:** https://www.google.com/business/

- Nombre: Pinguino Seguro
- Categoría: Servicios de TI, Consultoría informática
- Dirección: General Bonilla 205, Curanilahue, Bío Bío
- Teléfono: +56 9 XXXX XXXX
- Sitio web: https://www.pinguinoseguro.cl

### 7.2 LocalBusiness Schema

**Archivo: `app/components/schema/LocalBusinessSchema.tsx`**

```typescript
export function LocalBusinessSchema() {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    name: 'Pinguino Seguro',
    image: 'https://www.pinguinoseguro.cl/logo.png',
    '@id': 'https://www.pinguinoseguro.cl',
    url: 'https://www.pinguinoseguro.cl',
    telephone: '+56-9-XXXX-XXXX',
    priceRange: '$$',
    address: {
      '@type': 'PostalAddress',
      streetAddress: 'General Bonilla 205',
      addressLocality: 'Curanilahue',
      addressRegion: 'Bío Bío',
      postalCode: '8320000',
      addressCountry: 'CL',
    },
    geo: {
      '@type': 'GeoCoordinates',
      latitude: -37.4764, // Coordenadas de Curanilahue
      longitude: -73.3453,
    },
    openingHoursSpecification: {
      '@type': 'OpeningHoursSpecification',
      dayOfWeek: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      opens: '09:00',
      closes: '18:00',
    },
    sameAs: [
      // LinkedIn, Twitter, etc
    ],
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}
```

---

## Fase 8: Verificación y Testing

### 8.1 Herramientas de auditoría

**Ejecutar después de deploy:**

```bash
# Lighthouse CI
npm install -g @lhci/cli
lhci autorun --collect.url=https://www.pinguinoseguro.cl

# SEO analyzer
npx unlighthouse --site https://www.pinguinoseguro.cl
```

**Herramientas online:**
- PageSpeed Insights: https://pagespeed.web.dev/
- GTmetrix: https://gtmetrix.com/
- SEO Checker: https://www.seobility.net/en/seocheck/
- Schema Validator: https://validator.schema.org/

### 8.2 Checklist de validación

```bash
# Sitemap accesible
curl https://www.pinguinoseguro.cl/sitemap.xml

# Robots.txt accesible
curl https://www.pinguinoseguro.cl/robots.txt

# OG Image existe
curl -I https://www.pinguinoseguro.cl/og-image.jpg

# Canonical URL correcto
curl -s https://www.pinguinoseguro.cl | grep canonical
```

---

## Fase 9: Content Optimization (On-Page SEO)

### 9.1 Keywords research

**Herramientas gratuitas:**
- Google Keyword Planner: https://ads.google.com/home/tools/keyword-planner/
- Ubersuggest: https://neilpatel.com/ubersuggest/
- Answer The Public: https://answerthepublic.com/

**Keywords objetivo para Chile:**
- "VPN empresarial Chile"
- "Active Directory pymes"
- "servidor DNS redundante"
- "almacenamiento seguro empresas"
- "backup automático Chile"
- "soberanía de datos"
- "infraestructura TI Bío Bío"

### 9.2 Optimizar contenido de página principal

**Estructura recomendada:**

```html
<main>
  <!-- H1: Solo uno por página -->
  <h1>Infraestructura Crítica para Pymes en Chile</h1>

  <!-- H2: Servicios principales -->
  <h2>VPN Empresarial sin Depender de Terceros</h2>
  <p>Conecta equipos, sucursales y teletrabajadores...</p>

  <h2>Active Directory para Gestión Centralizada</h2>
  <p>Una sola contraseña para todos los sistemas...</p>

  <!-- H2: Beneficios -->
  <h2>¿Por Qué Elegir Pinguino Seguro?</h2>

  <!-- H3: Subsecciones -->
  <h3>Soberanía de Datos</h3>
  <h3>SLA Garantizado</h3>
  <h3>Soporte Local</h3>
</main>
```

**Densidad de keywords:** 1-2% del texto total

### 9.3 Internal linking

**Agregar enlaces internos relevantes:**

```tsx
// Desde homepage a servicios
<Link href="/servicios#vpn">Conoce nuestro servicio de VPN empresarial</Link>

// Desde servicios a contacto
<Link href="/contacto">Solicita una cotización personalizada</Link>
```

---

## Fase 10: Deploy y Monitoreo Post-Launch

### 10.1 Pre-deploy checklist

```bash
# Build local
cd ~/Desarrollo/pinguinoseguro_web
npm run build

# Verificar sin errores
npm run start

# Test en localhost:3000
curl http://localhost:3000/sitemap.xml
curl http://localhost:3000/robots.txt
```

### 10.2 Deploy a producción

```bash
# Copiar build a contenedor
cd ~/Desarrollo/pinguinoseguro_web
cp -r .next/standalone/* /ruta/donde/este/el/contenedor/

# Reiniciar contenedor
podman restart pinguinoseguro-web

# Verificar en producción
curl https://www.pinguinoseguro.cl/sitemap.xml
```

### 10.3 Monitoreo continuo

**Configurar alertas en Search Console:**
- Errores de indexación
- Problemas de Core Web Vitals
- Penalizaciones manuales
- Nuevos backlinks

**Métricas a trackear (primeras 4 semanas):**
- Impresiones en Google
- CTR (Click Through Rate)
- Posición promedio para keywords objetivo
- Páginas indexadas
- Errores 404

---

## Checklist Final

- [ ] Metadata completa en todas las páginas
- [ ] Open Graph tags configurados
- [ ] Twitter Cards configurados
- [ ] Schema.org (Organization + LocalBusiness + Services)
- [ ] Sitemap.xml generado y accesible
- [ ] Robots.txt configurado
- [ ] OG Image creado (1200x630px)
- [ ] Imágenes optimizadas (WebP)
- [ ] Next.js Image component usado
- [ ] Lazy loading implementado
- [ ] Fonts optimizadas con next/font
- [ ] Google Analytics instalado
- [ ] Google Search Console verificado
- [ ] Sitemap enviado a Search Console
- [ ] Google Business Profile creado
- [ ] Lighthouse score > 90
- [ ] Core Web Vitals en verde
- [ ] Canonical URLs correctos
- [ ] Internal linking implementado
- [ ] Keywords en H1/H2/H3
- [ ] Alt text en todas las imágenes

---

## Recursos Adicionales

- [Next.js SEO Docs](https://nextjs.org/learn/seo/introduction-to-seo)
- [Google SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [Schema.org Documentation](https://schema.org/)
- [Core Web Vitals](https://web.dev/vitals/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)

---

## KPIs Esperados (30 días post-implementación)

| Métrica | Objetivo |
|---------|----------|
| Lighthouse SEO Score | > 95 |
| Core Web Vitals | Verde en las 3 métricas |
| Páginas indexadas | 100% de páginas públicas |
| Posición "VPN empresarial Chile" | Top 20 |
| Impresiones orgánicas | > 1,000/mes |
| CTR orgánico | > 3% |

---

**Tiempo total estimado:** 3-4 horas
**Costo:** $0 (todas herramientas gratuitas)
**ROI esperado:** +200% en tráfico orgánico en 3 meses

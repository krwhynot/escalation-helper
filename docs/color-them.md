# HungerRush Brand Colors

#hungerrush #branding #design #reference

> A modern, approachable color palette with an extended range of bright tones for illustrations and icons.

---

## Primary Colors

| Color Name | Pantone | HEX | RGB | CMYK |
|------------|---------|-----|-----|------|
| **Teal** | 2244 C | `#0E8476` | 16, 131, 117 | 85, 25, 60, 10 |
| **Navy** | 2766 C | `#1A1346` | 26, 19, 71 | 100, 100, 35, 45 |
| **Cool Gray** | Cool Gray 9 C | `#5F6369` | 95, 99, 105 | 30, 22, 17, 57 |

---

## Secondary Colors

| Color Name | Pantone | HEX | RGB | CMYK |
|------------|---------|-----|-----|------|
| **Blue** | 2111 C | `#35508C` | 53, 79, 140 | 84, 8, 5, 19 |
| **Coral** | 178 C | `#FF585D` | 255, 88, 33 | 0, 75, 57, 0 |
| **Deep Teal** | 2223 C | `#1D8296` | 0, 128, 152 | 91, 11, 38, 40 |

---

## Accent & Illustration Colors

| Color Name | Pantone | HEX | RGB | CMYK |
|------------|---------|-----|-----|------|
| **Green** | 361 C | `#479C45` | 71, 156, 69 | 75, 16, 100, 2 |
| **Orange** | 7579 C | `#ED5C24` | 237, 92, 36 | 0, 79, 98, 0 |
| **Gold** | 715 C | `#ED9E24` | 237, 158, 36 | 5, 45, 98, 0 |
| **Yellow** | 012 C | `#EDD614` | 237, 214, 20 | 9, 99, 0, 0 |

---

## Quick Copy: CSS Variables

```css
:root {
  /* Primary */
  --hr-teal: #0E8476;
  --hr-navy: #1A1346;
  --hr-gray: #5F6369;
  
  /* Secondary */
  --hr-blue: #35508C;
  --hr-coral: #FF585D;
  --hr-deep-teal: #1D8296;
  
  /* Accent */
  --hr-green: #479C45;
  --hr-orange: #ED5C24;
  --hr-gold: #ED9E24;
  --hr-yellow: #EDD614;
}
```

---

## Quick Copy: Tailwind Config

```javascript
colors: {
  hungerrush: {
    teal: '#0E8476',
    navy: '#1A1346',
    gray: '#5F6369',
    blue: '#35508C',
    coral: '#FF585D',
    deepTeal: '#1D8296',
    green: '#479C45',
    orange: '#ED5C24',
    gold: '#ED9E24',
    yellow: '#EDD614',
  }
}
```

---

## Usage Notes

- **Primary Teal** (`#0E8476`): Main brand color, use for primary CTAs and key UI elements
- **Navy** (`#1A1346`): Text, headers, and dark backgrounds
- **Cool Gray** (`#5F6369`): Secondary text and borders
- **Coral** (`#FF585D`): Alerts, notifications, accent highlights
- **Accent colors**: Icons, illustrations, data visualization

---

*Source: HungerRush Brand Guidelines, Page 16*
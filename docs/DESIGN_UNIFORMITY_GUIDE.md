# Design Uniformity Guide - Balilihan Waterworks

This guide establishes the design standards for the Balilihan Waterworks Management System using Tailwind CSS.

---

## 1. Typography Hierarchy

| Element | CSS Class | Size | Usage |
|---------|-----------|------|-------|
| Page Title | `.page-title` | 24px (text-2xl) | Main page headings |
| Section Title | `.section-title` | 18px (text-lg) | Section headers, card titles |
| Body Text | `.text-base` | 16px | Standard paragraph text |
| Small Text | `.text-muted` | 14px (text-sm) | Descriptions, helper text |
| Caption | `.text-caption` | 12px (text-xs) | Labels, footnotes, status text |

### Example Usage
```html
<h1 class="page-title">Consumer Management</h1>
<h2 class="section-title">Water Consumption Rates</h2>
<p class="text-muted">Select a consumer to view their billing history.</p>
<span class="text-caption">Last updated: Nov 24, 2025</span>
```

---

## 2. Color Palette

All colors are defined in `base.html` Tailwind config with full shade ranges (50-900).

| Use Case | Color | Classes |
|----------|-------|---------|
| **Primary** (buttons, links, active states) | Blue | `bg-primary-600`, `text-primary-600` |
| **Success** (paid, active, confirmed) | Green | `bg-success-600`, `text-success-700` |
| **Danger** (disconnected, failed, errors) | Red | `bg-danger-600`, `text-danger-700` |
| **Warning** (pending, overdue) | Amber | `bg-warning-500`, `text-warning-800` |
| **Info** (informational) | Sky Blue | `bg-info-600`, `text-info-700` |
| **Dark** (text, borders) | Gray | `text-dark-700`, `border-dark-200` |
| **Light** (backgrounds) | Neutral | `bg-light-100`, `border-light-300` |

### Background Usage
- **Page background**: `bg-light-100`
- **Card background**: `bg-white`
- **Table header**: `bg-dark-50` (light gray)

---

## 3. Button Components

### Standard Button Classes

| Class | Usage | Example |
|-------|-------|---------|
| `.btn-primary` | Main actions (Save, Submit, Generate) | Blue background |
| `.btn-secondary` | Cancel, Back, secondary actions | Gray background with border |
| `.btn-success` | Confirm, Approve, positive actions | Green background |
| `.btn-danger` | Delete, Disconnect, destructive actions | Red background |

### Size Modifiers
- `.btn-sm` - Small buttons (12px font, less padding)
- `.btn-lg` - Large buttons (16px font, more padding)

### Example Usage
```html
<!-- Primary action -->
<button class="btn-primary">Save Changes</button>

<!-- Secondary action -->
<a href="/back" class="btn-secondary">Cancel</a>

<!-- Success action -->
<button class="btn-success">Confirm Reading</button>

<!-- Danger action -->
<button class="btn-danger btn-sm">Delete</button>

<!-- Large button -->
<a href="/dashboard" class="btn-primary btn-lg">Go to Dashboard</a>
```

### Inline Tailwind Alternative
If you prefer inline Tailwind classes:
```html
<button class="px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition">
    Generate Report
</button>
```

---

## 4. Card Components

### Standard Card Structure
```html
<div class="card">
    <div class="card-header">Card Title</div>
    <div class="card-body">
        <!-- Content here -->
    </div>
</div>
```

### CSS Classes
| Class | Properties |
|-------|------------|
| `.card` | `bg-white`, `border border-light-300`, `rounded-lg`, `shadow-sm` |
| `.card-header` | `py-4 px-6`, `border-b`, `font-semibold`, `text-lg` |
| `.card-body` | `p-6` |

### Inline Tailwind Alternative
```html
<div class="bg-white border border-light-300 rounded-lg shadow-sm">
    <div class="py-4 px-6 border-b border-light-200 font-semibold text-lg text-dark-800">
        Water Consumption Rates
    </div>
    <div class="p-6">
        <!-- Content -->
    </div>
</div>
```

---

## 5. Form Components

### Input Fields
```html
<label class="form-label">Consumer Name</label>
<input type="text" class="form-input" placeholder="Enter name">
```

### CSS Classes
| Class | Properties |
|-------|------------|
| `.form-label` | `text-sm`, `font-medium`, `text-dark-700`, `mb-1.5` |
| `.form-input` | `w-full`, `py-2.5 px-3`, `text-sm`, `border`, `rounded-lg`, `focus:ring` |

### Inline Tailwind Alternative
```html
<label class="block text-sm font-medium text-dark-700 mb-1.5">Consumer Name</label>
<input type="text"
       class="w-full px-3 py-2.5 text-sm border border-light-300 rounded-lg
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
```

---

## 6. Status Badges

### CSS Classes
```html
<span class="badge badge-success">Active</span>
<span class="badge badge-danger">Disconnected</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-info">Processing</span>
```

### Properties
| Class | Background | Text Color |
|-------|------------|------------|
| `.badge-success` | `#dcfce7` (success-100) | `#166534` (success-800) |
| `.badge-danger` | `#fee2e2` (danger-100) | `#991b1b` (danger-800) |
| `.badge-warning` | `#fef3c7` (warning-100) | `#92400e` (warning-800) |
| `.badge-info` | `#e0f2fe` (info-100) | `#075985` (info-800) |

### Inline Tailwind Alternative
```html
<span class="inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full bg-success-100 text-success-800">
    Active
</span>
```

---

## 7. Table Components

### Standard Table Structure
```html
<div class="table-container">
    <table class="w-full">
        <thead class="table-header">
            <tr>
                <th class="table-cell text-left">Column</th>
            </tr>
        </thead>
        <tbody>
            <tr class="table-row">
                <td class="table-cell">Data</td>
            </tr>
        </tbody>
    </table>
</div>
```

### CSS Classes
| Class | Properties |
|-------|------------|
| `.table-container` | `overflow-x-auto`, `border`, `rounded-lg` |
| `.table-header` | `bg-dark-50`, `text-xs`, `font-semibold`, `uppercase` |
| `.table-row` | `border-b`, `hover:bg-dark-50` |
| `.table-cell` | `py-3 px-4`, `text-sm` |

---

## 8. Layout Constants

CSS variables defined in `:root`:

```css
:root {
    --sidebar-width: 220px;
    --header-height: 50px;
}
```

### Main Layout Structure
```html
<!-- Header -->
<div style="height: var(--header-height);">...</div>

<!-- Sidebar -->
<div style="width: var(--sidebar-width); top: var(--header-height);">...</div>

<!-- Main Content -->
<div style="margin-left: var(--sidebar-width); margin-top: var(--header-height);">...</div>
```

---

## 9. Spacing Standards

| Spacing | Value | Usage |
|---------|-------|-------|
| `mb-2` | 8px | Between related elements |
| `mb-4` | 16px | Between form groups |
| `mb-6` | 24px | Between sections/cards |
| `p-4` | 16px | Standard card padding |
| `p-6` | 24px | Large card padding |
| `gap-2` | 8px | Button icon spacing |
| `gap-4` | 16px | Grid item spacing |

---

## 10. Responsive Grid Patterns

### Dashboard Stats
```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- 4 stat cards -->
</div>
```

### Form Fields
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Form fields -->
</div>
```

---

## 11. Do's and Don'ts

### DO
- Use the predefined CSS classes (`.btn-primary`, `.card`, `.badge-success`)
- Use CSS variables for layout dimensions
- Follow the typography hierarchy
- Use consistent spacing (mb-4, mb-6, p-6)

### DON'T
- Mix Bootstrap classes with Tailwind (no `.btn`, `.card-header` from Bootstrap)
- Hardcode pixel values for common dimensions
- Use inconsistent border-radius (`rounded` vs `rounded-lg` vs `rounded-xl`)
- Use inline styles for colors (use Tailwind color classes)

---

## 12. Migration Checklist

When updating existing templates:

1. [ ] Replace `.btn btn-primary` with `.btn-primary`
2. [ ] Replace Bootstrap `.card` structure with standard card classes
3. [ ] Replace `.badge bg-success` with `.badge badge-success`
4. [ ] Update inline `style="width: 220px"` to `style="width: var(--sidebar-width)"`
5. [ ] Ensure tables use `.table-container`, `.table-header`, `.table-row`, `.table-cell`
6. [ ] Use `.page-title` for main headings, `.section-title` for sub-sections

---

## Files Updated

- `base.html` - Added Design Uniformity System CSS classes
- `403.html`, `404.html`, `500.html` - Removed Bootstrap button classes
- `consumer_list_for_staff.html` - Converted from Bootstrap to Tailwind

---

*Last Updated: November 24, 2025*

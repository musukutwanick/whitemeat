# Simple Scroll Animations Documentation

## Overview
Your WhiteMeat project now includes clean, consistent scroll animations using the AOS (Animate on Scroll) library. The animations are simple and consistent across all pages, using only basic effects that won't dismantle existing elements.

## Animation Pattern Used (Like Rabbit Hole Hero)
All templates now follow the same simple animation pattern:

### Hero Sections:
- **Section**: `data-aos="fade-in"` (1000ms)
- **Title**: `data-aos="fade-down"` (800ms, 300ms delay)
- **Subtitle/Description**: `data-aos="fade-up"` (800ms, 500ms delay)
- **Buttons**: `data-aos="zoom-in"` (800ms, 700ms delay)

### Content Sections:
- **Section**: `data-aos="fade-up"` (1000ms)
- **Heading**: `data-aos="fade-down"` (800ms, 200ms delay)
- **Content**: `data-aos="fade-up"` (800ms, 400ms-800ms delay)

## Templates Updated

### 1. **Homepage (index.html)**
- Hero section with title/subtitle animations
- About section with simple fade effects
- Service cards with staggered fade-up
- Mission/Vision boxes with fade-up
- All complex animations removed

### 2. **Pagomo Restaurant (pagomo.html)**
- Hero with fade-in background, fade-down title, fade-up subtitle
- Menu section with fade-up and simple delays
- No complex slide or flip animations

### 3. **Rabbit Hole Restaurant (rabbithole.html)**
- Same pattern as original - fade-in, fade-down, fade-up, zoom-in
- Menu cards with simple fade-up and staggered delays

### 4. **Masterclass (masterclass.html)**
- Hero with fade animations
- Content sections with simple fade-up

### 5. **Cages (cages.html)**
- Hero with consistent fade pattern
- Equipment sections with fade-up

### 6. **Breeding (breeding.html)**
- Hero with fade animations
- Breed cards with simple fade-up

### 7. **Admin Dashboard**
- Welcome section fades down
- Stats and cards fade up with delays

## Animation Types Used (Simple Only)

1. **fade-in** - Element fades into view
2. **fade-up** - Fade with slide up from bottom
3. **fade-down** - Fade with slide down from top
4. **zoom-in** - Scale up while fading in

## Settings
```javascript
AOS.init({
  duration: 800,        // Standard animation duration
  easing: 'ease-out',   // Simple easing
  once: true,           // Animate only once
  offset: 50            // Trigger offset
});
```

## What Was Removed
- Complex flip, slide, rotate animations
- Shimmer text effects
- Parallax effects
- Staggered children animations
- Hover scale transforms that could break layout

## What Was Kept
- Simple hover effects (subtle lift)
- Basic form focus effects
- Clean fade transitions
- Consistent timing and delays

The animations are now clean, consistent, and won't interfere with existing elements or layouts.

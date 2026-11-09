import type { ImageRef } from '../types';

interface PictureProps extends ImageRef {
  alt: string;
  className?: string;
  eager?: boolean;
}

/** First-party image with explicit size (no layout shift) and an optional PNG fallback for WebP. */
export function Picture({ src, fallback, width, height, alt, className, eager = false }: PictureProps) {
  const img = (
    <img
      className={className}
      src={fallback ?? src}
      width={width}
      height={height}
      alt={alt}
      loading={eager ? 'eager' : 'lazy'}
      decoding="async"
    />
  );
  if (!fallback) return img;
  return (
    <picture>
      <source srcSet={src} type="image/webp" />
      {img}
    </picture>
  );
}

import { useRef, useState, type CSSProperties, type PointerEvent, type ReactNode } from 'react';

interface SpatialTiltProps {
  children: ReactNode;
  className?: string;
  max?: number;
  perspective?: number;
}

/**
 * Apple-grade spatial card: follows the pointer with a subtle 3D tilt and a
 * dynamic glass glare. Disables itself on coarse pointer (touch) devices.
 */
export function SpatialTilt({ children, className = '', max = 7, perspective = 1000 }: SpatialTiltProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [style, setStyle] = useState<CSSProperties>({});

  const onMove = (event: PointerEvent<HTMLDivElement>) => {
    if (event.pointerType !== 'mouse') return;
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const px = (event.clientX - rect.left) / rect.width;
    const py = (event.clientY - rect.top) / rect.height;
    const ry = (px - 0.5) * max * 2;
    const rx = (0.5 - py) * max * 2;
    setStyle({
      ['--rx' as string]: `${rx}deg`,
      ['--ry' as string]: `${ry}deg`,
      ['--gx' as string]: `${px * 100}%`,
      ['--gy' as string]: `${py * 100}%`,
      ['--glare-o' as string]: '1',
      transformStyle: 'preserve-3d',
    });
  };

  const onLeave = () => {
    setStyle({ ['--rx' as string]: '0deg', ['--ry' as string]: '0deg', ['--glare-o' as string]: '0' });
  };

  return (
    <div
      ref={ref}
      onPointerMove={onMove}
      onPointerLeave={onLeave}
      style={{ ...style, perspective }}
      className={`spatial-tilt ${className}`}
    >
      {children}
    </div>
  );
}
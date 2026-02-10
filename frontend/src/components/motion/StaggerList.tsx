import type { ReactNode } from 'react';
import { m } from 'framer-motion';

export function StaggerList({
  children,
  className = '',
  itemClassName = '',
}: {
  children: ReactNode[];
  className?: string;
  itemClassName?: string;
}) {
  return (
    <m.div
      className={className}
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: { transition: { staggerChildren: 0.06 } },
      }}
    >
      {children.map((child, idx) => (
        <m.div
          key={idx}
          className={itemClassName}
          variants={{
            hidden: { opacity: 0, y: 8 },
            visible: { opacity: 1, y: 0 },
          }}
          transition={{ duration: 0.22, ease: 'easeOut' }}
        >
          {child}
        </m.div>
      ))}
    </m.div>
  );
}


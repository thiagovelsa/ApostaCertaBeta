import type { ReactNode } from 'react';
import { m, type Variants } from 'framer-motion';

const variants: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0 },
};

export function MotionSection({
  id,
  children,
  className = '',
  delay = 0,
}: {
  id?: string;
  children: ReactNode;
  className?: string;
  delay?: number;
}) {
  return (
    <m.section
      id={id}
      className={className}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.2 }}
      variants={variants}
      transition={{ duration: 0.28, ease: 'easeOut', delay }}
    >
      {children}
    </m.section>
  );
}


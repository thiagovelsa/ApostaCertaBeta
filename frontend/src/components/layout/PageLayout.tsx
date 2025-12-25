import { type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Container } from './Container';
import { Icon } from '@/components/atoms';

interface PageLayoutProps {
  children: ReactNode;
  title?: string;
  showBackButton?: boolean;
  backTo?: string;
}

export function PageLayout({
  children,
  title,
  showBackButton = false,
  backTo = '/',
}: PageLayoutProps) {
  return (
    <div className="min-h-screen bg-dark-primary">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-dark-primary/80 backdrop-blur-lg border-b border-dark-tertiary">
        <Container>
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              {showBackButton && (
                <Link
                  to={backTo}
                  className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-tertiary transition-colors"
                >
                  <Icon name="arrow-left" size="md" />
                </Link>
              )}
              <Link to="/" className="flex items-center gap-2">
                <span className="text-xl font-bold text-white">
                  Palpite<span className="text-primary-400">Mestre</span>
                </span>
              </Link>
            </div>

            {title && (
              <h1 className="text-gray-400 font-medium hidden sm:block">{title}</h1>
            )}

            <div className="flex items-center gap-2">
              <Link
                to="/"
                className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-tertiary transition-colors"
              >
                <Icon name="home" size="md" />
              </Link>
            </div>
          </div>
        </Container>
      </header>

      {/* Main Content */}
      <main className="py-6">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-dark-tertiary py-6 mt-8">
        <Container>
          <div className="text-center text-gray-600 text-sm">
            <p>Palpite Mestre - Sistema de Análise de Estatísticas de Futebol</p>
          </div>
        </Container>
      </footer>
    </div>
  );
}

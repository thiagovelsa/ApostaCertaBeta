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
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus-ring focus:fixed focus:top-3 focus:left-3 focus:z-[60] bg-dark-secondary text-white px-3 py-2 rounded-lg border border-dark-tertiary"
      >
        Pular para conteúdo
      </a>

      {/* Header */}
      <header className="sticky top-0 z-50 bg-dark-primary/80 backdrop-blur-lg border-b border-dark-tertiary">
        <Container>
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              {showBackButton && (
                <Link
                  to={backTo}
                  className="focus-ring p-2.5 rounded-lg text-gray-400 hover:text-white hover:bg-dark-tertiary transition-colors"
                  aria-label="Voltar"
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
                className="focus-ring p-2.5 rounded-lg text-gray-400 hover:text-white hover:bg-dark-tertiary transition-colors"
                aria-label="Início"
              >
                <Icon name="home" size="md" />
              </Link>
            </div>
          </div>
        </Container>
      </header>

      {/* Main Content */}
      <main id="main" className="py-6">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-dark-tertiary py-6 mt-8">
        <Container>
          <div className="text-center text-gray-400 text-sm">
            <p>Palpite Mestre - Sistema de Análise de Estatísticas de Futebol</p>
          </div>
        </Container>
      </footer>
    </div>
  );
}

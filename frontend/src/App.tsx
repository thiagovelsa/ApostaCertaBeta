import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { HomePage } from '@/pages/HomePage';
import { EstatisticasPage } from '@/pages/EstatisticasPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/partida/:matchId" element={<EstatisticasPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

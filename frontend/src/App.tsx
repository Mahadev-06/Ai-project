import { Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import AnalyzePage from './components/analyze/AnalyzePage';
import HistoryPage from './components/history/HistoryPage';
import MethodologyPage from './components/methodology/MethodologyPage';
import ResultsPage from './components/results/ResultsPage';

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<AnalyzePage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/methodology" element={<MethodologyPage />} />
          <Route path="/results/:id" element={<ResultsPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;

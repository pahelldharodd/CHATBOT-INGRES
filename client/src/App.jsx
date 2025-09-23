import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Home from './pages/Home'
import ChatbotPage from './pages/ChatbotPage'
import DashboardPage from './pages/DashboardPage'
import SearchPage from './pages/SearchPage'
import HistoricalDataPage from './pages/HistoricalDataPage'
import HelpPage from './pages/HelpPage'
import Header from './components/common/Header'
import Footer from './components/common/Footer'

function App() {
	return (
		<BrowserRouter>
			<div className="min-h-screen flex flex-col bg-neutral-950 text-slate-100">
				<Header />
				<main className="flex-1">
					<Routes>
						<Route path="/" element={<Home />} />
						<Route path="/chat" element={<ChatbotPage />} />
						<Route path="/dashboard" element={<DashboardPage />} />
						<Route path="/search" element={<SearchPage />} />
						<Route path="/historical" element={<HistoricalDataPage />} />
						<Route path="/help" element={<HelpPage />} />
					</Routes>
				</main>
				<Footer />
			</div>
		</BrowserRouter>
	)
}

export default App

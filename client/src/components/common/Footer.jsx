import { useI18n } from '../../i18n/I18nContext'

export default function Footer() {
	const { t } = useI18n()
	return (
		<footer className="relative mt-16">
			{/* Glass morphism background with gradient border */}
			<div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-teal-500/10 to-blue-500/10 backdrop-blur-xl border-t border-white/20"></div>
			
			<div className="relative mx-auto max-w-7xl px-6 py-12">
				{/* Main Footer Content */}
				<div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
					{/* Brand Section */}
					<div className="col-span-1 md:col-span-2">
						<div className="flex items-center gap-3 mb-4">
							<div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-teal-500 flex items-center justify-center font-bold text-white">
								IG
							</div>
							<div>
								<h3 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-teal-400 bg-clip-text text-transparent">
									IN-GRES
								</h3>
								<p className="text-xs text-slate-400">Groundwater Resource Management</p>
							</div>
						</div>
						<p className="text-slate-300 text-sm leading-relaxed max-w-md">
							Advanced groundwater monitoring and analysis system providing real-time insights, 
							predictions, and comprehensive data management for sustainable water resource planning.
						</p>
						
						{/* Social/Contact Icons */}
						<div className="flex gap-3 mt-6">
							<div className="w-9 h-9 rounded-lg bg-white/5 backdrop-blur-sm border border-white/10 flex items-center justify-center hover:bg-white/10 transition-all cursor-pointer group">
								<svg className="w-4 h-4 text-slate-400 group-hover:text-cyan-400 transition-colors" fill="currentColor" viewBox="0 0 24 24">
									<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
								</svg>
							</div>
							<div className="w-9 h-9 rounded-lg bg-white/5 backdrop-blur-sm border border-white/10 flex items-center justify-center hover:bg-white/10 transition-all cursor-pointer group">
								<svg className="w-4 h-4 text-slate-400 group-hover:text-cyan-400 transition-colors" fill="currentColor" viewBox="0 0 24 24">
									<path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
								</svg>
							</div>
							<div className="w-9 h-9 rounded-lg bg-white/5 backdrop-blur-sm border border-white/10 flex items-center justify-center hover:bg-white/10 transition-all cursor-pointer group">
								<svg className="w-4 h-4 text-slate-400 group-hover:text-cyan-400 transition-colors" fill="currentColor" viewBox="0 0 24 24">
									<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
								</svg>
							</div>
						</div>
					</div>

					{/* Quick Links */}
					<div>
						<h4 className="text-white font-semibold mb-4 text-sm">Quick Links</h4>
						<nav className="space-y-3">
							<a href="/dashboard" className="block text-sm text-slate-400 hover:text-cyan-400 transition-colors">
								Dashboard
							</a>
							<a href="/prediction" className="block text-sm text-slate-400 hover:text-cyan-400 transition-colors">
								ML Predictions
							</a>
							<a href="/historical" className="block text-sm text-slate-400 hover:text-cyan-400 transition-colors">
								Historical Data
							</a>
							<a href="/search" className="block text-sm text-slate-400 hover:text-cyan-400 transition-colors">
								Data Search
							</a>
						</nav>
					</div>

					{/* Support & Legal */}
					<div>
						<h4 className="text-white font-semibold mb-4 text-sm">Support & Legal</h4>
						<nav className="space-y-3">
							<a href="/help" className="block text-sm text-slate-400 hover:text-cyan-400 transition-colors">
								Help Center
							</a>
							<a href="#" className="block text-sm text-slate-400 hover:text-cyan-400 transition-colors">
								{t.footer.privacy || 'Privacy Policy'}
							</a>
							<a href="#" className="block text-sm text-slate-400 hover:text-cyan-400 transition-colors">
								{t.footer.terms || 'Terms of Service'}
							</a>
							<a href="#" className="block text-sm text-slate-400 hover:text-cyan-400 transition-colors">
								{t.footer.contact || 'Contact Us'}
							</a>
						</nav>
					</div>
				</div>

				{/* Bottom Bar */}
				<div className="pt-8 border-t border-white/10">
					<div className="flex flex-col md:flex-row items-center justify-between gap-4">
						<div className="flex items-center gap-4 text-xs text-slate-400">
							<span>© {new Date().getFullYear()} IN-GRES System</span>
							<span className="hidden md:inline">•</span>
							<span className="hidden md:inline">Government of India Initiative</span>
							<span className="hidden md:inline">•</span>
							<span className="hidden md:inline">Version 2.1.0</span>
						</div>
						
						{/* Status Indicator */}
						<div className="flex items-center gap-2 text-xs">
							<div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
							<span className="text-slate-400">System Operational</span>
						</div>
					</div>
				</div>
			</div>
		</footer>
	)
}

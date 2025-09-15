export default function Button({ children, variant = 'primary', ...props }) {
	const base = 'inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors';
	const variants = {
		primary: 'bg-blue-600 text-white hover:bg-blue-500',
		secondary: 'bg-slate-800 text-white hover:bg-slate-700',
		ghost: 'bg-transparent text-slate-100 hover:bg-white/10',
	};
	return (
		<button className={`${base} ${variants[variant]}`} {...props}>
			{children}
		</button>
	)
}

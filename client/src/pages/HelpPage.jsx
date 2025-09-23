import FAQ from '../components/help/FAQ'
import Tutorial from '../components/help/Tutorial'
import ContactSupport from '../components/help/ContactSupport'

export default function HelpPage() {
	return (
		<div className="mx-auto max-w-4xl px-4 py-8 grid gap-8">
			<FAQ />
			<Tutorial />
			<ContactSupport />
		</div>
	)
}

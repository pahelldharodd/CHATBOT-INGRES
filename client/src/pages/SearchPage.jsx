import SearchForm from '../components/search/SearchForm'
import SearchResults from '../components/search/SearchResults'
import Filter from '../components/search/Filter'

export default function SearchPage() {
	return (
		<div className="mx-auto max-w-6xl px-4 py-8 grid gap-6">
			<SearchForm />
			<Filter />
			<SearchResults />
		</div>
	)
}

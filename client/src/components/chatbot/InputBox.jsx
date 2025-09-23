// import { useState } from 'react'
// import Button from '../common/Button'
// import { useI18n } from '../../i18n/I18nContext'

// export default function InputBox({ onSend }) {
// 	const [text, setText] = useState('')
// 	const { t } = useI18n()
// 	function submit(e) {
// 		e.preventDefault()
// 		if (!text.trim()) return
// 		onSend(text)
// 		setText('')
// 	}
// 	return (
// 		<form onSubmit={submit} className="flex items-center gap-2">
// 			<input
// 				type="text"
// 				value={text}
// 				onChange={(e) => setText(e.target.value)}
// 				placeholder={t.chat.placeholder}
// 				className="flex-1 rounded border border-white/10 bg-slate-800 text-slate-100 placeholder:text-slate-400 px-3 py-2"
// 			/>
// 			<Button type="submit">{t.common.send}</Button>
// 		</form>
// 	)
// }

import { createContext, useContext, useMemo, useState, useEffect } from 'react'

const translations = {
	EN: {
		brand: 'IN-GRES',
		common: {
			send: 'Send',
			filters: 'Filters:',
		},
		nav: {
			home: 'Home',
			chatbot: 'Chatbot',
			dashboard: 'Dashboard',
			search: 'Search',
			historical: 'Historical',
			help: 'Help',
		},
		home: {
			welcome: 'Welcome to IN-GRES',
			desc: 'Explore groundwater insights, chat with the assistant, and visualize data across regions.',
			startChat: 'Start Chat',
			exploreData: 'Explore Data',
			searchData: 'Search Data',
		},
		chat: {
			placeholder: 'Type your question...',
			greeting: 'Hi! Ask me about groundwater.',
			quick: [
				'Show groundwater status in Uttar Pradesh',
				'Compare extraction rates of 2020 and 2021',
				'Top 5 over-exploited regions',
			],
		},
		status: {
			safe: 'Safe',
			semiCritical: 'Semi-Critical',
			critical: 'Critical',
			overExploited: 'Over-Exploited',
		},
		dashboard: {
			overview: {
				safeRegions: 'Safe Regions',
				criticalRegions: 'Critical Regions',
				overExploited: 'Over-Exploited',
			},
			summaryTitle: 'Latest Groundwater Summary',
			summaryDesc: 'Summary of recent updates and metrics will appear here.',
		},
		search: {
			region: 'Region',
			year: 'Year',
			status: 'Status',
			searchBtn: 'Search',
			columns: {
				region: 'Region',
				year: 'Year',
				status: 'Status',
				extraction: 'Extraction',
			},
		},
		help: {
			faq: 'FAQ',
			faqItems: ['How to start a chat?', 'How to interpret status colors?', 'How to search by region?'],
			tutorial: 'Tutorial',
			tutorialSteps: ['Use the navbar to navigate.', 'Start a chat to ask questions.', 'Explore dashboard for quick insights.'],
			contact: 'Contact Support',
			emailPlaceholder: 'Your email',
			issuePlaceholder: 'Describe your issue',
			sendBtn: 'Send',
		},
		footer: {
			privacy: 'Privacy',
			contact: 'Contact',
			terms: 'Terms',
		},
		viz: {
			groundwaterStatus: 'Groundwater Status',
			mapPlaceholder: 'GroundwaterMap (Leaflet/Mapbox placeholder)',
			chartPlaceholder: 'GroundwaterChart (Chart.js/Plotly placeholder)',
			timelinePlaceholder: 'TimelineChart (Historical trends placeholder)'
		}
	},
	HI: {
		brand: 'IN-GRES',
		common: {
			send: 'भेजें',
			filters: 'फ़िल्टर:',
		},
		nav: {
			home: 'होम',
			chatbot: 'चैटबॉट',
			dashboard: 'डैशबोर्ड',
			search: 'खोज',
			historical: 'ऐतिहासिक',
			help: 'सहायता',
		},
		home: {
			welcome: 'IN-GRES में आपका स्वागत है',
			desc: 'भूजल जानकारियाँ देखें, सहायक से बात करें और क्षेत्रों में आँकड़ों का दृश्यांकन करें।',
			startChat: 'चैट शुरू करें',
			exploreData: 'डाटा देखें',
			searchData: 'डाटा खोजें',
		},
		chat: {
			placeholder: 'अपना प्रश्न लिखें...',
			greeting: 'नमस्ते! भूजल से संबंधित प्रश्न पूछें।',
			quick: [
				'उत्तर प्रदेश में भूजल स्थिति दिखाएँ',
				'2020 और 2021 की निकासी दर की तुलना करें',
				'शीर्ष 5 अतिदोहन वाले क्षेत्र',
			],
		},
		status: {
			safe: 'सुरक्षित',
			semiCritical: 'अर्ध-गंभीर',
			critical: 'गंभीर',
			overExploited: 'अतिदोहन',
		},
		dashboard: {
			overview: {
				safeRegions: 'सुरक्षित क्षेत्र',
				criticalRegions: 'गंभीर क्षेत्र',
				overExploited: 'अतिदोहन क्षेत्र',
			},
			summaryTitle: 'नवीनतम भूजल सारांश',
			summaryDesc: 'हाल के अपडेट और मेट्रिक्स का सारांश यहाँ दिखाई देगा।',
		},
		search: {
			region: 'क्षेत्र',
			year: 'वर्ष',
			status: 'स्थिति',
			searchBtn: 'खोजें',
			columns: {
				region: 'क्षेत्र',
				year: 'वर्ष',
				status: 'स्थिति',
				extraction: 'निकासी',
			},
		},
		help: {
			faq: 'अक्सर पूछे जाने वाले प्रश्न',
			faqItems: ['चैट कैसे शुरू करें?', 'स्थिति रंगों को कैसे समझें?', 'क्षेत्र के आधार पर खोज कैसे करें?'],
			tutorial: 'मार्गदर्शिका',
			tutorialSteps: ['नेवबार का उपयोग करके नेविगेट करें।', 'प्रश्न पूछने के लिए चैट शुरू करें।', 'त्वरित जानकारियों के लिए डैशबोर्ड देखें।'],
			contact: 'सहायता से संपर्क करें',
			emailPlaceholder: 'आपका ईमेल',
			issuePlaceholder: 'अपनी समस्या का वर्णन करें',
			sendBtn: 'भेजें',
		},
		footer: {
			privacy: 'गोपनीयता',
			contact: 'संपर्क',
			terms: 'नियम',
		},
		viz: {
			groundwaterStatus: 'भूजल स्थिति',
			mapPlaceholder: 'ग्राउंडवॉटर मैप (Leaflet/Mapbox प्लेसहोल्डर)',
			chartPlaceholder: 'ग्राउंडवॉटर चार्ट (Chart.js/Plotly प्लेसहोल्डर)',
			timelinePlaceholder: 'टाइमलाइन चार्ट (ऐतिहासिक रुझान प्लेसहोल्डर)'
		}
	}
}

const I18nContext = createContext({ locale: 'EN', setLocale: () => {}, t: translations.EN })

export function I18nProvider({ children }) {
	const [locale, setLocale] = useState(() => {
		try {
			return localStorage.getItem('locale') || 'EN'
		} catch {
			return 'EN'
		}
	})
	useEffect(() => {
		try {
			localStorage.setItem('locale', locale)
		} catch {}
	}, [locale])
	const value = useMemo(() => ({ locale, setLocale, t: translations[locale] }), [locale])
	return (
		<I18nContext.Provider value={value}>
			{children}
		</I18nContext.Provider>
	)
}

export function useI18n() {
	return useContext(I18nContext)
}

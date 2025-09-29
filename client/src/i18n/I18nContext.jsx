import { createContext, useContext, useMemo, useState, useEffect } from 'react'

const translations = {
	EN: {
		brand: 'JalSaathi',
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
			welcome: 'Welcome to JalSaathi',
			tagline: 'Where there is water, there is life',
			taglineHindi: 'जल है तो जीवन है',
			desc: 'Explore groundwater insights, chat with the assistant, and visualize data across regions.',
			heroDesc: 'Experience groundwater intelligence through our dual AI chatbot system',
			chatbotTitle: 'Choose Your AI Assistant',
			databaseBot: 'Database Query Assistant',
			databaseBotDesc: 'Query the INGRES database with natural language. Get instant insights from structured groundwater data across India.',
			realTimeQueries: 'Real-time data queries',
			structuredData: 'Structured data analysis',
			instantResults: 'Instant results',
			documentBot: 'Document Analysis Assistant',
			documentBotDesc: 'Understand complex information from CGWB reports and assessments. Decode technical terms and get insights from research reports.',
			documentAnalysis: 'Document analysis',
			researchInsights: 'Research insights',
			technicalExplanation: 'Technical explanation',
			startChat: 'Start Chat',
			exploreData: 'Explore Data',
			searchData: 'Search Data',
			chooseMode: 'Choose Your Mode',
			chooseModeDesc: 'Select between Database Queries for data analysis or Knowledge Assistant for CGWB reports and technical explanations.',
			askNaturally: 'Ask Naturally',
			askNaturallyDesc: 'Type your questions in plain Hindi or English. Our AI understands context.',
			getResults: 'Get Results',
			getResultsDesc: 'Receive instant detailed answers, charts, and data insights.',
			chooseMode: 'Choose Your Mode',
			chooseModeDesc: 'Select between Database Queries for data analysis or Knowledge Assistant for CGWB reports and technical explanations.',
			askNaturally: 'Ask Naturally',
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
			saline: 'Saline',
		},
			dashboard: {
				overview: {
					safeRegions: 'Safe Regions',
					criticalRegions: 'Critical Regions',
					overExploited: 'Over-Exploited',
				},
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
		},
		dashboard: {
			title: 'Groundwater Dashboard',
			extractionCategories: 'Groundwater Extraction Categories',
			total: 'Total',
			areas: 'areas'
		},
		historical: {
			title: 'Historical Data Assistant',
			subtitle: 'Ask questions about historical groundwater documents and get AI-powered insights',
			greeting: 'Ask me anything about historical groundwater data, assessments, or documents.',
			tryAsking: '💡 Try asking:',
			quickQuestions: [
				'What are the key findings in the historical assessments?',
				'How has groundwater quality changed over the years?',
				'What are the major challenges identified in past reports?'
			]
		}
	},
	HI: {
		brand: 'JalSaathi',
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
			welcome: 'JalSaathi में आपका स्वागत है',
			tagline: 'जल है तो जीवन है',
			taglineEnglish: 'Where there is water, there is life',
			desc: 'भूजल जानकारियाँ देखें, सहायक से बात करें और क्षेत्रों में आँकड़ों का दृश्यांकन करें।',
			heroDesc: 'हमारे द्विआधारी AI चैटबॉट सिस्टम के माध्यम से भूजल बुद्धिमत्ता का अनुभव करें',
			chatbotTitle: 'अपना AI सहायक चुनें',
			databaseBot: 'डेटाबेस क्वेरी सहायक',
			databaseBotDesc: 'प्राकृतिक भाषा के साथ INGRES डेटाबेस से पूछताछ करें। भारत भर के संरचित भूजल डेटा से तुरंत जानकारी प्राप्त करें।',
			realTimeQueries: 'रीयल-टाइम डेटा क्वेरी',
			structuredData: 'संरचित डेटा विश्लेषण',
			instantResults: 'तत्काल परिणाम',
			documentBot: 'दस्तावेज़ विश्लेषण सहायक',
			documentBotDesc: 'CGWB रिपोर्ट और आकलन से जटिल जानकारी को समझें। तकनीकी शब्दों को सुलझाएं और अनुसंधान रिपोर्ट से जानकारी प्राप्त करें।',
			documentAnalysis: 'दस्तावेज़ विश्लेषण',
			researchInsights: 'अनुसंधान जानकारी',
			technicalExplanation: 'तकनीकी व्याख्या',
			startChat: 'AI चैट अनुभव शुरू करें',
			exploreData: 'डेटा एक्सप्लोर करें',
			searchData: 'डेटा खोजें',
			databaseTitle: 'डेटाबेस क्वेरी सहायक',
			databaseDesc: 'प्राकृतिक भाषा के साथ INGRES डेटाबेस से पूछताछ करें। भारत भर के संरचित भूजल डेटा से तुरंत जानकारी प्राप्त करें।',
			documentTitle: 'CGWB ज्ञान सहायक',
			documentDesc: 'RAG तकनीक का उपयोग करके CGWB आंकलन का अन्वेषण करें। तकनीकी शब्दों को समझें और अनुसन्धान रिपोर्ट से अंतर्दृष्टि प्राप्त करें।',
			chooseMode: 'अपना मोड चुनें',
			chooseModeDesc: 'डेटा विश्लेषण के लिए डेटाबेस क्वेरी या CGWB रिपोर्ट और तकनीकी व्याख्या के लिए ज्ञान सहायक के बीच चुनें।',
			askNaturally: 'प्राकृतिक रूप से पूछें',
			askNaturallyDesc: 'सामान्य हिंदी या अंग्रेजी में अपने प्रश्न लिखें। हमारा AI संदर्भ समझता है।',
			getResults: 'परिणाम प्राप्त करें',
			getResultsDesc: 'तुरंत विस्तृत उत्तर, चार्ट और डेटा अंतर्दृष्टि प्राप्त करें।',
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
			saline: 'खारा',
		},
			dashboard: {
				title: 'भूजल डैशबोर्ड',
				extractionCategories: 'भूजल निष्कर्षण श्रेणियां',
				total: 'कुल',
				areas: 'क्षेत्र',
				overview: {
					safeRegions: 'सुरक्षित क्षेत्र',
					criticalRegions: 'गंभीर क्षेत्र',
					overExploited: 'अतिदोहन क्षेत्र',
				},
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
		},
		historical: {
			title: 'ऐतिहासिक डेटा सहायक',
			subtitle: 'ऐतिहासिक भूजल दस्तावेजों के बारे में प्रश्न पूछें और AI-संचालित अंतर्दृष्टि प्राप्त करें',
			greeting: 'ऐतिहासिक भूजल डेटा, आकलन या दस्तावेजों के बारे में मुझसे कुछ भी पूछें।',
			tryAsking: '💡 इन्हें पूछकर देखें:',
			quickQuestions: [
				'ऐतिहासिक आकलन में मुख्य निष्कर्ष क्या हैं?',
				'वर्षों के दौरान भूजल की गुणवत्ता कैसे बदली है?',
				'पिछली रिपोर्टों में पहचानी गई मुख्य चुनौतियां क्या हैं?'
			]
		}
	}
}

const I18nContext = createContext({ locale: 'HI', setLocale: () => {}, t: translations.HI })

export function I18nProvider({ children }) {
	const [locale, setLocale] = useState(() => {
		try {
			return localStorage.getItem('locale') || 'HI'
		} catch {
			return 'HI'
		}
	})
	useEffect(() => {
		try {
			localStorage.setItem('locale', locale)
		} catch { /* ignore localStorage errors */ }
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
 
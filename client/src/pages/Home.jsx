import { useI18n } from "../i18n/I18nContext";

export default function Home() {
  const { t, locale } = useI18n();
  return (
    <div className="min-h-screen bg-[#030714] overflow-hidden relative pt-24 font-inter">
      {/* Animated background gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_0%_0%,_#1a365d_0%,_transparent_50%)] animate-pulse"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_100%_100%,_#0d9488_0%,_transparent_50%)] animate-pulse [animation-delay:1s]"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,_#1e40af_0%,_transparent_50%)] animate-pulse [animation-delay:2s]"></div>

      {/* Particle effect overlay */}
      <div className="absolute inset-0 bg-[url('/noise.png')] opacity-[0.02] mix-blend-overlay"></div>

      {/* Hero Section */}
      <section className="relative mx-auto max-w-6xl px-4 py-2">
        <div className="text-center">
          {/* Clean logo without blur */}
          <div className="relative mb-4"> 
            <img
              src="/logo1.png"
              alt={t.brand}
              className="relative h-20 w-20 md:h-28 md:w-28 mx-auto"
            />
          </div>

          {/* Clean title */}
          <h1 className="text-4xl md:text-5xl font-bold mb-2 text-white">
            {t.home.welcome}
          </h1>

          {/* Tagline */}
          <p className="text-lg text-teal-300 mb-6 italic font-medium">
            {locale === 'HI' ? 'जल ही जीवन है' : 'Jal Hai Toh Jeevan Hai'}
          </p>

          {/* Dual Chatbot Cards */}
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-16">
            {/* Data Analysis Card */}
            <a href="/chat" className="group block">
              <div className="relative bg-slate-800/50 backdrop-blur-sm p-8 rounded-2xl hover:border-teal-400/50 transition-all duration-300 h-full min-h-[280px] hover-trace">
                <div className="flex flex-col h-full">
                  <div className="flex items-center mb-6">
                    <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-500 p-3 mr-4 shadow-lg">
                      <svg
                        className="w-full h-full text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                        />
                      </svg>
                    </div>
                    <h3 className="text-2xl font-semibold text-white">
                      Data Analysis
                    </h3>
                  </div>
                  
                  <p className="text-slate-300 mb-8 leading-relaxed flex-grow">
                    {t.home.databaseDesc}
                  </p>
                  
                  <div className="space-y-3 mb-8">
                    <div className="text-slate-300 text-left">
                      Real-time data queries
                    </div>
                    <div className="text-slate-300 text-left">
                      Multi-year comparisons
                    </div>
                    <div className="text-slate-300 text-left">
                      Statistical analysis
                    </div>
                  </div>

                  <div className="flex items-center justify-center text-teal-400 font-medium">
                    Start Chat
                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </a>

            {/* Historical Insights Card */}
            <a href="/historical" className="group block">
              <div className="relative bg-slate-800/50 backdrop-blur-sm p-8 rounded-2xl hover:border-teal-400/50 transition-all duration-300 h-full min-h-[280px] hover-trace">
                <div className="flex flex-col h-full">
                  <div className="flex items-center mb-6">
                    <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-500 p-3 mr-4 shadow-lg">
                      <svg
                        className="w-full h-full text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                        />
                      </svg>
                    </div>
                    <h3 className="text-2xl font-semibold text-white">
                      Historical Insights
                    </h3>
                  </div>
                  
                  <p className="text-slate-300 mb-8 leading-relaxed flex-grow">
                    {t.home.documentDesc}
                  </p>
                  
                  <div className="space-y-3 mb-8">
                    <div className="text-slate-300 text-left">
                      CGWB report analysis
                    </div>
                    <div className="text-slate-300 text-left">
                      Technical term explanations
                    </div>
                    <div className="text-slate-300 text-left">
                      Research insights
                    </div>
                  </div>

                  <div className="flex items-center justify-center text-teal-400 font-medium">
                    Start Chat
                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </a>
          </div>

          {/* Navigation buttons */}
          <div className="flex flex-wrap gap-4 justify-center mb-8">
            <a
              href="/dashboard"
              className="group relative px-6 py-3 overflow-hidden rounded-xl"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/50 to-indigo-600/50 transition-all duration-300 group-hover:scale-110"></div>
              <div className="absolute -inset-1 opacity-0 group-hover:opacity-100 transition-opacity blur-lg bg-gradient-to-r from-blue-500 to-indigo-500"></div>
              <span className="relative text-white font-medium">
                Visualize Data
              </span>
            </a>
            <a
              href="/search"
              className="group relative px-6 py-3 overflow-hidden rounded-xl"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-slate-600/50 to-slate-700/50 transition-all duration-300 group-hover:scale-110"></div>
              <div className="absolute -inset-1 opacity-0 group-hover:opacity-100 transition-opacity blur-lg bg-gradient-to-r from-slate-500 to-slate-600"></div>
              <span className="relative text-white font-medium">
                Search Data
              </span>
            </a>
          </div>

          {/* Bobbing arrow indicator */}
          <div className="flex justify-center mt-8">
            <div className="animate-bounce">
              <svg
                className="w-6 h-6 text-teal-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M19 14l-7 7m0 0l-7-7m7 7V3"
                />
              </svg>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="relative py-16">
        <div className="mx-auto max-w-4xl px-4 relative">
          <h2 className="text-3xl font-bold mb-12 text-center text-white">
            How Our AI Works
          </h2>
          <div className="relative">
            <div className="grid md:grid-cols-3 gap-8">
              {/* Step 1 */}
              <div className="text-center">
                <div className="w-16 h-16 mb-6 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center text-white text-xl font-bold shadow-lg mx-auto">
                  1
                </div>
                <h3 className="text-xl font-semibold mb-4 text-white">
                  {t.home.chooseMode}
                </h3>
                <p className="text-slate-300 leading-relaxed">
                  {t.home.chooseModeDesc}
                </p>
              </div>

              {/* Step 2 */}
              <div className="text-center">
                <div className="w-16 h-16 mb-6 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center text-white text-xl font-bold shadow-lg mx-auto">
                  2
                </div>
                <h3 className="text-xl font-semibold mb-4 text-white">
                  {t.home.askNaturally}
                </h3>
                <p className="text-slate-300 leading-relaxed">
                  Type your questions in plain English. Our AI understands context and provides relevant insights.
                </p>
              </div>

              {/* Step 3 */}
              <div className="text-center">
                <div className="w-16 h-16 mb-6 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center text-white text-xl font-bold shadow-lg mx-auto">
                  3
                </div>
                <h3 className="text-xl font-semibold mb-4 text-white">
                  Get Smart Answers
                </h3>
                <p className="text-slate-300 leading-relaxed">
                  Receive comprehensive answers with data visualizations and actionable insights.
                </p>
              </div>
            </div>

            {/* Floating arrows positioned between steps */}
            <div className="hidden md:block">
              {/* Arrow between step 1 and 2 */}
              <div className="absolute top-8 left-1/3 transform -translate-x-1/2">
                <span className="text-3xl text-teal-400">→</span>
              </div>
              
              {/* Arrow between step 2 and 3 */}
              <div className="absolute top-8 left-2/3 transform -translate-x-1/2">
                <span className="text-3xl text-teal-400">→</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Key Features Section */}
      <section className="relative py-16">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="text-3xl font-bold mb-12 text-center text-white">
            Key Features
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                title: "Natural Language Queries",
                desc: "Ask questions about groundwater data in plain English with intelligent context understanding.",
                icon: "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z",
              },
              {
                title: "CGWB Document Analysis",
                desc: "Access previous CGWB assessments through intelligent document parsing and search.",
                icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
              },
              {
                title: "Technical Dictionary",
                desc: "Get instant explanations of hydrogeological terms and water quality parameters.",
                icon: "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
              },
              {
                title: "Multi-Modal Responses",
                desc: "Comprehensive answers with charts, tables, and visualizations for better understanding.",
                icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
              },
              {
                title: "Context-Aware Intelligence",
                desc: "AI maintains conversation context and automatically switches between data sources.",
                icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
              },
              {
                title: "Real-Time Data Access",
                desc: "Up-to-date information from INGRES database with instant processing and analysis.",
                icon: "M13 10V3L4 14h7v7l9-11h-7z",
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="bg-slate-800/30 backdrop-blur-sm p-6 rounded-xl border border-slate-600/30 hover:border-teal-400/50 transition-all duration-300"
              >
                <div className="w-12 h-12 mb-4 rounded-lg bg-slate-700/50 p-2.5 border border-slate-600/30">
                  <svg
                    className="w-full h-full text-teal-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d={feature.icon}
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold mb-3 text-white">
                  {feature.title}
                </h3>
                <p className="text-slate-300 leading-relaxed text-sm">
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

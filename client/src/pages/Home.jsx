import { useI18n } from "../i18n/I18nContext";

export default function Home() {
  const { t } = useI18n();
  return (
    <div className="min-h-screen bg-[#030714] overflow-hidden relative pt-24">
      {/* Animated background gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_0%_0%,_#1a365d_0%,_transparent_50%)] animate-pulse"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_100%_100%,_#0d9488_0%,_transparent_50%)] animate-pulse [animation-delay:1s]"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,_#1e40af_0%,_transparent_50%)] animate-pulse [animation-delay:2s]"></div>

      {/* Particle effect overlay */}
      <div className="absolute inset-0 bg-[url('/noise.png')] opacity-[0.02] mix-blend-overlay"></div>

      {/* Hero Section */}
      <section className="relative mx-auto max-w-6xl px-4 py-8">
        <div className="text-center">
          {/* Animated logo with glow effect - smaller size */}
          <div className="relative mb-6">
            <div className="absolute inset-0 blur-xl bg-cyan-500/30 rounded-full animate-pulse"></div>
            <img
              src="/logo1.png"
              alt={t.brand}
              className="relative h-20 w-20 mx-auto animate-float"
            />
          </div>

          {/* Glowing title with animated gradient - smaller size */}
          <h1 className="text-4xl md:text-5xl font-bold mb-4 animate-gradient-text bg-gradient-to-r from-cyan-300 via-teal-300 to-blue-300 bg-clip-text text-transparent bg-[length:400%_400%]">
            {t.home.welcome}
          </h1>

          {/* Animated description with typewriter effect */}
          <p className="text-lg text-cyan-100/80 mb-6 max-w-2xl mx-auto animate-fade-in">
            Experience groundwater intelligence through our dual AI chatbot
            system
          </p>

          {/* Dual Chatbot Showcase - Main Feature */}
          <div className="mb-8 relative">
            <div className="absolute -inset-2 bg-gradient-to-r from-cyan-500 via-blue-500 to-teal-500 rounded-3xl blur-2xl opacity-20 animate-pulse"></div>
            <div className="relative bg-slate-900/70 backdrop-blur-xl p-6 rounded-3xl border border-cyan-500/30">
              <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-cyan-300 to-teal-300 bg-clip-text text-transparent text-center">
                Choose Your AI Assistant
              </h2>

              <div className="grid md:grid-cols-2 gap-6 mb-6">
                {/* Database Query Bot */}
                <div className="group relative bg-slate-800/60 backdrop-blur-sm p-6 rounded-2xl border border-cyan-500/20 hover:border-cyan-400/50 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-cyan-500/25">
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  <div className="relative">
                    <div className="flex items-center mb-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 p-2.5 mr-4 shadow-lg">
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
                            d="M4 7v10c0 2.21 1.79 4 4 4h8c2.21 0 4-1.79 4-4V7c0-2.21-1.79-4-4-4H8c-2.21 0-4 1.79-4 4z"
                          />
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M9 12l2 2 4-4"
                          />
                        </svg>
                      </div>
                      <h3 className="text-xl font-bold text-cyan-300">
                        Database Query Assistant
                      </h3>
                    </div>
                    <p className="text-slate-300/90 mb-6 leading-relaxed">
                      Query the INGRES database with natural language. Get
                      instant insights from structured groundwater data across
                      India.
                    </p>
                    <div className="space-y-2">
                      <div className="flex items-center text-sm text-cyan-300">
                        <div className="w-2 h-2 bg-cyan-400 rounded-full mr-3 animate-pulse"></div>
                        Real-time data queries
                      </div>
                      <div className="flex items-center text-sm text-cyan-300">
                        <div className="w-2 h-2 bg-cyan-400 rounded-full mr-3 animate-pulse"></div>
                        Multi-year comparisons
                      </div>
                      <div className="flex items-center text-sm text-cyan-300">
                        <div className="w-2 h-2 bg-cyan-400 rounded-full mr-3 animate-pulse"></div>
                        Statistical analysis
                      </div>
                    </div>
                  </div>
                </div>

                {/* RAG Assessment Bot */}
                <div className="group relative bg-slate-800/60 backdrop-blur-sm p-6 rounded-2xl border border-teal-500/20 hover:border-teal-400/50 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-teal-500/25">
                  <div className="absolute inset-0 bg-gradient-to-br from-teal-500/5 to-emerald-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  <div className="relative">
                    <div className="flex items-center mb-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-500 p-2.5 mr-4 shadow-lg">
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
                      <h3 className="text-xl font-bold text-teal-300">
                        CGWB Knowledge Assistant
                      </h3>
                    </div>
                    <p className="text-slate-300/90 mb-6 leading-relaxed">
                      Explore CGWB assessments using RAG technology. Understand
                      technical terms and get insights from research reports.
                    </p>
                    <div className="space-y-2">
                      <div className="flex items-center text-sm text-teal-300">
                        <div className="w-2 h-2 bg-teal-400 rounded-full mr-3 animate-pulse"></div>
                        CGWB report analysis
                      </div>
                      <div className="flex items-center text-sm text-teal-300">
                        <div className="w-2 h-2 bg-teal-400 rounded-full mr-3 animate-pulse"></div>
                        Technical term explanations
                      </div>
                      <div className="flex items-center text-sm text-teal-300">
                        <div className="w-2 h-2 bg-teal-400 rounded-full mr-3 animate-pulse"></div>
                        Research insights
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Enhanced Primary CTA */}
              <div className="text-center">
                <a
                  href="/chat"
                  className="group relative inline-flex items-center px-12 py-5 text-xl font-bold text-white overflow-hidden rounded-2xl animate-bounce hover:animate-none"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 via-blue-500 to-teal-500 transition-all duration-300 group-hover:scale-110"></div>
                  <div className="absolute inset-0 opacity-50 group-hover:opacity-0 transition-opacity bg-[radial-gradient(circle_at_50%_50%,_white_0%,_transparent_100%)]"></div>
                  <div className="absolute -inset-2 opacity-0 group-hover:opacity-100 transition-opacity blur-2xl bg-gradient-to-r from-cyan-400 via-blue-400 to-teal-400"></div>
                  <span className="relative mr-3">
                    Start AI Chat Experience
                  </span>
                  <svg
                    className="w-6 h-6 relative transition-transform group-hover:translate-x-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                </a>
              </div>
            </div>
          </div>

          {/* Secondary navigation */}
          <div className="flex flex-wrap gap-4 justify-center">
            <a
              href="/dashboard"
              className="group relative px-6 py-3 overflow-hidden rounded-xl"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/50 to-indigo-600/50 transition-all duration-300 group-hover:scale-110"></div>
              <div className="absolute -inset-1 opacity-0 group-hover:opacity-100 transition-opacity blur-lg bg-gradient-to-r from-blue-500 to-indigo-500"></div>
              <span className="relative text-white font-medium">
                {t.home.exploreData}
              </span>
            </a>
            <a
              href="/search"
              className="group relative px-6 py-3 overflow-hidden rounded-xl"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-slate-600/50 to-slate-700/50 transition-all duration-300 group-hover:scale-110"></div>
              <div className="absolute -inset-1 opacity-0 group-hover:opacity-100 transition-opacity blur-lg bg-gradient-to-r from-slate-500 to-slate-600"></div>
              <span className="relative text-white font-medium">
                {t.home.searchData}
              </span>
            </a>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="relative py-12">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-blue-950/30 to-transparent"></div>
        <div className="mx-auto max-w-6xl px-4 relative">
          <h2 className="text-3xl font-bold mb-8 text-center">
            <span className="bg-gradient-to-r from-cyan-300 to-blue-300 bg-clip-text text-transparent">
              How Our AI Works
            </span>
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {/* Step 1: Choose Mode */}
            <div className="group relative">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl blur opacity-50 group-hover:opacity-100 transition duration-1000"></div>
              <div className="relative flex flex-col h-full bg-slate-900/80 backdrop-blur-xl p-6 rounded-xl border border-slate-800/50">
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5 rounded-xl"></div>
                <div className="w-12 h-12 mb-4 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center text-white text-lg font-bold shadow-lg">
                  1
                </div>
                <h3 className="text-lg font-semibold mb-3 text-cyan-300">
                  Choose Your Mode
                </h3>
                <p className="text-slate-300/90 text-sm">
                  Select between Database Queries for data analysis or Knowledge
                  Assistant for CGWB reports and technical explanations.
                </p>
              </div>
            </div>

            {/* Step 2: Ask Questions */}
            <div className="group relative">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-teal-500 rounded-xl blur opacity-50 group-hover:opacity-100 transition duration-1000"></div>
              <div className="relative flex flex-col h-full bg-slate-900/80 backdrop-blur-xl p-6 rounded-xl border border-slate-800/50">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-teal-500/5 rounded-xl"></div>
                <div className="w-12 h-12 mb-4 rounded-xl bg-gradient-to-br from-blue-500 to-teal-500 flex items-center justify-center text-white text-lg font-bold shadow-lg">
                  2
                </div>
                <h3 className="text-lg font-semibold mb-3 text-blue-300">
                  Ask Naturally
                </h3>
                <p className="text-slate-300/90 text-sm">
                  Type your questions in plain English. Our AI understands
                  context and provides relevant insights from the appropriate
                  data source.
                </p>
              </div>
            </div>

            {/* Step 3: Get Insights */}
            <div className="group relative">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-teal-500 to-emerald-500 rounded-xl blur opacity-50 group-hover:opacity-100 transition duration-1000"></div>
              <div className="relative flex flex-col h-full bg-slate-900/80 backdrop-blur-xl p-6 rounded-xl border border-slate-800/50">
                <div className="absolute inset-0 bg-gradient-to-br from-teal-500/5 to-emerald-500/5 rounded-xl"></div>
                <div className="w-12 h-12 mb-4 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center text-white text-lg font-bold shadow-lg">
                  3
                </div>
                <h3 className="text-lg font-semibold mb-3 text-teal-300">
                  Get Smart Answers
                </h3>
                <p className="text-slate-300/90 text-sm">
                  Receive comprehensive answers with data visualizations,
                  technical explanations, and actionable insights tailored to
                  your query.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Chatbot Capabilities Section */}
      <section className="relative py-12">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="text-3xl font-bold mb-8 text-center">
            <span className="bg-gradient-to-r from-teal-300 to-cyan-300 bg-clip-text text-transparent">
              Advanced AI Capabilities
            </span>
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Feature Cards with Interactive Hover Effects */}
            {[
              {
                title: "Natural Language Queries",
                desc: "Ask questions about groundwater data in plain English. Our AI understands context and provides accurate database insights.",
                gradient: "from-cyan-500 to-teal-500",
                icon: "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z",
              },
              {
                title: "CGWB Document Analysis",
                desc: "Access and understand previous CGWB assessments through RAG-powered search and intelligent document parsing.",
                gradient: "from-teal-500 to-emerald-500",
                icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
              },
              {
                title: "Technical Term Dictionary",
                desc: "Get instant explanations of hydrogeological terms, water quality parameters, and technical concepts used in groundwater studies.",
                gradient: "from-emerald-500 to-cyan-500",
                icon: "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
              },
              {
                title: "Multi-Modal Responses",
                desc: "Receive comprehensive answers with charts, tables, and visualizations that make complex data easy to understand.",
                gradient: "from-blue-500 to-indigo-500",
                icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
              },
              {
                title: "Context-Aware Intelligence",
                desc: "Our AI maintains conversation context and automatically switches between SQL queries and RAG searches based on your needs.",
                gradient: "from-indigo-500 to-violet-500",
                icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
              },
              {
                title: "Real-Time Data Access",
                desc: "Get up-to-date information from the INGRES database with instant processing of complex queries and statistical analysis.",
                gradient: "from-violet-500 to-purple-500",
                icon: "M13 10V3L4 14h7v7l9-11h-7z",
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="group relative transform transition-all duration-500 hover:scale-105"
              >
                <div
                  className={`absolute -inset-0.5 bg-gradient-to-r ${feature.gradient} rounded-xl blur opacity-50 group-hover:opacity-100 transition duration-1000`}
                ></div>
                <div className="relative flex flex-col h-full bg-slate-900/80 backdrop-blur-xl p-8 rounded-xl border border-slate-800/50">
                  <div
                    className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-[0.03] rounded-xl group-hover:opacity-[0.06] transition-opacity duration-500`}
                  ></div>
                  <div className="w-12 h-12 mb-4 rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 p-2.5 border border-slate-600">
                    <svg
                      className="w-full h-full text-cyan-300"
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
                  <h3 className="text-xl font-semibold mb-4 bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                    {feature.title}
                  </h3>
                  <p className="text-slate-300/90 leading-relaxed">
                    {feature.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

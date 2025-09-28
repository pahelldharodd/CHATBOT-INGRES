import { useState } from "react";

export default function Tutorial() {
  const [currentStep, setCurrentStep] = useState(0);

  // Interactive tutorial steps with visual guides
  const tutorialSteps = [
    {
      title: "Welcome to INGRES Dashboard",
      description: "This comprehensive tutorial will guide you through the features of our groundwater monitoring system. The interface is designed to provide clear access to critical groundwater data and analysis tools.",
      visual: "▣",
      action: "Click 'Next' to begin the tutorial",
      highlight: "welcome"
    },
    {
      title: "System Navigation",
      description: "The top navigation bar provides access to all major system modules including Dashboard, Chat Interface, Historical Data Analysis, and Help Documentation. Each section serves a specific function in groundwater monitoring and analysis.",
      visual: "▤",
      action: "Navigate between different system modules",
      highlight: "navigation"
    },
    {
      title: "Dashboard Overview",
      description: "The Dashboard provides a comprehensive overview of current groundwater metrics including extraction rates, water levels, and regional assessments. Key performance indicators are displayed in organized information cards for quick reference.",
      visual: "▦",
      action: "Review the statistical overview cards",
      highlight: "dashboard"
    },
    {
      title: "Interactive Mapping System",
      description: "The mapping interface displays geographical groundwater data with color-coded indicators representing different measurement levels and extraction stages. Click on regions to access detailed area-specific information.",
      visual: "▩",
      action: "Select different regions on the interactive map",
      highlight: "maps"
    },
    {
      title: "AI-Powered Query System",
      description: "The intelligent chat interface allows you to submit natural language queries about groundwater data. The system processes your questions and provides relevant information from the comprehensive database.",
      visual: "▨",
      action: "Submit a query about groundwater data",
      highlight: "chat"
    },
    {
      title: "Historical Data Analysis",
      description: "Access comprehensive historical records and trend analysis through this specialized interface. The system maintains extensive archives of groundwater data for longitudinal studies and comparative analysis.",
      visual: "▧",
      action: "Explore historical data trends",
      highlight: "historical"
    },
    {
      title: "Data Interpretation Guide",
      description: "The system provides contextual information and explanations for all data points. Hover over charts, graphs, and numerical displays to access detailed explanations and measurement contexts.",
      visual: "▢",
      action: "Use hover tooltips for data explanations",
      highlight: "data"
    },
    {
      title: "Support and Documentation",
      description: "Comprehensive help documentation is available through the Help section. Additional technical support can be accessed through the contact information provided in the support section.",
      visual: "▣",
      action: "Access help documentation when needed",
      highlight: "help"
    },
    {
      title: "System Ready for Operation",
      description: "You have completed the system overview tutorial. The INGRES platform is now ready for your groundwater monitoring and analysis requirements. All system functions are accessible through the main navigation.",
      visual: "▤",
      action: "Begin using the system for data analysis",
      highlight: "complete"
    }
  ];

  const nextStep = () => {
    if (currentStep < tutorialSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const currentStepData = tutorialSteps[currentStep];
  const progress = ((currentStep + 1) / tutorialSteps.length) * 100;

  return (
    <div className="rounded-2xl border border-teal-500/20 bg-slate-900/40 backdrop-blur-xl p-6 text-slate-100 shadow-lg">
      <div className="mb-6">
        <h3 className="font-semibold text-teal-300 text-xl">
          System Tutorial
        </h3>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-slate-400 mb-2">
          <span>Step {currentStep + 1} of {tutorialSteps.length}</span>
          <span>{Math.round(progress)}% Complete</span>
        </div>
        <div className="w-full bg-slate-700/50 rounded-full h-2 overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-cyan-500 to-teal-500 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Tutorial Content */}
      <div className="min-h-[300px] relative overflow-hidden rounded-xl bg-slate-800/30 border border-slate-600/30 p-6">
        <div className="text-center">
          {/* Visual Icon */}
          <div className="text-6xl mb-4 animate-bounce-slow">
            {currentStepData.visual}
          </div>

          {/* Title */}
          <h4 className="text-2xl font-bold text-white mb-4 text-glow">
            {currentStepData.title}
          </h4>

          {/* Description */}
          <p className="text-slate-300 leading-relaxed mb-6 max-w-2xl mx-auto text-lg">
            {currentStepData.description}
          </p>

          {/* Action Tip */}
          <div className="bg-gradient-to-r from-cyan-600/20 to-teal-600/20 border border-cyan-500/30 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-center gap-2 text-cyan-300">
              <span className="text-xl">→</span>
              <span className="font-medium">Next Step:</span>
            </div>
            <p className="text-cyan-200 mt-2">{currentStepData.action}</p>
          </div>
        </div>
      </div>

      {/* Navigation Controls */}
      <div className="flex items-center justify-between mt-6">
        <button
          onClick={prevStep}
          disabled={currentStep === 0}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-700/50 border border-slate-600/30 text-slate-300 hover:bg-slate-700/70 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          <span>←</span> Previous
        </button>

        <button
          onClick={nextStep}
          disabled={currentStep === tutorialSteps.length - 1}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-teal-600 border border-cyan-500/30 text-white hover:from-cyan-500 hover:to-teal-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          Next <span>→</span>
        </button>
      </div>

      {/* System Information */}
      <div className="mt-6 p-4 bg-slate-800/40 rounded-lg border border-slate-600/20">
        <div className="flex items-start gap-3">
          <span className="text-2xl text-cyan-400">ⓘ</span>
          <div>
            <h5 className="font-medium text-slate-200 mb-1">Tutorial Information:</h5>
            <p className="text-sm text-slate-400">
              This tutorial provides comprehensive system guidance. Reference this documentation anytime through the Help section for operational assistance.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

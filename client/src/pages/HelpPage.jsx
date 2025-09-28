import FAQ from "../components/help/FAQ";
import Tutorial from "../components/help/Tutorial";
import ContactSupport from "../components/help/ContactSupport";

export default function HelpPage() {
  return (
    <div className="min-h-screen pt-20 bg-[#030714] relative">
      {/* Animated background gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_0%_0%,_#1a365d_0%,_transparent_50%)] animate-pulse"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_100%_100%,_#0d9488_0%,_transparent_50%)] animate-pulse [animation-delay:1s]"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,_#1e40af_0%,_transparent_50%)] animate-pulse [animation-delay:2s]"></div>

      <div className="mx-auto max-w-4xl px-4 py-8 grid gap-8 relative z-10">
        <FAQ />
        <Tutorial />
        <ContactSupport />
      </div>
    </div>
  );
}

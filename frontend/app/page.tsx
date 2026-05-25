import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />
      <Hero />
      
      {/* Features Section - Placeholder for premium look */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard 
              title="Verified Professionals" 
              description="Every worker on our platform goes through a rigorous vetting process to ensure quality."
            />
            <FeatureCard 
              title="Secure Payments" 
              description="Safe and fast payment processing for every job, guaranteed by BlueHire."
            />
            <FeatureCard 
              title="Real-time Tracking" 
              description="Track job progress and communicate with your team effortlessly in real-time."
            />
          </div>
        </div>
      </section>
      
      <footer className="py-12 border-t">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>© 2026 BlueHire. All rights reserved.</p>
        </div>
      </footer>
    </main>
  );
}

function FeatureCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="p-6 rounded-xl border bg-card text-card-foreground shadow-sm hover:shadow-md transition-shadow">
      <h3 className="text-xl font-bold mb-3">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}

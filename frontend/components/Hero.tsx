import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Hero() {
  return (
    <section className="pt-32 pb-16 md:pt-48 md:pb-32 px-4">
      <div className="container mx-auto text-center max-w-4xl">
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          Find Skilled Workers. <br className="hidden md:block" />
          Find Better Jobs.
        </h1>
        <p className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed">
          The premium marketplace connecting professional contractors with skilled blue-collar workers. Fast, reliable, and built for the modern trades.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button size="lg" className="h-12 px-8 text-lg" asChild>
            <Link href="/jobs">Hire Talent</Link>
          </Button>
          <Button size="lg" variant="outline" className="h-12 px-8 text-lg" asChild>
            <Link href="/worker-registration">Find Work</Link>
          </Button>
        </div>
      </div>
    </section>
  );
}

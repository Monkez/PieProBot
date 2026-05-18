import type { Metadata } from "next";
import { Nav, TopBar } from "@/components/nav";
import "./globals.css";

export const metadata: Metadata = {
  title: "PiePro",
  description: "AI agent platform operations console"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen p-3 sm:p-5">
          <div className="playful-outline lifted-shadow mx-auto min-h-[calc(100vh-2.5rem)] max-w-[1500px] rounded-[32px] bg-[#e8f2e9] p-4 sm:p-7">
            <TopBar />
            <div className="flex gap-5">
              <Nav />
              <main className="min-w-0 flex-1">{children}</main>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}

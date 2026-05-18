import type { Metadata } from "next";
import { Sidebar } from "@/components/nav";
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
          <div className="playful-outline lifted-shadow mx-auto min-h-[calc(100vh-2.5rem)] max-w-[1500px] rounded-[32px] bg-[#fbfcfe] p-4 sm:p-7">
            <div className="grid min-h-[calc(100vh-5.5rem)] gap-5 lg:grid-cols-[260px_1fr]">
              <Sidebar />
              <main className="min-w-0">{children}</main>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}

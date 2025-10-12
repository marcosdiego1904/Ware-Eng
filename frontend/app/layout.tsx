import type { Metadata, Viewport } from "next";
import { Inter, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { ToastManager } from "@/components/ui/toast-manager";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Warehouse Intelligence Dashboard",
  description: "Advanced warehouse anomaly detection and inventory management",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#FF6B35", // Safety Orange - Warehouse Intelligence brand
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body
        className={`${inter.variable} ${geistMono.variable} antialiased h-full bg-background text-foreground`}
      >
        <ErrorBoundary>
          <AuthProvider>
            {children}
            <ToastManager />
          </AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}

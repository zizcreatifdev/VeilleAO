import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Veille AO — Configuration",
  description: "Configurer les sources, thèmes et destinataires de la veille appels d'offres",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body className="min-h-screen bg-gray-950 text-gray-100 antialiased">
        {children}
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "A&G CRM",
  description: "Panel de gestion para A&G Electronica e Informatica",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es-PY">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

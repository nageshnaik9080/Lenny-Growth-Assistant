import "./globals.css";

export const metadata = {
  title: "Lenny Growth Assistant",
  description: "Grounded product and growth knowledge from Lenny's Podcast transcripts",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

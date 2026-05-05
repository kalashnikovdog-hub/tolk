import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Discount Hub PWA',
  description: 'Discount Hub Progressive Web Application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

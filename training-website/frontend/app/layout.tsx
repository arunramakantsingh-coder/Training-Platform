import Link from "next/link";
import "./globals.css";

export const metadata = {
  title: "Lab Training Portal · IIHT",
  description: "IIHT Arista VeloCloud SD-WAN training and hands-on lab portal",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <nav className="site-nav">
            <Link className="brand" href="/">Lab <span>Training Portal</span></Link>
            <div className="nav-links">
              <Link href="/courses">Course</Link>
              <Link href="/schedule">Schedule</Link>
              <Link href="/lab">Lab Access</Link>
              <Link href="/login">Student Login</Link>
            </div>
          </nav>
          {children}
        </div>
      </body>
    </html>
  );
}

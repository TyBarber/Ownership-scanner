import type { ReactNode } from "react";
import { Link, useLocation } from "wouter";
import styles from "./AppLayout.module.css";

const navigation = [
  { to: "/products", label: "Products" },
  { to: "/methodology", label: "Methodology" },
  { to: "/about", label: "About" },
];

export function AppLayout({ children }: { children: ReactNode }) {
  const [location] = useLocation();

  return (
    <>
      <a className={styles.skipLink} href="#main-content">
        Skip to main content
      </a>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <Link className={styles.brand} to="/" aria-label="Protest home">
            <span>PROTEST</span>
            <small>Product Ownership Intelligence</small>
          </Link>
          <nav aria-label="Primary navigation">
            <ul className={styles.navigation}>
              {navigation.map((item) => (
                <li key={item.to}>
                  <Link
                    aria-current={
                      location === item.to ||
                      (item.to === "/products" &&
                        location.startsWith("/products/"))
                        ? "page"
                        : undefined
                    }
                    className={
                      location === item.to ||
                      (item.to === "/products" &&
                        location.startsWith("/products/"))
                        ? styles.active
                        : undefined
                    }
                    to={item.to}
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </header>
      <main id="main-content" className={styles.main}>
        {children}
      </main>
      <footer className={styles.footer}>
        <div>
          <strong>Protest</strong>
          <span>Know Who Profits.</span>
        </div>
        <p>
          Development research tool. Ownership records may include explicitly
          identified gaps.
        </p>
      </footer>
    </>
  );
}

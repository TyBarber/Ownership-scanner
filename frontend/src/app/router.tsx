import { Route, Switch } from "wouter";
import { AppLayout } from "../components/layout/AppLayout";
import { AboutPage } from "../pages/AboutPage";
import { HomePage } from "../pages/HomePage";
import { MethodologyPage } from "../pages/MethodologyPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { ProductPage } from "../pages/ProductPage";
import { ProductsPage } from "../pages/ProductsPage";

export function AppRouter() {
  return (
    <AppLayout>
      <Switch>
        <Route path="/" component={HomePage} />
        <Route path="/products" component={ProductsPage} />
        <Route path="/products/:gtin" component={ProductPage} />
        <Route path="/methodology" component={MethodologyPage} />
        <Route path="/about" component={AboutPage} />
        <Route component={NotFoundPage} />
      </Switch>
    </AppLayout>
  );
}

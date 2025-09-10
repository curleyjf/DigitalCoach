import type { AppProps } from "next/app";

import "@App/styles/globals.css";
import "@fullcalendar/core";
import "@fullcalendar/common/main.css";
import "@fullcalendar/daygrid";
import "@App/lib/firebase/firebase.config";
import CoreLayout from "@App/components/layouts/CoreLayout";
import { AuthContextProvider } from "@App/lib/auth/AuthContextProvider";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

function MyApp({ Component, pageProps }: AppProps) {
  const queryClient = new QueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <AuthContextProvider>
        <CoreLayout>
          <Component {...pageProps} />
        </CoreLayout>
      </AuthContextProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default MyApp;

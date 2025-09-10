import { useEffect } from "react";
import AuthService from "@App/lib/auth/AuthService";

export default function TestAuthListener() {
  useEffect(() => {
    console.log("Setting up auth state listener...");
    const unsubscribe = AuthService.onAuthStateChanged((user) => {
      console.log("🔥 Auth state changed:", user);
    });

    return () => unsubscribe?.();
  }, []);

  return <div>Testing auth listener...</div>;
}

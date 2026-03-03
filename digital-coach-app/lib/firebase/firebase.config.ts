import { getStorage, connectStorageEmulator } from "firebase/storage";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";
import { getAuth, connectAuthEmulator } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";
import { initializeApp, getApps } from "firebase/app";

export const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID,
};
// If we're in the browser (window exists), use localhost. If we're in a Docker container, use the service name 'firebase'.
const emulatorHost = typeof window !== "undefined" ? "localhost" : "firebase";
// If we're in the browser, use localhost for auth emulator. If in Docker, use 'firebase' service name.
const authURL = typeof window !== "undefined" ? "http://localhost:9099" : "http://firebase:9099";

if (!getApps().length) {
  const app = initializeApp(firebaseConfig);

  if (typeof window !== "undefined" && "measurementId" in firebaseConfig) {
    getAnalytics(app);
  }

  const auth = getAuth(app);
  connectAuthEmulator(auth, authURL, {
    disableWarnings: true,
  });

  const db = getFirestore(app);
  connectFirestoreEmulator(db, emulatorHost, 8080);

  const storage = getStorage(app);
  connectStorageEmulator(storage, emulatorHost, 9199);
}

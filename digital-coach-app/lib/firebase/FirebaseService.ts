import { FirebaseApp, getApps, getApp, initializeApp } from "firebase/app";
import { firebaseConfig } from "./firebase.config";

export default class FirebaseService {
  app: FirebaseApp;

  constructor() {
    this.app = getApps().length ? getApp() : initializeApp(firebaseConfig);
  }
}

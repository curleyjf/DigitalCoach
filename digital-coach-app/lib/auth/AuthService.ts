import {
  getAuth,
  Auth,
  signInWithEmailAndPassword,
  UserCredential,
  signOut,
  // signInWithPopup,
  // GoogleAuthProvider,
  User,
  onAuthStateChanged as firebaseOnAuthStateChanged,
  createUserWithEmailAndPassword,
} from "firebase/auth";
import FirebaseService from "@App/lib/firebase/FirebaseService";

class AuthService extends FirebaseService {
  auth: Auth;

  constructor() {
    super();

    this.auth = getAuth(this.app);
  }

  async login(email: string, password: string): Promise<UserCredential> {
    return signInWithEmailAndPassword(this.auth, email, password);
  }

  async signup(email: string, password: string): Promise<UserCredential> {
    return createUserWithEmailAndPassword(this.auth, email, password);
  }

  // async loginWithGoogle(): Promise<UserCredential> {
  //   const provider = new GoogleAuthProvider();
  //   return signInWithPopup(this.auth, provider);
  // }

  async logout(): Promise<void> {
    signOut(this.auth);
  }

  isSignedIn() {
    return !!this.auth.currentUser?.uid;
  }

  onAuthStateChanged(callback: (user: User | null) => void) {
    return firebaseOnAuthStateChanged(this.auth, callback);
  }
}

export default new AuthService();

import { initializeApp } from "firebase/app";
import {
  getAuth,
  GoogleAuthProvider,
  GithubAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  updateProfile,
  signOut,
} from "firebase/auth";
import {
  getFirestore,
  collection,
  addDoc,
  query,
  where,
  getDocs,
  serverTimestamp,
} from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyAzIDskZrns4MfGtk6zfnY_Q2YoUcHUTgY",
  authDomain: "socialmedia-20756.firebaseapp.com",
  projectId: "socialmedia-20756",
  storageBucket: "socialmedia-20756.firebasestorage.app",
  messagingSenderId: "933396662386",
  appId: "1:933396662386:web:8682af00de89adcfd4daeb",
  measurementId: "G-WW2K79BNXM",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);

// Auth providers
const googleProvider = new GoogleAuthProvider();
const githubProvider = new GithubAuthProvider();

export const signInWithGoogle = () => signInWithPopup(auth, googleProvider);
export const signInWithGithub = () => signInWithPopup(auth, githubProvider);

export const loginWithEmail = (email, password) =>
  signInWithEmailAndPassword(auth, email, password);

export const signupWithEmail = async (name, email, password) => {
  const cred = await createUserWithEmailAndPassword(auth, email, password);
  await updateProfile(cred.user, { displayName: name });
  return cred;
};

export const resetPassword = (email) => sendPasswordResetEmail(auth, email);
export const logout = () => signOut(auth);

// ---- Firestore: Analysis History ----

export async function saveAnalysis(uid, result) {
  return addDoc(collection(db, "analyses"), {
    uid,
    platform: result.platform,
    probability: result.probability,
    risk_level: result.risk_level,
    label: result.label,
    message: result.message,
    input_data: result.input_data || {},
    feature_importances: result.feature_importances || [],
    createdAt: serverTimestamp(),
  });
}

export async function getAnalysisHistory(uid) {
  try {
    const q = query(
      collection(db, "analyses"),
      where("uid", "==", uid)
    );
    // Race with a timeout so the page doesn't hang if Firestore is unreachable
    const snap = await Promise.race([
      getDocs(q),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error("Firestore timeout")), 5000)
      ),
    ]);
    const results = snap.docs.map((doc) => ({
      id: doc.id,
      ...doc.data(),
      createdAt: doc.data().createdAt?.toDate?.()?.toISOString() || null,
    }));
    results.sort((a, b) => (b.createdAt || "").localeCompare(a.createdAt || ""));
    return results;
  } catch (err) {
    console.warn("Firestore query failed (database may need to be enabled in Firebase Console):", err.message);
    return [];
  }
}

import { initializeApp } from "firebase/app";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  updateProfile,
  signOut,
} from "firebase/auth";

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

const googleProvider = new GoogleAuthProvider();

export const signInWithGoogle = () => signInWithPopup(auth, googleProvider);

export const loginWithEmail = (email, password) =>
  signInWithEmailAndPassword(auth, email, password);

export const signupWithEmail = async (name, email, password) => {
  const cred = await createUserWithEmailAndPassword(auth, email, password);
  await updateProfile(cred.user, { displayName: name });
  return cred;
};

export const logout = () => signOut(auth);

import "./firebase.config";
import * as functions from "firebase-functions";
import { getApp } from "firebase/app";
import { getDownloadURL, getStorage, ref } from "firebase/storage";

import { getDoc, getFirestore, doc, updateDoc } from "firebase/firestore";

import { default as axios } from "axios";
import { answerOneResponse, answerTwoResponse } from "./sampledata";

const app = getApp();

export const answerReceive = functions.https.onRequest(async (req, res) => {
  const { evaluation, userId, interviewId, questionId, answerId } = req.body;
  if (!evaluation || !userId || !interviewId || !questionId || !answerId) {
    res.status(400).send("Bad request");
  }
  const firestore = getFirestore();
  const answerRef = doc(
    firestore,
    `users/${userId}/interviews/${interviewId}/questions/${questionId}/answers/${answerId}`,
  );
  const answer = await getDoc(answerRef);
  if (!answer.exists) {
    res.status(400).send("Resource not found");
  }
  await updateDoc(answerRef, { evaluation });
  res.status(200).send("Success");
});

/* A function that is triggered when a new document is created in the specified path. */
export const answerUpload = functions.firestore
  .onDocumentCreated(
    "users/{userId}/interviews/{interviewId}/interviewQuestions/{questionId}/answers/{answerId}", async (event) => {
    const snapshot = event.data;
    const { userId, interviewId, questionId, answerId } = event.params;

    if (!snapshot) return;

    const data = snapshot.data();

    const videoRefUrl = data.videoUrl;
    const videoRef = ref(getStorage(app), videoRefUrl);
    const videoDownloadUrl = await getDownloadURL(videoRef);

    if (!process.env.ML_API_URL) {
      functions.logger.log("ML_API_URL is not set, using dummy data...");

      const evaluation = videoRef.toString().includes("answer-0")
        ? answerOneResponse
        : answerTwoResponse;

      snapshot.ref.update({ ...evaluation });
    } else {
      try {
        const MLApiResponse = await axios.post(process.env.ML_API_URL, {
          videoUrl: videoDownloadUrl,
          userId,
          interviewId,
          questionId,
          answerId,
        });
        functions.logger.log("MLApiResponse sent: ", MLApiResponse);
      } catch (error) {
        functions.logger.error(error);
      }
    }
  });

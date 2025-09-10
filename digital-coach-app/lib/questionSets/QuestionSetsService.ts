import {
  addDoc,
  collection,
  CollectionReference,
  DocumentReference,
  doc,
  Firestore,
  getDoc,
  getDocs,
  getFirestore,
  query,
  setDoc,
  Timestamp,
  where,
  updateDoc,
  arrayUnion,
} from "firebase/firestore";
import FirebaseService from "../firebase/FirebaseService";
import { IBaseQuestion } from "../question/models";

interface IQuestionSetAttributes {
  title: string;
  description: string;
  questions: string[];
  isFeatured: boolean;
  createdBy: string | null;
}

interface IQuestionSet extends IQuestionSetAttributes {
  createdAt: Timestamp;
}

class QuestionSetsService extends FirebaseService {
  private firestore: Firestore;

  constructor() {
    super();

    this.firestore = getFirestore(this.app);
  }

  private getCollectionRef() {
    return collection(
      this.firestore,
      "questionSets"
    ) as CollectionReference<IQuestionSet>;
  }

  private getDocRef(qsId: string) {
    return doc(
      this.firestore,
      "questionSets",
      qsId
    ) as DocumentReference<IQuestionSetAttributes>;
  }

  /**
   * This function creates a new question set in the database and returns a promise that resolves to
   * the newly created question set.
   * @param {IQuestionSetAttributes} questionSetAttr - IQuestionSetAttributes
   * @returns A promise that resolves to a document reference.
   */
  async createQuestionSet(questionSetAttr: IQuestionSetAttributes) {
    const collectionRef = this.getCollectionRef();

    const questionSet = {
      ...questionSetAttr,
      createdAt: Timestamp.now(),
    };

    const questionSetRef = await addDoc(collectionRef, questionSet);
    return getDoc(questionSetRef);
  }

  async getAllQuestionSets() {
    const collectionRef = this.getCollectionRef();

    return getDocs(collectionRef);
  }

  /**
   * Get all the documents in the collection where the isFeatured field is true.
   * @returns An array of question sets.
   */
  getFeaturedQuestionSets() {
    const collectionRef = this.getCollectionRef();
    const isFeaturedFilter = where("isFeatured", "==", true);
    const q = query(collectionRef, isFeaturedFilter);

    return getDocs(q);
  }

  async updateQuestionSet({
    qsid,
    title,
    description,
    questions = [],
  }: {
    qsid: string;
    title?: string;
    description?: string;
    questions?: string[];
  }) {
    const ref = this.getCollectionRef();

    const foundQuestionSet = (await getDoc(doc(ref, qsid))).data();

    if (!foundQuestionSet) throw new Error("Question set not found");

    await setDoc(
      doc(ref, qsid),
      {
        ...foundQuestionSet,
        title: title || foundQuestionSet.title,
        description: description || foundQuestionSet.description,
        questions: questions || foundQuestionSet.questions,
      },
      { merge: true }
    );
    return await getDoc(doc(ref, qsid));
  }

  async addQuestionToSet(qsid: string, questionData) {
    console.log(qsid);
    const { question, subject, type } = questionData;
    const questionSetRef = this.getCollectionRef();
    console.log(questionSetRef);
    const questionsRef = collection(
      this.firestore,
      "questions"
    ) as CollectionReference<IBaseQuestion>;
    console.log(questionsRef);

    const foundQuestionSet = await getDoc(doc(questionSetRef, qsid));
    // Use composite key to query the question
    const questionQuery = query(
      collection(this.firestore, "questions"),
      where("question", "==", question),
      where("subject", "==", subject),
      where("type", "==", type)
    );

    const querySnapshot = await getDocs(questionQuery);
    if (querySnapshot.empty) {
      throw new Error("Error adding question set: Question not found!");
    }

    // Assuming there's only one matching question, get its ID
    const questionId = querySnapshot.docs[0].id;

    // Check if the question already exists in the set
    if (foundQuestionSet.data()?.questions.includes(questionId)) {
      throw new Error(
        "Error adding question set: Question already exists in set!"
      );
    }

    // Update the question set with the new question
    await updateDoc(doc(questionSetRef, qsid), {
      questions: arrayUnion(questionId),
    });
  }

  async getQuestionSetByUserId(userId: string) {
    const collectionRef = this.getCollectionRef();
    const createdByFilter = where("createdBy", "==", userId);
    const q = query(collectionRef, createdByFilter);

    return await getDocs(q);
  }

  async getQuestionSetById(qsId: string) {
    const qsDocRef = this.getDocRef(qsId);
    try {
      return await getDoc(qsDocRef);
    } catch (e) {
      throw e;
    }
  }

  async getQuestionSetByName(qsName: string) {
    const qsCollection = this.getCollectionRef();
    const thisQsFilter = where("title", "==", qsName);
    const qs = query(qsCollection, thisQsFilter);

    return await getDocs(qs);
  }
}

export default new QuestionSetsService();

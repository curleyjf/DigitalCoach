import { Timestamp } from "firebase/firestore";

export type TSubject =
  | "Business and Accounting"
  | "Data Science"
  | "Finance"
  | "Human Resources"
  | "Information Technology"
  | "Law"
  | "Marketing"
  | "Operations"
  | "Product Management"
  | "Computer Science"
  | "Engineering"
  | "Storytelling"
  | "Scenarios"
  | "Any";

export type TQuestionType = "behaviorial" | "technical" | "Any";

export type TExperienceLevel = "Entry" | "Mid" | "Senior" | "Any";

export interface IBaseQuestionAttributes {
  subject: TSubject;
  question: string;
  type: TQuestionType;
  experienceLevel: TExperienceLevel;
  companies: string[];
  popularity?: number;
  createdBy?: string | null; // nullable
  keywords: string[];
}

export interface IBaseQuestion extends IBaseQuestionAttributes {
  lastUpdatedAt: Timestamp;
  createdAt: Timestamp;
}

export interface IQuestion extends IBaseQuestion {
  gid: string;
}

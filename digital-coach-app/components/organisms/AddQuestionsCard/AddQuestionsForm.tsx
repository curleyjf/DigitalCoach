import React, { useState } from "react";
import styles from "./AddQuestionsCard.module.scss";
import { MenuItem, Button, FormControl, TextField } from "@mui/material";
import {
  TSubject,
  TQuestionType,
  TExperienceLevel,
  IBaseQuestionAttributes,
} from "@App/lib/question/models";
import QuestionService from "@App/lib/question/QuestionService";
import QuestionSetsService from "@App/lib/questionSets/QuestionSetsService";
import Link from "next/link";

interface propsInfo {
  selectedSet: { questions: any[]; title: string; id: string };
  setSelectedSet: (set: {
    questions: any[];
    title: string;
    id: string;
  }) => void;
}

const sampleSubjects = [
  "Business Accounting and Analytics",
  "Data Science",
  "Finance",
  "Human Resources",
  "Information Technology",
  "Law",
  "Marketing",
  "Operations",
  "Product Management",
  "Computer Science",
  "Any",
];

export default function AddQuestionsForm(props: propsInfo) {
  const [questionText, setQuestionText] = useState("");
  const [subject, setSubject] = useState<TSubject>("Any");
  const [experienceLevel, setExperienceLevel] =
    useState<TExperienceLevel>("Any");
  const [questionType, setQuestionType] = useState<TQuestionType>("Any");
  const [company, setCompany] = useState("");

  const handleSubmit = async (e: { preventDefault: () => void }) => {
    e.preventDefault();
    console.log("Called handleSubmit");
    console.log("Selected State: " + props.selectedSet.title);
    let thisCompany = [] as string[];
    if (company !== "") thisCompany = [company];
    const baseQuestion = {
      subject: subject,
      question: questionText,
      type: questionType,
      experienceLevel: experienceLevel,
      companies: thisCompany,
      keywords: questionText
        .toLowerCase()
        .replace(/[^a-zA-Z0-9 ]/g, "")
        .split(" "),
    };
    const newQuestion = await QuestionService.addQuestion(baseQuestion);
    try {
      await QuestionSetsService.addQuestionToSet(
        props.selectedSet.id,
        newQuestion.id
      );
    } catch (e) {
      console.log(e);
    }
    location.reload();
  };

  return (
    <div className={styles.AddQuestionsCard}>
      <form
        className={styles.AddQuestionsCard_browseList}
        onSubmit={handleSubmit}
      >
        <FormControl fullWidth>
          <TextField
            id="questionText"
            label="Question Text"
            placeholder="Enter Custom Question text"
            required
            onChange={(event) => {
              setQuestionText(event.target.value);
            }}
          />
          <br />
          <br />{" "}
          <TextField
            id="subject-select"
            label="Subject"
            required
            select
            onChange={(event) => setSubject(event.target.value as TSubject)}
          >
            {sampleSubjects.map((subject) => (
              <MenuItem key={subject} value={subject}>
                {subject}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            id="jobPosition"
            label="Experience level"
            required
            select
            onChange={(event) => {
              setExperienceLevel(event.target.value as TExperienceLevel);
            }}
          >
            <MenuItem value="Any">Any Level</MenuItem>
            <MenuItem value="Entry">Entry Level</MenuItem>
            <MenuItem value="Mid">Mid Career</MenuItem>
            <MenuItem value="Senior">Senior Level</MenuItem>
          </TextField>
          <br />
          <br />
          <TextField
            id="questionType"
            label="Question Type"
            required
            select
            onChange={(event) => {
              setQuestionType(event.target.value as TQuestionType);
            }}
          >
            <MenuItem value="Behavioral">Behavioral</MenuItem>
            <MenuItem value="Technical">Technical</MenuItem>
          </TextField>
          <br />
          <TextField
            id="company"
            label="Company"
            placeholder="Enter the company who asked the question"
            helperText="Optional"
            onChange={(event) => {
              setCompany(event.target.value);
            }}
          />
          <div style={{ display: "flex", gap: "2rem" }}>
            <Button
              variant="contained"
              sx={{
                maxWidth: "50%",
                textAlign: "center",
                backgroundColor: "#023047",
              }}
              type="submit"
            >
              Add Question
            </Button>
            <Button
              variant="contained"
              sx={{
                maxWidth: "50%",
                textAlign: "center",
                backgroundColor: "#023047",
              }}
            >
              <Link
                href="/browsequestions"
                style={{ textDecoration: "none", color: "white" }}
              >
                Browse & Add Questions to a Set
              </Link>
            </Button>
          </div>
        </FormControl>
        <br />
      </form>
    </div>
  );
}

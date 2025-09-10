import useAuthContext from "@App/lib/auth/AuthContext";
import AuthGuard from "@App/lib/auth/AuthGuard";
import { useState, useEffect } from "react";

import QuestionService from "@App/lib/question/QuestionService";
import QuestionSetsService from "@App/lib/questionSets/QuestionSetsService";

import AddQuestionToSetModal from "@App/components/molecules/modals/AddQuestionToSetModal";

import styles from "@App/styles/BrowseQuestionsPage.module.scss";

import {
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Divider,
  TextField,
  Box,
  Checkbox,
  Select,
  MenuItem,
  FormControl,
  FormGroup,
  Button,
} from "@mui/material";

import AddIcon from "@mui/icons-material/Add";
import {
  TExperienceLevel,
  TQuestionType,
  TSubject,
} from "@App/lib/question/models";

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
  "Storytelling",
  "Scenarios"
];

function BrowseQuestionsPage() {
  const { currentUser } = useAuthContext();

  const RESULT_LIMIT = 20;

  const [popularityCheckbox, setPopularityCheckbox] = useState(true);
  const [experienceLevelSelect, setExperienceLevelSelect] = useState("Any");
  const [subjectSelect, setSubjectSelect] = useState("Any");
  const [typeSelect, setTypeSelect] = useState("Any");
  const [searchText, setSearchText] = useState("");

  const [showAddQuestionModal, setShowAddQuestionModal] = useState(false);

  const [selectedQuestion, setSelectedQuestion] = useState<any>({});

  const [questionsData, setQuestionsData] = useState<any[]>([]);
  const [userQuestionSets, setUserQuestionSets] = useState<any[]>([]);

  const [page, setPage] = useState(1);
  const [totalNumberOfQuestions, setTotalNumberOfQuestions] = useState(0);

  const [lastVisible, setLastVisible] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    console.log("fired");
    async function fetchQuestions() {
      setLoading(true);
      const questions = await QuestionService.getByFilters(
        subjectSelect as TSubject,
        typeSelect as TQuestionType,
        experienceLevelSelect as TExperienceLevel,
        popularityCheckbox,
        searchText.toLowerCase().trim(),
        RESULT_LIMIT,
        lastVisible
      );
      console.log(questions);
      let allq = await QuestionService.getAllQuestions();
      console.log(allq);
      let sub = await QuestionService.getByPopularityDesc();
      console.log(sub);
      setLastVisible(questions.docs[questions.docs.length - 1]);
      setQuestionsData(questions.docs.map((doc) => doc.data()));
      setLoading(false);
    }
    async function fetchUserQuestionSets() {
      const userQuestionSets: any[] = (
        await QuestionSetsService.getQuestionSetByUserId(currentUser!.id)
      ).docs.map((doc) => {
        return { id: doc.id, ...doc.data() };
      });
      setUserQuestionSets(userQuestionSets);
      let allqs = await QuestionSetsService.getAllQuestionSets();
      console.log(allqs);
    }

    fetchQuestions();
    fetchUserQuestionSets();
  }, []);

  useEffect(() => {
    async function getTotalNumberOfQuestions() {
      const questions = await QuestionService.getAllQuestions();
      setTotalNumberOfQuestions(questions.docs.length);
      console.log(questions);
    }
    getTotalNumberOfQuestions();
  }, []);

  const handleViewMore = async () => {
    setPage(page + 1);
    const data = await QuestionService.getByFilters(
      subjectSelect as TSubject,
      typeSelect as TQuestionType,
      experienceLevelSelect as TExperienceLevel,
      popularityCheckbox,
      searchText.toLowerCase().trim(),
      RESULT_LIMIT,
      lastVisible
    );
    setLastVisible(data.docs[data.docs.length - 1]);
    setQuestionsData(questionsData.concat(data.docs.map((doc) => doc.data())));
  };

  const handleFilterSubmit = async (
    event: React.FormEvent<HTMLButtonElement>
  ) => {
    event.preventDefault();
    setPage(page + 1);
    setLoading(true);
    const data = await QuestionService.getByFilters(
      subjectSelect as TSubject,
      typeSelect as TQuestionType,
      experienceLevelSelect as TExperienceLevel,
      popularityCheckbox,
      searchText.toLowerCase().trim(),
      RESULT_LIMIT,
      null
    );
    setLastVisible(data.docs[data.docs.length - 1]);
    setQuestionsData(data.docs.map((doc) => doc.data()));
    setLoading(false);
  };

  const handleTextFieldChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setSearchText(event.target.value);
  };

  const handleOpenAddQuestionModal = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    if (userQuestionSets.length === 0) {
      alert(
        "You have no question sets to add questions to. Please create a question set first."
      );
      return;
    }
    console.log(event);
    setSelectedQuestion(event);
    setShowAddQuestionModal(true);
  };

  const handleAddQuestionToSet = async (
    questionId: string,
    questionSetId: string
  ) => {
    await QuestionSetsService.addQuestionToSet(questionId, questionSetId);
  };

  return (
    <div className={styles.BrowseQuestionsPage}>
      <h1>Browse Questions</h1>
      <Box
        sx={{
          display: "flex",
          flexDirection: "row",
          verticalAlign: "top",
          mt: 2,
        }}
      >
        {loading ? (
          <p>Loading...</p>
        ) : (
          <List sx={{ bgcolor: "background.paper", width: "90%" }}>
            {questionsData.map((question) => (
              <div>
                <ListItem>
                  <ListItemIcon>
                    <IconButton
                      onClick={() => handleOpenAddQuestionModal(question)}
                    >
                      <AddIcon />
                    </IconButton>
                  </ListItemIcon>
                  <div>
                    <ListItemText
                      primary={question.question}
                      secondary={[
                        "Subject: " + question.subject,
                        "Type: " + question.type,
                        question.companies &&
                        question.companies.length > 0 &&
                        question.companies[0]
                          ? "Company: " + question.companies[0]
                          : null,
                      ]
                        .filter(Boolean)
                        .join(" | ")}
                    />
                    <ListItemText
                      secondary={"Experience: " + question.experienceLevel}
                    />
                  </div>
                </ListItem>
                <Divider />
              </div>
            ))}
            {page * RESULT_LIMIT >= totalNumberOfQuestions ? (
              <></>
            ) : (
              <Button variant="contained" onClick={() => handleViewMore()}>
                View More
              </Button>
            )}
          </List>
        )}
        <Box
          id="#filters"
          sx={{
            height: "50%",
            display: "flex",
            minWidth: "20%",
            flexDirection: "column",
            verticalAlign: "top",
            mt: 2,
            ml: 4,
            border: "1px solid black",
            padding: 4,
          }}
        >
          <h2>Filters</h2>

          {/* <FormControl size="small"> */}
          <TextField
            variant="outlined"
            size="small"
            label="Question Keyword Search"
            onChange={handleTextFieldChange}
          ></TextField>
          <label htmlFor="subject-select">Subject</label>
          <Select
            id="subject-select"
            value={subjectSelect}
            size="small"
            onChange={(event) => setSubjectSelect(event.target.value)}
          >
            <MenuItem key="any" value="Any">
              Any
            </MenuItem>
            {sampleSubjects.map((subject, index) => (
              <MenuItem key={index} value={subject}>
                {subject}
              </MenuItem>
            ))}
          </Select>
          <label htmlFor="type-select">Type</label>
          <Select
            id="type-select"
            value={typeSelect}
            size="small"
            onChange={(event) => setTypeSelect(event.target.value)}
          >
            <MenuItem key={"type-any"} value="Any">
              Any
            </MenuItem>
            <MenuItem key={"type-technical"} value="Technical">
              Technical
            </MenuItem>
            <MenuItem key={"type-behavioral"} value="Behavioral">
              Behavioral
            </MenuItem>
          </Select>
          <label htmlFor="experience-level-select">Experience Level</label>
          <Select
            id="experience-level-select"
            value={experienceLevelSelect}
            size="small"
            onChange={(event) => setExperienceLevelSelect(event.target.value)}
          >
            <MenuItem key={"experience-any"} value="Any">
              Any
            </MenuItem>
            <MenuItem key={"experience-entry"} value="Entry">
              Entry
            </MenuItem>
            <MenuItem key={"experience-mid"} value="Mid">
              Mid
            </MenuItem>
            <MenuItem key={"experience-senior"} value="Senior">
              Senior
            </MenuItem>
          </Select>
          <Button
            sx={{ mt: 1 }}
            variant="contained"
            onClick={handleFilterSubmit}
          >
            Apply Filters
          </Button>
          {/* </FormControl> */}
        </Box>
      </Box>
      {showAddQuestionModal && userQuestionSets && questionsData && (
        <AddQuestionToSetModal
          isOpen={showAddQuestionModal}
          handleClose={() => setShowAddQuestionModal(false)}
          handleAdd={handleAddQuestionToSet}
          modal="addModal"
          questionSets={userQuestionSets}
          question={selectedQuestion}
        />
      )}
    </div>
  );
}

export default function BrowseQuestions() {
  return (
    <AuthGuard>
      <BrowseQuestionsPage />
    </AuthGuard>
  );
}

import Link from "next/link";
import Avatar from "@App/components/atoms/Avatar";
import Card from "@App/components/atoms/Card";
import Grid from "@mui/material/Grid";
import useAuthContext from "@App/lib/auth/AuthContext";
import AuthGuard from "@App/lib/auth/AuthGuard";
import styles from "@App/styles/ProgressPage.module.scss";

function ProgressPage() {
  const { currentUser } = useAuthContext();
  return (
    <div className={styles.ProgressPage}>
      <h1>Your Progress</h1>
      <div className={styles.ProgressPage_avatarWrapper}>
        {currentUser?.data()?.avatarUrl && (
          <Avatar size={125} src={currentUser?.data()!.avatarUrl} />
        )}
      </div>
      <Grid
        className={styles.ProgressPage_body}
        container
        alignItems="center"
        justifyContent="center"
        columns={3}
      >
        <Card
          className={styles.ProgressPage_bodyCard}
          title="Followup Interview"
        >
          <Link href="/start" className={styles.linksText}>
            Start Followup Interview
          </Link>
          <p></p>
        </Card>
        <Card className={styles.ProgressPage_bodyCard} title="Big Five Score">
          Current Score: 75<br></br>
          Target Score: 100<br></br>
        </Card>
        <Card className={styles.ProgressPage_bodyCard} title="How to Improve">
          1) Make more eye contact<br></br>
          2) Say "Um" less<br></br>
        </Card>
        <Card
          className={styles.ProgressPage_bodyGraph}
          title="Graph of User's Score Progress"
        >
          <img
            src="sampleLineGraph.png"
            alt="Sample Graph"
            width="300"
            height="200"
          ></img>
        </Card>
      </Grid>
    </div>
  );
}

function ProgressInit() {
  const { currentUser } = useAuthContext();
  return (
    <div className={styles.ProgressPage}>
      <h1>Your Progress</h1>

      <div className={styles.ProgressPage_avatarWrapper}>
        {currentUser?.data()?.avatarUrl && (
          <Avatar size={125} src={currentUser?.data()!.avatarUrl} />
        )}
      </div>

      <div className={styles.ProgressPage_body}>
        <div className={styles.ProgressPage_bodyLeft}>
          <Card title="Initial Interview">
            <Link href="/video" className={styles.linksText}>
              Start an Interview
            </Link>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default function Progress() {
  //Store user's id here
  const { currentUser } = useAuthContext();
  let hasInterviewed = currentUser?.get("hasCompletedInterview");
  //Add flag to user that says if they've completed an interview or not
  if (hasInterviewed) {
    return (
      <AuthGuard>
        <ProgressPage />
      </AuthGuard>
    );
  } else {
    return (
      <AuthGuard>
        <ProgressInit />
      </AuthGuard>
    );
  }
}

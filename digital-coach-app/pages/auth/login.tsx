import { SubmitHandler, useForm } from "react-hook-form";
import Button from "@App/components/atoms/Button";
import useAuthContext from "@App/lib/auth/AuthContext";
import styles from "@App/styles/LoginPage.module.scss";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import Link from "next/link";
import UnAuthGuard from "@App/lib/auth/UnAuthGuard";
import { TextField } from "@App/components/molecules/TextField";
import LoginIcon from "@mui/icons-material/Login";
import CenteredComponent from "@App/components/atoms/CenteredComponent";

interface LoginFormInputs {
  email: string;
  password: string;
}

const inputValidationSchema = yup
  .object({
    email: yup
      .string()
      .email("Must be a valid email")
      .max(255)
      .required("Email is required"),
    password: yup.string().max(255).required("Password is required"),
  })
  .required();

export default function LoginPage() {
  const {
    error: authError,
    currentUser,
    // loginWithGoogle,
    login,
  } = useAuthContext();
  const {
    register,
    handleSubmit,
    formState: { errors: formError },
  } = useForm<LoginFormInputs>({
    mode: "onSubmit",
    resolver: yupResolver(inputValidationSchema),
  });

  const onSubmit: SubmitHandler<LoginFormInputs> = (data: LoginFormInputs) => {
    const { email, password } = data;
    login(email, password);
  };

  return (
    <UnAuthGuard>
      <CenteredComponent>
        <div className={styles.loginBox}>
          <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
            <div className={styles.logo}>
              <h1>Digital Coach</h1>
            </div>
            <h2>Login</h2>
            {authError && (
              <p className={styles.issue}>
                username and password did not match
              </p>
            )}
            <h3>Email</h3>
            <TextField type="email" placeholder="" {...register("email")} />
            {formError.email && <span>{formError.email.message}</span>}
            <h3>Password</h3>
            <TextField
              type="password"
              autoComplete="on"
              placeholder=""
              {...register("password")}
            />
            {formError.password && <span>{formError.password.message}</span>}

            <Button type="submit">
              <LoginIcon />
              Login
            </Button>
            {/* <Button onClick={loginWithGoogle}>Login with Google</Button> */}
            <Link href="/auth/signup">New user? sign up</Link>
          </form>
        </div>
      </CenteredComponent>
    </UnAuthGuard>
  );
}

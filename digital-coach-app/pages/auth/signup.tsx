import { useForm } from "react-hook-form";
import Button from "@App/components/atoms/Button";
import useAuthContext from "@App/lib/auth/AuthContext";
import styles from "@App/styles/LoginPage.module.scss";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { TextField } from "@App/components/molecules/TextField";
import Link from "next/link";
import UnAuthGuard from "@App/lib/auth/UnAuthGuard";
import CenteredComponent from "@App/components/atoms/CenteredComponent";
import HowToRegIcon from "@mui/icons-material/HowToReg";

interface LoginFormInputs {
  email: string;
  password: string;
  passwordConfirm: string;
}

const inputValidationSchema = yup
  .object({
    email: yup
      .string()
      .email("Must be a valid email")
      .max(255)
      .required("Email is required"),
    password: yup.string().min(7).max(255).required("Password is required"),
    passwordConfirm: yup
      .string()
      .oneOf([yup.ref("password"), null], "Passwords must match"),
  })
  .required();

export default function SignUpPage() {
  const { error: authError, currentUser, signup } = useAuthContext();
  const {
    register,
    handleSubmit,
    formState: { errors: formError },
  } = useForm<LoginFormInputs>({
    mode: "onSubmit",
    resolver: yupResolver(inputValidationSchema),
  });

  const onSubmit = (data: LoginFormInputs) => {
    const { email, password } = data;
    signup(email, password);
  };

  return (
    <UnAuthGuard>
      <CenteredComponent>
        <div className={styles.loginBox}>
          <h1>{currentUser?.id}</h1>
          <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
            <div className={styles.logo}>
              <h1>Digital Coach</h1>
            </div>
            <h2>Register an Account</h2>
            <h3>Email</h3>
            <TextField type="email" placeholder="" {...register("email")} />
            {formError.email && (
              <p className={styles.issue}>{formError.email.message}</p>
            )}
            <h3>Password</h3>
            <TextField
              type="password"
              autoComplete="on"
              placeholder=""
              {...register("password")}
            />
            {formError.password && (
              <p className={styles.issue}>{formError.password.message}</p>
            )}
            <h3>Confirm Password</h3>

            <TextField
              type="password"
              autoComplete="on"
              placeholder=""
              {...register("passwordConfirm")}
            />
            {formError.passwordConfirm && (
              <p className={styles.issue}>
                {formError.passwordConfirm.message}
              </p>
            )}

            <Button type="submit">
              <HowToRegIcon />
              Register
            </Button>
            <Link href="/auth/login">Have an account? log in</Link>
          </form>
        </div>
      </CenteredComponent>
    </UnAuthGuard>
  );
}

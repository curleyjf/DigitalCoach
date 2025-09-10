import classNames from "classnames";
import { PropsWithChildren } from "react";
import styles from "./Transcript.module.scss";

interface Props
  extends React.DetailedHTMLProps<
    React.HTMLAttributes<HTMLElement>,
    HTMLElement
  > {
  title?: string;
  multiline?: boolean;
  height?: string;
}

export default function Transcript(props: PropsWithChildren<Props>) {
  const { title, className, multiline, height, ...rest } = props;

  return (
    <section
      className={classNames(
        multiline ? styles.CardMulti : styles.Card,
        className
      )}
      style={{ height: height }}
      {...rest}
    >
      {title && <p className={styles.Cardtitle}>{title}</p>}
      {props.children}
    </section>
  );
}

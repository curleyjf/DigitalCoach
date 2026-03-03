import Image, { ImageProps } from "next/image";
import styles from "@App/styles/components/Avatar.module.scss";
import classNames from "classnames";

interface Props extends ImageProps {
  size?: number;
}

export default function Avatar(props: Props) {
  const { className, alt, size, height, width, ...rest } = props;

  return (
    <Image
      className={classNames(styles.Avatar, className)}
      alt={alt}
      height={height ?? size ?? 52}
      width={width ?? size ?? 52}
      unoptimized // Disable optimization for faster loading during development
      {...rest}
    />
  );
}

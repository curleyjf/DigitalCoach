/** @type {import('next').NextConfig} */
const withTM = require("next-transpile-modules")([
  "@fullcalendar/common",
  "@babel/preset-react",
  "@fullcalendar/common",
  "@fullcalendar/daygrid",
  "@fullcalendar/react",
]);
module.exports = withTM({
  reactStrictMode: true,
  images: {
    domains: ["localhost", "127.0.0.1"],
  },
  typescript:{
    ignoreBuildErrors: true,
  }
});

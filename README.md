# DigitalCoach

Senior Design Project for Fall 2022-Spring 2023

DigitalCoach is an AI-powered interview prep web application that allows job seekers to practice interviewing and receive immediate feedback. Some key features of DigitalCoach include creating interview sets from our database of questions and then recording corresponding video responses. Our AI uses machine learning models to analyze audio and video through a sentiment analysis. At the end, users are left with an overall score and actionable feedback.

For more detailed documentation on the different parts of the app ([frontend](/digital-coach-app/README.md), [ml-api](/ml-api/README.md), [ml model](/ml/README.md)) refer to the README.md file in the root directory of the folders.

# Setup Instructions

## Setup

1. Create a firebase app [here](https://console.firebase.google.com)
1. Create a service account for the firebase app you've created using the Google Cloud console with [instructions here](https://cloud.google.com/iam/docs/creating-managing-service-accounts#creating)
1. Populate the `.env` files in `digital-coach-app/` and `digital-coach-app/functions/` directory with the service account credentials. The files in the repository are just sample env files. Make sure that the files are named .env without the example part!
1. Install the latest stable version of Node [here](https://nodejs.org/en/)
1. Install yarn [here](https://classic.yarnpkg.com/en/docs/install)
1. Install Python 3.10 [here](https://www.python.org/downloads/)
1. Install redis [here](https://redis.io/docs/getting-started/)
1. Install pipenv [here](https://pipenv.pypa.io/en/latest/)
   - Make sure you run this in administrator mode if you're on Windows!
1. Install nltk with `pip install nltk`
1. Open python with `python` in the command line
   - Ensure you are running python 3.10!
1. Type into the python console:
   ```
   import nltk
   nltk.download()
   ```
   and download all packages in the UI prompt (sorry we didn't figure out which ones you really need)
1. Create an account with Assembly AI and get an API key
1. Populate the .env file in `ml-api/` with the API key from AssemblyAI. The files in the repository are just sample env files. Make sure that the files are named .env without the example part!
1. Ensure that firebase is connected: run `firebase login` and click the link to login and authenticate
1. Run `firebase projects:list` to see the projectId
1. Set the current project using the projectId from the previous step: `firebase use <projectId>`

## Frontend

- Prerequisites
  - Ensure you are running Windows or Ubuntu to avoid complier issues
  - Use Node v20.19.2

1. cd to the `digital-coach-app` directory
1. run `yarn install` to install dependencies for Next.JS
1. run `npm install -g firebase-tools` to install firebase
1. cd to the `functions` directory
1. run `yarn install` to install dependencies for the firebase functions
1. run `yarn add typescript@latest` to upgrade typescript
1. run `yarn build --skipLibCheck` to build the firebase functions modules
1. cd back to the `digital-coach-app` directory
1. run `yarn run emulate` to run the firebase emulator
1. in another terminal in the `digital-coach-app` directory, run `yarn run dev` to run the Next.JS dev server
1. Navigate to `localhost:3000/api/seed` to seed the database.

- The Next.JS dev server is served at `localhost:3000`
- The Firebase emulation console is served at `localhost:4000`

## Backend

1. start your redis server with the instructions from the installation page [here](https://redis.io/docs/getting-started/)
1. cd to the `ml-api` directory
1. run `pipenv install` to install the dependencies for the flask API
1. run `pipenv run serve` to start the Flask API server

# Technologies Used

## Frontend

- Next.JS
- React
- Firebase
  - Storage
  - Firestore
  - Functions
- Sass

## Build Tools

- Yarn
- Pipenv

## Machine Learning API

- Flask
- Redis

## Machine Learning Model

- RQ
- AssemblyAI
- FER
- Numpy
- Scipy
- Matplotlib
- Jupyter Notebook
- Keras
- OpenCV
- Tensorflow
- NLTK

# Members

- Ming Lin (Fullstack)
- Max Shi (Fullstack)
- Hamzah Nizami (Machine Learning)
- Suzy Shailesh (UX/UI Design)
- Michael McCreesh (QA)
- Aparajita Rana (Product Management)

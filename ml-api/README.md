This is the ML API server for Digital Coach, written in Flask.

Please install the Python package black on your machine. for linting purposes. More information here: https://github.com/psf/black

Setup at bottom of page

- If running using Nvidia GPU, Ctrl+C out of flask app and download all missing libraries mentioned in the Tensorflow console output.

- Note for team: Ensure env variable "FIREBASE_FUNCTIONS_ENDPOINT" exists (ml-api/db_monitor.py sends the results from redis to this specified Firebase database endpoint)
- Note ffmpeg must me installed

# RUNNING THE PRODUCTION FLASK SERVER

1. cd into ml-api folder
2. Enter `redis-cli` into console
   - If not running, enter `sudo service redis-server restart` to restart server
3. Enter `python -m flask` into console
4. Enter `gunicorn server.wsgi:app` into console
5. Open a new console and create a RedisQueue(RQ) Worker _instructions below_

## Different consoles

- RQ Worker:

  - Add new workers as deemed fit (only really need 1-4 workers at any given time during production, only need 1 for development)

  1.  create new console
  2.  cd into ml-api folder
  3.  enter `rq worker high default low` into console

- Redis console (_optional to keep terminal open, but redis server must always be running_):

  1.  cd into ml-api folder
  2.  If still in development, ensure redis server is running by entering `sudo service redis-server restart` into console
  3.  Enter `redis-cli` into console

  - `ping`: returns `PONG` if server is running
  - `keys *`: returns all active keys in redis (including active queue data and job/worker data)
  - `hgetall *insert-job-here*`: returns live data on current status of job
  - `flushall`: clears redis server of all data

## Testing

To test model output with specific video (IDEAL FOR TESTING):

1.  move your `.mp4` file to the `ml-api/data` folder and rename to `test.mp4`
2.  cd into ml-api folder and run `python test.py`

To test production server with specific video:

1.  Follow instructions in _RUNNING THE PRODUCTION FLASK SERVER_
    - Ensure there is at least one rq worker initialized
2.  move your `.mp4` file to the `ml-api/data` folder and rename to `test.mp4`
3.  send a Postman POST request to http://127.0.0.1:8000/predict
4.  wait until worker has completed job (can be monitored through rq workers terminal)
5.  use redis commands to monitor/view the job and response

To test with Firebase video submission:

- INCOMPLETE
- All results are stored in redis and are queued to send to specified Firebase endpoint
- Uncomment req conditions in main.py and db_monitor.py when implemented

# Setup

Confirm that you are running on python 3.10\*

1. cd into ml-api folder
2. Populate or create the .env file with the text below:
   - Note: Future groups must change `AAPI_KEY` variable
     AAPI_KEY='35071e34c03b44e2881c7bf5ee0d0134'
     UPLOAD_ENDPOINT = 'https://api.assemblyai.com/v2/upload'
     TRANSCRIPT_ENDPOINT = 'https://api.assemblyai.com/v2/transcript'
3. Create an empty folder in ml-api called `data` if it does not exist yet
4. Install gunicorn by entering `python -m pip install gunicorn` into console
5. Enter `pipenv install` into console to install dependencies
6. Enter `pipenv lock` into console to create Pipfile.lock file
7. For any missing packages, run `python -m pip install *packageName*`

Note: If you run into errors with finding `MutableMapping` when downloading missing packages, this is because post-Python3.8, they
have moved to the `Collections.abc` folder path instead of remaining inside `Collections` path. THIS IS STILL AN UNRESOLVED ERROR,
MAY BE FIXED IN FUTURE PYTHON VERSIONS.

1.  If possible, route any references of `MutableMapping` to the `Collections.abc` path and the flask app should compile. You can find these referenced at `/usr/lib/python3.10/dist-packages`.
    - If the errored package is not included with python, use pip to download the latest version and reference it at `/usr/local/lib/python3.10/dist-packages`.
2.  In the case that you do not have permissions to edit these dist-packages, please use pip to install the corresponding site-package
    instead of the preinstalled dist-package. Newer versions of these packages should not have the same issues, but you can reference the
    site-packages at `/usr/local/lib/python3.10/site-packages`.

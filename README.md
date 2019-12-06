# minesweeper-API description

## How to play?

* Go to https://rjaime.pythonanywhere.com/api/matches/
* Create a new match using the form and using POST button.
* Look for the match 'id' value.
* Go to https://rjaime.pythonanywhere.com/match/:id/
* Fill the coords in terms of row, column and choose action: Reveal, Flag/Unflag.
* Good luck!

## API details

### Authentication

By default all requests are automatically logged in as the same and unique user: common. 
The a simple multiple user feature is not difficult to add, requires some extra steps such as:
* user gets their chosen username passed to the requests to get authentincated as that user.
* each match belong to a user now, so we can activate the ownership controls.

### Errors

They are presented with fields 'detail' and optionally 'code'.

### API endpoints

* /api/matches/
  * GET:
    * Input: -
      * Response:
        * 200, {id, created_at, last_action_at}
        * 4xx/5xx, {detail: <>}
  * POST:
    * Input: rows (int), columns (int), mines (int)
      * Response:
        * 200, {id, created_at, last_action_at, board}
        * 4xx/5xx, {detail: <>}
* /api/matches/:id/
  * GET:
    * Input: -
    * Response:
      * 200, {id, created_at, last_action_at, board}
      * 4xx/5xx, {detail: <>}
  * DELETE:
    * Input: -
    * Response:
      * 204, {}
* /api/matches/:id/reveal/
  * POST:
    * Input: x, y (integer > 0)
    * Response:
      * 200, {target: [x, y], game_status: int, cells: {"(x, y)": cell_value, ..}}
      * 4xx/5xx, {detail: <>}
* /matches/:id/flag/
  * POST:
    * Input: x, y (integer > 0)
    * Response:
      * 200, {target: [x, y], game_status: int, cells: {"(x, y)": cell_value, ..}}
      * 4xx/5xx, {detail: <>}

## Game design:

* Game parameters:
  * Rows (> 0, max limit?)
  * Columns (> 0, max limit?)
  * Mines (> 0, max limit: c * r - 1)

* Properties:
  * There's at least 1 mine and at least 1 free cell.
  * Cells can be flagged.
  * Mines distribution is uniform (all cells have the same probability to have a mine).

## Data format

* Cells values:
  * are represented in the backend as:
    * -1: bomb
    * integer >= 0: bomb count
  * are stored in a TextField as a string representing lists of lists (numpy array string).
* Cells visibility:
  * is represented in the backend as:
    * 0: revealed
    * 1: hidden
    * 2: flagged
  * is exposed in the api as:
    * -2: hidden
    * -3: flagged
* Initially the client receives the whole board matrix. After performing an action, the client receives only the values to update in the board matrix.
* Revealed cells values are sent. If a cell is not revealed, instead of its value it will have the cell visibility representation
* In the matrix generation, the mines are placed in random cells with uniform probabilty. The mine counting for remaining cells is done through 2d convolution and a filter that sums inmediate neighbors (3x3).


## Database

* Sqlite3.

## Models

* Match
  * user (fk)
  * created_at (dt)
  * last_action_at (dt)
* Board
    * match (fk)
    * cells (str)
    * cells_visibility (str)
    * rows (int)
    * cols (int)
* User
    * username (str)
    * email (str)
    * password (str)
    * Using CustomUser model based on Django's AbstractUser, to be able to modify User fields in the future.


# minesweeper-API
API test

We ask that you complete the following challenge to evaluate your development skills. Please use the programming language and framework discussed during your interview to accomplish the following task.

## The Game
Develop the classic game of [Minesweeper](https://en.wikipedia.org/wiki/Minesweeper_(video_game))

## Show your work

1.  Create a Public repository ( please dont make a pull request, clone the private repository and create a new plublic one on your profile)
2.  Commit each step of your process so we can follow your thought process.

## What to build
The following is a list of items (prioritized from most important to least important) we wish to see:
* Design and implement  a documented RESTful API for the game (think of a mobile app for your API)
* Implement an API client library for the API designed above. Ideally, in a different language, of your preference, to the one used for the API
* When a cell with no adjacent mines is revealed, all adjacent squares will be revealed (and repeat)
* Ability to 'flag' a cell with a question mark or red flag
* Detect when game is over
* Persistence
* Time tracking
* Ability to start a new game and preserve/resume the old ones
* Ability to select the game parameters: number of rows, columns, and mines
* Ability to support multiple users/accounts
 
## Deliverables we expect:
* URL where the game can be accessed and played (use any platform of your preference: heroku.com, aws.amazon.com, etc)
* Code in a public Github repo
* README file with the decisions taken and important notes

## Time Spent
You do not need to fully complete the challenge. We suggest not to spend more than 5 hours total, which can be done over the course of 2 days.  Please make commits as often as possible so we can see the time you spent and please do not make one commit.  We will evaluate the code and time spent.
 
What we want to see is how well you handle yourself given the time you spend on the problem, how you think, and how you prioritize when time is insufficient to solve everything.

Please email your solution as soon as you have completed the challenge or the time is up.

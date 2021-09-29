DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    games_played INTEGER NOT NULL,
    quests_ans INTEGER NOT NULL,
    high_score INTEGER NOT NULL,
    admin_value INTEGER NOT NULL
);

DROP TABLE IF EXISTS quizTable;

CREATE TABLE quizTable
(
    quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    trueA TEXT NOT NULL,
    falseA TEXT NOT NULL,
    falseB TEXT NOT NULL,
    falseC TEXT NOT NULL,
    valid INTEGER NOT NULL
);

INSERT INTO quizTable (question, trueA, falseA, falseB, falseC, valid)
VALUES
  ('What is the capital of Ireland?', 'Dublin', 'Cork', 'Belfast', 'Galway', '1'),
  ('What is the name of a popular Japanese blue-haired virtual signer?', 'Hatsune Miku', 'Hikaru Utada', 'Kagamine Rin', 'Taneda Risa', '1'),
  ('What is the subtitle of the fifth live-action Resident Evil movie?', 'Retribution', 'Afterlife', 'The Final Chapter', 'Apocalypse', '1'),
  ('What is the 12th film in the Marvel Cinematic Universe?', 'Ant-Man', 'Captain America: Civil War', 'Avengers: Age of Ultron', 'Guardians of the Galaxy', '1'),
  ('What artist released the smash-hit song Old Town Road?', 'Lil Nas X', 'DaBaby', 'Takeshi69', 'Logic', '1'),
  ('Which of these is a part of the K-Pop group BTS?', 'Jin', 'Jonghyun', 'Kai', 'Sehun', '1'),
  ('Which of these is an enemy mob in Minecraft', 'Vindicator', 'Endertusk', 'Stalker', 'Lich', '1'),
  ('What album did Taylor Swift release in 2019?', 'Lover', 'evermore', 'reputation', 'folklore', '1'),
  ('What fighting game franchise features the character Ragna?', 'Blazblue', 'Street Fighter', 'Melty Blood', 'Tekken', '1'),
  ('Who wrote the Zero Escape series?', 'Kotaro Uchikoshi', 'Kinoko Nasu', 'Kazutaka Kodaka', 'amphibian', '1');
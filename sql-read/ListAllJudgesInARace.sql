SELECT Judge.FirstName, Judge.LastName, Judge.CountryCode
FROM Judge
         INNER JOIN RaceJudge ON (Judge.IDJudge = RaceJudge.IDJudge)
WHERE RaceJudge.IDRace = :race_id
ORDER BY Judge.LastName, Judge.FirstName;

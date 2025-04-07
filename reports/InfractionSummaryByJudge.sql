SELECT Judge.FirstName,
       Judge.LastName,
       IFNULL(MAX(CASE WHEN Color = 'Yellow' AND Infraction = '~' THEN NbrInfractions END), 0) YellowLOC,
       IFNULL(MAX(CASE WHEN Color = 'Yellow' AND Infraction = '<' THEN NbrInfractions END), 0) YellowBent,
       IFNULL(MAX(CASE WHEN Color = 'Red' AND Infraction = '~' THEN NbrInfractions END), 0)    RedLOC,
       IFNULL(MAX(CASE WHEN Color = 'Red' AND Infraction = '<' THEN NbrInfractions END), 0)    RedBent
FROM (SELECT Judge.FirstName,
             Judge.LastName,
             JudgeCall.Color,
             COUNT(JudgeCall.Infraction) AS NbrInfractions,
             JudgeCall.Infraction,
             Judge.IDJudge
      FROM RACE
               INNER JOIN RaceJudge ON (Race.IDRace = RaceJudge.IDRace)
               INNER JOIN Judge ON (RaceJudge.IDJudge = Judge.IDJudge)
               INNER JOIN JudgeCall ON (RaceJudge.IDJudge = JudgeCall.IDJudge) AND (RaceJudge.IDRace = JudgeCall.IDRace)
               INNER JOIN Bib ON (JudgeCall.BibNumber = Bib.BibNumber AND Bib.IDRace = :race_id)
               INNER JOIN Athlete ON (Athlete.IDAthlete = Bib.IDAthlete)
      WHERE (Race.IDRace = :race_id)
      GROUP BY JudgeCall.Color, JudgeCall.Infraction, Judge.IDJudge) JudgeInfractionSummarySub
         INNER JOIN Judge ON Judge.IDJudge = JudgeInfractionSummarySub.IDJudge
GROUP BY Judge.idJudge, Judge.FirstName, Judge.LastName
ORDER BY JudgeInfractionSummarySub.LastName, JudgeInfractionSummarySub.FirstName

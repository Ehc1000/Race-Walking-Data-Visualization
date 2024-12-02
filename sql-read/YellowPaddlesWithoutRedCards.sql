Select JudgeSelect.FirstName,
       JudgeSelect.LastName,
       max(case WHEN Infraction = '~' then InfractionCount else 0 end) LOC,
       max(case WHEN Infraction = '<' then InfractionCount else 0 end) Bent
FROM (SELECT Judge.FirstName, Judge.LastName, Judge.IDJudge
      FROM Judge
               INNER JOIN RaceJudge ON Judge.IDJudge = RaceJudge.IDJudge
      WHERE RaceJudge.IDRace = :race_id) JudgeSelect
         LEFT JOIN (Select RedCardSub.IDJudge, RedCardSub.Infraction, COUNT(RedCardSub.IDJudge) as InfractionCount
                    FROM (SELECT JudgeCall.Infraction, JudgeCall.BibNumber, JudgeCall.IDJudge, JudgeCall.IDRace
                          FROM JudgeCall
                                   INNER JOIN Bib
                                              ON (Bib.BibNumber = JudgeCall.BibNumber AND Bib.IDRace = JudgeCall.IDRace)
                                   INNER JOIN Athlete ON (Athlete.IDAthlete = Bib.IDAthlete)
                          WHERE JudgeCall.IDRace = :race_id
                          GROUP BY JudgeCall.BibNumber, JudgeCall.IDJudge, JudgeCall.IDRace, JudgeCall.Infraction
                          HAVING Count(JudgeCall.BibNumber) = 1
                             AND MAX(JudgeCall.Color) = 'Yellow') RedCardSub
                    GROUP BY RedCardSub.IDJudge, RedCardSub.Infraction) RedCardSubOuter
                   ON JudgeSelect.IDJudge = RedCardSubOuter.IDJudge
GROUP BY RedCardSubOuter.IDJudge, JudgeSelect.FirstName, JudgeSelect.LastName
ORDER BY JudgeSelect.LastName, JudgeSelect.FirstName

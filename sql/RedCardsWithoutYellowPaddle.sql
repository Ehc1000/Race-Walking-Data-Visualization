SELECT FirstName, LastName,
        SUM(CASE WHEN Color = 'Red' AND Infraction = '~' AND NOT EXISTS (
                SELECT * FROM JudgeCall J2
                WHERE J1.IDJudge = J2.IDJudge AND J1.IDRace = J2.IDRace AND J1.BibNumber = J2.BibNumber AND J2.Infraction = '~' AND J2.Color = 'Yellow' AND J2.TOD < J1.TOD LIMIT 1)
        THEN 1 ELSE 0 END) AS `# of ~ Red cards without Yellow`,
        
        SUM(CASE WHEN Color = 'Red' AND Infraction = '<' AND NOT EXISTS (
                SELECT * FROM JudgeCall J2
                WHERE J1.IDJudge = J2.IDJudge AND J1.IDRace = J2.IDRace AND J1.BibNumber = J2.BibNumber AND J2.Infraction = '<' AND J2.Color = 'Yellow' AND J2.TOD < J1.TOD LIMIT 1)
        THEN 1 ELSE 0 END) AS `# of < Red cards without Yellow`
                
FROM JudgeCall J1
JOIN Judge J ON J1.IDJudge = J.IDJudge
WHERE J1.IDRace = ?
Group By J1.IDJudge
Order By FirstName, LastName

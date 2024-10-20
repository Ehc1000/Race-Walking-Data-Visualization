SELECT BibNumber,FirstName, LastName,
max(case WHEN Color = 'Yellow' AND Infraction = '~' then NbrInfractions else 0  end) YellowLOC,
max(case WHEN Color = 'Yellow' AND Infraction = '<' then NbrInfractions else 0 end) YellowBent,
max(case WHEN Color = 'Red' AND Infraction = '~' then NbrInfractions else 0  end) RedLOC,
max(case WHEN Color = 'Red' AND Infraction = '<' then NbrInfractions else 0  end) RedBent
FROM 
(SELECT 
    Bib.BibNumber, 
    MAX(Athlete.LastName) as LastName, 
    MAX(Athlete.FirstName) AS FirstName, 
    JudgeCall.Color, JudgeCall.Infraction,
    COUNT(JudgeCall.Color) AS NbrInfractions
FROM 
    Athlete 
INNER JOIN Bib ON (Bib.IDAthlete = Athlete.IDAthlete)
INNER JOIN JudgeCall ON (Bib.BibNumber = JudgeCall.BibNumber AND Bib.IDRace = JudgeCall.IDRace) 
        WHERE JudgeCall.IDRace = ?
GROUP BY 
    Bib.BibNumber, JudgeCall.Color, JudgeCall.Infraction) AthleteInfractions
    GROUP BY AthleteInfractions.BibNumber
ORDER BY 
    AthleteInfractions.BibNumber
